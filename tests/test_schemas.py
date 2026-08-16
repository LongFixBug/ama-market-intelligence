import pytest
from pydantic import ValidationError
from ml.schemas.market_report import (
    MarketReport,
    NicheAnalysis,
    PricingStrategy,
    RiskItem,
    AIPromptItem,
)

def test_market_report_valid_schema():
    """Test that a pragmatic MarketReport validates correctly"""
    report_data = {
        "id": "rep-kindle-001",
        "topic": "kinh doanh kindle",
        "createdAt": "16/08/2026 09:50",
        "niche_analysis": {
            "summary": "Thị trường máy đọc sách Kindle tập trung vào đối tượng học sinh, sinh viên...",
            "growth_potential": "Cao trong ngách mục tiêu",
        },
        "pricing": {
            "price_range": "2.500.000 VNĐ - 4.500.000 VNĐ",
            "rationale": "Mức giá này phù hợp với các dòng máy phổ biến như Kindle Paperwhite...",
            "tagline": "Tối ưu điểm hòa vốn & tỷ lệ chuyển đổi ban đầu",
        },
        "risks": [
            {
                "index": 1,
                "title": "Cạnh tranh gay gắt từ các thương hiệu máy đọc sách Android khác như Kobo, Boox.",
            }
        ],
        "seo_keywords": ["máy đọc sách kindle", "kindle paperwhite chính hãng"],
        "ai_prompts": [
            {
                "prompt": "Viết một bài đăng Facebook quảng cáo máy đọc sách Kindle Paperwhite..."
            }
        ],
    }

    report = MarketReport(**report_data)
    assert report.topic == "kinh doanh kindle"
    assert report.pricing.price_range == "2.500.000 VNĐ - 4.500.000 VNĐ"
    assert len(report.risks) == 1
    assert len(report.ai_prompts) == 1

def test_market_report_missing_field():
    """Test missing required field"""
    with pytest.raises(ValidationError):
        MarketReport(id="rep-1", createdAt="16/08/2026")
