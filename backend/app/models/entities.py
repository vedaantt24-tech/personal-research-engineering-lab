from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, Table, Column, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

def now(): return datetime.now(timezone.utc)

project_tags = Table("project_tags", Base.metadata,
    Column("project_id", ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True))
idea_tags = Table("idea_tags", Base.metadata,
    Column("idea_id", ForeignKey("ideas.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True))

class PublicationState(str, Enum): DRAFT="DRAFT"; REVIEW="REVIEW"; PUBLISHED="PUBLISHED"; ARCHIVED="ARCHIVED"
class Visibility(str, Enum): PUBLIC="PUBLIC"; UNLISTED="UNLISTED"; PRIVATE="PRIVATE"; CONFIDENTIAL="CONFIDENTIAL"
class IdeaStatus(str, Enum): THOUGHT="THOUGHT"; CONCEPT="CONCEPT"; RESEARCHING="RESEARCHING"; EXPERIMENTING="EXPERIMENTING"; PROTOTYPING="PROTOTYPING"; TESTED="TESTED"; DEVELOPING="DEVELOPING"
class ExperimentStatus(str, Enum): FAILED="FAILED"; PARTIAL="PARTIAL"; PROMISING="PROMISING"; SUCCESSFUL="SUCCESSFUL"; NEEDS_VALIDATION="NEEDS_VALIDATION"
class RequestStatus(str, Enum): PENDING="PENDING"; APPROVED="APPROVED"; REJECTED="REJECTED"; NEEDS_INFO="NEEDS_INFO"
class ContentClassification(str, Enum): PUBLIC="PUBLIC"; PROFESSIONAL="PROFESSIONAL"; RESEARCH="RESEARCH"; EXPERIMENTAL="EXPERIMENTAL"; CONCEPT="CONCEPT"; DRAFT="DRAFT"; PRIVATE="PRIVATE"; CONFIDENTIAL="CONFIDENTIAL"

class User(Base):
    __tablename__="users"
    id: Mapped[int]=mapped_column(primary_key=True)
    email: Mapped[str]=mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str]=mapped_column(String(255))
    is_active: Mapped[bool]=mapped_column(Boolean, default=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)

class Profile(Base):
    __tablename__="profiles"
    id: Mapped[int]=mapped_column(primary_key=True)
    user_id: Mapped[int]=mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    name: Mapped[str]=mapped_column(String(200), default="[OWNER NAME]")
    tagline: Mapped[str]=mapped_column(Text, default="Building, researching and exploring practical technology for real-world problems.")
    bio: Mapped[str]=mapped_column(Text, default="")
    education: Mapped[str]=mapped_column(String(500), default="Diploma in Computer Science / Computer Engineering")
    board: Mapped[str]=mapped_column(String(200), default="Maharashtra State Board of Technical Education (MSBTE)")
    contact_email: Mapped[str|None]=mapped_column(String(320), nullable=True)
    contact_email_public: Mapped[bool]=mapped_column(Boolean, default=False)
    linkedin_url: Mapped[str|None]=mapped_column(String(500), nullable=True)
    github_url: Mapped[str|None]=mapped_column(String(500), nullable=True)
    current_learning: Mapped[str]=mapped_column(Text, default="")
    research_interests: Mapped[str]=mapped_column(Text, default="")
    problem_solving: Mapped[str]=mapped_column(Text, default="")
    open_to: Mapped[str]=mapped_column(Text, default="")
    avatar_url: Mapped[str|None]=mapped_column(String(500), nullable=True)
    github_username: Mapped[str|None]=mapped_column(String(120), nullable=True)
    github_featured_repos: Mapped[str]=mapped_column(Text, default="[]")
    orcid_url: Mapped[str|None]=mapped_column(String(500), nullable=True)
    google_scholar_url: Mapped[str|None]=mapped_column(String(500), nullable=True)
    arxiv_url: Mapped[str|None]=mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now, onupdate=now)

class Skill(Base):
    __tablename__="skills"
    id: Mapped[int]=mapped_column(primary_key=True)
    category: Mapped[str]=mapped_column(String(100), index=True)
    name: Mapped[str]=mapped_column(String(120))
    level: Mapped[str|None]=mapped_column(String(50), nullable=True)
    published: Mapped[bool]=mapped_column(Boolean, default=True)
    state: Mapped[PublicationState]=mapped_column(default=PublicationState.PUBLISHED, index=True)

class Education(Base):
    __tablename__="education"
    id: Mapped[int]=mapped_column(primary_key=True)
    institution: Mapped[str]=mapped_column(String(250))
    qualification: Mapped[str]=mapped_column(String(250))
    board: Mapped[str|None]=mapped_column(String(250), nullable=True)
    period: Mapped[str|None]=mapped_column(String(100), nullable=True)
    description: Mapped[str|None]=mapped_column(Text, nullable=True)
    published: Mapped[bool]=mapped_column(Boolean, default=True)
    state: Mapped[PublicationState]=mapped_column(default=PublicationState.PUBLISHED, index=True)

class Experience(Base):
    __tablename__="experiences"
    id: Mapped[int]=mapped_column(primary_key=True)
    role: Mapped[str]=mapped_column(String(250))
    organization: Mapped[str]=mapped_column(String(250))
    date_label: Mapped[str|None]=mapped_column(String(100), nullable=True)
    description: Mapped[str]=mapped_column(Text, default="")
    technologies: Mapped[str]=mapped_column(Text, default="")
    link: Mapped[str|None]=mapped_column(String(500), nullable=True)
    published: Mapped[bool]=mapped_column(Boolean, default=True)
    state: Mapped[PublicationState]=mapped_column(default=PublicationState.PUBLISHED, index=True)

class Achievement(Base):
    __tablename__="achievements"
    id: Mapped[int]=mapped_column(primary_key=True)
    title: Mapped[str]=mapped_column(String(250))
    organization: Mapped[str|None]=mapped_column(String(250), nullable=True)
    date_label: Mapped[str|None]=mapped_column(String(100), nullable=True)
    description: Mapped[str]=mapped_column(Text, default="")
    link: Mapped[str|None]=mapped_column(String(500), nullable=True)
    published: Mapped[bool]=mapped_column(Boolean, default=True)
    state: Mapped[PublicationState]=mapped_column(default=PublicationState.DRAFT, index=True)

class TimelineEntry(Base):
    __tablename__="timeline_entries"
    id: Mapped[int]=mapped_column(primary_key=True)
    date_label: Mapped[str]=mapped_column(String(100), default="")
    title: Mapped[str]=mapped_column(String(250))
    category: Mapped[str]=mapped_column(String(100), default="Milestone", index=True)
    description: Mapped[str]=mapped_column(Text, default="")
    link: Mapped[str|None]=mapped_column(String(500), nullable=True)
    published: Mapped[bool]=mapped_column(Boolean, default=True)
    state: Mapped[PublicationState]=mapped_column(default=PublicationState.PUBLISHED, index=True)

class Tag(Base):
    __tablename__="tags"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(80), unique=True)

