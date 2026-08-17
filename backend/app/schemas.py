import re
import unicodedata
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Literal, Optional

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator

from ml.agents.content_models import Platform
from ml.schemas.market_report import MarketReport


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    topic: str = Field(min_length=2, max_length=200)

    @field_validator("topic", mode="before")
    @classmethod
    def normalize_topic(cls, value: object) -> str:
        if not isinstance(value, str):
            raise ValueError("topic must be a string")

        normalized = unicodedata.normalize("NFC", " ".join(value.split()))
        if re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", normalized):
            raise ValueError("topic contains control characters")
        return normalized


class ContentCampaignRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    report: MarketReport
    platforms: list[Platform] = Field(
        default_factory=lambda: [Platform.BLOG, Platform.X, Platform.LINKEDIN, Platform.FACEBOOK],
        min_length=1,
        max_length=4,
    )
    canonical_url: AnyHttpUrl | None = None
    # A caller must not turn off the human gate through the public API. An
    # explicitly authenticated internal automation path can be added later.
    approval_required: Literal[True] = True
    scheduled_at: datetime | None = None

    @field_validator("platforms")
    @classmethod
    def unique_platforms(cls, value: list[Platform]) -> list[Platform]:
        unique = list(dict.fromkeys(value))
        if not unique:
            raise ValueError("at least one platform is required")
        return unique

    @field_validator("scheduled_at")
    @classmethod
    def normalize_schedule_timezone(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            normalized = value.replace(tzinfo=timezone.utc)
        else:
            normalized = value.astimezone(timezone.utc)
        now = datetime.now(timezone.utc)
        if normalized <= now:
            raise ValueError("scheduled_at must be in the future")
        if normalized > now + timedelta(days=31):
            raise ValueError("scheduled_at cannot be more than 31 days ahead")
        return normalized

class TargetAudience(BaseModel):
    title: str = Field(description="Tên nhóm khách hàng mục tiêu")
    desc: str = Field(description="Mô tả hành vi, thu nhập, lối sống")
    pain_points: List[str] = Field(description="Danh sách nỗi đau lớn nhất")

class MarketGap(BaseModel):
    title: str = Field(description="Tên khoảng trống thị trường")
    opportunity: str = Field(description="Chi tiết cơ hội chưa được khai thác")
    priority: str = Field(description="Ưu tiên: Cao / Trung bình / Thấp")

class SWOT(BaseModel):
    strengths: List[str] = Field(description="Điểm mạnh thị trường")
    weaknesses: List[str] = Field(description="Điểm yếu thị trường")
    opportunities: List[str] = Field(description="Cơ hội thị trường")
    threats: List[str] = Field(description="Thách thức thị trường")

class CompetitorItem(BaseModel):
    name: str = Field(description="Tên đối thủ cạnh tranh")
    type: str = Field(description="Loại đối thủ: Trực tiếp / Gián tiếp")
    positioning: str = Field(description="Định vị thương hiệu")
    strengths: List[str] = Field(description="Điểm mạnh")
    weaknesses: List[str] = Field(description="Điểm yếu")
    price_range: str = Field(description="Khoảng giá sản phẩm")
    market_share_est: Optional[str] = Field(default=None, description="Ước tính thị phần")
    website: Optional[str] = Field(default=None, description="Website chính thức nếu có")

class PricingTier(BaseModel):
    tier: str = Field(description="Tên gói sản phẩm (ví dụ: Starter, Pro, Enterprise)")
    price: float = Field(description="Mức giá (VNĐ)")
    description: str = Field(description="Mô tả đối tượng dùng")
    features: List[str] = Field(description="Các tính năng / quyền lợi kèm theo")

class PricingStrategy(BaseModel):
    min_market_price: float = Field(description="Giá thấp nhất thị trường")
    median_market_price: float = Field(description="Giá trung vị thị trường")
    recommended_price: float = Field(description="Mức giá đề xuất tối ưu (Sweet spot)")
    premium_market_price: float = Field(description="Giá phân khúc cao cấp")
    unit: str = Field(default="VNĐ / sản phẩm", description="Đơn vị tính giá")
    pricing_logic: str = Field(description="Lý luận & cơ sở cho mức giá đề xuất")
    margin_est: str = Field(default="60% - 70%", description="Ước tính biên lợi nhuận gộp")
    tiers: List[PricingTier] = Field(default_factory=list, description="3 gói định giá phân tầng")

class RiskItem(BaseModel):
    category: str = Field(description="Danh mục: Thị trường / Đối thủ / Vận hành / Pháp lý / Tài chính")
    risk_title: str = Field(description="Tên rủi ro")
    risk_level: str = Field(description="Mức độ: Cao / Trung bình / Thấp")
    impact: str = Field(description="Mức độ tác động cụ thể")
    mitigation: str = Field(description="Biện pháp phòng ngừa & giảm thiểu")

class SEOKeywordItem(BaseModel):
    keyword: str = Field(description="Từ khóa mục tiêu")
    intent: str = Field(description="Ý định: Mua hàng (Commercial) / Tìm hiểu (Informational) / So sánh (Navigational)")
    search_volume_est: str = Field(description="Volume ước tính: Rất cao / Cao / Trung bình / Ngách")
    competition: str = Field(description="Độ cạnh tranh: Cao / Trung bình / Thấp")
    content_angle: str = Field(description="Gợi ý góc tiếp cận bài viết marketing")

class GTMRoadmapPhase(BaseModel):
    phase: str = Field(description="Tên giai đoạn")
    timeline: str = Field(description="Thời gian thực thi (ví dụ: Tháng 1 - 2)")
    key_actions: List[str] = Field(description="Danh sách các hành động then chốt")

class GraphNode(BaseModel):
    id: str
    name: str
    category: str
    size: Optional[int] = 16

class GraphLink(BaseModel):
    source: str
    target: str
    relationship: str

class KnowledgeGraphData(BaseModel):
    nodes: List[GraphNode] = Field(default_factory=list)
    links: List[GraphLink] = Field(default_factory=list)

class MarketReport(BaseModel):
    id: str
    topic: str
    createdAt: str
    executive_summary: str
    market_size_est: str
    growth_rate: str
    target_audience: List[TargetAudience]
    market_gaps: List[MarketGap]
    swot: SWOT
    competitors: List[CompetitorItem]
    pricing: PricingStrategy
    risks: List[RiskItem]
    seo_strategy: List[SEOKeywordItem]
    gtm_roadmap: List[GTMRoadmapPhase]
    graph_data: KnowledgeGraphData
