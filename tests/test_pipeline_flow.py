import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from ml.pipelines.market_analysis_pipeline import execute_market_pipeline

@pytest.mark.asyncio
async def test_execute_market_pipeline_deepseek_emits_ordered_events():
    """
    Test that the pragmatic multi-agent pipeline triggers the event_emitter in the correct sequential order
    and returns a valid pragmatic business report.
    """
    emitted_stages = []

    async def mock_event_emitter(stage: str, message: str, report=None):
        emitted_stages.append(stage)

    # Mock OpenCode Go / DeepSeek Chat Completion Responses
    mock_plan_choice = MagicMock()
    mock_plan_choice.message.content = '["Giá kindle paperwhite", "Đối thủ kobo boox", "Nhu cầu đọc sách"]'
    mock_plan_resp = MagicMock(choices=[mock_plan_choice])

    mock_synth_choice = MagicMock()
    mock_synth_choice.message.content = """
    {
        "id": "rep-kindle-test",
        "topic": "kinh doanh kindle",
        "createdAt": "16/08/2026 09:55",
        "niche_analysis": {
            "summary": "Thị trường máy đọc sách Kindle tập trung vào đối tượng học sinh, sinh viên, nhân viên văn phòng...",
            "growth_potential": "Cao trong ngách mục tiêu"
        },
        "pricing": {
            "price_range": "2.500.000 VNĐ - 4.500.000 VNĐ",
            "rationale": "Mức giá này phù hợp với các dòng máy phổ biến như Kindle Paperwhite...",
            "tagline": "Tối ưu điểm hòa vốn & tỷ lệ chuyển đổi ban đầu"
        },
        "risks": [
            {"index": 1, "title": "Cạnh tranh gay gắt từ Kobo, Boox."},
            {"index": 2, "title": "Rủi ro nguồn hàng xách tay."},
            {"index": 3, "title": "Tâm lý người dùng e ngại màn hình đơn sắc."}
        ],
        "seo_keywords": ["máy đọc sách kindle", "kindle paperwhite chính hãng"],
        "ai_prompts": [
            {"prompt": "Viết một bài đăng Facebook quảng cáo máy đọc sách Kindle Paperwhite..."}
        ]
    }
    """
    mock_synth_resp = MagicMock(choices=[mock_synth_choice])

    mock_openai_client = MagicMock()
    mock_openai_client.chat.completions.create = AsyncMock(side_effect=[mock_plan_resp, mock_synth_resp])

    with patch("ml.pipelines.market_analysis_pipeline.get_async_openai_client", return_value=mock_openai_client), \
         patch("ml.pipelines.market_analysis_pipeline.search_and_scrape_sources", return_value=[{"title": "Doc 1", "url": "https://a.com", "content": "Nội dung"}]):

        result = await execute_market_pipeline("kinh doanh kindle", mock_event_emitter)

        # Validate sequential state transitions
        assert emitted_stages == ["planning", "scraping", "synthesizing", "completed"]

        # Validate returned schema
        assert result["topic"] == "kinh doanh kindle"
        assert result["pricing"]["price_range"] == "2.500.000 VNĐ - 4.500.000 VNĐ"
        assert len(result["risks"]) == 3
        assert len(result["ai_prompts"]) == 1
