from __future__ import annotations

import asyncio
import hashlib
import html
import os
import re
import unicodedata
from dataclasses import dataclass
from time import time
from typing import Protocol
from urllib.parse import quote

import httpx

from ml.agents.content_models import Platform, PlatformDraft, PublishResult


class Publisher(Protocol):
    platform: Platform

    async def publish(self, draft: PlatformDraft) -> PublishResult: ...

    async def verify(self, draft: PlatformDraft, result: PublishResult) -> bool: ...


class PublishError(RuntimeError):
    def __init__(self, code: str, detail: str):
        super().__init__(detail)
        self.code = code
        self.detail = detail


def _rate_limit_detail(response: httpx.Response, provider: str) -> str:
    retry_after = response.headers.get("retry-after")
    if retry_after and retry_after.isdigit():
        return f"{provider} rate limit reached; retry after {retry_after} seconds."
    reset = response.headers.get("x-rate-limit-reset")
    if reset and reset.isdigit():
        wait = max(1, int(reset) - int(time()))
        return f"{provider} rate limit reached; retry after {wait} seconds."
    return f"{provider} rate limit reached; retry later."


@dataclass
class MockPublisher:
    platform: Platform

    async def publish(self, draft: PlatformDraft) -> PublishResult:
        stable_id = hashlib.sha256(f"{self.platform.value}:{draft.content_hash or draft.body}".encode()).hexdigest()[:20]
        return PublishResult(
            platform=self.platform,
            success=True,
            code="mock_published",
            provider_post_id=f"mock-{stable_id}",
            published_url=f"https://example.com/mock/{self.platform.value}/{stable_id}",
            verified=True,
            detail="Mock publisher; no external platform was contacted.",
        )

    async def verify(self, draft: PlatformDraft, result: PublishResult) -> bool:
        return result.success and result.provider_post_id is not None


@dataclass
class UnavailablePublisher:
    platform: Platform
    missing: str

    async def publish(self, draft: PlatformDraft) -> PublishResult:
        return PublishResult(
            platform=self.platform,
            success=False,
            code="provider_not_configured",
            detail=f"Configure {self.missing} before live publishing.",
        )

    async def verify(self, draft: PlatformDraft, result: PublishResult) -> bool:
        return False


@dataclass
class XPublisher:
    consumer_key: str
    consumer_secret: str
    access_token: str
    access_token_secret: str
    platform: Platform = Platform.X

    async def publish(self, draft: PlatformDraft) -> PublishResult:
        return await asyncio.to_thread(self._publish_sync, draft)

    def _publish_sync(self, draft: PlatformDraft) -> PublishResult:
        from requests_oauthlib import OAuth1Session

        session = OAuth1Session(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=self.access_token,
            resource_owner_secret=self.access_token_secret,
        )
        response = session.post(
            "https://api.x.com/2/tweets",
            json={"text": draft.body},
            timeout=20,
        )
        if response.status_code == 429:
            raise PublishError("provider_rate_limited", _rate_limit_detail(response, "X"))
        if response.status_code != 201:
            raise PublishError("x_api_error", f"X API returned HTTP {response.status_code}")
        payload = response.json().get("data", {})
        post_id = str(payload.get("id", ""))
        if not post_id:
            raise PublishError("x_invalid_response", "X API did not return a post id")
        return PublishResult(
            platform=self.platform,
            success=True,
            code="published",
            provider_post_id=post_id,
            published_url=f"https://x.com/i/web/status/{post_id}",
        )

    async def verify(self, draft: PlatformDraft, result: PublishResult) -> bool:
        if not result.provider_post_id:
            return False
        return await asyncio.to_thread(self._verify_sync, result.provider_post_id)

    def _verify_sync(self, post_id: str) -> bool:
        from requests_oauthlib import OAuth1Session

        session = OAuth1Session(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=self.access_token,
            resource_owner_secret=self.access_token_secret,
        )
        response = session.get(f"https://api.x.com/2/tweets/{quote(post_id, safe='')}", timeout=20)
        return response.status_code == 200 and response.json().get("data", {}).get("id") == post_id


