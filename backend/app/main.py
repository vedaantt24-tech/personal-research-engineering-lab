from contextlib import asynccontextmanager
from time import monotonic

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.session import Base, engine
from app.models import entities  # noqa: F401
from app.api.routes import router

_rate_window: dict[tuple[str, str], list[float]] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.auto_create_tables:
        Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title=settings.app_name, version="1.3.0", lifespan=lifespan)

@app.middleware("http")
async def simple_rate_limit(request: Request, call_next):
    limited = request.url.path in {"/api/v1/contact", "/api/v1/collaboration-requests", "/api/v1/analytics/event", "/api/v1/auth/login"} or request.url.path.startswith("/api/v1/shared/")
    if limited:
        bucket = "/api/v1/shared" if request.url.path.startswith("/api/v1/shared/") else request.url.path
        key = (request.client.host if request.client else "unknown", bucket)
        now = monotonic()
        timestamps = [t for t in _rate_window.get(key, []) if now - t < 60]
        if len(_rate_window) > 20000:
            stale = [k for k, ts in _rate_window.items() if not ts or now - ts[-1] >= 60]
            for stale_key in stale[:5000]:
                _rate_window.pop(stale_key, None)
        limit = {"/api/v1/contact":5, "/api/v1/collaboration-requests":10, "/api/v1/analytics/event":30, "/api/v1/auth/login":8, "/api/v1/shared":30}[bucket]
        if len(timestamps) >= limit:
            return JSONResponse({"detail":"Too many requests. Please try again later."}, status_code=429, headers={"Retry-After":"60"})
        timestamps.append(now)
        _rate_window[key] = timestamps
    return await call_next(request)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in settings.cors_origins.split(",") if x.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-CSRF-Token"],
)

@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Cache-Control"] = "no-store" if request.url.path.startswith("/api/") else response.headers.get("Cache-Control", "public, max-age=300")
    return response

app.include_router(router)
