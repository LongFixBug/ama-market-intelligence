import pytest
import httpx

import backend.app.services.publishers as publishers_module
from backend.app.services.publishers import PublisherRegistry, WordPressPublisher, build_publishers
from ml.agents.content_models import Platform, PlatformDraft


@pytest.mark.asyncio
async def test_mock_publishers_return_stable_provider_ids(monkeypatch):
    monkeypatch.setenv("PUBLISH_MODE", "mock")
    registry = build_publishers()
    draft = PlatformDraft(
        id="draft-001",
        platform=Platform.X,
        title="",
        body="Một nội dung kiểm thử.",
    )

    first = await registry.publish(draft)
    second = await registry.publish(draft)

    assert first.success is True
    assert first.provider_post_id == second.provider_post_id
    assert await registry.verify(draft, first) is True


@pytest.mark.asyncio
async def test_live_publisher_is_not_available_without_credentials(monkeypatch):
    monkeypatch.delenv("PUBLISH_MODE", raising=False)
    for name in (
        "X_CONSUMER_KEY",
        "X_CONSUMER_SECRET",
        "X_ACCESS_TOKEN",
        "X_ACCESS_TOKEN_SECRET",
    ):
        monkeypatch.delenv(name, raising=False)

    registry = build_publishers()
    result = await registry.publish(
            PlatformDraft(id="draft-002", platform=Platform.X, title="", body="test")
    )

    assert result.success is False
    assert result.code == "provider_not_configured"


@pytest.mark.asyncio
async def test_live_mode_fails_closed_for_every_unconfigured_platform(monkeypatch):
    monkeypatch.delenv("PUBLISH_MODE", raising=False)
    for name in (
        "WORDPRESS_BASE_URL",
        "WORDPRESS_USERNAME",
        "WORDPRESS_APPLICATION_PASSWORD",
        "X_CONSUMER_KEY",
        "X_CONSUMER_SECRET",
        "X_ACCESS_TOKEN",
        "X_ACCESS_TOKEN_SECRET",
        "LINKEDIN_ACCESS_TOKEN",
        "LINKEDIN_AUTHOR_URN",
        "LINKEDIN_VERSION",
        "META_PAGE_ID",
        "META_PAGE_ACCESS_TOKEN",
        "META_GRAPH_VERSION",
    ):
        monkeypatch.delenv(name, raising=False)

    registry = build_publishers()
    for platform in Platform:
        result = await registry.publish(
            PlatformDraft(id=f"draft-{platform.value}-missing", platform=platform, title="", body="test")
        )
        assert result.success is False
        assert result.code == "provider_not_configured"


@pytest.mark.asyncio
async def test_missing_registry_platform_fails_closed():
    registry = PublisherRegistry({})
    result = await registry.publish(
        PlatformDraft(id="draft-003", platform=Platform.X, title="", body="test")
    )

    assert result.success is False
    assert result.code == "provider_not_configured"
    assert await registry.verify(
        PlatformDraft(id="draft-003", platform=Platform.X, title="", body="test"), result
    ) is False


def test_wordpress_markdown_renderer_escapes_html():
    rendered = WordPressPublisher._markdown_to_html(
        "# Title\n\n<script>alert('x')</script>\n\n- item"
    )

    assert "<script>" not in rendered
    assert "&lt;script&gt;" in rendered
    assert "<h1>Title</h1>" in rendered


def test_wordpress_payload_contains_safe_seo_slug_and_excerpt():
    payload = WordPressPublisher._build_payload(
        PlatformDraft(
            id="draft-seo-001",
            platform=Platform.BLOG,
            title="Máy đọc sách Kindle chính hãng",
            slug="máy đọc sách kindle",
            excerpt="Tóm tắt <script>không chạy</script>",
            body="# Nội dung",
        )
    )

    assert payload["slug"] == "may-doc-sach-kindle"
    assert "<script>" not in payload["excerpt"]
    assert "&lt;script&gt;" in payload["excerpt"]


class FakeAsyncClient:
    calls = []

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, **kwargs):
        self.calls.append(("post", url, kwargs))
        if "linkedin.com" in url:
            return httpx.Response(201, headers={"x-restli-id": "urn:li:share:1"}, json={})
        return httpx.Response(201, json={"id": 42, "link": "https://example.com/post/42"})

    async def get(self, url, **kwargs):
        self.calls.append(("get", url, kwargs))
        post_id = "urn:li:share:1" if "linkedin.com" in url else "42"
        return httpx.Response(200, json={"id": post_id})


@pytest.mark.asyncio
async def test_live_http_connectors_use_expected_auth_and_payloads(monkeypatch):
    FakeAsyncClient.calls = []
    monkeypatch.setattr(publishers_module.httpx, "AsyncClient", FakeAsyncClient)

    linkedin = publishers_module.LinkedInPublisher("li-secret", "urn:li:person:1", "202601")
    linkedin_draft = PlatformDraft(
        id="draft-li-001",
        platform=Platform.LINKEDIN,
        title="",
        body="LinkedIn content",
    )
    linkedin_result = await linkedin.publish(linkedin_draft)
    assert linkedin_result.provider_post_id == "urn:li:share:1"
    linkedin_call = next(call for call in FakeAsyncClient.calls if "linkedin.com" in call[1])
    assert linkedin_call[2]["headers"]["Authorization"] == "Bearer li-secret"
    assert linkedin_call[2]["json"]["commentary"] == "LinkedIn content"

    facebook = publishers_module.FacebookPublisher("page-1", "fb-secret", "v23.0")
    facebook_draft = PlatformDraft(
        id="draft-fb-001",
        platform=Platform.FACEBOOK,
        title="",
        body="Facebook content",
    )
    facebook_result = await facebook.publish(facebook_draft)
    assert facebook_result.provider_post_id == "42"
    facebook_call = next(call for call in FakeAsyncClient.calls if "graph.facebook.com" in call[1])
    assert facebook_call[2]["headers"]["Authorization"] == "Bearer fb-secret"
    assert "access_token" not in facebook_call[2].get("params", {})
