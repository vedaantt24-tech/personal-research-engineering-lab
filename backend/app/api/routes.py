from datetime import datetime, timezone, timedelta
import hashlib
import hmac
import ipaddress
import json
import os
import re
import secrets
from urllib.parse import urlparse
from urllib.request import Request as UrlRequest, urlopen
from io import BytesIO
from typing import Any

from email_validator import EmailNotValidError, validate_email
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_token, decode_token, hash_password, verify_password
from app.core.storage import get_storage, LocalStorage
from app.core.notifications import send_email
from app.db.session import get_db
from app.models.entities import (
    AgreementTemplate, AnalyticsEvent, AuditLog, BlogPost, CollaborationRequest,
    ContactMessage, Education, Experiment, ExperimentStatus, Experience, Idea,
    IdeaStatus, Media, PermissionGrant, Profile, Publication, PublicationState,
    Project, Research, RequestStatus, Resume, Skill, SocialLink, User, Visibility,
    ContentClassification, Interest, MediaLink, ProjectTechnology, ResearchReference, ExperimentDatum, ContentRevision, Achievement, TimelineEntry, VisibilitySetting,
)
from app.schemas.api import AnalyticsIn, LoginIn, ProfileOut, RequestIn, RequestOut

router = APIRouter(prefix="/api/v1")

ALLOWED_REQUEST_RIGHTS = {"Concept", "Technical documentation", "Prototype", "Source code", "Dataset", "Research", "Collaboration", "Commercial development"}
ALLOWED_REQUEST_KINDS = {"COLLABORATION", "INVESTOR_OUTREACH", "FUNDING_REQUEST"}
KIND_DEFAULT_AGREEMENT = {"COLLABORATION": "COLLABORATION", "INVESTOR_OUTREACH": "INVESTOR_DISCUSSION", "FUNDING_REQUEST": "FUNDING_REQUEST"}

CONTENT_MODELS = {
    "projects": Project,
    "research": Research,
    "ideas": Idea,
    "experiments": Experiment,
    "publications": Publication,
    "blog": BlogPost,
    "skills": Skill,
    "education": Education,
    "experience": Experience,
    "social-links": SocialLink,
    "media": Media,
    "resume": Resume,
    "interests": Interest,
    "achievements": Achievement,
    "timeline": TimelineEntry,
}

STATE_MODELS = (Project, Research, Idea, Experiment, Publication, BlogPost, Skill, Education, Experience, SocialLink, Resume, Interest, Achievement, TimelineEntry)

PUBLIC_STATUS = {
    "projects": (Project, "/work"),
    "research": (Research, "/research"),
    "ideas": (Idea, "/ideas"),
    "experiments": (Experiment, "/experiments"),
}


def seed_if_empty(db: Session):
    user = db.scalar(select(User).where(User.email == settings.owner_email))
    if not user:
        user = User(email=settings.owner_email, password_hash=hash_password(settings.owner_password))
        db.add(user)
        db.flush()
        db.add(Profile(
            user_id=user.id,
            name="[OWNER NAME]",
            contact_email=settings.owner_email,
            education="Diploma in Computer Science / Computer Engineering",
            board="Maharashtra State Board of Technical Education (MSBTE)",
            tagline="Building, researching and exploring practical technology for real-world problems.",
        ))
        db.add(Project(
            slug="payore",
            title="PayOre",
            summary="Professional payroll and HR management system — currently in development.",
            status="In Development",
            visibility=Visibility.PRIVATE,
            state=PublicationState.DRAFT,
            classification=ContentClassification.PROFESSIONAL.value,
        ))
        for category, name in [("Programming","Python"),("Programming","C"),("Programming","C++"),("Programming","Object-Oriented Programming")]:
            db.add(Skill(category=category,name=name,published=True))
        agreements = [
            ("SITE_TERMS", "1.0", "Website Terms of Use",
             "WEBSITE TERMS OF USE — TEMPLATE\n\n"
             "1. Use. Use the website lawfully and do not attempt unauthorized access or interfere with its operation.\n"
             "2. Content. Public viewing does not itself grant a license to reproduce, distribute, commercialize or claim protected material as your own.\n"
             "3. Accuracy. Research, experiments and projects are presented at the status recorded by the owner.\n"
             "4. Legal review. This text is a software template and should be reviewed for the owner's actual jurisdiction and intended use."),
            ("IDEA_EVALUATION", "1.0", "Idea Evaluation & Collaboration Agreement",
             "IDEA USE & COLLABORATION AGREEMENT — TEMPLATE\n\n"
             "1. Scope. This agreement applies to a specific request submitted for evaluation or collaboration around the identified material.\n"
             "2. Viewing. Public viewing is not a grant of a license to reproduce, distribute, commercialize, disclose confidential information, or represent the owner's protected material as the requester's own.\n"
             "3. Permission. Any use beyond ordinary viewing must be separately authorized in writing by the owner, with the permitted rights and duration recorded in the permission record.\n"
             "4. Confidentiality. Where confidential information is disclosed, the parties should use an appropriate confidentiality/NDA agreement that matches the disclosure.\n"
             "5. Attribution and ownership. Each party retains ownership of its pre-existing materials unless a separate written agreement states otherwise. Ownership of jointly created material must be expressly agreed.\n"
             "6. No automatic license. Submitting a request, accepting this template, or viewing a page does not itself authorize implementation, commercial exploitation, redistribution, or transfer of rights.\n"
             "7. Legal review. This is a product implementation template and should be reviewed by qualified counsel before commercial reliance."),
            ("COLLABORATION", "1.0", "General Collaboration Agreement",
             "GENERAL COLLABORATION AGREEMENT — TEMPLATE\n\n"
             "This template is intended to document a proposed collaboration, roles, contributions, confidentiality, ownership of background materials, treatment of newly created materials, publication and commercialization terms.\n\n"
             "No collaboration should be treated as having transferred intellectual-property rights unless the parties expressly agree in a suitable written agreement.\n\n"
             "Legal review recommended before signature."),
            ("RESEARCH_COLLABORATION", "1.0", "Research Collaboration Agreement",
             "RESEARCH COLLABORATION AGREEMENT — TEMPLATE\n\n"
             "This template is intended for research discussions involving methodology, data, code, authorship, confidentiality, publication, attribution, and ownership.\n\n"
             "Detailed terms should be adapted to the research institution, sponsor, jurisdiction and applicable policies. Legal review recommended."),
            ("NDA", "1.0", "Confidentiality / NDA Template",
             "CONFIDENTIALITY AGREEMENT / NDA — TEMPLATE\n\n"
             "This is an implementation placeholder for a separately reviewed confidentiality agreement. Confidential disclosures should not rely on this template without appropriate legal review and execution by the relevant parties."),
            ("INVESTOR_DISCUSSION", "1.0", "Investor Discussion Agreement",
             "INVESTOR DISCUSSION AGREEMENT — TEMPLATE\n\n"
             "This template records a request to discuss investment, strategic investment or related support. It does not create an investment commitment, securities offering, partnership, agency relationship or transfer of ownership. Any investment terms must be documented in separate definitive agreements reviewed for the relevant jurisdiction."),
            ("FUNDING_REQUEST", "1.0", "Funding Request Agreement",
             "FUNDING REQUEST AGREEMENT — TEMPLATE\n\n"
             "This template records a request for funding or financial support for a project, research activity, product or concept. Submission does not create a funding commitment. Amounts, valuation, securities, use of funds and other financial terms require separate written documentation where applicable."),
        ]
        for agreement_type, version, title, body in agreements:
            db.add(AgreementTemplate(agreement_type=agreement_type, version=version, title=title, body=body, sha256=hashlib.sha256(body.encode()).hexdigest(), active=True))
    else:
        user.password_hash = hash_password(settings.owner_password)
        user.is_active = True
        profile = db.scalar(select(Profile).where(Profile.user_id == user.id))
        if not profile:
            db.add(Profile(
                user_id=user.id,
                name="[OWNER NAME]",
                contact_email=settings.owner_email,
                education="Diploma in Computer Science / Computer Engineering",
                board="Maharashtra State Board of Technical Education (MSBTE)",
                tagline="Building, researching and exploring practical technology for real-world problems.",
            ))
    db.commit()


def require_owner(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(401, "Authentication required")
    try:
        email = decode_token(token)
    except Exception:
        raise HTTPException(401, "Invalid or expired session")
    user = db.scalar(select(User).where(User.email == email, User.is_active.is_(True)))
    if not user or user.email.casefold() != settings.owner_email.casefold():
        raise HTTPException(401, "Invalid session")
    csrf_cookie = request.cookies.get("csrf_token")
    csrf_header = request.headers.get("X-CSRF-Token")
    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        if not csrf_cookie or not csrf_header or not secrets.compare_digest(csrf_cookie, csrf_header):
            raise HTTPException(403, "CSRF validation failed")
    return user


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:160] or secrets.token_hex(5)


def safe_json(value):
    return json.dumps(value, ensure_ascii=False, default=str)

def enum_text(value):
    return value.value if hasattr(value, "value") else str(value)


def serialize_row(row):
    data = {c.name: getattr(row, c.name) for c in row.__table__.columns}
    for key, value in list(data.items()):
        if hasattr(value, "value"):
            data[key] = value.value
    return data


def record_revision(db: Session, actor_email: str, row, change_note: str | None = None):
    entity_type = row.__class__.__name__
    entity_id = int(row.id)
    latest = db.scalar(
        select(func.max(ContentRevision.version_no)).where(
            ContentRevision.entity_type == entity_type,
            ContentRevision.entity_id == entity_id,
        )
    ) or 0
    db.add(ContentRevision(
        entity_type=entity_type,
        entity_id=entity_id,
        version_no=int(latest) + 1,
        snapshot_json=safe_json(serialize_row(row)),
        actor_email=actor_email,
        change_note=(change_note or "")[:2000] or None,
    ))