class Interest(Base):
    __tablename__="interests"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(120), unique=True)
    published: Mapped[bool]=mapped_column(Boolean, default=True)
    state: Mapped[PublicationState]=mapped_column(default=PublicationState.PUBLISHED, index=True)

class ProjectTechnology(Base):
    __tablename__="project_technologies"
    id: Mapped[int]=mapped_column(primary_key=True)
    project_id: Mapped[int]=mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    technology: Mapped[str]=mapped_column(String(120), index=True)
    project = relationship("Project", back_populates="technologies")

class Project(Base):
    __tablename__="projects"
    id: Mapped[int]=mapped_column(primary_key=True)
    slug: Mapped[str]=mapped_column(String(180), unique=True, index=True)
    title: Mapped[str]=mapped_column(String(250))
    summary: Mapped[str]=mapped_column(Text)
    problem: Mapped[str]=mapped_column(Text, default="")
    motivation: Mapped[str]=mapped_column(Text, default="")
    solution: Mapped[str]=mapped_column(Text, default="")
    architecture: Mapped[str]=mapped_column(Text, default="")
    challenges: Mapped[str]=mapped_column(Text, default="")
    results: Mapped[str]=mapped_column(Text, default="")
    learned: Mapped[str]=mapped_column(Text, default="")
    future_work: Mapped[str]=mapped_column(Text, default="")
    image_url: Mapped[str|None]=mapped_column(String(500), nullable=True)
    status: Mapped[str]=mapped_column(String(100), default="In Development")
    visibility: Mapped[Visibility]=mapped_column(default=Visibility.PRIVATE)
    classification: Mapped[str]=mapped_column(String(40), default="PROFESSIONAL", index=True)
    state: Mapped[PublicationState]=mapped_column(default=PublicationState.DRAFT, index=True)
    github_url: Mapped[str|None]=mapped_column(String(500), nullable=True)
    demo_url: Mapped[str|None]=mapped_column(String(500), nullable=True)
    case_study_url: Mapped[str|None]=mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now, onupdate=now)
    tags = relationship("Tag", secondary=project_tags)
    technologies = relationship("ProjectTechnology", back_populates="project", cascade="all, delete-orphan")

