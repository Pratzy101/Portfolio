"""
Database tables.

A "model" here is a Python class that maps to a table. SQLAlchemy reads
these classes and knows how to create the table and read/write rows.

Note the distinction that trips up most people first meeting this stack:
  models.py  = what is STORED in the database
  schemas.py = what is ACCEPTED and RETURNED over the API
They are deliberately separate. You store the submitter's IP address for
spam triage, but you never send it back in an API response.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ContactSubmission(Base):
    __tablename__ = "contact_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    # Populated server-side, never from the request body.
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Kept for spam triage. Never returned in an API response.
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Records whether the notification email actually went out. If the email
    # provider is down, the submission is still saved and this stays False —
    # so a delivery failure never costs you a lead.
    email_sent: Mapped[bool] = mapped_column(default=False, nullable=False)

    def __repr__(self) -> str:
        return f"<ContactSubmission id={self.id} email={self.email!r}>"