def log(db: Session, user_email: str, action: str, entity_type: str, entity_id: str, metadata=None):
    db.add(AuditLog(
        actor_email=user_email, action=action, entity_type=entity_type,
        entity_id=entity_id, metadata_json=safe_json(metadata or {}),
    ))


def require_valid_url(value: str | None):
    if not value:
        return
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise HTTPException(422, "Links must use http or https")



def require_social_url(value: str | None):
    if not value:
        return
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https", "mailto"}:
        raise HTTPException(422, "Social links must use http, https, or mailto")
    if parsed.scheme in {"http", "https"} and not parsed.netloc:
        raise HTTPException(422, "Social links must include a host")
    if parsed.scheme == "mailto" and not parsed.path:
        raise HTTPException(422, "Mailto social links must include an email address")

def network_hash(request: Request) -> str:
    raw = (request.client.host if request.client else "unknown").encode()
    return hmac.new(settings.secret_key.encode(), raw, hashlib.sha256).hexdigest()


def verify_turnstile_token(token: str | None, request: Request) -> bool:
    if not settings.turnstile_enabled:
        return True
    if not token:
        return False
    try:
        payload = f"secret={settings.turnstile_secret_key or ""}&response={token}"
        req = UrlRequest(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data=payload.encode(), method="POST",
            headers={"Content-Type":"application/x-www-form-urlencoded"},
        )
        with urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode())
        return bool(result.get("success"))
    except Exception:
        return False


def safe_featured_repos(value: str) -> list[str]:
    try:
        data = json.loads(value or "[]")
        if not isinstance(data, list):
            return []
        return [str(x).strip() for x in data[:24] if str(x).strip()]
    except Exception:
        return []


def github_repositories(username: str, selected: list[str]) -> list[dict[str, Any]]:
    if not username:
        return []
    url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=100"
    try:
        req = UrlRequest(url, headers={"Accept":"application/vnd.github+json", "User-Agent":"personal-research-lab"})
        with urlopen(req, timeout=settings.github_timeout_seconds) as response:
            rows = json.loads(response.read().decode())
        if not isinstance(rows, list):
            return []
        selected_set = {x.casefold() for x in selected}
        if selected_set:
            rows = [r for r in rows if str(r.get("name", "")).casefold() in selected_set]
        return [{
            "name": r.get("name"), "full_name": r.get("full_name"), "description": r.get("description") or "",
            "html_url": r.get("html_url"), "language": r.get("language"), "stars": r.get("stargazers_count", 0),
            "forks": r.get("forks_count", 0), "updated_at": r.get("updated_at"), "topics": r.get("topics") or [],
        } for r in rows[:24]]
    except Exception:
        return []


