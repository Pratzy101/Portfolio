# Portfolio — V1.4

Personal portfolio site, rebuilt from a static GitHub Pages deployment into a
running web application with a Python backend.

**Live:** _(add URL after first deploy)_

---

## What changed from V1.3.1

V1.3.1 was static HTML, CSS and JavaScript. There was no server, so the
contact section could only offer a `mailto:` link — nothing was captured, and
there was no record of who had reached out.

V1.4 adds a backend. The same frontend is now served by a FastAPI application
that also exposes a small API, so the contact form actually submits, persists,
and notifies.

| | V1.3.1 | V1.4 |
|---|---|---|
| Frontend | HTML / CSS / JS | Unchanged |
| Backend | None | FastAPI (Python) |
| Data | None | SQLAlchemy + SQLite |
| Contact | `mailto:` link | Validated form, stored + emailed |
| Hosting | GitHub Pages | Single app host |

---

## Stack

| Layer | Choice | Why |
|---|---|---|
| Backend | FastAPI | Async, typed, validation built into the request model |
| ORM | SQLAlchemy 2.x | Typed models, portable across SQLite and Postgres |
| Database | SQLite | Single writer, low volume — Postgres is one config line away |
| Validation | Pydantic v2 | Schema is the validation; malformed requests never reach handler code |
| Email | Resend HTTP API | Falls back to console logging when unconfigured |
| Frontend | Vanilla HTML/CSS/JS | No build step; the existing site needed a backend, not a framework |

---

## Architecture

```
Browser
   │  POST /api/contact   (JSON)
   ▼
FastAPI
   ├── Pydantic validation ── malformed input rejected with 422
   ├── Honeypot check ────── bot submissions discarded silently
   ├── Rate limit ────────── 3 submissions per IP per hour
   ├── SQLAlchemy ────────── write to contact_submissions
   └── Email notification ── best-effort; failure is logged, not fatal
   │
   └── StaticFiles ───────── serves the portfolio itself at /
```

The API and the site are served from the same origin, so there is no CORS
configuration and no second deployment to keep in sync.

### Design decisions worth calling out

**The database write and the email send are separate steps.** The submission
is committed before any email is attempted. If the email provider is
unreachable, the message is still stored and `email_sent` stays `false` on the
row. A delivery failure costs a notification, never a lead.

**Validation lives in the schema, not in handler code.** `ContactRequest`
declares what valid input is; FastAPI rejects anything else before the endpoint
function runs. Client-side validation exists only to save a round trip — it is
never treated as a security control.

**Bots get a success response.** A honeypot field, hidden from humans and from
screen readers, is checked server-side. Filled submissions are discarded and
answered with `201`, because an error response just teaches a bot to retry.

**Secrets are never in the repo.** All configuration reads from environment
variables. `.env.example` documents what is needed without exposing anything.

---

## API

| Method | Route | Purpose |
|---|---|---|
| `POST` | `/api/contact` | Submit the contact form |
| `GET` | `/api/health` | Liveness check used by the host |

Interactive documentation is generated at `/docs` in development and disabled
in production.

### `POST /api/contact`

```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "message": "Saw the GAP Reporting Tool write-up — can we set up a call?"
}
```

| Status | Meaning |
|---|---|
| `201` | Received (also returned for discarded honeypot submissions) |
| `422` | Validation failed; body lists the offending fields |

---

## Running locally

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 for the site, or http://127.0.0.1:8000/docs to test
the API directly.

With no email key configured, submissions are saved and printed to the
terminal — the whole form works without signing up for anything.

Full walkthrough — 10 phases, each naming the concepts it introduces, from
environment setup through deployment: [`SETUP_GUIDE.md`](SETUP_GUIDE.md).

---

## Project layout

```
portfolio-app/
├── app/
│   ├── main.py            App entrypoint; mounts API + static site
│   ├── config.py          Settings from environment variables
│   ├── database.py        Engine, session, table creation
│   ├── models.py          Database tables
│   ├── schemas.py         API request/response shapes + validation
│   ├── email_service.py   Notification sending, with console fallback
│   └── routers/
│       └── contact.py     POST /api/contact
├── static/                The portfolio site itself
├── requirements.txt
├── .env.example
└── SETUP_GUIDE.md
```

---

## Roadmap

- [ ] V1.4 — backend, working contact form, single-host deploy
- [ ] Move project and experience content into the database, served via API
- [ ] Authenticated admin view for editing content without a redeploy
- [ ] Alembic migrations once the schema starts changing against real data
- [ ] Server-side GitHub activity feed, replacing the client-side fetch

---

Built by [Prathit Shaandilya](https://www.linkedin.com/in/shaandilyaprathit/).
