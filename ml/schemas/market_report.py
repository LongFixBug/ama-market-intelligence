from pydantic import BaseModel, Field
from typing import List, Optional

class NicheAnalysis(BaseModel):
    summary: str = Field(description="Đánh giá tiềm năng, USP và cơ hội cạnh tranh trong ngách")
    growth_potential: str = Field(default="Cao trong ngách mục tiêu", description="Tiềm năng tăng trưởng")

class PricingStrategy(BaseModel):
    price_range: str = Field(description="Khoảng giá tối ưu (ví dụ: 2.500.000 VNĐ - 4.500.000 VNĐ)")
    rationale: str = Field(description="Cơ sở & cơ chế định giá chi tiết")
    tagline: str = Field(default="Tối ưu điểm hòa vốn & tỷ lệ chuyển đổi ban đầu", description="Luận điểm hòa vốn")

class RiskItem(BaseModel):
    index: int = Field(description="Số thứ tự rủi ro 1, 2, 3")
    title: str = Field(description="Mô tả rủi ro và thách thức kinh doanh cụ thể")

class AIPromptItem(BaseModel):
    prompt: str = Field(description="Câu lệnh AI thực chiến (viết bài ads, so sánh đối thủ, kịch bản video TikTok)")

class MarketReport(BaseModel):
    id: str
    topic: str
    createdAt: str
    niche_analysis: NicheAnalysis
    pricing: PricingStrategy
    risks: List[RiskItem]
    seo_keywords: List[str]
    ai_prompts: List[AIPromptItem]
