import pytest
from pydantic import ValidationError
from ml.schemas.market_report import (
    MarketReport,
    CompetitorItem,
    PricingStrategy,
    PricingTier,
    RiskItem,
    SEOKeywordItem,
    SWOT,
    TargetAudience,
    MarketGap,
    GTMRoadmapPhase,
    KnowledgeGraphData,
    GraphNode,
    GraphLink,
)

def test_market_report_valid_schema():
    """Test that a fully populated MarketReport object validates correctly"""
    report_data = {
        "id": "rep-test-001",
        "topic": "Mỹ phẩm thuần chay Việt Nam",
        "createdAt": "16/08/2026 09:00",
        "executive_summary": "Tóm tắt thị trường mỹ phẩm thuần chay...",
        "market_size_est": "~2,400 Tỷ VNĐ",
        "growth_rate": "18.5% CAGR",
        "target_audience": [
            {
                "title": "Gen Z",
                "desc": "Người trẻ 18-25 tuổi",
                "pain_points": ["Ngân sách có hạn", "Sợ hàng giả"],
            }
        ],
        "market_gaps": [
            {
                "title": "Kem chống nắng kiềm dầu",
                "opportunity": "Chưa có sản phẩm thuần chay tối ưu kiềm dầu",
                "priority": "Cao",
            }
        ],
        "swot": {
            "strengths": ["Nguồn nguyên liệu dồi dào"],
            "weaknesses": ["Hạn sử dụng ngắn"],
            "opportunities": ["Bùng nổ TikTok Shop"],
            "threats": ["Cạnh tranh đối thủ ngoại"],
        },
        "competitors": [
            {
                "name": "Cocoon Vietnam",
                "type": "Trực tiếp",
                "positioning": "Thương hiệu thuần chay 100%",
                "strengths": ["Thương hiệu dẫn đầu"],
                "weaknesses": ["Chưa có dòng active mạnh"],
                "price_range": "120.000đ - 380.000đ",
                "market_share_est": "38%",
                "website": "https://cocoonvietnam.com",
            }
        ],
        "pricing": {
            "min_market_price": 120000,
            "median_market_price": 260000,
            "recommended_price": 245000,
            "premium_market_price": 580000,
            "unit": "VNĐ / sản phẩm",
            "pricing_logic": "Sweet spot phân khúc Mass-Premium",
            "margin_est": "65%",
            "tiers": [
                {
                    "tier": "Starter Size",
                    "price": 145000,
                    "description": "Dung tích 50ml",
                    "features": ["Giảm rào cản thử nghiệm"],
                }
            ],
        },
        "risks": [
            {
                "category": "Pháp lý",
                "risk_title": "Rủi ro chứng chỉ thuần chay",
                "risk_level": "Cao",
                "impact": "Ảnh hưởng uy tín",
                "mitigation": "Công khai chứng chỉ kiểm nghiệm",
            }
        ],
        "seo_strategy": [
            {
                "keyword": "mỹ phẩm thuần chay",
                "intent": "Mua hàng (Commercial)",
                "search_volume_est": "Cao",
                "competition": "Cao",
                "content_angle": "Top 10 mỹ phẩm thuần chay tốt nhất",
            }
        ],
        "gtm_roadmap": [
            {
                "phase": "Giai đoạn 1",
                "timeline": "Tháng 1",
                "key_actions": ["Seeding sản phẩm mẫu"],
            }
        ],
        "graph_data": {
            "nodes": [
                {"id": "market", "name": "Mỹ phẩm", "category": "product", "size": 24},
                {"id": "cocoon", "name": "Cocoon", "category": "competitor", "size": 18},
            ],
            "links": [
                {"source": "market", "target": "cocoon", "relationship": "COMPETES_WITH"}
            ],
        },
    }

    report = MarketReport(**report_data)
    assert report.id == "rep-test-001"
    assert report.topic == "Mỹ phẩm thuần chay Việt Nam"
    assert len(report.competitors) == 1
    assert report.competitors[0].name == "Cocoon Vietnam"
    assert report.pricing.recommended_price == 245000
    assert len(report.graph_data.nodes) == 2

def test_market_report_missing_required_field_raises_validation_error():
    """Test that missing required fields properly raises a ValidationError"""
    invalid_data = {
        "id": "rep-002",
        # topic is missing!
        "createdAt": "16/08/2026",
    }
    with pytest.raises(ValidationError):
        MarketReport(**invalid_data)
