"""
Application entrypoint.

This single app does two jobs:
  1. Serves the API (everything under /api)
  2. Serves your existing portfolio files from static/

Because both are served from the same origin, there is no CORS setup to
get wrong. Run it with:

    uvicorn app.main:app --reload
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.database import init_db
from app.routers import contact
from app.schemas import HealthResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs once on startup and once on shutdown."""
    logger.info("Starting %s in %s mode", settings.APP_NAME, settings.ENVIRONMENT)
    init_db()
    logger.info("Database ready")
    if not settings.RESEND_API_KEY:
        logger.warning(
            "No email key set — submissions will be saved and printed here "
            "instead of emailed."
        )
    yield
    logger.info("Shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.4.0",
    lifespan=lifespan,
    # The interactive docs are genuinely useful while building, but there's
    # no reason to leave a public map of your API on a portfolio site.
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None,
    openapi_url=None if settings.is_production else "/openapi.json",
)

# --- API routes ---------------------------------------------------------
app.include_router(contact.router)


@app.get("/api/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    """
    Confirms the app is running. Hosting platforms ping this to decide
    whether a deploy succeeded, and it's the first thing to check when
    something looks broken.
    """
    return HealthResponse(
        status="ok",
        environment=settings.ENVIRONMENT,
        database="sqlite" if settings.DATABASE_URL.startswith("sqlite") else "postgres",
        email_configured=bool(settings.RESEND_API_KEY),
    )


# --- Error handling -----------------------------------------------------
@app.exception_handler(StarletteHTTPException)
async def not_found_handler(request: Request, exc: StarletteHTTPException):
    """
    Serves the site's own themed 404.html for unknown page URLs.

    Without this, StaticFiles returns a bare JSON error and the designed
    error page never gets used. API routes keep returning JSON, because a
    caller of /api/... wants a machine-readable response, not HTML.
    """
    is_api = request.url.path.startswith("/api")
    if exc.status_code == 404 and not is_api:
        page = STATIC_DIR / "404.html"
        if page.is_file():
            return FileResponse(page, status_code=404)
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


# --- Static site --------------------------------------------------------
# Mounted last, so it never shadows an /api route.
if STATIC_DIR.is_dir() and any(STATIC_DIR.iterdir()):
    app.mount(
        "/",
        StaticFiles(directory=STATIC_DIR, html=True),
        name="static",
    )
else:
    @app.get("/", tags=["system"])
    def placeholder() -> dict:
        return {
            "message": "API is running. Copy your portfolio files into static/ "
                       "to serve the site from here.",
            "docs": "/docs" if not settings.is_production else "disabled",
        }