class Research(Base):
    __tablename__="research"
    id: Mapped[int]=mapped_column(primary_key=True)
    slug: Mapped[str]=mapped_column(String(180), unique=True, index=True)
    title: Mapped[str]=mapped_column(String(250))
    area: Mapped[str]=mapped_column(String(150), default="")
    abstract: Mapped[str]=mapped_column(Text, default="")
    question: Mapped[str]=mapped_column(Text, default="")
    problem: Mapped[str]=mapped_column(Text, default="")
    existing_work: Mapped[str]=mapped_column(Text, default="")
    hypothesis: Mapped[str]=mapped_column(Text, default="")
    methodology: Mapped[str]=mapped_column(Text, default="")
    experiment: Mapped[str]=mapped_column(Text, default="")
    results: Mapped[str]=mapped_column(Text, default="")
    limitations: Mapped[str]=mapped_column(Text, default="")
    future_work: Mapped[str]=mapped_column(Text, default="")
    references_text: Mapped[str]=mapped_column(Text, default="")
    paper_url: Mapped[str|None]=mapped_column(String(500), nullable=True)
    code_url: Mapped[str|None]=mapped_column(String(500), nullable=True)
    dataset_url: Mapped[str|None]=mapped_column(String(500), nullable=True)
    status: Mapped[str]=mapped_column(String(100), default="Idea")
    visibility: Mapped[Visibility]=mapped_column(default=Visibility.PRIVATE)
    classification: Mapped[str]=mapped_column(String(40), default="RESEARCH", index=True)
    state: Mapped[PublicationState]=mapped_column(default=PublicationState.DRAFT, index=True)
    date_label: Mapped[str|None]=mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now, onupdate=now)
    references = relationship("ResearchReference", back_populates="research", cascade="all, delete-orphan")

class ResearchReference(Base):
    __tablename__="research_references"
    id: Mapped[int]=mapped_column(primary_key=True)
    research_id: Mapped[int]=mapped_column(ForeignKey("research.id", ondelete="CASCADE"), index=True)
    title: Mapped[str]=mapped_column(String(400))
    authors: Mapped[str]=mapped_column(Text, default="")
    venue: Mapped[str|None]=mapped_column(String(250), nullable=True)
    year: Mapped[int|None]=mapped_column(Integer, nullable=True)
    doi: Mapped[str|None]=mapped_column(String(300), nullable=True)
    url: Mapped[str|None]=mapped_column(String(500), nullable=True)
    citation_text: Mapped[str|None]=mapped_column(Text, nullable=True)
    research = relationship("Research", back_populates="references")

class Idea(Base):
    __tablename__="ideas"
    id: Mapped[int]=mapped_column(primary_key=True)
    public_id: Mapped[str]=mapped_column(String(50), unique=True, index=True)
    slug: Mapped[str]=mapped_column(String(180), unique=True, index=True)
    title: Mapped[str]=mapped_column(String(250))
    one_line: Mapped[str]=mapped_column(Text, default="")
    question: Mapped[str]=mapped_column(Text, default="")
    problem: Mapped[str]=mapped_column(Text, default="")
    current_approach: Mapped[str]=mapped_column(Text, default="")
    proposed_concept: Mapped[str]=mapped_column(Text, default="")
    how_it_works: Mapped[str]=mapped_column(Text, default="")
    required_technology: Mapped[str]=mapped_column(Text, default="")
    assumptions: Mapped[str]=mapped_column(Text, default="")
    risks: Mapped[str]=mapped_column(Text, default="")
    open_questions: Mapped[str]=mapped_column(Text, default="")
    applications: Mapped[str]=mapped_column(Text, default="")
    prototype_status: Mapped[str]=mapped_column(String(100), default="None")
    status: Mapped[IdeaStatus]=mapped_column(default=IdeaStatus.CONCEPT)
    visibility: Mapped[Visibility]=mapped_column(default=Visibility.PRIVATE)
    classification: Mapped[str]=mapped_column(String(40), default="CONCEPT", index=True)
    state: Mapped[PublicationState]=mapped_column(default=PublicationState.DRAFT, index=True)
    requires_permission: Mapped[bool]=mapped_column(Boolean, default=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now, onupdate=now)
    tags = relationship("Tag", secondary=idea_tags)

