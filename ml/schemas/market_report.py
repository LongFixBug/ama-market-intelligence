from pydantic import BaseModel, Field
from typing import List, Optional
from pydantic import AnyHttpUrl

class NicheAnalysis(BaseModel):
    summary: str = Field(
        min_length=1,
        max_length=5000,
        description="Đánh giá tiềm năng, USP và cơ hội cạnh tranh trong ngách",
    )
    growth_potential: str = Field(
        default="Cao trong ngách mục tiêu",
        max_length=200,
        description="Tiềm năng tăng trưởng",
    )

class PricingStrategy(BaseModel):
    price_range: str = Field(
        min_length=1,
        max_length=300,
        description="Khoảng giá tối ưu (ví dụ: 2.500.000 VNĐ - 4.500.000 VNĐ)",
    )
    rationale: str = Field(
        min_length=1,
        max_length=5000,
        description="Cơ sở & cơ chế định giá chi tiết",
    )
    tagline: str = Field(
        default="Tối ưu điểm hòa vốn & tỷ lệ chuyển đổi ban đầu",
        max_length=300,
        description="Luận điểm hòa vốn",
    )

class RiskItem(BaseModel):
    index: int = Field(ge=1, le=20, description="Số thứ tự rủi ro 1, 2, 3")
    title: str = Field(
        min_length=1,
        max_length=1000,
        description="Mô tả rủi ro và thách thức kinh doanh cụ thể",
    )

class AIPromptItem(BaseModel):
    prompt: str = Field(
        min_length=1,
        max_length=3000,
        description="Câu lệnh AI thực chiến (viết bài ads, so sánh đối thủ, kịch bản video TikTok)",
    )


class SourceRef(BaseModel):
    title: str = Field(default="", max_length=300)
    url: AnyHttpUrl
    snippet: str = Field(default="", max_length=2000)
    published_at: Optional[str] = Field(default=None, max_length=80)

class MarketReport(BaseModel):
    id: str = Field(min_length=1, max_length=100)
    topic: str = Field(min_length=2, max_length=200)
    createdAt: str = Field(min_length=1, max_length=80)
    niche_analysis: NicheAnalysis
    pricing: PricingStrategy
    risks: List[RiskItem] = Field(max_length=20)
    seo_keywords: List[str] = Field(max_length=50)
    ai_prompts: List[AIPromptItem] = Field(max_length=20)
    sources: List[SourceRef] = Field(default_factory=list, max_length=20)