@dataclass
class LinkedInPublisher:
    access_token: str
    author_urn: str
    api_version: str
    platform: Platform = Platform.LINKEDIN

    async def publish(self, draft: PlatformDraft) -> PublishResult:
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
            "Linkedin-Version": self.api_version,
        }
        payload = {
            "author": self.author_urn,
            "commentary": draft.body,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post("https://api.linkedin.com/rest/posts", headers=headers, json=payload)
        if response.status_code == 429:
            raise PublishError("provider_rate_limited", _rate_limit_detail(response, "LinkedIn"))
        if response.status_code not in {200, 201}:
            raise PublishError("linkedin_api_error", f"LinkedIn API returned HTTP {response.status_code}")
        post_id = response.headers.get("x-restli-id") or str(response.json().get("id", ""))
        if not post_id:
            raise PublishError("linkedin_invalid_response", "LinkedIn API did not return a post id")
        return PublishResult(
            platform=self.platform,
            success=True,
            code="published",
            provider_post_id=post_id,
        )

    async def verify(self, draft: PlatformDraft, result: PublishResult) -> bool:
        if not result.provider_post_id:
            return False
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Linkedin-Version": self.api_version,
        }
        encoded = quote(result.provider_post_id, safe="")
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(f"https://api.linkedin.com/rest/posts/{encoded}", headers=headers)
        return response.status_code == 200


@dataclass
class FacebookPublisher:
    page_id: str
    page_access_token: str
    graph_version: str
    platform: Platform = Platform.FACEBOOK

    async def publish(self, draft: PlatformDraft) -> PublishResult:
        url = f"https://graph.facebook.com/{self.graph_version}/{self.page_id}/feed"
        headers = {"Authorization": f"Bearer {self.page_access_token}"}
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                url,
                headers=headers,
                data={"message": draft.body},
            )
        if response.status_code == 429:
            raise PublishError("provider_rate_limited", _rate_limit_detail(response, "Facebook"))
        if response.status_code not in {200, 201}:
            raise PublishError("facebook_api_error", f"Facebook API returned HTTP {response.status_code}")
        post_id = str(response.json().get("id", ""))
        if not post_id:
            raise PublishError("facebook_invalid_response", "Facebook API did not return a post id")
        return PublishResult(platform=self.platform, success=True, code="published", provider_post_id=post_id)

    async def verify(self, draft: PlatformDraft, result: PublishResult) -> bool:
        if not result.provider_post_id:
            return False
        url = f"https://graph.facebook.com/{self.graph_version}/{result.provider_post_id}"
        headers = {"Authorization": f"Bearer {self.page_access_token}"}
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url, headers=headers, params={"fields": "id"})
        return response.status_code == 200 and response.json().get("id") == result.provider_post_id


@dataclass
class WordPressPublisher:
    base_url: str
    username: str
    application_password: str
    platform: Platform = Platform.BLOG

    async def publish(self, draft: PlatformDraft) -> PublishResult:
        payload = self._build_payload(draft)
        url = f"{self.base_url.rstrip('/')}/wp-json/wp/v2/posts"
        async with httpx.AsyncClient(timeout=20, auth=(self.username, self.application_password)) as client:
            response = await client.post(url, json=payload)
        if response.status_code == 429:
            raise PublishError("provider_rate_limited", _rate_limit_detail(response, "WordPress"))
        if response.status_code != 201:
            raise PublishError("wordpress_api_error", f"WordPress API returned HTTP {response.status_code}")
        data = response.json()
        post_id = str(data.get("id", ""))
        if not post_id:
            raise PublishError("wordpress_invalid_response", "WordPress API did not return a post id")
        return PublishResult(
            platform=self.platform,
            success=True,
            code="published",
            provider_post_id=post_id,
            published_url=data.get("link"),
        )

    @staticmethod
    def _build_payload(draft: PlatformDraft) -> dict[str, str]:
        status = os.getenv("WORDPRESS_POST_STATUS", "publish")
        if status not in {"publish", "draft", "pending", "private"}:
            status = "publish"
        slug_source = draft.slug or draft.title or (draft.seo_keywords[0] if draft.seo_keywords else "ama-content")
        ascii_slug = slug_source.replace("đ", "d").replace("Đ", "D")
        ascii_slug = unicodedata.normalize("NFKD", ascii_slug).encode("ascii", "ignore").decode("ascii")
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_slug.lower()).strip("-")[:120] or "ama-content"
        return {
            "title": draft.title or "AMA Market Intelligence",
            "slug": slug,
            "excerpt": html.escape(draft.excerpt),
            "content": WordPressPublisher._markdown_to_html(draft.body),
            "status": status,
        }

    async def verify(self, draft: PlatformDraft, result: PublishResult) -> bool:
        if not result.provider_post_id:
            return False
        url = f"{self.base_url.rstrip('/')}/wp-json/wp/v2/posts/{quote(result.provider_post_id, safe='')}"
        async with httpx.AsyncClient(timeout=20, auth=(self.username, self.application_password)) as client:
            response = await client.get(url)
        return response.status_code == 200 and str(response.json().get("id")) == result.provider_post_id

    @staticmethod
    def _markdown_to_html(markdown: str) -> str:
        lines: list[str] = []
        for raw_line in markdown.splitlines():
            line = html.escape(raw_line.strip())
            if not line:
                continue
            if line.startswith("## "):
                lines.append(f"<h2>{line[3:]}</h2>")
            elif line.startswith("# "):
                lines.append(f"<h1>{line[2:]}</h1>")
            elif line.startswith("- "):
                lines.append(f"<li>{line[2:]}</li>")
            else:
                lines.append(f"<p>{line}</p>")
        return "\n".join(lines)