class Experiment(Base):
    __tablename__="experiments"
    id: Mapped[int]=mapped_column(primary_key=True)
    slug: Mapped[str]=mapped_column(String(180), unique=True, index=True)
    title: Mapped[str]=mapped_column(String(250))
    date_label: Mapped[str|None]=mapped_column(String(100), nullable=True)
    question: Mapped[str]=mapped_column(Text, default="")
    hypothesis: Mapped[str]=mapped_column(Text, default="")
    setup: Mapped[str]=mapped_column(Text, default="")
    tools: Mapped[str]=mapped_column(Text, default="")
    procedure: Mapped[str]=mapped_column(Text, default="")
    data: Mapped[str]=mapped_column(Text, default="")
    result: Mapped[str]=mapped_column(Text, default="")
    observation: Mapped[str]=mapped_column(Text, default="")
    conclusion: Mapped[str]=mapped_column(Text, default="")
    next_step: Mapped[str]=mapped_column(Text, default="")
    status: Mapped[ExperimentStatus]=mapped_column(default=ExperimentStatus.NEEDS_VALIDATION)
    visibility: Mapped[Visibility]=mapped_column(default=Visibility.PRIVATE)
    classification: Mapped[str]=mapped_column(String(40), default="EXPERIMENTAL", index=True)
    state: Mapped[PublicationState]=mapped_column(default=PublicationState.DRAFT, index=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)

class ContentRevision(Base):
    __tablename__="content_revisions"
    id: Mapped[int]=mapped_column(primary_key=True)
    entity_type: Mapped[str]=mapped_column(String(80), index=True)
    entity_id: Mapped[int]=mapped_column(Integer, index=True)
    version_no: Mapped[int]=mapped_column(Integer)
    snapshot_json: Mapped[str]=mapped_column(Text)
    actor_email: Mapped[str]=mapped_column(String(320), index=True)
    change_note: Mapped[str|None]=mapped_column(Text, nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)

class ExperimentDatum(Base):
    __tablename__="experiment_data"
    id: Mapped[int]=mapped_column(primary_key=True)
    experiment_id: Mapped[int]=mapped_column(ForeignKey("experiments.id", ondelete="CASCADE"), index=True)
    series: Mapped[str]=mapped_column(String(100), default="default", index=True)
    x_label: Mapped[str|None]=mapped_column(String(160), nullable=True)
    x_value: Mapped[float|None]=mapped_column(Float, nullable=True)
    y_value: Mapped[float]=mapped_column(Float)
    unit: Mapped[str|None]=mapped_column(String(80), nullable=True)
    note: Mapped[str|None]=mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)

class Publication(Base):
    __tablename__="publications"
    id: Mapped[int]=mapped_column(primary_key=True)
    title: Mapped[str]=mapped_column(String(300))
    authors: Mapped[str]=mapped_column(Text, default="")
    venue: Mapped[str|None]=mapped_column(String(250), nullable=True)
    year: Mapped[int|None]=mapped_column(Integer, nullable=True)
    abstract: Mapped[str]=mapped_column(Text, default="")
    doi: Mapped[str|None]=mapped_column(String(300), nullable=True)
    pdf_url: Mapped[str|None]=mapped_column(String(500), nullable=True)
    preprint_url: Mapped[str|None]=mapped_column(String(500), nullable=True)
    github_url: Mapped[str|None]=mapped_column(String(500), nullable=True)
    status: Mapped[str]=mapped_column(String(100), default="Preprint")
    visibility: Mapped[Visibility]=mapped_column(default=Visibility.PRIVATE)
    classification: Mapped[str]=mapped_column(String(40), default="PROFESSIONAL", index=True)
    state: Mapped[PublicationState]=mapped_column(default=PublicationState.DRAFT, index=True)

