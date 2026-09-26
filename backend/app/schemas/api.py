from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl

class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=200)

class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    tagline: str
    bio: str
    education: str
    board: str
    contact_email: str | None = None
    contact_email_public: bool = False
    linkedin_url: str | None = None
    github_url: str | None = None
    current_learning: str = ""
    research_interests: str = ""
    problem_solving: str = ""
    open_to: str = ""
    avatar_url: str | None = None
    github_username: str | None = None
    github_featured_repos: str = "[]"
    orcid_url: str | None = None
    google_scholar_url: str | None = None
    arxiv_url: str | None = None

class RequestIn(BaseModel):
    request_kind: str = Field(default="COLLABORATION", max_length=40)
    name: str = Field(min_length=2, max_length=200)
    email: EmailStr
    organization: str | None = Field(default=None, max_length=250)
    role: str | None = Field(default=None, max_length=180)
    country: str | None = Field(default=None, max_length=120)
    professional_profile_url: HttpUrl | None = None
    website_url: HttpUrl | None = None
    signature_name: str = Field(min_length=2, max_length=200)
    purpose: str = Field(min_length=5, max_length=2000)
    requested_rights: list[str] = Field(min_length=1, max_length=20)
    message: str = Field(default="", max_length=4000)
    agreement_type: str = Field(default="IDEA_EVALUATION", max_length=100)
    agreement_version: str = Field(max_length=40)
    agreement_sha256: str = Field(min_length=64, max_length=64)
    idea_public_id: str | None = Field(default=None, max_length=50)
    honeypot: str = Field(default="", max_length=200)
    turnstile_token: str | None = Field(default=None, max_length=4096)
    investment_interest: str | None = Field(default=None, max_length=500)
    funding_amount: float | None = Field(default=None, gt=0, le=100_000_000_000)
    funding_currency: str = Field(default="INR", min_length=3, max_length=3)
    funding_stage: str | None = Field(default=None, max_length=120)
    funding_instrument: str | None = Field(default=None, max_length=120)
    funding_use: str | None = Field(default=None, max_length=2000)
    pitch_deck_url: HttpUrl | None = None
    site_terms_version: str = Field(max_length=40)
    site_terms_sha256: str = Field(min_length=64, max_length=64)
    privacy_acknowledged: bool = False

class RequestOut(BaseModel):
    request_id: str
    request_kind: str = "COLLABORATION"
    status: str
    accepted_at: datetime
    agreement_type: str
    agreement_version: str
    agreement_sha256: str
    funding_amount: float | None = None
    funding_currency: str | None = None

class AnalyticsIn(BaseModel):
    event_type: str = Field(min_length=2, max_length=80)
    path: str = Field(min_length=1, max_length=500)
    entity_type: str | None = Field(default=None, max_length=120)
    entity_id: str | None = Field(default=None, max_length=120)
    referrer: str | None = Field(default=None, max_length=1000)