def build_resume_pdf(profile, db: Session) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=34, bottomMargin=34)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="SmallGray", parent=styles["BodyText"], fontSize=8.5, leading=12, textColor=colors.HexColor("#666666")))
    styles["Title"].fontSize=24; styles["Title"].leading=28
    story=[Paragraph(profile.name, styles["Title"]), Paragraph(profile.tagline or "", styles["SmallGray"]), Spacer(1,10)]
    contact=" · ".join([x for x in [profile.contact_email, profile.linkedin_url, profile.github_url] if x])
    if contact: story += [Paragraph(contact, styles["SmallGray"]), Spacer(1,12)]
    if profile.bio: story += [Paragraph("ABOUT", styles["Heading2"]), Paragraph(profile.bio, styles["BodyText"]), Spacer(1,10)]
    story += [Paragraph("EDUCATION", styles["Heading2"])]
    edu = db.scalars(select(Education).where(Education.published.is_(True), Education.state == PublicationState.PUBLISHED).order_by(Education.id.desc())).all()
    for x in edu:
        meta=" · ".join([v for v in [x.board, x.period] if v])
        story += [Paragraph(f"{x.qualification} — {x.institution}", styles["Heading3"]), Paragraph(meta, styles["SmallGray"]), Paragraph(x.description or "", styles["BodyText"]), Spacer(1,6)]
    story += [Paragraph("SKILLS", styles["Heading2"])]
    skills = db.scalars(select(Skill).where(Skill.published.is_(True), Skill.state == PublicationState.PUBLISHED).order_by(Skill.category.asc(), Skill.name.asc())).all()
    grouped={}
    for x in skills: grouped.setdefault(x.category, []).append(x.name)
    skill_rows=[[cat, ", ".join(vals)] for cat,vals in grouped.items()]
    if skill_rows:
        t=Table(skill_rows, colWidths=[120, 370])
        t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("FONTSIZE",(0,0),(-1,-1),8.5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
        story += [t, Spacer(1,8)]
    story += [Paragraph("EXPERIENCE", styles["Heading2"])]
    experiences=db.scalars(select(Experience).where(Experience.published.is_(True), Experience.state==PublicationState.PUBLISHED).order_by(Experience.id.desc()).limit(8)).all()
    for x in experiences:
        meta=" · ".join([v for v in [x.organization, x.date_label] if v])
        story += [Paragraph(x.role, styles["Heading3"]), Paragraph(meta, styles["SmallGray"]), Paragraph(x.description or "", styles["BodyText"]), Spacer(1,5)]
    story += [Paragraph("PROJECTS", styles["Heading2"])]
    projects=db.scalars(select(Project).where(Project.state==PublicationState.PUBLISHED, Project.visibility==Visibility.PUBLIC).order_by(Project.updated_at.desc()).limit(8)).all()
    for x in projects: story += [Paragraph(x.title, styles["Heading3"]), Paragraph(x.summary, styles["BodyText"]), Spacer(1,5)]
    story += [Paragraph("PUBLICATIONS", styles["Heading2"])]
    publications=db.scalars(select(Publication).where(Publication.state==PublicationState.PUBLISHED, Publication.visibility==Visibility.PUBLIC).order_by(Publication.year.desc().nullslast(), Publication.id.desc()).limit(8)).all()
    for x in publications:
        meta=" · ".join([v for v in [x.venue, str(x.year) if x.year else None, x.status] if v])
        story += [Paragraph(x.title, styles["Heading3"]), Paragraph(meta, styles["SmallGray"]), Paragraph(x.authors or "", styles["BodyText"]), Spacer(1,5)]
    story += [Paragraph("ACHIEVEMENTS", styles["Heading2"])]
    achievements=db.scalars(select(Achievement).where(Achievement.published.is_(True), Achievement.state==PublicationState.PUBLISHED).order_by(Achievement.id.desc()).limit(12)).all()
    for x in achievements:
        meta=" · ".join([v for v in [x.organization, x.date_label] if v])
        story += [Paragraph(x.title, styles["Heading3"]), Paragraph(meta, styles["SmallGray"]), Paragraph(x.description or "", styles["BodyText"]), Spacer(1,5)]
    doc.build(story)
    return buffer.getvalue()


@router.get("/health/live")
def health_live():
    return {"status":"ok","service":settings.app_name}

@router.get("/health/ready")
def health_ready(db: Session=Depends(get_db)):
    try:
        db.execute(select(func.count()).select_from(User))
        return {"status":"ok","database":"ready"}
    except Exception:
        raise HTTPException(503,"Database not ready")

@router.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        seed_if_empty(db)
        return {"status": "ok", "service": settings.app_name, "database": "ready", "time": datetime.now(timezone.utc).isoformat()}
    except Exception:
        return {"status": "degraded", "service": settings.app_name, "database": "unavailable", "time": datetime.now(timezone.utc).isoformat()}


@router.post("/auth/login")
def login(payload: LoginIn, response: Response, db: Session = Depends(get_db)):
    seed_if_empty(db)
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    response.set_cookie(
        "access_token", create_token(user.email), httponly=True, samesite="lax",
        secure=settings.environment == "production", max_age=settings.access_token_minutes * 60, path="/",
    )
    csrf = secrets.token_urlsafe(32)
    response.set_cookie(
        "csrf_token", csrf, httponly=False, samesite="lax",
        secure=settings.environment == "production", max_age=settings.access_token_minutes * 60, path="/",
    )
    return {"authenticated": True}


@router.post("/auth/logout")
def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("csrf_token", path="/")
    return {"authenticated": False}


@router.get("/auth/me")
def me(user=Depends(require_owner)):
    return {"email": user.email, "authenticated": True}


@router.get("/public/profile", response_model=ProfileOut)
def public_profile(db: Session = Depends(get_db)):
    profile = db.scalar(select(Profile).order_by(Profile.id.asc()))
    if not profile:
        raise HTTPException(404, "Profile not configured")
    data = serialize_row(profile)
    if not profile.contact_email_public:
        data["contact_email"] = None
    return data

@router.get("/public/timeline")
def public_timeline(db: Session = Depends(get_db)):
    return db.scalars(select(TimelineEntry).where(TimelineEntry.published.is_(True), TimelineEntry.state == PublicationState.PUBLISHED).order_by(TimelineEntry.id.asc())).all()


@router.get("/public/skills")
def public_skills(db: Session = Depends(get_db)):
    return db.scalars(select(Skill).where(Skill.published.is_(True), Skill.state == PublicationState.PUBLISHED).order_by(Skill.category.asc(), Skill.id.asc())).all()


@router.get("/public/education")
def public_education(db: Session = Depends(get_db)):
    return db.scalars(select(Education).where(Education.published.is_(True), Education.state == PublicationState.PUBLISHED).order_by(Education.id.desc())).all()


@router.get("/public/experience")
def public_experience(db: Session = Depends(get_db)):
    return db.scalars(select(Experience).where(Experience.published.is_(True), Experience.state == PublicationState.PUBLISHED).order_by(Experience.id.desc())).all()


@router.get("/public/achievements")
def public_achievements(db: Session = Depends(get_db)):
    return db.scalars(select(Achievement).where(Achievement.published.is_(True), Achievement.state == PublicationState.PUBLISHED).order_by(Achievement.id.desc())).all()


@router.get("/public/social-links")
def public_social_links(db: Session = Depends(get_db)):
    return db.scalars(select(SocialLink).where(SocialLink.published.is_(True), SocialLink.state == PublicationState.PUBLISHED).order_by(SocialLink.id.asc())).all()


@router.get("/public/interests")
def public_interests(db: Session = Depends(get_db)):
    return db.scalars(select(Interest).where(Interest.published.is_(True), Interest.state == PublicationState.PUBLISHED).order_by(Interest.id.asc())).all()


@router.get("/public/resume")
def public_resume(db: Session = Depends(get_db)):
    row = db.scalar(select(Resume).where(Resume.active.is_(True), Resume.state == PublicationState.PUBLISHED).order_by(Resume.id.desc()))
    return row or {"active": False}


def published_rows(db: Session, model):
    stmt = select(model).where(model.visibility.in_([Visibility.PUBLIC, Visibility.UNLISTED]), model.state == PublicationState.PUBLISHED)
    if hasattr(model, "updated_at"):
        stmt = stmt.order_by(model.updated_at.desc())
    else:
        stmt = stmt.order_by(model.id.desc())
    return db.scalars(stmt).all()


def public_collection(db, model):
    stmt = select(model).where(model.visibility == Visibility.PUBLIC, model.state == PublicationState.PUBLISHED)
    if hasattr(model, "updated_at"):
        stmt = stmt.order_by(model.updated_at.desc())
    else:
        stmt = stmt.order_by(model.id.desc())
    return db.scalars(stmt).all()


@router.get("/public/github")
def public_github(db: Session = Depends(get_db)):
    profile = db.scalar(select(Profile).order_by(Profile.id.asc()))
    if not profile or not profile.github_username:
        return {"configured": False, "username": None, "repositories": []}
    return {"configured": True, "username": profile.github_username, "repositories": github_repositories(profile.github_username.strip(), safe_featured_repos(profile.github_featured_repos))}


@router.get("/public/projects")
def public_projects(db: Session = Depends(get_db)):
    return public_collection(db, Project)


@router.get("/public/research")
def public_research(db: Session = Depends(get_db)):
    return public_collection(db, Research)


@router.get("/public/ideas")
def public_ideas(db: Session = Depends(get_db)):
    rows = public_collection(db, Idea)
    return [{
        "id": row.id, "public_id": row.public_id, "slug": row.slug, "title": row.title,
        "one_line": row.one_line, "status": row.status.value if hasattr(row.status, "value") else row.status,
        "prototype_status": row.prototype_status, "visibility": row.visibility.value if hasattr(row.visibility, "value") else row.visibility,
        "state": row.state.value if hasattr(row.state, "value") else row.state, "requires_permission": row.requires_permission,
    } for row in rows]


@router.get("/public/experiments")
def public_experiments(db: Session = Depends(get_db)):
    return public_collection(db, Experiment)


@router.get("/public/experiments/{experiment_id}/data")
def public_experiment_data(experiment_id: int, db: Session = Depends(get_db)):
    exp = db.get(Experiment, experiment_id)
    if not exp or exp.state != PublicationState.PUBLISHED or exp.visibility in {Visibility.PRIVATE, Visibility.CONFIDENTIAL}:
        raise HTTPException(404, "Experiment not found")
    rows = db.scalars(select(ExperimentDatum).where(ExperimentDatum.experiment_id == experiment_id).order_by(ExperimentDatum.series.asc(), ExperimentDatum.id.asc())).all()
    return [serialize_row(r) for r in rows]


@router.get("/public/publications")
def public_publications(db: Session = Depends(get_db)):
    return public_collection(db, Publication)


@router.get("/public/notes")
def public_notes(db: Session = Depends(get_db)):
    return public_collection(db, BlogPost)


@router.get("/public/notes/{slug}")
def public_note_detail(slug: str, db: Session = Depends(get_db)):
    row = db.scalar(select(BlogPost).where(BlogPost.slug == slug, BlogPost.state == PublicationState.PUBLISHED, BlogPost.visibility.in_([Visibility.PUBLIC, Visibility.UNLISTED])))
    if not row:
        raise HTTPException(404, "Note not found")
    return row


@router.get("/public/projects/{slug}")
def public_project_detail(slug: str, db: Session = Depends(get_db)):
    row = db.scalar(select(Project).where(Project.slug == slug, Project.state == PublicationState.PUBLISHED, Project.visibility.in_([Visibility.PUBLIC, Visibility.UNLISTED])))
    if not row:
        raise HTTPException(404, "Project not found")
    return row


@router.get("/public/research/{slug}")
def public_research_detail(slug: str, db: Session = Depends(get_db)):
    row = db.scalar(select(Research).where(Research.slug == slug, Research.state == PublicationState.PUBLISHED, Research.visibility.in_([Visibility.PUBLIC, Visibility.UNLISTED])))
    if not row:
        raise HTTPException(404, "Research not found")
    return row


@router.get("/public/ideas/{slug}")
def public_idea_detail(slug: str, db: Session = Depends(get_db)):
    row = db.scalar(select(Idea).where(Idea.slug == slug, Idea.state == PublicationState.PUBLISHED, Idea.visibility.in_([Visibility.PUBLIC, Visibility.UNLISTED])))
    if not row:
        raise HTTPException(404, "Idea not found")
    return {
        "id": row.id, "public_id": row.public_id, "slug": row.slug, "title": row.title,
        "one_line": row.one_line, "question": row.question, "problem": row.problem,
        "current_approach": row.current_approach, "proposed_concept": row.proposed_concept,
        "status": row.status.value if hasattr(row.status, "value") else row.status,
        "prototype_status": row.prototype_status, "visibility": row.visibility.value if hasattr(row.visibility, "value") else row.visibility,
        "state": row.state.value if hasattr(row.state, "value") else row.state,
        "requires_permission": row.requires_permission,
        "disclosure_note": "Only the owner's deliberately published high-level description is exposed here. Detailed implementation material is not public unless separately authorized.",
    }


@router.get("/public/experiments/{slug}")
def public_experiment_detail(slug: str, db: Session = Depends(get_db)):
    row = db.scalar(select(Experiment).where(Experiment.slug == slug, Experiment.state == PublicationState.PUBLISHED, Experiment.visibility.in_([Visibility.PUBLIC, Visibility.UNLISTED])))
    if not row:
        raise HTTPException(404, "Experiment not found")
    return row


@router.get("/public/agreements/{agreement_type}")
def current_agreement(agreement_type: str, db: Session = Depends(get_db)):
    row = db.scalar(select(AgreementTemplate).where(AgreementTemplate.agreement_type == agreement_type, AgreementTemplate.active.is_(True)).order_by(AgreementTemplate.id.desc()))
    if not row:
        raise HTTPException(404, "Agreement not found")
    return {"agreement_type": row.agreement_type, "version": row.version, "title": row.title, "body": row.body, "sha256": row.sha256}


@router.get("/public/search")
def public_search(q: str = "", limit: int = 20, db: Session = Depends(get_db)):
    query = q.strip()
    limit = max(1, min(50, int(limit or 20)))
    if len(query) < 2:
        return {"query": query, "results": []}
    pattern = f"%{query}%"
    results = []
    models = [
        (Project, "project", "/work"),
        (Research, "research", "/research"),
        (Idea, "idea", "/ideas"),
        (Experiment, "experiment", "/experiments"),
        (Publication, "publication", "/publications"),
        (BlogPost, "note", "/notes"),
        (Achievement, "achievement", "/about#achievements"),
        (TimelineEntry, "timeline", "/timeline"),
    ]
    for model, kind, base_path in models:
        searchable = [getattr(model, name) for name in ("title", "summary", "abstract", "one_line", "question", "excerpt", "venue") if hasattr(model, name)]
        if not searchable:
            continue
        visibility_filters = []
        if hasattr(model, "visibility"):
            visibility_filters.append(model.visibility == Visibility.PUBLIC)
        if hasattr(model, "published"):
            visibility_filters.append(model.published.is_(True))
        visibility_filters.append(model.state == PublicationState.PUBLISHED)
        stmt = select(model).where(
            *visibility_filters,
            or_(*[col.ilike(pattern) for col in searchable]),
        )
        if hasattr(model, "updated_at"):
            stmt = stmt.order_by(model.updated_at.desc())
        else:
            stmt = stmt.order_by(model.id.desc())
        for row in db.scalars(stmt.limit(limit)).all():
            slug_or_id = getattr(row, "slug", None) or str(row.id)
            results.append({
                "id": row.id,
                "type": kind,
                "title": getattr(row, "title", ""),
                "description": getattr(row, "summary", None) or getattr(row, "abstract", None) or getattr(row, "one_line", None) or getattr(row, "excerpt", None) or getattr(row, "question", None) or "",
                "status": getattr(getattr(row, "status", None), "value", getattr(row, "status", None)),
                "url": base_path if kind == "achievement" else f"{base_path}/{slug_or_id}",
            })
    results.sort(key=lambda item: (item["title"] or "").casefold())
    return {"query": query, "results": results[:limit]}


@router.post("/analytics/event", status_code=202)
def analytics_event(payload: AnalyticsIn, request: Request, db: Session = Depends(get_db)):
    if payload.event_type not in {"page_view", "external_click", "search", "content_view"}:
        raise HTTPException(422, "Unsupported analytics event")
    db.add(AnalyticsEvent(
        event_type=payload.event_type, path=payload.path,
        entity_type=payload.entity_type, entity_id=payload.entity_id,
        referrer=(request.headers.get("referer") or "")[:1000] or None,
    ))
    db.commit()
    return {"accepted": True}


@router.post("/collaboration-requests", response_model=RequestOut, status_code=201)
def create_request(payload: RequestIn, request: Request, db: Session = Depends(get_db)):
    if payload.request_kind not in ALLOWED_REQUEST_KINDS:
        raise HTTPException(422, "Invalid request type")
    if payload.request_kind == "INVESTOR_OUTREACH" and payload.funding_amount is not None:
        raise HTTPException(422, "Funding amount belongs on a Funding Request")
    if payload.request_kind == "FUNDING_REQUEST" and payload.funding_amount is None:
        raise HTTPException(422, "Funding amount is required for a Funding Request")
    if payload.funding_currency.upper() != payload.funding_currency:
        raise HTTPException(422, "Funding currency must use uppercase ISO-style letters")
    if not verify_turnstile_token(getattr(payload, "turnstile_token", None), request):
        raise HTTPException(403, "Human verification failed")
    if payload.honeypot:
        return RequestOut(
            request_id="REQ-BLOCKED", status="REJECTED", accepted_at=datetime.now(timezone.utc),
            agreement_type=payload.agreement_type, agreement_version=payload.agreement_version,
            agreement_sha256=payload.agreement_sha256,
        )
    if payload.signature_name.strip().casefold() != payload.name.strip().casefold():
        raise HTTPException(422, "Typed signature must match full name")
    invalid_rights = [right for right in payload.requested_rights if right not in ALLOWED_REQUEST_RIGHTS]
    if invalid_rights:
        raise HTTPException(422, f"Unsupported requested rights: {invalid_rights[0]}")
    require_valid_url(str(payload.professional_profile_url) if payload.professional_profile_url else None)
    require_valid_url(str(payload.website_url) if payload.website_url else None)
    require_valid_url(str(payload.pitch_deck_url) if payload.pitch_deck_url else None)
    expected_agreement_type = KIND_DEFAULT_AGREEMENT[payload.request_kind]
    if payload.request_kind in {"INVESTOR_OUTREACH", "FUNDING_REQUEST"} and payload.agreement_type != expected_agreement_type:
        raise HTTPException(422, f"{payload.request_kind} must use its designated agreement template")
    agreement = db.scalar(select(AgreementTemplate).where(
        AgreementTemplate.agreement_type == payload.agreement_type,
        AgreementTemplate.version == payload.agreement_version,
        AgreementTemplate.active.is_(True),
    ))
    site_terms = db.scalar(select(AgreementTemplate).where(
        AgreementTemplate.agreement_type == "SITE_TERMS",
        AgreementTemplate.active.is_(True),
    ))
    if not site_terms or site_terms.version != payload.site_terms_version or site_terms.sha256 != payload.site_terms_sha256:
        raise HTTPException(409, "Site terms version is not current; reload and try again")
    if not payload.privacy_acknowledged:
        raise HTTPException(422, "Privacy acknowledgement is required")
    if not agreement or agreement.sha256 != payload.agreement_sha256:
        raise HTTPException(409, "Agreement version is not current; reload the agreement and try again")
    idea_id = None
    if payload.idea_public_id:
        idea = db.scalar(select(Idea).where(Idea.public_id == payload.idea_public_id))
        if idea:
            idea_id = idea.id
    ip_hash = network_hash(request)
    request_id = f"REQ-{datetime.now(timezone.utc).year}-{secrets.token_hex(6).upper()}"
    row = CollaborationRequest(
        request_id=request_id, request_kind=payload.request_kind, idea_id=idea_id, name=payload.name.strip(), email=payload.email,
        organization=payload.organization, role=payload.role, country=payload.country,
        professional_profile_url=str(payload.professional_profile_url) if payload.professional_profile_url else None,
        website_url=str(payload.website_url) if payload.website_url else None,
        signature_name=payload.signature_name.strip(), acceptance_ip_hash=ip_hash,
        purpose=payload.purpose.strip(), requested_rights=json.dumps(payload.requested_rights),
        message=payload.message.strip(), investment_interest=payload.investment_interest, funding_amount=payload.funding_amount,
        funding_currency=payload.funding_currency.upper(), funding_stage=payload.funding_stage, funding_instrument=payload.funding_instrument,
        funding_use=payload.funding_use, pitch_deck_url=str(payload.pitch_deck_url) if payload.pitch_deck_url else None,
        agreement_type=agreement.agreement_type,
        agreement_version=agreement.version, agreement_sha256=agreement.sha256, agreement_body_snapshot=agreement.body,
        accepted_at=datetime.now(timezone.utc), status=RequestStatus.PENDING, site_terms_version=site_terms.version, site_terms_sha256=site_terms.sha256, site_terms_body_snapshot=site_terms.body, privacy_acknowledged_at=datetime.now(timezone.utc),
    )
    db.add(row)
    log(db, payload.email, "AGREEMENT_ACCEPTED_AND_REQUEST_CREATED", "CollaborationRequest", request_id, {
        "request_kind": payload.request_kind, "idea_public_id": payload.idea_public_id, "rights": payload.requested_rights,
        "funding_amount": payload.funding_amount, "funding_currency": payload.funding_currency.upper(), "funding_stage": payload.funding_stage,
        "agreement_version": agreement.version, "agreement_sha256": agreement.sha256, "site_terms_version": site_terms.version, "site_terms_sha256": site_terms.sha256,
        "professional_profile_url": str(payload.professional_profile_url) if payload.professional_profile_url else None,
    })
    db.commit()
    db.refresh(row)
    send_email(settings.owner_email, f"New collaboration request {request_id}", f"{payload.name} ({payload.email}) submitted request {request_id}. Purpose: {payload.purpose}")
    return row


@router.get("/admin/experiments/{experiment_id}/data")
def admin_experiment_data(experiment_id: int, user=Depends(require_owner), db: Session = Depends(get_db)):
    if not db.get(Experiment, experiment_id):
        raise HTTPException(404, "Experiment not found")
    rows = db.scalars(select(ExperimentDatum).where(ExperimentDatum.experiment_id == experiment_id).order_by(ExperimentDatum.series.asc(), ExperimentDatum.id.asc())).all()
    return [serialize_row(r) for r in rows]


@router.put("/admin/experiments/{experiment_id}/data")
def replace_experiment_data(experiment_id: int, payload: dict, user=Depends(require_owner), db: Session = Depends(get_db)):
    if not db.get(Experiment, experiment_id):
        raise HTTPException(404, "Experiment not found")
    data = payload.get("data", [])
    if not isinstance(data, list) or len(data) > 5000:
        raise HTTPException(422, "data must be a list with at most 5000 points")
    for old in db.scalars(select(ExperimentDatum).where(ExperimentDatum.experiment_id == experiment_id)).all():
        db.delete(old)
    rows=[]
    for item in data:
        if not isinstance(item, dict) or "y_value" not in item:
            raise HTTPException(422, "Each data point requires y_value")
        try: y=float(item["y_value"])
        except Exception: raise HTTPException(422,"y_value must be numeric")
        x=item.get("x_value")
        try: x=float(x) if x not in (None, "") else None
        except Exception: raise HTTPException(422,"x_value must be numeric when provided")
        row=ExperimentDatum(experiment_id=experiment_id,series=str(item.get("series") or "default")[:100],x_label=str(item.get("x_label") or "")[:160] or None,x_value=x,y_value=y,unit=str(item.get("unit") or "")[:80] or None,note=str(item.get("note") or "")[:500] or None)
        db.add(row); rows.append(row)
    log(db,user.email,"EXPERIMENT_DATA_REPLACED","Experiment",str(experiment_id),{"points":len(rows)})
    db.commit()
    return [serialize_row(r) for r in rows]


@router.get("/admin/analytics/report")
def analytics_report(user=Depends(require_owner), db: Session = Depends(get_db)):
    since=datetime.now(timezone.utc)-timedelta(days=30)
    total=db.scalar(select(func.count()).select_from(AnalyticsEvent).where(AnalyticsEvent.created_at>=since)) or 0
    by_type=db.execute(select(AnalyticsEvent.event_type,func.count()).where(AnalyticsEvent.created_at>=since).group_by(AnalyticsEvent.event_type).order_by(func.count().desc())).all()
    top_paths=db.execute(select(AnalyticsEvent.path,func.count()).where(AnalyticsEvent.created_at>=since).group_by(AnalyticsEvent.path).order_by(func.count().desc()).limit(15)).all()
    top_content=db.execute(select(AnalyticsEvent.entity_type,AnalyticsEvent.entity_id,func.count()).where(AnalyticsEvent.created_at>=since,AnalyticsEvent.entity_id.is_not(None)).group_by(AnalyticsEvent.entity_type,AnalyticsEvent.entity_id).order_by(func.count().desc()).limit(20)).all()
    return {"window_days":30,"total_events":total,"by_type":[{"event_type":a,"count":b} for a,b in by_type],"top_paths":[{"path":a,"count":b} for a,b in top_paths],"top_content":[{"entity_type":a,"entity_id":b,"count":c} for a,b,c in top_content]}


@router.get("/admin/summary")
def admin_summary(user=Depends(require_owner), db: Session = Depends(get_db)):
    return {
        "projects": db.query(Project).count(), "research": db.query(Research).count(),
        "ideas": db.query(Idea).count(), "experiments": db.query(Experiment).count(),
        "publications": db.query(Publication).count(), "requests": db.query(CollaborationRequest).count(),
        "pending_requests": db.query(CollaborationRequest).filter(CollaborationRequest.status == RequestStatus.PENDING).count(),
        "unread_messages": db.query(ContactMessage).filter(ContactMessage.read_at.is_(None)).count(),
        "page_views_30d": db.query(AnalyticsEvent).filter(AnalyticsEvent.event_type == "page_view", AnalyticsEvent.created_at >= datetime.now(timezone.utc) - timedelta(days=30)).count(),
    }


@router.get("/admin/requests")
def admin_requests(user=Depends(require_owner), db: Session = Depends(get_db)):
    rows = db.scalars(select(CollaborationRequest).order_by(CollaborationRequest.created_at.desc())).all()
    return [serialize_row(r) for r in rows]


@router.patch("/admin/requests/{request_id}")
def admin_request_status(request_id: str, payload: dict, user=Depends(require_owner), db: Session = Depends(get_db)):
    row = db.scalar(select(CollaborationRequest).where(CollaborationRequest.request_id == request_id))
    if not row:
        raise HTTPException(404, "Request not found")
    status = payload.get("status")
    if status not in [x.value for x in RequestStatus]:
        raise HTTPException(422, "Invalid status")
    row.status = RequestStatus(status)
    row.owner_notes = str(payload.get("owner_notes", row.owner_notes))[:5000]
    grant = db.scalar(select(PermissionGrant).where(PermissionGrant.request_id == request_id))
    if row.status == RequestStatus.APPROVED:
        rights = payload.get("rights")
        if rights is not None and not isinstance(rights, list):
            raise HTTPException(422, "Rights must be a list")
        rights = rights if isinstance(rights, list) else json.loads(row.requested_rights)
        if not rights:
            raise HTTPException(422, "Approved permissions must contain at least one right")
        if grant is None:
            grant = PermissionGrant(request_id=request_id, rights_json=json.dumps(rights), notes=row.owner_notes)
            db.add(grant)
        else:
            grant.rights_json = json.dumps(rights)
            grant.revoked_at = None
            grant.notes = row.owner_notes
    elif row.status == RequestStatus.REJECTED and grant:
        grant.revoked_at = datetime.now(timezone.utc)
    log(db, user.email, "COLLABORATION_REQUEST_UPDATED", "CollaborationRequest", request_id, payload)
    db.commit()
    if row.status == RequestStatus.APPROVED:
        send_email(row.email, f"Collaboration request {request_id} approved", "Your requested collaboration/use request was approved by the owner. Any use remains limited to the permissions recorded in the permission grant.")
    elif row.status == RequestStatus.REJECTED:
        send_email(row.email, f"Collaboration request {request_id} update", "Your request was rejected or access was revoked by the owner. Please contact the owner if you need clarification.")
    return {"request_id": request_id, "status": row.status.value, "permission_granted": row.status == RequestStatus.APPROVED}


@router.post("/admin/agreements")
def admin_create_agreement(payload: dict, user=Depends(require_owner), db: Session = Depends(get_db)):
    agreement_type = str(payload.get("agreement_type", "")).strip()
    version = str(payload.get("version", "")).strip()
    title = str(payload.get("title", "")).strip()
    body = str(payload.get("body", "")).strip()
    if not agreement_type or not version or not title or not body:
        raise HTTPException(422, "Agreement type, version, title and body are required")
    digest = hashlib.sha256(body.encode()).hexdigest()
    if payload.get("active", True):
        db.query(AgreementTemplate).filter(AgreementTemplate.agreement_type == agreement_type).update({"active": False})
    row = AgreementTemplate(agreement_type=agreement_type, version=version, title=title, body=body, sha256=digest, active=bool(payload.get("active", True)))
    db.add(row)
    log(db, user.email, "AGREEMENT_VERSION_CREATED", "AgreementTemplate", version, {"agreement_type": agreement_type, "sha256": digest})
    db.commit(); db.refresh(row)
    return serialize_row(row)


@router.patch("/admin/agreements/{agreement_id}")
def admin_update_agreement(agreement_id: int, payload: dict, user=Depends(require_owner), db: Session = Depends(get_db)):
    row = db.get(AgreementTemplate, agreement_id)
    if not row:
        raise HTTPException(404, "Agreement not found")
    if "body" in payload or "version" in payload or "agreement_type" in payload:
        raise HTTPException(409, "Agreement versions are immutable after creation; create a new version instead")
    if "active" in payload:
        row.active = bool(payload["active"])
        if row.active:
            db.query(AgreementTemplate).filter(AgreementTemplate.agreement_type == row.agreement_type, AgreementTemplate.id != row.id).update({"active": False})
    log(db, user.email, "AGREEMENT_STATUS_UPDATED", "AgreementTemplate", str(row.id), {"active": row.active})
    db.commit(); db.refresh(row)
    return serialize_row(row)


@router.get("/admin/agreements")
def agreements(user=Depends(require_owner), db: Session = Depends(get_db)):
    return [serialize_row(r) for r in db.scalars(select(AgreementTemplate).order_by(AgreementTemplate.id.desc())).all()]


@router.get("/admin/permissions")
def permissions(user=Depends(require_owner), db: Session = Depends(get_db)):
    rows = db.scalars(select(PermissionGrant).order_by(PermissionGrant.granted_at.desc())).all()
    return [serialize_row(r) | {"access_link_issued": bool(r.access_token_hash)} for r in rows]


@router.post("/admin/requests/{request_id}/access-link")
def issue_access_link(request_id: str, payload: dict | None = None, user=Depends(require_owner), db: Session = Depends(get_db)):
    row = db.scalar(select(CollaborationRequest).where(CollaborationRequest.request_id == request_id))
    if not row:
        raise HTTPException(404, "Request not found")
    if row.status != RequestStatus.APPROVED:
        raise HTTPException(409, "Only approved requests can receive a restricted-access link")
    if not row.idea_id:
        raise HTTPException(409, "This request is not attached to an idea")
    grant = db.scalar(select(PermissionGrant).where(PermissionGrant.request_id == request_id))
    if not grant:
        raise HTTPException(409, "Permission grant does not exist")
    idea = db.get(Idea, row.idea_id)
    if not idea:
        raise HTTPException(404, "Linked idea not found")
    days = 30
    if payload and payload.get("expires_days") is not None:
        try:
            days = max(1, min(3650, int(payload["expires_days"])))
        except Exception:
            raise HTTPException(422, "expires_days must be an integer")
    token = secrets.token_urlsafe(32)
    grant.access_token_hash = hashlib.sha256(token.encode()).hexdigest()
    grant.access_token_issued_at = datetime.now(timezone.utc)
    grant.expires_at = datetime.now(timezone.utc) + timedelta(days=days)
    grant.revoked_at = None
    log(db, user.email, "RESTRICTED_ACCESS_LINK_ISSUED", "PermissionGrant", str(grant.id), {"request_id": request_id, "idea_public_id": idea.public_id, "expires_days": days})
    db.commit()
    return {
        "request_id": request_id,
        "idea_public_id": idea.public_id,
        "expires_at": grant.expires_at,
        "access_token": token,
        "access_path": f"/api/v1/shared/{token}/ideas/{idea.slug}",
        "warning": "Treat this access URL as a bearer credential. Send it only to the approved requester."
    }


@router.delete("/admin/requests/{request_id}/access-link")
def revoke_access_link(request_id: str, user=Depends(require_owner), db: Session = Depends(get_db)):
    grant = db.scalar(select(PermissionGrant).where(PermissionGrant.request_id == request_id))
    if not grant:
        raise HTTPException(404, "Permission grant not found")
    grant.access_token_hash = None
    grant.revoked_at = datetime.now(timezone.utc)
    log(db, user.email, "RESTRICTED_ACCESS_LINK_REVOKED", "PermissionGrant", str(grant.id), {"request_id": request_id})
    db.commit()
    return {"request_id": request_id, "revoked": True}


IDEA_PERMISSION_FIELDS = {
    "Concept": {"question", "problem", "current_approach", "proposed_concept"},
    "Technical documentation": {"how_it_works", "required_technology", "assumptions", "risks", "open_questions"},
    "Prototype": {"prototype_status", "applications"},
    "Research": {"open_questions", "applications"},
}

def scoped_idea_view(idea, rights: list[str]):
    data = serialize_row(idea)
    base = {"id", "public_id", "slug", "title", "one_line", "status", "visibility", "state", "requires_permission", "created_at", "updated_at"}
    allowed = set(base)
    for right in rights:
        allowed.update(IDEA_PERMISSION_FIELDS.get(str(right), set()))
    return {key: data[key] for key in allowed if key in data}

@router.get("/shared/{token}/ideas/{slug}")
def shared_idea(token: str, slug: str, db: Session = Depends(get_db)):
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    grant = db.scalar(select(PermissionGrant).where(PermissionGrant.access_token_hash == token_hash))
    if not grant or grant.revoked_at is not None:
        raise HTTPException(404, "Shared access link is invalid or revoked")
    if grant.expires_at:
        expires_at = grant.expires_at if grant.expires_at.tzinfo else grant.expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(410, "Shared access link has expired")
    request_row = db.scalar(select(CollaborationRequest).where(CollaborationRequest.request_id == grant.request_id, CollaborationRequest.status == RequestStatus.APPROVED))
    if not request_row or not request_row.idea_id:
        raise HTTPException(404, "Shared access is no longer available")
    idea = db.scalar(select(Idea).where(Idea.id == request_row.idea_id, Idea.slug == slug))
    if not idea:
        raise HTTPException(404, "Idea not found")
    rights = json.loads(grant.rights_json or "[]")
    log(db, request_row.email, "RESTRICTED_ACCESS_USED", "PermissionGrant", str(grant.id), {
        "request_id": request_row.request_id,
        "idea_public_id": idea.public_id,
        "rights": rights,
    })
    db.commit()
    return {"access_scope": rights, "request_id": request_row.request_id, "expires_at": grant.expires_at, "idea": scoped_idea_view(idea, rights)}


@router.get("/admin/projects/{project_id}/technologies")
def admin_project_technologies(project_id: int, user=Depends(require_owner), db: Session = Depends(get_db)):
    if not db.get(Project, project_id):
        raise HTTPException(404, "Project not found")
    return [serialize_row(r) for r in db.scalars(select(ProjectTechnology).where(ProjectTechnology.project_id == project_id).order_by(ProjectTechnology.id.asc())).all()]


@router.put("/admin/projects/{project_id}/technologies")
def admin_set_project_technologies(project_id: int, payload: dict, user=Depends(require_owner), db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    technologies = payload.get("technologies", [])
    if not isinstance(technologies, list):
        raise HTTPException(422, "technologies must be a list")
    cleaned = []
    for value in technologies[:30]:
        v = str(value).strip()[:120]
        if v and v not in cleaned:
            cleaned.append(v)
    for row in list(project.technologies):
        db.delete(row)
    db.flush()
    for value in cleaned:
        db.add(ProjectTechnology(project_id=project_id, technology=value))
    log(db, user.email, "PROJECT_TECHNOLOGIES_REPLACED", "Project", str(project_id), {"technologies": cleaned})
    db.commit()
    return [serialize_row(r) for r in db.scalars(select(ProjectTechnology).where(ProjectTechnology.project_id == project_id).order_by(ProjectTechnology.id.asc())).all()]


@router.get("/public/projects/{project_id}/technologies")
def public_project_technologies(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project or project.state != PublicationState.PUBLISHED or project.visibility == Visibility.PRIVATE or project.visibility == Visibility.CONFIDENTIAL:
        raise HTTPException(404, "Project not found")
    return [r.technology for r in db.scalars(select(ProjectTechnology).where(ProjectTechnology.project_id == project_id).order_by(ProjectTechnology.id.asc())).all()]


@router.get("/admin/research/{research_id}/references")
def admin_research_references(research_id: int, user=Depends(require_owner), db: Session = Depends(get_db)):
    if not db.get(Research, research_id):
        raise HTTPException(404, "Research not found")
    return [serialize_row(r) for r in db.scalars(select(ResearchReference).where(ResearchReference.research_id == research_id).order_by(ResearchReference.id.asc())).all()]


@router.put("/admin/research/{research_id}/references")
def admin_set_research_references(research_id: int, payload: dict, user=Depends(require_owner), db: Session = Depends(get_db)):
    research = db.get(Research, research_id)
    if not research:
        raise HTTPException(404, "Research not found")
    refs = payload.get("references", [])
    if not isinstance(refs, list):
        raise HTTPException(422, "references must be a list")
    for old in list(research.references):
        db.delete(old)
    db.flush()
    created=[]
    for ref in refs[:50]:
        if not isinstance(ref, dict) or not str(ref.get("title", "")).strip():
            continue
        url = str(ref.get("url") or "").strip() or None
        if url:
            require_valid_url(url)
        created.append(ResearchReference(
            research_id=research_id, title=str(ref["title"]).strip()[:400], authors=str(ref.get("authors") or "")[:5000],
            venue=str(ref.get("venue") or "")[:250] or None, year=ref.get("year"), doi=str(ref.get("doi") or "")[:300] or None,
            url=url, citation_text=str(ref.get("citation_text") or "")[:5000] or None
        ))
    db.add_all(created)
    log(db, user.email, "RESEARCH_REFERENCES_REPLACED", "Research", str(research_id), {"count": len(created)})
    db.commit()
    return [serialize_row(r) for r in db.scalars(select(ResearchReference).where(ResearchReference.research_id == research_id).order_by(ResearchReference.id.asc())).all()]


@router.get("/public/research/{research_id}/references")
def public_research_references(research_id: int, db: Session = Depends(get_db)):
    research = db.get(Research, research_id)
    if not research or research.state != PublicationState.PUBLISHED or research.visibility in {Visibility.PRIVATE, Visibility.CONFIDENTIAL}:
        raise HTTPException(404, "Research not found")
    return [serialize_row(r) for r in db.scalars(select(ResearchReference).where(ResearchReference.research_id == research_id).order_by(ResearchReference.id.asc())).all()]


@router.get("/admin/scholarly/doi/{doi:path}")
def scholarly_doi_lookup(doi: str, user=Depends(require_owner), db: Session = Depends(get_db)):
    clean = doi.strip()
    if not clean or len(clean) > 300:
        raise HTTPException(422, "DOI is required")
    url = f"https://api.crossref.org/works/{clean}"
    try:
        req = UrlRequest(url, headers={"Accept":"application/json","User-Agent":"personal-research-lab/1.0"})
        with urlopen(req, timeout=settings.github_timeout_seconds) as response:
            payload = json.loads(response.read().decode())
        message = payload.get("message") or {}
        authors = ", ".join(
            [f"{a.get('given','')} {a.get('family','')}".strip() for a in (message.get("author") or []) if (a.get("given") or a.get("family"))]
        )
        published = message.get("published-print") or message.get("published-online") or message.get("issued") or {}
        parts = published.get("date-parts") or []
        year = parts[0][0] if parts and parts[0] else None
        return {
            "doi": message.get("DOI") or clean,
            "title": (message.get("title") or [""])[0],
            "authors": authors,
            "venue": message.get("container-title", [""])[0] if message.get("container-title") else None,
            "year": year,
            "publisher": message.get("publisher"),
            "type": message.get("type"),
            "url": message.get("URL"),
            "abstract": message.get("abstract"),
            "source": "Crossref",
        }
    except Exception as exc:
        raise HTTPException(404, f"DOI lookup failed: {exc.__class__.__name__}")

@router.post("/admin/resume/generate")
def generate_resume(user=Depends(require_owner), db: Session = Depends(get_db)):
    profile=db.scalar(select(Profile).where(Profile.user_id==user.id))
    if not profile:
        raise HTTPException(404,"Profile not found")
    try:
        data=build_resume_pdf(profile,db)
    except Exception as exc:
        raise HTTPException(500,f"Resume generation failed: {exc}")
    digest=hashlib.sha256(data).hexdigest(); key=f"generated-resume-{digest}.pdf"
    storage=get_storage(); storage.save(key,data)
    db.query(Resume).update({"active":False})
    row=Media(filename="generated-resume.pdf",storage_key=key,mime_type="application/pdf",size_bytes=len(data),sha256=digest,visibility=Visibility.PUBLIC)
    db.add(row); db.flush()
    resume=Resume(label="Generated Resume",file_url=f"/api/v1/public/media/{key}",active=True,state=PublicationState.PUBLISHED)
    db.add(resume)
    log(db,user.email,"RESUME_GENERATED","Resume",str(resume.id),{"media_id":row.id,"sha256":digest})
    db.commit(); db.refresh(resume)
    return serialize_row(resume)|{"media_id":row.id}


@router.get("/admin/messages")
def messages(user=Depends(require_owner), db: Session = Depends(get_db)):
    return [serialize_row(r) for r in db.scalars(select(ContactMessage).order_by(ContactMessage.created_at.desc()).limit(250)).all()]


@router.patch("/admin/messages/{message_id}/read")
def mark_message_read(message_id: int, user=Depends(require_owner), db: Session = Depends(get_db)):
    row = db.get(ContactMessage, message_id)
    if not row:
        raise HTTPException(404, "Message not found")
    row.read_at = datetime.now(timezone.utc)
    log(db, user.email, "CONTACT_MESSAGE_READ", "ContactMessage", str(message_id))
    db.commit()
    return {"id": message_id, "read": True}


@router.get("/admin/audit-logs")
def audit_logs(user=Depends(require_owner), db: Session = Depends(get_db)):
    return [serialize_row(r) for r in db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(500)).all()]


@router.get("/admin/content")
def admin_content(user=Depends(require_owner), db: Session = Depends(get_db)):
    result = {}
    for name, model in CONTENT_MODELS.items():
        result[name] = [serialize_row(r) for r in db.scalars(select(model).order_by(model.id.desc()).limit(250)).all()]
    return result


@router.get("/admin/content/{collection}")
def admin_list(collection: str, user=Depends(require_owner), db: Session = Depends(get_db)):
    model = CONTENT_MODELS.get(collection)
    if not model:
        raise HTTPException(404, "Unknown collection")
    rows = db.scalars(select(model).order_by(model.id.desc()).limit(250)).all()
    return [serialize_row(r) for r in rows]


@router.post("/admin/content/{collection}")
def admin_create(collection: str, payload: dict, user=Depends(require_owner), db: Session = Depends(get_db)):
    model = CONTENT_MODELS.get(collection)
    if not model:
        raise HTTPException(404, "Unknown collection")
    wants_public = (
        str(payload.get("state", "")) == PublicationState.PUBLISHED.value
        and (
            str(payload.get("visibility", "")) == Visibility.PUBLIC.value
            or ("published" in model.__table__.columns and payload.get("published") is True)
            or (model is Resume and payload.get("active") is True)
        )
    )
    if wants_public and payload.get("publication_safety_confirmed") is not True:
        raise HTTPException(409, "Public publishing requires explicit safety confirmation")
    allowed = {c.name for c in model.__table__.columns if c.name not in {"id", "created_at", "updated_at"}}
    data = {k: v for k, v in payload.items() if k in allowed}
    for url_key in ("github_url", "demo_url", "case_study_url", "paper_url", "code_url", "dataset_url", "doi", "pdf_url", "preprint_url", "file_url", "url", "link", "linkedin_url", "avatar_url", "orcid_url", "google_scholar_url", "arxiv_url", "contact_email"):
        if url_key in data and url_key.endswith("_url"):
            require_valid_url(data[url_key])
    if model is SocialLink and "url" in data:
        require_social_url(str(data["url"]))
    if "slug" in allowed:
        data["slug"] = slugify(str(data.get("slug") or data.get("title") or "item"))
        existing = db.scalar(select(model).where(model.slug == data["slug"]))
        if existing:
            data["slug"] = f"{data['slug']}-{secrets.token_hex(3)}"
    if model is Idea and not data.get("public_id"):
        data["public_id"] = f"IDEA-{secrets.token_hex(4).upper()}"
    if "state" in data:
        data["state"] = PublicationState(str(data["state"]))
    if "visibility" in data:
        data["visibility"] = Visibility(str(data["visibility"]))
    if "status" in data:
        if model is Idea: data["status"] = IdeaStatus(str(data["status"]))
        elif model is Experiment: data["status"] = ExperimentStatus(str(data["status"]))
    if "classification" in data:
        data["classification"] = ContentClassification(str(data["classification"])).value
    if "published" in data:
        data["published"] = bool(data["published"])
    row = model(**data)
    db.add(row); db.flush()
    record_revision(db, user.email, row, "Created record")
    log(db, user.email, "CONTENT_CREATED", model.__name__, str(row.id), {"collection": collection, "title": getattr(row, "title", "")})
    db.commit(); db.refresh(row)
    return serialize_row(row)


@router.put("/admin/content/{collection}/{item_id}")
def admin_update(collection: str, item_id: int, payload: dict, user=Depends(require_owner), db: Session = Depends(get_db)):
    model = CONTENT_MODELS.get(collection)
    if not model: raise HTTPException(404, "Unknown collection")
    row = db.get(model, item_id)
    if not row: raise HTTPException(404, "Item not found")
    next_state = enum_text(payload.get("state", getattr(row, "state", "")))
    next_visibility = enum_text(payload.get("visibility", getattr(row, "visibility", "")))
    wants_public = (
        next_state == PublicationState.PUBLISHED.value
        and (
            next_visibility == Visibility.PUBLIC.value
            or (hasattr(row, "published") and bool(payload.get("published", getattr(row, "published", False))))
            or (model is Resume and bool(payload.get("active", getattr(row, "active", False))))
        )
    )
    if wants_public and payload.get("publication_safety_confirmed") is not True:
        raise HTTPException(409, "Public publishing requires explicit safety confirmation")
    allowed = {c.name for c in model.__table__.columns if c.name not in {"id", "created_at", "updated_at"}}
    before_state = getattr(row, "state", None)
    for k, v in payload.items():
        if k not in allowed: continue
        if k in {"github_url", "demo_url", "case_study_url", "paper_url", "code_url", "dataset_url", "pdf_url", "preprint_url", "file_url", "url", "link", "linkedin_url", "avatar_url", "orcid_url", "google_scholar_url", "arxiv_url"}:
            require_valid_url(v)
        if k == "state": v = PublicationState(str(v))
        if k == "visibility": v = Visibility(str(v))
        if k == "classification": v = ContentClassification(str(v)).value
        if k == "status" and model is Idea: v = IdeaStatus(str(v))
        if k == "status" and model is Experiment: v = ExperimentStatus(str(v))
        if k == "published": v = bool(v)
        setattr(row, k, v)
    if hasattr(row, "slug") and not getattr(row, "slug"):
        row.slug = slugify(getattr(row, "title", "item"))
    after_state = getattr(row, "state", None)
    db.flush()
    record_revision(db, user.email, row, str(payload.get("change_note") or ("Published record" if after_state == PublicationState.PUBLISHED and before_state != after_state else "Updated record")))
    action = "CONTENT_PUBLISHED" if before_state != after_state and after_state == PublicationState.PUBLISHED else "CONTENT_UPDATED"
    log(db, user.email, action, model.__name__, str(item_id), payload)
    db.commit(); db.refresh(row)
    return serialize_row(row)


@router.get("/admin/content/{collection}/{item_id}/revisions")
def admin_content_revisions(collection: str, item_id: int, user=Depends(require_owner), db: Session = Depends(get_db)):
    model = CONTENT_MODELS.get(collection)
    if not model or model not in STATE_MODELS:
        raise HTTPException(404, "Revision history is available for project, research, idea, experiment, publication and notes records")
    if not db.get(model, item_id):
        raise HTTPException(404, "Item not found")
    rows = db.scalars(select(ContentRevision).where(ContentRevision.entity_type == model.__name__, ContentRevision.entity_id == item_id).order_by(ContentRevision.version_no.desc())).all()
    return [serialize_row(r) for r in rows]

@router.post("/admin/content/{collection}/{item_id}/restore/{revision_id}")
def admin_restore_revision(collection: str, item_id: int, revision_id: int, user=Depends(require_owner), db: Session=Depends(get_db)):
    model = CONTENT_MODELS.get(collection)
    if not model or model not in STATE_MODELS:
        raise HTTPException(404, "Revision history is available for project, research, idea, experiment, publication and notes records")
    row = db.get(model, item_id)
    revision = db.get(ContentRevision, revision_id)
    if not row or not revision or revision.entity_type != model.__name__ or revision.entity_id != item_id:
        raise HTTPException(404, "Revision not found")
    try:
        snapshot = json.loads(revision.snapshot_json)
    except Exception:
        raise HTTPException(409, "Revision snapshot is invalid")
    allowed = {c.name for c in model.__table__.columns} - {"id", "created_at", "updated_at"}
    if "publication_safety_confirmed" in snapshot:
        snapshot.pop("publication_safety_confirmed", None)
    is_public = snapshot.get("state") == PublicationState.PUBLISHED.value and snapshot.get("visibility") == Visibility.PUBLIC.value
    if is_public:
        raise HTTPException(409, "Restoring a public revision requires the owner to republish it through the safety check")
    for k, v in snapshot.items():
        if k not in allowed: continue
        if k == "state": v = PublicationState(str(v))
        if k == "visibility": v = Visibility(str(v))
        if k == "classification": v = ContentClassification(str(v)).value
        if k == "status" and model is Idea: v = IdeaStatus(str(v))
        if k == "status" and model is Experiment: v = ExperimentStatus(str(v))
        if k == "published": v = bool(v)
        setattr(row, k, v)
    db.flush()
    record_revision(db, user.email, row, f"Restored revision {revision.version_no}")
    log(db, user.email, "CONTENT_REVISION_RESTORED", model.__name__, str(item_id), {"revision_id": revision_id, "revision_version": revision.version_no})
    db.commit(); db.refresh(row)
    return serialize_row(row)

@router.delete("/admin/content/{collection}/{item_id}", status_code=204)
def admin_delete(collection: str, item_id: int, user=Depends(require_owner), db: Session = Depends(get_db)):
    model = CONTENT_MODELS.get(collection)
    if not model: raise HTTPException(404, "Unknown collection")
    row = db.get(model, item_id)
    if not row: raise HTTPException(404, "Item not found")
    db.delete(row)
    log(db, user.email, "CONTENT_DELETED", model.__name__, str(item_id))
    db.commit()
    return Response(status_code=204)


@router.get("/admin/github/repositories")
def admin_github_repositories(user=Depends(require_owner), db: Session = Depends(get_db)):
    profile = db.scalar(select(Profile).where(Profile.user_id == user.id))
    if not profile or not profile.github_username:
        return {"configured": False, "username": None, "repositories": []}
    selected = safe_featured_repos(profile.github_featured_repos)
    return {"configured": True, "username": profile.github_username, "repositories": github_repositories(profile.github_username, []), "selected": selected}

@router.get("/admin/visibility-settings")
def admin_visibility_settings(user=Depends(require_owner), db: Session=Depends(get_db)):
    rows=db.scalars(select(VisibilitySetting).order_by(VisibilitySetting.key.asc())).all()
    return [serialize_row(r) for r in rows]

@router.put("/admin/visibility-settings/{key}")
def admin_set_visibility_setting(key: str, payload: dict, user=Depends(require_owner), db: Session=Depends(get_db)):
    clean=re.sub(r"[^a-z0-9._-]+", "-", key.lower()).strip("-")[:120]
    if not clean:
        raise HTTPException(422, "Invalid visibility setting key")
    value=str(payload.get("default_visibility", "PRIVATE")).upper()
    if value not in {v.value for v in Visibility}:
        raise HTTPException(422, "Invalid default visibility")
    row=db.scalar(select(VisibilitySetting).where(VisibilitySetting.key==clean))
    if row is None:
        row=VisibilitySetting(key=clean, default_visibility=Visibility(value), notes=str(payload.get("notes", ""))[:2000])
        db.add(row)
    else:
        row.default_visibility=Visibility(value)
        row.notes=str(payload.get("notes", row.notes))[:2000]
    log(db, user.email, "VISIBILITY_SETTING_UPDATED", "VisibilitySetting", clean, {"default_visibility": value})
    db.commit(); db.refresh(row)
    return serialize_row(row)

@router.get("/admin/profile")
def admin_profile(user=Depends(require_owner), db: Session = Depends(get_db)):
    return db.scalar(select(Profile).where(Profile.user_id == user.id))


@router.put("/admin/profile")
def update_profile(payload: dict, user=Depends(require_owner), db: Session = Depends(get_db)):
    profile = db.scalar(select(Profile).where(Profile.user_id == user.id))
    if not profile:
        profile = Profile(user_id=user.id)
        db.add(profile)
        db.flush()
    allowed = {c.name for c in Profile.__table__.columns} - {"id", "user_id", "created_at", "updated_at"}
    for k, v in payload.items():
        if k in allowed:
            if k.endswith("_url"):
                require_valid_url(v)
            if k == "contact_email" and v:
                try:
                    v = str(validate_email(str(v), check_deliverability=False).normalized)
                except EmailNotValidError:
                    raise HTTPException(422, "Invalid contact email")
            if k == "contact_email_public":
                v = bool(v)
            setattr(profile, k, v)
    log(db, user.email, "PROFILE_UPDATED", "Profile", str(profile.id), payload)
    record_revision(db, user.email, profile, "Profile updated")
    db.commit(); db.refresh(profile)
    return profile


@router.post("/contact")
def contact(payload: dict, request: Request, db: Session = Depends(get_db)):
    if not verify_turnstile_token(str(payload.get("turnstile_token") or ""), request):
        raise HTTPException(403, "Human verification failed")
    if payload.get("website"):
        return {"status": "received", "message": "Your message has been received."}
    try:
        validate_email(str(payload.get("email", "")), check_deliverability=False)
    except EmailNotValidError:
        raise HTTPException(422, "Invalid email")
    name = str(payload.get("name", "")).strip()
    message = str(payload.get("message", "")).strip()
    if len(name) < 2 or len(message) < 5 or len(message) > 5000:
        raise HTTPException(422, "Name and message are required")
    site_terms_version=str(payload.get("site_terms_version") or "")
    site_terms_sha256=str(payload.get("site_terms_sha256") or "")
    site_terms = db.scalar(select(AgreementTemplate).where(AgreementTemplate.agreement_type=="SITE_TERMS", AgreementTemplate.active.is_(True)))
    if not site_terms or site_terms.version != site_terms_version or site_terms.sha256 != site_terms_sha256:
        raise HTTPException(409, "Site terms version is not current; reload and try again")
    if payload.get("privacy_acknowledged") is not True:
        raise HTTPException(422, "Privacy acknowledgement is required")
    accepted_at=datetime.now(timezone.utc)
    row = ContactMessage(name=name, email=str(payload["email"]), organization=str(payload.get("organization") or "")[:250] or None, message=message, network_ip_hash=network_hash(request), site_terms_version=site_terms.version, site_terms_sha256=site_terms.sha256, site_terms_body_snapshot=site_terms.body, terms_accepted_at=accepted_at)
    db.add(row); db.commit(); db.refresh(row)
    send_email(settings.owner_email, f"New website message from {name}", f"From: {name} <{payload['email']}>\nOrganization: {payload.get('organization') or '-'}\n\n{message}")
    return {"status": "received", "message": "Your message has been received."}


@router.get("/admin/dashboard-data")
def dashboard_data(user=Depends(require_owner), db: Session = Depends(get_db)):
    return {
        "summary": admin_summary(user, db),
        "recent_requests": admin_requests(user, db)[:6],
        "recent_messages": messages(user, db)[:6],
        "recent_audit": audit_logs(user, db)[:12],
    }


@router.get("/public/media/{storage_key}")
def public_media(storage_key: str, db: Session = Depends(get_db)):
    row = db.scalar(select(Media).where(Media.storage_key == storage_key, Media.visibility == Visibility.PUBLIC))
    if not row:
        raise HTTPException(404, "Media not found")
    storage = get_storage()
    if not isinstance(storage, LocalStorage):
        try:
            location = storage.public_url(row.storage_key)
        except Exception:
            raise HTTPException(503, "S3 media delivery is not configured")
        return Response(status_code=302, headers={"Location": location})
    try:
        path = storage.path(row.storage_key).resolve()
        root = storage.root.resolve()
        if root != path and root not in path.parents:
            raise HTTPException(400, "Invalid media key")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(400, "Invalid media key")
    if not path.is_file():
        raise HTTPException(404, "Media file not found")
    return FileResponse(path, media_type=row.mime_type, filename=row.filename)


def content_is_public(entity_type: str, entity_id: int, db: Session) -> bool:
    model_map = {
        "project": Project, "projects": Project,
        "research": Research,
        "idea": Idea, "ideas": Idea,
        "experiment": Experiment, "experiments": Experiment,
        "publication": Publication, "publications": Publication,
        "blog": BlogPost, "notes": BlogPost,
    }
    model = model_map.get(entity_type)
    if not model:
        return False
    row = db.get(model, entity_id)
    return bool(row and getattr(row, "state", None) == PublicationState.PUBLISHED and getattr(row, "visibility", None) not in {Visibility.PRIVATE, Visibility.CONFIDENTIAL})


@router.get("/admin/media-links/{entity_type}/{entity_id}")
def admin_media_links(entity_type: str, entity_id: int, user=Depends(require_owner), db: Session = Depends(get_db)):
    rows = db.scalars(select(MediaLink).where(MediaLink.entity_type == entity_type, MediaLink.entity_id == entity_id).order_by(MediaLink.sort_order.asc(), MediaLink.id.asc())).all()
    return [serialize_row(r) for r in rows]


@router.put("/admin/media-links/{entity_type}/{entity_id}")
def set_media_links(entity_type: str, entity_id: int, payload: dict, user=Depends(require_owner), db: Session = Depends(get_db)):
    media_ids = payload.get("media_ids", [])
    if not isinstance(media_ids, list):
        raise HTTPException(422, "media_ids must be a list")
    unique=[]
    for value in media_ids[:30]:
        try: unique.append(int(value))
        except (TypeError, ValueError): continue
    unique=list(dict.fromkeys(unique))
    media_rows = db.scalars(select(Media).where(Media.id.in_(unique))).all() if unique else []
    if len(media_rows) != len(unique):
        raise HTTPException(422, "One or more media IDs do not exist")
    for old in db.scalars(select(MediaLink).where(MediaLink.entity_type == entity_type, MediaLink.entity_id == entity_id)).all():
        db.delete(old)
    db.flush()
    for idx, media_id in enumerate(unique):
        db.add(MediaLink(media_id=media_id, entity_type=entity_type, entity_id=entity_id, role="attachment", sort_order=idx))
    log(db, user.email, "MEDIA_LINKS_REPLACED", entity_type, str(entity_id), {"media_ids": unique})
    db.commit()
    return [serialize_row(r) for r in db.scalars(select(MediaLink).where(MediaLink.entity_type == entity_type, MediaLink.entity_id == entity_id).order_by(MediaLink.sort_order.asc(), MediaLink.id.asc())).all()]


@router.get("/public/media-links/{entity_type}/{entity_id}")
def public_media_links(entity_type: str, entity_id: int, db: Session = Depends(get_db)):
    if not content_is_public(entity_type, entity_id, db):
        raise HTTPException(404, "Content not found")
    rows = db.scalars(select(MediaLink).where(MediaLink.entity_type == entity_type, MediaLink.entity_id == entity_id).order_by(MediaLink.sort_order.asc(), MediaLink.id.asc())).all()
    media_ids = [r.media_id for r in rows]
    media_rows = {r.id: r for r in db.scalars(select(Media).where(Media.id.in_(media_ids), Media.visibility == Visibility.PUBLIC)).all()} if media_ids else {}
    return [{"id": r.id, "role": r.role, "sort_order": r.sort_order, "filename": media_rows[r.media_id].filename, "mime_type": media_rows[r.media_id].mime_type, "url": f"/api/v1/public/media/{media_rows[r.media_id].storage_key}"} for r in rows if r.media_id in media_rows]


@router.get("/admin/media")
def admin_media(user=Depends(require_owner), db: Session = Depends(get_db)):
    return [serialize_row(r) for r in db.scalars(select(Media).order_by(Media.created_at.desc()).limit(500)).all()]


@router.delete("/admin/media/{media_id}", status_code=204)
def delete_media(media_id: int, user=Depends(require_owner), db: Session = Depends(get_db)):
    row = db.get(Media, media_id)
    if not row:
        raise HTTPException(404, "Media not found")
    storage = get_storage()
    db.delete(row)
    log(db, user.email, "MEDIA_DELETED", "Media", str(media_id), {"storage_key": row.storage_key})
    db.commit()
    storage.delete(row.storage_key)
    return Response(status_code=204)


@router.post("/admin/media")
async def upload_media(file: UploadFile = File(...), visibility: Visibility = Form(Visibility.PRIVATE), user=Depends(require_owner), db: Session = Depends(get_db)):
    allowed = {"image/jpeg", "image/png", "image/webp", "application/pdf", "text/plain", "text/markdown"}
    if file.content_type not in allowed:
        raise HTTPException(415, "Unsupported file type")
    max_size = 10 * 1024 * 1024
    data = await file.read(max_size + 1)
    if len(data) > max_size:
        raise HTTPException(413, "File exceeds 10 MB limit")
    if file.content_type == "application/pdf" and not data.startswith(b"%PDF"):
        raise HTTPException(415, "File content does not match PDF type")
    if file.content_type == "image/png" and not data.startswith(b"\x89PNG"):
        raise HTTPException(415, "File content does not match PNG type")
    if file.content_type == "image/jpeg" and not data.startswith(b"\xff\xd8\xff"):
        raise HTTPException(415, "File content does not match JPEG type")
    if file.content_type == "image/webp" and not (data.startswith(b"RIFF") and data[8:12] == b"WEBP"):
        raise HTTPException(415, "File content does not match WebP type")
    digest = hashlib.sha256(data).hexdigest()
    ext = os.path.splitext(file.filename or "")[1].lower()
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", file.filename or "upload")[:200]
    storage_key = f"{digest}{ext}"
    storage = get_storage()
    storage.save(storage_key, data, file.content_type)
    row = Media(filename=safe_name, storage_key=storage_key, mime_type=file.content_type, size_bytes=len(data), sha256=digest, visibility=visibility)
    db.add(row); db.flush()
    log(db, user.email, "MEDIA_UPLOADED", "Media", str(row.id), {"filename": safe_name, "mime_type": file.content_type, "size": len(data)})
    db.commit(); db.refresh(row)
    return {"id": row.id, "filename": row.filename, "storage_key": row.storage_key, "sha256": row.sha256, "size_bytes": row.size_bytes, "visibility": row.visibility.value, "public_url": f"/api/v1/public/media/{row.storage_key}" if row.visibility == Visibility.PUBLIC else None}
