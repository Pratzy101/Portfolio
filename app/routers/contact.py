"""
Contact form endpoint.

Route:  POST /api/contact

Flow:
  1. FastAPI validates the request body against ContactRequest.
     Anything malformed is rejected with HTTP 422 before this code runs.
  2. Honeypot check — bots get a success response and are discarded.
  3. Rate limit check — one IP cannot flood the form.
  4. Save to the database. This is the step that must not fail.
  5. Attempt the email notification. Failure here is logged, not fatal.
  6. Return a response the frontend can show the visitor.
"""

import logging
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.email_service import send_contact_notification
from app.models import ContactSubmission
from app.schemas import ContactRequest, ContactResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["contact"])

# --- Rate limiting ------------------------------------------------------
# Deliberately simple: an in-memory record of recent submissions per IP.
# It resets when the app restarts and doesn't work across multiple server
# instances — both fine at this scale. Redis is the answer if this ever
# needs to be shared across processes.
MAX_SUBMISSIONS = 3
WINDOW = timedelta(hours=1)
_recent: dict[str, deque[datetime]] = defaultdict(deque)


def _client_ip(request: Request) -> str:
    """
    Behind a host like Render, the real visitor IP arrives in the
    X-Forwarded-For header; request.client.host would be the proxy.
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _is_rate_limited(ip: str) -> bool:
    now = datetime.now(timezone.utc)
    history = _recent[ip]
    while history and now - history[0] > WINDOW:
        history.popleft()
    if len(history) >= MAX_SUBMISSIONS:
        return True
    history.append(now)
    return False


@router.post(
    "/contact",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit the contact form",
)
async def submit_contact(
    payload: ContactRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> ContactResponse:
    ip = _client_ip(request)

    # 2. Honeypot. A human never sees this field, so anything in it is a bot.
    # Respond as if it worked — a bot that sees an error will just retry.
    if payload.website:
        logger.info("Honeypot triggered from %s — discarding", ip)
        return ContactResponse(
            status="received",
            message="Thanks — your message is on its way.",
        )

    # 3. Rate limit.
    if _is_rate_limited(ip):
        logger.warning("Rate limit hit for %s", ip)
        return ContactResponse(
            status="error",
            message="You've sent a few messages already. Try again in an hour, "
                    "or email shaandilyaprathit@gmail.com directly.",
        )

    # 4. Save first. If this fails, the visitor is told honestly.
    submission = ContactSubmission(
        name=payload.name,
        email=payload.email,
        message=payload.message,
        ip_address=ip,
        user_agent=request.headers.get("user-agent", "")[:255],
    )

    try:
        db.add(submission)
        db.commit()
        db.refresh(submission)
    except Exception:
        db.rollback()
        logger.exception("Failed to save contact submission")
        return ContactResponse(
            status="error",
            message="Something went wrong saving your message. "
                    "Email shaandilyaprathit@gmail.com and it'll reach me.",
        )

    # 5. Notify. Best-effort — the message is already safely stored.
    delivered = await send_contact_notification(
        name=payload.name,
        email=payload.email,
        message=payload.message,
    )

    if delivered:
        submission.email_sent = True
        db.commit()
    else:
        logger.error("Submission %s saved but notification failed", submission.id)

    # 6. Same message either way — a delivery hiccup on my side isn't the
    # visitor's problem, and the message did get through.
    return ContactResponse(
        status="received",
        message="Thanks — message received. I reply within a day.",
    )
