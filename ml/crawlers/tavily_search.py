import os
from typing import List, Dict
from tavily import TavilyClient
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

def get_tavily_client() -> TavilyClient | None:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return None
    return TavilyClient(api_key=api_key)

def clean_html_content(raw_html: str) -> str:
    """Sanitizes HTML content to readable plain text"""
    soup = BeautifulSoup(raw_html, "html.parser")
    # Remove script and style elements
    for script in soup(["script", "style", "nav", "footer", "header"]):
        script.extract()
    return soup.get_text(separator=" ", strip=True)

async def search_and_scrape_sources(queries: List[str]) -> List[Dict[str, str]]:
    """
    Search and fetch multi-angle market source documents.
    """
    client = get_tavily_client()
    if not client:
        return [
            {
                "url": "https://example.com/fallback-data",
                "title": f"Dữ liệu thị trường sơ bộ: {queries[0]}",
                "content": f"Báo cáo phân tích sơ bộ về {queries[0]} với các đối thủ dẫn đầu và bảng giá tham khảo.",
            }
        ]

    results = []
    seen_urls = set()

    for query in queries:
        try:
            res = client.search(
                query=query,
                search_depth="advanced",
                max_results=3,
                include_raw_content=True,
            )
            for item in res.get("results", []):
                url = item.get("url")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    raw = item.get("raw_content") or item.get("content") or ""
                    cleaned = clean_html_content(raw)
                    if len(cleaned) > 150:
                        results.append({
                            "url": url,
                            "title": item.get("title", ""),
                            "content": cleaned[:3500],
                        })
        except Exception as err:
            print(f"[Crawler Warning] Error querying '{query}': {err}")

    return results
