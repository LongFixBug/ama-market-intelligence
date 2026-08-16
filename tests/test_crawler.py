import pytest
from ml.crawlers.tavily_search import clean_html_content, search_and_scrape_sources

def test_clean_html_content_removes_scripts_and_styles():
    """Test that scripts, styles, and unwanted tags are sanitized"""
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
async def test_search_and_scrape_sources_fallback():
    """Test fallback when no Tavily API key is provided"""
    # Should safely return fallback mock structure without crashing
    docs = await search_and_scrape_sources(["Nước ép trái cây"])
    assert len(docs) > 0
    assert "url" in docs[0]
    assert "title" in docs[0]
    assert "content" in docs[0]