class BlogPost(Base):
    __tablename__="blog_posts"
    id: Mapped[int]=mapped_column(primary_key=True)
    slug: Mapped[str]=mapped_column(String(180), unique=True, index=True)
    title: Mapped[str]=mapped_column(String(300))
    excerpt: Mapped[str]=mapped_column(Text, default="")
    body: Mapped[str]=mapped_column(Text, default="")
    visibility: Mapped[Visibility]=mapped_column(default=Visibility.PRIVATE)
    state: Mapped[PublicationState]=mapped_column(default=PublicationState.DRAFT, index=True)

class Resume(Base):
    __tablename__="resumes"
    id: Mapped[int]=mapped_column(primary_key=True)
    label: Mapped[str]=mapped_column(String(200), default="Current Resume")
    file_url: Mapped[str|None]=mapped_column(String(500), nullable=True)
    active: Mapped[bool]=mapped_column(Boolean, default=False)
    state: Mapped[PublicationState]=mapped_column(default=PublicationState.DRAFT, index=True)

class Media(Base):
    __tablename__="media"
    id: Mapped[int]=mapped_column(primary_key=True)
    filename: Mapped[str]=mapped_column(String(300))
    storage_key: Mapped[str]=mapped_column(String(500), unique=True)
    mime_type: Mapped[str]=mapped_column(String(150))
    size_bytes: Mapped[int]=mapped_column(Integer)
    sha256: Mapped[str]=mapped_column(String(64), index=True)
    visibility: Mapped[Visibility]=mapped_column(default=Visibility.PRIVATE)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)

class SocialLink(Base):
    __tablename__="social_links"
    id: Mapped[int]=mapped_column(primary_key=True)
    platform: Mapped[str]=mapped_column(String(100))
    url: Mapped[str]=mapped_column(String(500))
    label: Mapped[str|None]=mapped_column(String(150), nullable=True)
    published: Mapped[bool]=mapped_column(Boolean, default=True)
    state: Mapped[PublicationState]=mapped_column(default=PublicationState.PUBLISHED, index=True)

class ContactMessage(Base):
    __tablename__="contact_messages"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(200))
    email: Mapped[str]=mapped_column(String(320), index=True)
    organization: Mapped[str|None]=mapped_column(String(250), nullable=True)
    message: Mapped[str]=mapped_column(Text)
    network_ip_hash: Mapped[str|None]=mapped_column(String(64), nullable=True, index=True)
    site_terms_version: Mapped[str|None]=mapped_column(String(40), nullable=True)
    site_terms_sha256: Mapped[str|None]=mapped_column(String(64), nullable=True)
    site_terms_body_snapshot: Mapped[str]=mapped_column(Text, default="")
    terms_accepted_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)
    read_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True), nullable=True)

class AgreementTemplate(Base):
    __tablename__="agreement_templates"
    id: Mapped[int]=mapped_column(primary_key=True)
    agreement_type: Mapped[str]=mapped_column(String(100), index=True)
    version: Mapped[str]=mapped_column(String(40))
    title: Mapped[str]=mapped_column(String(250))
    body: Mapped[str]=mapped_column(Text)
    sha256: Mapped[str]=mapped_column(String(64), index=True)
    active: Mapped[bool]=mapped_column(Boolean, default=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)

