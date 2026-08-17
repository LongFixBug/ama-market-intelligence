import os
import asyncio
import logging
from typing import List, Dict
from tavily import TavilyClient
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("ama.legacy_crawler")

def get_tavily_client():
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return None
    return TavilyClient(api_key=api_key)

async def search_and_scrape(queries: List[str]) -> List[Dict[str, str]]:
    """
    Search multi-perspective queries via Tavily and clean raw content.
    """
    client = get_tavily_client()
    if not client:
        # Fallback dummy data if no key configured yet
        return [
            {
                "url": "https://example.com/market-sample",
                "title": f"Báo cáo sơ bộ về {queries[0]}",
                "content": f"Dữ liệu thị trường cho {queries[0]} bao gồm các đối thủ chính, khoảng giá phổ biến và phân khúc khách hàng mục tiêu."
            }
        ]

    all_docs = []
    seen_urls = set()

    for query in queries:
        try:
            response = client.search(
                query=query,
                search_depth="advanced",
                max_results=3,
                include_raw_content=True
            )
            for res in response.get("results", []):
                url = res.get("url")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    raw_content = res.get("raw_content") or res.get("content") or ""
                    soup = BeautifulSoup(raw_content, "html.parser")
                    cleaned_text = soup.get_text(separator=" ", strip=True)
                    if len(cleaned_text) > 150:
                        all_docs.append({
                            "url": url,
                            "title": res.get("title", ""),
                            "content": cleaned_text[:3500]
                        })
        except Exception:
            logger.warning("Legacy crawler query failed", extra={"query_length": len(query)}, exc_info=True)

    return all_docs
