# Spec: Project Foundation

## Overview
Establish the Django monolith foundation for FabricVision so the team can build MVP features reliably, with environment-based settings, Celery wiring, core utilities, and base templates aligned to the PRD/TRD/SAD. This phase enables early developer workflow and production readiness while keeping within MVP constraints for a single-repo, template-driven architecture that serves both end customers and shop users.

## Depends on
No dependencies.

## User Stories
* As a developer, I want a consistent Django project scaffold so that future features can be implemented quickly and safely.
* As an operator, I want a health check endpoint so that Railway uptime monitoring can verify the service is running.
* As a user, I want the root URL to redirect me to the correct starting page so that navigation is predictable.

## Routes
* `GET /` -- root redirect to /tryon/ if logged in, else /accounts/login/ -- public
* `GET /health/` -- uptime check returning plain text `ok` -- public

## Database Changes
No database changes.

## Celery / Async Tasks
* Add Celery app configuration in `fabricvision/celery.py` with autodiscovery and Redis broker/backend from `REDIS_URL`.
* Configure task time limits and concurrency per TRD; no business tasks are introduced in this phase.
* No job status transitions in this phase.

## External Services
* **PostgreSQL (Railway)** -- primary database via `DATABASE_URL` -- required for Django startup, no fallback. PostgreSQL (Railway) is production database but local development can use SQLite or a local PostgreSQL instance.
* **Redis / Upstash** -- Celery broker/result backend via `REDIS_URL` -- required for worker startup; web can run even if broker is unavailable.
* **Cloudinary** -- storage configuration via `CLOUDINARY_*` env vars -- required for future uploads, no calls in this phase.
* **Replicate** -- API token via `REPLICATE_API_TOKEN` -- configured only, no calls in this phase.
* **Gmail SMTP** -- email settings via `EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD` -- configured only, no emails sent in this phase.

## Templates

### Create
* `templates/base.html`
* `templates/navbar.html`

### Modify
No template changes.

## Files to Change

### accounts
No changes.

### tryon
No changes.

### catalog
No changes.

### core
No changes.

### project config
* `manage.py`
* `fabricvision/__init__.py`
* `fabricvision/settings.py`
* `fabricvision/settings_prod.py`
* `fabricvision/urls.py`
* `fabricvision/wsgi.py`
* `fabricvision/asgi.py`
* `fabricvision/celery.py`
* `requirements.txt`
* `Procfile`

## Files to Create
* `manage.py`
* `requirements.txt`
* `Procfile`
* `fabricvision/__init__.py`
* `fabricvision/settings.py`
* `fabricvision/settings_prod.py`
* `fabricvision/urls.py`
* `fabricvision/wsgi.py`
* `fabricvision/asgi.py`
* `fabricvision/celery.py`
* `apps/__init__.py`
* `apps/core/__init__.py`
* `apps/core/apps.py`
* `apps/core/cloudinary_utils.py`
* `apps/core/replicate_client.py`
* `templates/base.html`
* `templates/navbar.html`

## Validation Rules
* `DJANGO_SECRET_KEY`, `DATABASE_URL`, and `ALLOWED_HOSTS` must be defined in production settings.
* `REDIS_URL` required for Celery worker startup; missing broker should not crash web process.
* Health check returns `ok` with HTTP 200 and no authentication required.
* Root URL redirects based on authentication state and never exposes protected content.

## Implementation Rules
* Django monolith only -- no microservices
* Django templates + HTMX only
* No React, Vue, Next.js, or frontend frameworks
* All AI work must run asynchronously in Celery
* Never call Replicate inside request/response cycle
* Use Cloudinary for all image persistence
* Use PostgreSQL via Django ORM
* All protected routes require login
* Shop routes require account_type == "shop"
* HTMX polling every 3 seconds maximum
* Keep business logic out of templates
* Use Django forms for validation
* Use environment variables for secrets
* Never hardcode Cloudinary or Replicate credentials
* Follow existing app separation:
  * accounts
  * tryon
  * catalog
  * core

## API Contract Impact
* `GET /` -- no params -- 302 redirect to `/tryon/` if authenticated, else `/accounts/login/` -- public
* `GET /health/` -- no params -- 200 OK with plain text `ok` -- public

## Acceptance Criteria
* [ ] Django project boots with separate base and prod settings.
* [ ] `GET /` redirects to `/tryon/` for authenticated users and `/accounts/login/` for anonymous users.
* [ ] `GET /health/` returns HTTP 200 with body `ok`.
* [ ] Celery app is configured with Redis broker/backend and autodiscovery enabled.
* [ ] Base templates exist and can be extended by future app templates.
* [ ] No Replicate or Cloudinary calls happen during request/response in this phase.

## Edge Cases
* Missing `DJANGO_SECRET_KEY` or `DATABASE_URL` prevents startup in production settings.
* `REDIS_URL` unavailable: Celery worker fails to start, web process still serves requests.
* Requests to `/health/` should not depend on database or cache availability.

## Manual Testing Plan
1. Start the Django server with base settings and verify it runs without errors.
2. Visit `/` as an anonymous user and confirm redirect to `/accounts/login/`.
3. Log in (if auth exists locally) and confirm `/` redirects to `/tryon/`.
4. Visit `/health/` and confirm response body is `ok` with HTTP 200.

## Future Considerations
* Add CI checks for formatting, migrations, and tests.
* Add Sentry integration and basic logging configuration.
* Provide a `.env.example` for local setup guidance.
