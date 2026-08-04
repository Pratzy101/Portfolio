"""
API schemas.

These define the shape of data going in and out of the API. FastAPI reads
them and does three jobs automatically:
  1. Rejects malformed requests before your code runs (returns HTTP 422)
  2. Documents the endpoint on the /docs page
  3. Shapes the response so you can't accidentally leak a stored field

This is the "validation for free" part — you describe what valid input
looks like, you never write if-statements checking it.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator


class ContactRequest(BaseModel):
    """What the browser is allowed to send to POST /api/contact."""

    name: str = Field(
        min_length=2,
        max_length=100,
        description="Sender's name",
    )
    email: EmailStr = Field(
        description="Sender's email — format is validated, not just presence"
    )
    message: str = Field(
        min_length=10,
        max_length=5000,
        description="Message body",
    )

    # Honeypot field. It is rendered in the HTML but hidden from humans with
    # CSS, so a real visitor never fills it in. Bots fill every field they
    # find. If this arrives with anything in it, the submission is silently
    # discarded — the bot gets a success response and stops retrying.
    website: str = Field(default="", max_length=200)

    @field_validator("name", "message")
    @classmethod
    def not_only_whitespace(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("This field cannot be empty")
        return cleaned

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Jane Doe",
                    "email": "jane@example.com",
                    "message": "Saw your GAP Reporting Tool write-up — "
                               "would like to set up a call this week.",
                    "website": "",
                }
            ]
        }
    }


class ContactResponse(BaseModel):
    """What the API sends back. Deliberately minimal."""

    status: str = Field(description="Either 'received' or 'error'")
    message: str = Field(description="Text safe to display to the visitor")


class HealthResponse(BaseModel):
    """Returned by GET /api/health — used to confirm the app is alive."""

    status: str
    environment: str
    database: str
    email_configured: bool
