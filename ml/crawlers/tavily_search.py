from __future__ import annotations

import asyncio
import logging
import os
from functools import lru_cache
from typing import Any, Dict, List, Optional, Set

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from tavily import TavilyClient

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_env = os.path.abspath(os.path.join(current_dir, "../../backend/.env"))
if os.path.exists(backend_env):
    load_dotenv(backend_env)
else:
    load_dotenv()

logger = logging.getLogger("ama.crawler")


class SourceUnavailableError(RuntimeError):
    """Raised when the live market-source layer cannot provide trustworthy data."""


@lru_cache(maxsize=1)
def get_tavily_client() -> Optional[TavilyClient]:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return None
    return TavilyClient(api_key=api_key)


def clean_html_content(raw_html: str) -> str:
    """Sanitize HTML content to readable plain text."""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.extract()
    return soup.get_text(separator=" ", strip=True)


def _search_single_query(client: TavilyClient, query: str) -> List[Dict[str, str]]:
    """Synchronous worker to run in a thread for parallel execution."""
    try:
        res: Dict[str, Any] = client.search(
            query=query,
            search_depth="basic",
            max_results=3,
        )
        items: List[Dict[str, str]] = []
        for item in res.get("results", []):
            url: Optional[str] = item.get("url")
            content: str = item.get("content") or ""
            if url and len(content) > 60:
                items.append(
                    {
                        "url": url,
                        "title": item.get("title", ""),
                        "content": content[:3000],
                    }
                )
        return items
    except Exception:
        logger.warning(
            "Tavily query failed",
            extra={"query_length": len(query)},
            exc_info=True,
        )
        return []


def normalize_queries(raw_queries: Any, topic: str) -> List[str]:
    """Keep planner output small and predictable before it reaches Tavily."""
    candidates = raw_queries if isinstance(raw_queries, list) else []
    normalized: List[str] = []
    seen: Set[str] = set()

    for candidate in candidates:
        if not isinstance(candidate, str):
            continue
        query = " ".join(candidate.split())
        if len(query) < 3 or len(query) > 200:
            continue
        key = query.casefold()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(query)
        if len(normalized) == 3:
            break

    if normalized:
        return normalized

    safe_topic = " ".join(str(topic).split())[:160].strip() or "thị trường"
    return [
        f"giá {safe_topic}",
        f"đối thủ {safe_topic}",
        f"kinh doanh {safe_topic}",
    ]


async def search_and_scrape_sources(queries: List[str]) -> List[Dict[str, str]]:
    """Search multiple market angles in parallel and fail closed without real sources."""
    bounded_queries = [
        query
        for query in queries[:3]
        if isinstance(query, str) and 3 <= len(query) <= 200
    ]
    if not bounded_queries:
        raise SourceUnavailableError("No valid market-search queries were provided")

    client = get_tavily_client()
    if not client:
        logger.error("TAVILY_API_KEY is not configured; refusing to fabricate market sources")
        raise SourceUnavailableError("TAVILY_API_KEY is not configured")

    semaphore = asyncio.Semaphore(3)

    async def run_query(query: str) -> List[Dict[str, str]]:
        async with semaphore:
            try:
                return await asyncio.wait_for(
                    asyncio.to_thread(_search_single_query, client, query),
                    timeout=10,
                )
            except asyncio.TimeoutError:
                logger.warning(
                    "Tavily query timed out",
                    extra={"query_length": len(query)},
                )
                return []

    query_results = await asyncio.gather(
        *(run_query(query) for query in bounded_queries),
    )

    results: List[Dict[str, str]] = []
    seen_urls: Set[str] = set()

    for batch in query_results:
        for item in batch:
            url = item.get("url", "").strip()
            if url and url not in seen_urls:
                seen_urls.add(url)
                results.append(item)

    if not results:
        raise SourceUnavailableError("No trustworthy market sources were retrieved")

    return results
