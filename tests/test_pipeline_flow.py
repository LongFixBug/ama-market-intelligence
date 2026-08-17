import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ml.crawlers.tavily_search import SourceUnavailableError
from ml.pipelines.market_analysis_pipeline import execute_market_pipeline


def _response(content: str) -> MagicMock:
    choice = MagicMock()
    choice.message.content = content
    return MagicMock(choices=[choice])


def _valid_report_json() -> str:
    return json.dumps(
        {
            "id": "rep-kindle-test",
            "topic": "kinh doanh kindle",
            "createdAt": "16/08/2026 09:55",
            "niche_analysis": {
                "summary": (
                    "Thị trường máy đọc sách Kindle tập trung vào học sinh, sinh viên "
                    "và nhân viên văn phòng."
                ),
                "growth_potential": "Cao trong ngách mục tiêu",
            },
            "pricing": {
                "price_range": "2.500.000 VNĐ - 4.500.000 VNĐ",
                "rationale": (
                    "Mức giá này phù hợp với các dòng máy phổ biến như Kindle Paperwhite "
                    "theo dữ liệu nguồn."
                ),
                "tagline": "Tối ưu điểm hòa vốn & tỷ lệ chuyển đổi ban đầu",
            },
            "risks": [
                {"index": 1, "title": "Cạnh tranh gay gắt từ Kobo, Boox."},
                {"index": 2, "title": "Rủi ro nguồn hàng xách tay."},
                {"index": 3, "title": "Tâm lý người dùng e ngại màn hình đơn sắc."},
            ],
            "seo_keywords": [
                "máy đọc sách kindle",
                "kindle paperwhite chính hãng",
            ],
            "ai_prompts": [
                {
                    "prompt": (
                        "Viết một bài đăng Facebook quảng cáo máy đọc sách Kindle Paperwhite."
                    )
                }
            ],
        },
        ensure_ascii=False,
    )


@pytest.mark.asyncio
async def test_execute_market_pipeline_emits_ordered_events():
    emitted_stages = []

    async def mock_event_emitter(stage: str, message: str, report=None):
        emitted_stages.append(stage)

    mock_openai_client = MagicMock()
    mock_openai_client.chat.completions.create = AsyncMock(
        side_effect=[
            _response(
                '["Giá kindle paperwhite", "Đối thủ kobo boox", "Nhu cầu đọc sách"]'
            ),
            _response(_valid_report_json()),
        ]
    )

    source_content = (
        "Kindle Paperwhite và các máy Kobo, Boox đang được bán tại Việt Nam "
        "với nhiều phân khúc giá, kèm khác biệt về bảo hành và nguồn hàng."
    )

    with patch(
        "ml.pipelines.market_analysis_pipeline.get_async_openai_client",
        return_value=mock_openai_client,
    ), patch(
        "ml.pipelines.market_analysis_pipeline.search_and_scrape_sources",
        return_value=[
            {
                "title": "Doc 1",
                "url": "https://a.com",
                "content": source_content,
            }
        ],
    ):
        result = await execute_market_pipeline(
            "kinh doanh kindle",
            mock_event_emitter,
        )

    assert emitted_stages == ["planning", "scraping", "synthesizing", "completed"]
    assert result["topic"] == "kinh doanh kindle"
    assert result["pricing"]["price_range"] == "2.500.000 VNĐ - 4.500.000 VNĐ"
    assert len(result["risks"]) == 3
    assert len(result["ai_prompts"]) == 1
    assert result["sources"][0]["url"] == "https://a.com/"


@pytest.mark.asyncio
async def test_execute_market_pipeline_repairs_invalid_structured_output_once():
    emitted_stages = []

    async def mock_event_emitter(stage: str, message: str, report=None):
        emitted_stages.append(stage)

    mock_openai_client = MagicMock()
    mock_openai_client.chat.completions.create = AsyncMock(
        side_effect=[
            _response(
                '["Giá kindle paperwhite", "Đối thủ kobo boox", "Nhu cầu đọc sách"]'
            ),
            _response('{"topic":"kinh doanh kindle"}'),
            _response(_valid_report_json()),
        ]
    )

    source_content = (
        "Kindle Paperwhite có dữ liệu giá bán và thông tin đối thủ Kobo, Boox "
        "trên các kênh bán lẻ tại Việt Nam, đủ dài để trở thành nguồn hợp lệ."
    )

    with patch(
        "ml.pipelines.market_analysis_pipeline.get_async_openai_client",
        return_value=mock_openai_client,
    ), patch(
        "ml.pipelines.market_analysis_pipeline.search_and_scrape_sources",
        return_value=[
            {
                "title": "Doc 1",
                "url": "https://a.com",
                "content": source_content,
            }
        ],
    ):
        result = await execute_market_pipeline(
            "kinh doanh kindle",
            mock_event_emitter,
        )

    assert result["topic"] == "kinh doanh kindle"
    assert mock_openai_client.chat.completions.create.await_count == 3
    assert emitted_stages[-1] == "completed"


@pytest.mark.asyncio
async def test_execute_market_pipeline_rejects_untrusted_or_empty_sources():
    async def mock_event_emitter(stage: str, message: str, report=None):
        return None

    mock_openai_client = MagicMock()
    mock_openai_client.chat.completions.create = AsyncMock(
        return_value=_response(
            '["Giá kindle paperwhite", "Đối thủ kobo boox", "Nhu cầu đọc sách"]'
        )
    )

    with patch(
        "ml.pipelines.market_analysis_pipeline.get_async_openai_client",
        return_value=mock_openai_client,
    ), patch(
        "ml.pipelines.market_analysis_pipeline.search_and_scrape_sources",
        return_value=[
            {
                "title": "Bad source",
                "url": "not-a-url",
                "content": "short",
            }
        ],
    ):
        with pytest.raises(SourceUnavailableError):
            await execute_market_pipeline(
                "kinh doanh kindle",
                mock_event_emitter,
            )

    assert mock_openai_client.chat.completions.create.await_count == 1
