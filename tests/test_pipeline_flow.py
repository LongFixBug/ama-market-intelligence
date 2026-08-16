import pytest
from unittest.mock import patch, MagicMock
from ml.pipelines.market_analysis_pipeline import execute_market_pipeline
from ml.schemas.market_report import MarketReport

@pytest.mark.asyncio
async def test_execute_market_pipeline_emits_ordered_events():
    """
    Test that the 7-step pipeline triggers the event_emitter in the correct sequential order
    and finishes with a valid MarketReport output.
    """
    emitted_stages = []

    async def mock_event_emitter(stage: str, message: str, report=None):
        emitted_stages.append(stage)

    # Mock Google Generative AI to avoid consuming real API quota during unit tests
    mock_plan_resp = MagicMock()
    mock_plan_resp.text = '["Đối thủ chính", "Bảng giá", "Khách hàng mục tiêu", "Rủi ro"]'

    mock_synth_resp = MagicMock()
    mock_synth_resp.text = """
    {
        "id": "rep-test-001",
        "topic": "Test Topic",
        "createdAt": "16/08/2026",
        "executive_summary": "Tóm tắt kiểm thử",
        "market_size_est": "1,000 Tỷ",
        "growth_rate": "15%",
        "target_audience": [{"title": "Người dùng", "desc": "Mô tả", "pain_points": ["Nỗi đau"]}],
        "market_gaps": [{"title": "Khoảng trống", "opportunity": "Cơ hội", "priority": "Cao"}],
        "swot": {"strengths": ["Mạnh"], "weaknesses": ["Yếu"], "opportunities": ["Cơ hội"], "threats": ["Rủi ro"]},
        "competitors": [{"name": "Đối thủ A", "type": "Trực tiếp", "positioning": "Định vị", "strengths": ["Mạnh"], "weaknesses": ["Yếu"], "price_range": "100k"}],
        "pricing": {"min_market_price": 50000, "median_market_price": 100000, "recommended_price": 90000, "premium_market_price": 200000, "unit": "VNĐ", "pricing_logic": "Lý do", "margin_est": "60%", "tiers": []},
        "risks": [{"category": "Thị trường", "risk_title": "Rủi ro A", "risk_level": "Cao", "impact": "Ảnh hưởng", "mitigation": "Giải pháp"}],
        "seo_strategy": [{"keyword": "từ khóa", "intent": "Mua hàng", "search_volume_est": "Cao", "competition": "Thấp", "content_angle": "Bài viết"}],
        "gtm_roadmap": [{"phase": "Pha 1", "timeline": "Tháng 1", "key_actions": ["Action 1"]}],
        "graph_data": {"nodes": [], "links": []}
    }
    """

    with patch("os.getenv", return_value="fake_key_for_testing"), \
         patch("google.generativeai.configure"), \
         patch("google.generativeai.GenerativeModel") as mock_model_cls, \
         patch("ml.pipelines.market_analysis_pipeline.search_and_scrape_sources", return_value=[{"title": "Doc 1", "url": "https://a.com", "content": "Nội dung"}]), \
         patch("ml.pipelines.market_analysis_pipeline.create_market_property_graph") as mock_graph_cls:

        # Mock the model responses
        mock_instance = MagicMock()
        mock_instance.generate_content.side_effect = [mock_plan_resp, mock_synth_resp]
        mock_model_cls.return_value = mock_instance

        # Mock query engine
        mock_query_engine = MagicMock()
        mock_query_engine.query.return_value = MagicMock(response="Graph retrieval result")
        mock_graph_cls.return_value.as_query_engine.return_value = mock_query_engine

        result = await execute_market_pipeline("Chủ đề kiểm thử", mock_event_emitter)

        # Validate sequential state transitions
        assert "planning" in emitted_stages
        assert "scraping" in emitted_stages
        assert "graph_rag" in emitted_stages
        assert "analyzing" in emitted_stages
        assert "synthesizing" in emitted_stages
        assert "completed" in emitted_stages
        assert emitted_stages == ["planning", "scraping", "graph_rag", "analyzing", "synthesizing", "completed"]

        # Validate returned schema
        assert result["topic"] == "Test Topic"
        assert result["pricing"]["recommended_price"] == 90000