class CollaborationRequest(Base):
    __tablename__="collaboration_requests"
    id: Mapped[int]=mapped_column(primary_key=True)
    request_id: Mapped[str]=mapped_column(String(60), unique=True, index=True)
    request_kind: Mapped[str]=mapped_column(String(40), default="COLLABORATION", index=True)
    idea_id: Mapped[int|None]=mapped_column(ForeignKey("ideas.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str]=mapped_column(String(200))
    email: Mapped[str]=mapped_column(String(320), index=True)
    organization: Mapped[str|None]=mapped_column(String(250), nullable=True)
    role: Mapped[str|None]=mapped_column(String(180), nullable=True)
    country: Mapped[str|None]=mapped_column(String(120), nullable=True)
    professional_profile_url: Mapped[str|None]=mapped_column(String(500), nullable=True)
    website_url: Mapped[str|None]=mapped_column(String(500), nullable=True)
    signature_name: Mapped[str]=mapped_column(String(200), default="")
    acceptance_ip_hash: Mapped[str|None]=mapped_column(String(64), nullable=True)
    purpose: Mapped[str]=mapped_column(Text)
    requested_rights: Mapped[str]=mapped_column(Text)
    message: Mapped[str]=mapped_column(Text, default="")
    investment_interest: Mapped[str|None]=mapped_column(String(500), nullable=True)
    funding_amount: Mapped[float|None]=mapped_column(Float, nullable=True)
    funding_currency: Mapped[str]=mapped_column(String(3), default="INR")
    funding_stage: Mapped[str|None]=mapped_column(String(120), nullable=True)
    funding_instrument: Mapped[str|None]=mapped_column(String(120), nullable=True)
    funding_use: Mapped[str|None]=mapped_column(Text, nullable=True)
    pitch_deck_url: Mapped[str|None]=mapped_column(String(500), nullable=True)
    agreement_type: Mapped[str]=mapped_column(String(100))
    agreement_version: Mapped[str]=mapped_column(String(40))
    agreement_sha256: Mapped[str]=mapped_column(String(64))
    agreement_body_snapshot: Mapped[str]=mapped_column(Text, default="")
    site_terms_version: Mapped[str|None]=mapped_column(String(40), nullable=True)
    site_terms_sha256: Mapped[str|None]=mapped_column(String(64), nullable=True)
    site_terms_body_snapshot: Mapped[str]=mapped_column(Text, default="")
    privacy_acknowledged_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True), nullable=True)
    accepted_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)
    status: Mapped[RequestStatus]=mapped_column(default=RequestStatus.PENDING, index=True)
    owner_notes: Mapped[str]=mapped_column(Text, default="")
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)

class PermissionGrant(Base):
    __tablename__="permission_grants"
    id: Mapped[int]=mapped_column(primary_key=True)
    request_id: Mapped[str]=mapped_column(ForeignKey("collaboration_requests.request_id", ondelete="CASCADE"), unique=True, index=True)
    rights_json: Mapped[str]=mapped_column(Text, default="[]")
    granted_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)
    expires_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str]=mapped_column(Text, default="")
    access_token_hash: Mapped[str|None]=mapped_column(String(64), nullable=True, unique=True, index=True)
    access_token_issued_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True), nullable=True)


class MediaLink(Base):
    __tablename__="media_links"
    id: Mapped[int]=mapped_column(primary_key=True)
    media_id: Mapped[int]=mapped_column(ForeignKey("media.id", ondelete="CASCADE"), index=True)
    entity_type: Mapped[str]=mapped_column(String(80), index=True)
    entity_id: Mapped[int]=mapped_column(Integer, index=True)
    role: Mapped[str]=mapped_column(String(80), default="attachment")
    sort_order: Mapped[int]=mapped_column(Integer, default=0)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)


class AnalyticsEvent(Base):
    __tablename__="analytics_events"
    id: Mapped[int]=mapped_column(primary_key=True)
    event_type: Mapped[str]=mapped_column(String(80), index=True)
    path: Mapped[str]=mapped_column(String(500), index=True)
    entity_type: Mapped[str|None]=mapped_column(String(120), nullable=True, index=True)
    entity_id: Mapped[str|None]=mapped_column(String(120), nullable=True)
    referrer: Mapped[str|None]=mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now, index=True)

class VisibilitySetting(Base):
    __tablename__="visibility_settings"
    id: Mapped[int]=mapped_column(primary_key=True)
    key: Mapped[str]=mapped_column(String(120), unique=True, index=True)
    default_visibility: Mapped[Visibility]=mapped_column(default=Visibility.PRIVATE)
    notes: Mapped[str]=mapped_column(Text, default="")
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now, onupdate=now)

class AuditLog(Base):
    __tablename__="audit_logs"
    id: Mapped[int]=mapped_column(primary_key=True)
    actor_email: Mapped[str]=mapped_column(String(320))
    action: Mapped[str]=mapped_column(String(120), index=True)
    entity_type: Mapped[str]=mapped_column(String(120))
    entity_id: Mapped[str]=mapped_column(String(120))
    metadata_json: Mapped[str]=mapped_column(Text, default="{}")
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now, index=True)
