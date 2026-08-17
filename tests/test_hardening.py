from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from backend.app.rate_limit import InMemoryRateLimiter
from backend.app.schemas import AnalyzeRequest
from ml.pipelines.market_analysis_pipeline import execute_market_pipeline, normalize_queries


def test_analyze_request_normalizes_topic_and_rejects_unsafe_size():
    request = AnalyzeRequest(topic="  Nước   ép\nđóng chai  ")

    assert request.topic == "Nước ép đóng chai"

    with pytest.raises(ValidationError):
        AnalyzeRequest(topic="  ")

    with pytest.raises(ValidationError):
        AnalyzeRequest(topic="x" * 201)

    with pytest.raises(ValidationError):
        AnalyzeRequest(topic="thị trường\x00bẩn")


@pytest.mark.asyncio
async def test_in_memory_rate_limiter_blocks_after_limit():
    limiter = InMemoryRateLimiter(max_requests=2, window_seconds=60)

    assert (await limiter.check("client-a"))[0] is True
    assert (await limiter.check("client-a"))[0] is True
    allowed, retry_after = await limiter.check("client-a")

    assert allowed is False
    assert retry_after >= 1


def test_normalize_queries_is_bounded_and_deduplicated():
    queries = normalize_queries(
        ["  giá kindle  ", "giá kindle", "đối thủ kindle", "x" * 500, 42],
        topic="kinh doanh kindle",
    )

    assert queries == ["giá kindle", "đối thủ kindle"]
    assert len(queries) <= 3
    assert all(len(query) <= 200 for query in queries)


@pytest.mark.asyncio
async def test_pipeline_does_not_emit_completed_for_invalid_report():
    plan_response = MagicMock(
        choices=[MagicMock(message=MagicMock(content='["giá kindle"]'))]
    )
    malformed_report_response = MagicMock(
        choices=[MagicMock(message=MagicMock(content='{"id":"x","topic":"t"}'))]
    )
    client = MagicMock()
    client.chat.completions.create = AsyncMock(
        side_effect=[plan_response, malformed_report_response]
    )
    emitted_stages = []

    async def emit(stage, message, report=None):
        emitted_stages.append(stage)

    with patch(
        "ml.pipelines.market_analysis_pipeline.get_async_openai_client",
        return_value=client,
    ), patch(
        "ml.pipelines.market_analysis_pipeline.search_and_scrape_sources",
        return_value=[{"title": "Doc", "url": "https://example.com", "content": "Data"}],
    ):
        with pytest.raises(ValidationError):
            await execute_market_pipeline("t", emit)

    assert "completed" not in emitted_stages
