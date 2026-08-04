"""
Email notifications.

Sends you a message when someone submits the contact form.

Two modes:
  Console mode  — no API key set. The submission is printed to the terminal.
                  This is the default, so you can build and test the entire
                  form without signing up for anything.
  Live mode     — RESEND_API_KEY is set. A real email is sent.

The send is deliberately isolated from the database write in routers/contact.py:
if this function fails, the submission is already saved. You lose the
notification, never the lead.
"""

import logging
from datetime import datetime, timezone

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

RESEND_ENDPOINT = "https://api.resend.com/emails"


def _build_body(name: str, email: str, message: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return (
        f"New contact form submission\n"
        f"{'-' * 40}\n"
        f"Name:    {name}\n"
        f"Email:   {email}\n"
        f"Time:    {timestamp}\n"
        f"{'-' * 40}\n\n"
        f"{message}\n"
    )


async def send_contact_notification(name: str, email: str, message: str) -> bool:
    """
    Returns True if the notification was delivered (or logged in console mode).

    Never raises. The caller treats a False return as "saved but not notified",
    which is recorded on the submission row.
    """
    body = _build_body(name, email, message)

    # --- Console mode ---------------------------------------------------
    if not settings.RESEND_API_KEY:
        logger.info("Email not configured — printing submission instead:\n%s", body)
        return True

    # --- Live mode ------------------------------------------------------
    payload = {
        "from": settings.MAIL_FROM,
        "to": [settings.MAIL_TO],
        # reply_to means hitting Reply in your inbox replies to the visitor,
        # not to your own sending address.
        "reply_to": email,
        "subject": f"Portfolio contact — {name}",
        "text": body,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                RESEND_ENDPOINT,
                json=payload,
                headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
            )
        if response.status_code >= 400:
            logger.error(
                "Email provider rejected the send (%s): %s",
                response.status_code,
                response.text,
            )
            return False
        return True

    except httpx.RequestError as exc:
        logger.error("Could not reach the email provider: %s", exc)
        return False