class PublisherRegistry:
    def __init__(self, publishers: dict[Platform, Publisher]):
        self.publishers = publishers

    async def publish(self, draft: PlatformDraft) -> PublishResult:
        try:
            publisher = self.publishers.get(draft.platform)
            if publisher is None:
                return PublishResult(
                    platform=draft.platform,
                    success=False,
                    code="provider_not_configured",
                    detail="No publisher connector is configured for this platform.",
                )
            return await publisher.publish(draft)
        except PublishError as exc:
            return PublishResult(platform=draft.platform, success=False, code=exc.code, detail=exc.detail)
        except Exception:
            return PublishResult(
                platform=draft.platform,
                success=False,
                code="provider_error",
                detail="Provider request failed; inspect server logs for the request id.",
            )

    async def verify(self, draft: PlatformDraft, result: PublishResult) -> bool:
        if not result.success:
            return False
        try:
            publisher = self.publishers.get(draft.platform)
            if publisher is None:
                return False
            return await publisher.verify(draft, result)
        except Exception:
            return False


def _env_complete(*names: str) -> bool:
    return all(os.getenv(name, "").strip() for name in names)


def build_publishers() -> PublisherRegistry:
    mode = os.getenv("PUBLISH_MODE", "live").strip().lower()
    if mode == "mock":
        return PublisherRegistry({platform: MockPublisher(platform) for platform in Platform})

    if _env_complete("WORDPRESS_BASE_URL", "WORDPRESS_USERNAME", "WORDPRESS_APPLICATION_PASSWORD"):
        publishers: dict[Platform, Publisher] = {
            Platform.BLOG: WordPressPublisher(
                base_url=os.environ["WORDPRESS_BASE_URL"],
                username=os.environ["WORDPRESS_USERNAME"],
                application_password=os.environ["WORDPRESS_APPLICATION_PASSWORD"],
            ),
        }
    else:
        publishers = {
            Platform.BLOG: UnavailablePublisher(
                Platform.BLOG,
                "WORDPRESS_BASE_URL/WORDPRESS_USERNAME/WORDPRESS_APPLICATION_PASSWORD",
            ),
        }
    if _env_complete("X_CONSUMER_KEY", "X_CONSUMER_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"):
        publishers[Platform.X] = XPublisher(
            consumer_key=os.environ["X_CONSUMER_KEY"],
            consumer_secret=os.environ["X_CONSUMER_SECRET"],
            access_token=os.environ["X_ACCESS_TOKEN"],
            access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
        )
    else:
        publishers[Platform.X] = UnavailablePublisher(
            Platform.X,
            "X_CONSUMER_KEY/X_CONSUMER_SECRET/X_ACCESS_TOKEN/X_ACCESS_TOKEN_SECRET",
        )

    if _env_complete("LINKEDIN_ACCESS_TOKEN", "LINKEDIN_AUTHOR_URN", "LINKEDIN_VERSION"):
        publishers[Platform.LINKEDIN] = LinkedInPublisher(
            access_token=os.environ["LINKEDIN_ACCESS_TOKEN"],
            author_urn=os.environ["LINKEDIN_AUTHOR_URN"],
            api_version=os.environ["LINKEDIN_VERSION"],
        )
    else:
        publishers[Platform.LINKEDIN] = UnavailablePublisher(
            Platform.LINKEDIN,
            "LINKEDIN_ACCESS_TOKEN/LINKEDIN_AUTHOR_URN/LINKEDIN_VERSION",
        )

    if _env_complete("META_PAGE_ID", "META_PAGE_ACCESS_TOKEN", "META_GRAPH_VERSION"):
        publishers[Platform.FACEBOOK] = FacebookPublisher(
            page_id=os.environ["META_PAGE_ID"],
            page_access_token=os.environ["META_PAGE_ACCESS_TOKEN"],
            graph_version=os.environ["META_GRAPH_VERSION"],
        )
    else:
        publishers[Platform.FACEBOOK] = UnavailablePublisher(
            Platform.FACEBOOK,
            "META_PAGE_ID/META_PAGE_ACCESS_TOKEN/META_GRAPH_VERSION",
        )

    return PublisherRegistry(publishers)
