from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field


class Platform(str, Enum):
    BLOG = "blog"
    X = "x"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"


class CampaignStatus(str, Enum):
    DRAFTING = "drafting"
    VERIFYING = "verifying"
    WAITING_APPROVAL = "waiting_approval"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    COMPLETED = "completed"
    NEEDS_REVIEW = "needs_review"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ActionType(str, Enum):
    EXTRACT_CLAIMS = "extract_claims"
    DRAFT_VARIANTS = "draft_variants"
    VERIFY_DRAFTS = "verify_drafts"
    WAIT_APPROVAL = "wait_approval"
    PUBLISH_VARIANTS = "publish_variants"
    VERIFY_PUBLICATION = "verify_publication"
    COMPLETE = "complete"


class SourceRef(BaseModel):
    title: str = Field(default="", max_length=300)
    url: AnyHttpUrl
    snippet: str = Field(default="", max_length=2000)
    published_at: str | None = Field(default=None, max_length=80)


class Claim(BaseModel):
    text: str = Field(min_length=1, max_length=1000)
    evidence: list[SourceRef] = Field(default_factory=list, max_length=5)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class PlatformDraft(BaseModel):
    model_config = ConfigDict(use_enum_values=False)

    id: str = Field(min_length=8, max_length=80)
    platform: Platform
    title: str = Field(default="", max_length=300)
    slug: str = Field(default="", max_length=200)
    excerpt: str = Field(default="", max_length=500)
    body: str = Field(min_length=1, max_length=12000)
    canonical_url: AnyHttpUrl | None = None
    seo_keywords: list[str] = Field(default_factory=list, max_length=20)
    hashtags: list[str] = Field(default_factory=list, max_length=20)
    content_hash: str = Field(default="", max_length=64)
    status: str = Field(default="draft", max_length=40)
    provider_post_id: str | None = Field(default=None, max_length=300)
    published_url: AnyHttpUrl | None = None
    error_code: str | None = Field(default=None, max_length=80)


class ActionRecord(BaseModel):
    action: ActionType
    step: int = Field(ge=1, le=50)
    message: str = Field(min_length=1, max_length=500)
    created_at: datetime


class PublishResult(BaseModel):
    platform: Platform
    success: bool
    code: str = Field(min_length=1, max_length=100)
    provider_post_id: str | None = Field(default=None, max_length=300)
    published_url: AnyHttpUrl | None = None
    verified: bool = False
    detail: str | None = Field(default=None, max_length=500)


class ContentCampaign(BaseModel):
    model_config = ConfigDict(use_enum_values=False)

    id: str = Field(min_length=8, max_length=80)
    report_id: str = Field(min_length=1, max_length=100)
    topic: str = Field(min_length=2, max_length=200)
    platforms: list[Platform] = Field(min_length=1, max_length=4)
    status: CampaignStatus = CampaignStatus.DRAFTING
    step: int = Field(default=0, ge=0, le=50)
    max_steps: int = Field(default=8, ge=1, le=20)
    claims: list[Claim] = Field(default_factory=list, max_length=30)
    drafts: list[PlatformDraft] = Field(default_factory=list, max_length=4)
    publish_results: list[PublishResult] = Field(default_factory=list, max_length=4)
    issues: list[str] = Field(default_factory=list, max_length=30)
    actions: list[ActionRecord] = Field(default_factory=list, max_length=50)
    revision_count: int = Field(default=0, ge=0, le=3)
    approval_required: bool = True
    approved_at: datetime | None = None
    scheduled_at: datetime | None = None
    created_at: datetime
    completed_at: datetime | None = None


def model_to_json_dict(value: BaseModel) -> dict[str, Any]:
    """Serialize enums/URLs/datetimes consistently for SSE and API responses."""
    return value.model_dump(mode="json")
