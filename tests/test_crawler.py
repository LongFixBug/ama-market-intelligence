from unittest.mock import patch

import pytest

from ml.crawlers.tavily_search import (
    SourceUnavailableError,
    clean_html_content,
    search_and_scrape_sources,
)


def test_clean_html_content_removes_scripts_and_styles():
    """Test that scripts, styles, and unwanted tags are sanitized."""
    raw_html = """
    <html>
        <head>
            <style>body { color: red; }</style>
            <script>alert('malicious');</script>
        </head>
        <body>
            <header><nav>Menu links</nav></header>
            <main>
                <h1>Cocoon Mỹ Phẩm Thuần Chay</h1>
                <p>Sản phẩm chiết xuất từ bí đao Đắk Lắk giá 245.000 VNĐ.</p>
            </main>
            <footer>Footer copyright 2026</footer>
        </body>
    </html>
    """
    cleaned = clean_html_content(raw_html)
    assert "alert" not in cleaned
    assert "color: red" not in cleaned
    assert "Cocoon Mỹ Phẩm Thuần Chay" in cleaned
    assert "245.000 VNĐ" in cleaned


@pytest.mark.asyncio
async def test_search_and_scrape_sources_fails_closed_without_tavily_key():
    """Missing live search credentials must never create a fake market source."""
    with patch("ml.crawlers.tavily_search.get_tavily_client", return_value=None):
        with pytest.raises(SourceUnavailableError, match="TAVILY_API_KEY"):
            await search_and_scrape_sources(["Nước ép trái cây"])


@pytest.mark.asyncio
async def test_search_and_scrape_sources_fails_closed_when_all_queries_fail():
    """An empty live search result must surface as unavailable rather than a fabricated fallback."""
    with patch("ml.crawlers.tavily_search.get_tavily_client", return_value=object()), \
         patch("ml.crawlers.tavily_search._search_single_query", return_value=[]):
        with pytest.raises(SourceUnavailableError, match="No trustworthy market sources"):
            await search_and_scrape_sources(["Nước ép trái cây"])
