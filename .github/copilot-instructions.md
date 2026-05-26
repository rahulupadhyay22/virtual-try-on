# FabricVision Copilot Instructions

## Build, test, lint
- Tests: `python manage.py test`
- Targeted suites: `python manage.py test apps.tryon.tests` or `pytest apps/tryon/tests/`
- Single test (Django pattern): `python manage.py test <app>.tests.<TestCaseClass>.<test_method>`
- Single test (pytest pattern): `pytest <path>::<TestCaseClass>::<test_method>`

## Stack
- Django monolith
- PostgreSQL
- Celery
- Redis / Upstash
- HTMX
- Django Templates
- Tailwind CSS
- Cloudinary
- Replicate AI API

## Architecture rules
- Replicate API calls MUST NEVER happen inside Django views.
- AI orchestration happens ONLY inside Celery tasks.
- Views should remain thin.
- Business logic belongs in forms, services, tasks, or utilities.

## Async workflow
Generation flow: Upload → Cloudinary → GenerationJob → Celery task → Replicate processing → polling → result persistence

Status values: `pending`, `processing`, `completed`, `failed`

Polling endpoints should reflect database state only.

## HTMX rules
- HTMX endpoints should return partial templates only.
- Polling endpoints must remain lightweight.
- Avoid duplicated template fragments.

## Security rules
- All protected routes require authentication.
- Shop routes require account_type == "shop".
- Users may only access their own GenerationJob records.
- Validate upload MIME types and file sizes server-side.
- Never expose secrets in templates or logs.

## Upload rules
- All uploads use Cloudinary.
- Allowed image types: image/jpeg, image/png, image/webp.
- Reject oversized uploads.
- Never trust client-side validation alone.

## ORM rules
- Use Django ORM only.
- Avoid raw SQL unless necessary.
- Use select_related/prefetch_related when appropriate.
- Prevent N+1 queries.

## Testing rules
- Tests must remain deterministic.
- Mock: Cloudinary, Replicate API, SMTP, external HTTP requests.
- Never call real external APIs during tests.

## Project structure
apps/
├── accounts/
├── catalog/
├── tryon/
└── core/

## Code style
- Prefer readability over abstraction.
- Keep functions focused and small.
- Use clear naming.
- Avoid giant views and templates.
- Reuse shared utilities when appropriate.
