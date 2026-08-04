"""
Application settings.

Everything configurable lives here and is read from environment variables
(or the .env file when running locally). Nothing secret is ever hardcoded,
which is what lets this repo stay public on GitHub safely.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Database -------------------------------------------------------
    # SQLite by default: a single file on disk, zero setup.
    # To switch to Postgres later, change only this one value, e.g.
    # postgresql+psycopg2://user:password@host:5432/dbname
    DATABASE_URL: str = "sqlite:///./portfolio.db"

    # --- Email ----------------------------------------------------------
    # If RESEND_API_KEY is empty, the app runs in "console mode": submissions
    # are saved to the database and printed to the terminal instead of emailed.
    # That means you can build and test the whole form without signing up
    # for anything.
    RESEND_API_KEY: str = ""
    # The address the notification is sent FROM. Resend gives you
    # onboarding@resend.dev to test with before you verify your own domain.
    MAIL_FROM: str = "onboarding@resend.dev"
    # Where you want to receive contact form notifications.
    MAIL_TO: str = "shaandilyaprathit@gmail.com"

    # --- App ------------------------------------------------------------
    APP_NAME: str = "Portfolio API"
    # Set to "production" on the deployment host. Controls whether the
    # interactive /docs page is exposed publicly.
    ENVIRONMENT: str = "development"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"


settings = Settings()
