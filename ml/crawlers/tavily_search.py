from __future__ import annotations
import os
import asyncio
from typing import List, Dict, Optional, Any, Set
from tavily import TavilyClient
from bs4 import BeautifulSoup
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_env = os.path.abspath(os.path.join(current_dir, "../../backend/.env"))
if os.path.exists(backend_env):
    load_dotenv(backend_env)
else:
    load_dotenv()

def get_tavily_client() -> Optional[TavilyClient]:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return None
    return TavilyClient(api_key=api_key)

def clean_html_content(raw_html: str) -> str:
    """Sanitizes HTML content to readable plain text"""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.extract()
    return soup.get_text(separator=" ", strip=True)

def _search_single_query(client: TavilyClient, query: str) -> List[Dict[str, str]]:
    """Synchronous worker to run in thread for parallel execution"""
    try:
        res: Dict[str, Any] = client.search(
            query=query,
            search_depth="basic",
            max_results=3,
        )
        items = []
        for item in res.get("results", []):
            url: Optional[str] = item.get("url")
            content: str = item.get("content") or ""
            if url and len(content) > 60:
                items.append({
                    "url": url,
                    "title": item.get("title", ""),
                    "content": content[:2000],
                })
        return items
    except Exception as err:
        print(f"[Crawler Warning] Error querying '{query}': {err}")
        return []

async def search_and_scrape_sources(queries: List[str]) -> List[Dict[str, str]]:
    """
    Search and fetch multi-angle market source documents in PARALLEL (< 2 seconds).
    """
    client = get_tavily_client()
    if not client:
        return [
            {
                "url": "https://example.com/sample-market-data",
                "title": f"Dữ liệu thị trường sơ bộ: {queries[0] if queries else 'Thị trường'}",
                "content": "Báo cáo phân tích sơ bộ về thị trường với các đối thủ dẫn đầu và bảng giá tham khảo.",
            }
        ]

    # Run all search queries concurrently in parallel threads
    tasks = [asyncio.to_thread(_search_single_query, client, q) for q in queries]
    query_results = await asyncio.gather(*tasks, return_exceptions=True)

    results: List[Dict[str, str]] = []
    seen_urls: Set[str] = set()

    for batch in query_results:
        if isinstance(batch, list):
            for item in batch:
                url = item.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    results.append(item)

    return results
