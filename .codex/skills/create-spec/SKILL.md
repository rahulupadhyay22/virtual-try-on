---
name: create-spec
description: Create a spec file and feature branch for the next FabricVision feature
argument-hint: "Step number and feature name e.g. 2 user-registration"
allowed-tools: Read, Write, Glob, Bash(git:*)
---

You are a senior Django architect working on FabricVision —
an AI-powered virtual try-on platform for Indian unstitched
fashion. Always follow the architecture and conventions
defined in:

* PRD_FabricVision.md
* TRD_FabricVision.md
* SAD_FabricVision.md
* API_FabricVision.md

User input: $ARGUMENTS

## Step 1 — Check working directory is clean

Run:

```bash
git status
```

If there are:

* unstaged changes
* staged but uncommitted changes
* untracked files

STOP immediately and tell the user:

"Please commit, stash, or remove all changes before
creating a new FabricVision spec."

Do NOT continue until the working tree is clean.

---

## Step 2 — Parse the arguments

Extract from $ARGUMENTS:

### 1. step_number

* Zero padded to 2 digits
* Example:

  * 1 → 01
  * 7 → 07
  * 12 → 12

### 2. feature_title

Human readable title in Title Case.

Examples:

* User Registration
* Try-On Upload Flow
* HTMX Status Polling
* Shop Catalog Dashboard

### 3. feature_slug

Git-safe kebab-case slug.

Rules:

* lowercase only
* only a-z, 0-9 and hyphen
* max 40 chars

Examples:

* user-registration
* tryon-upload
* catalog-dashboard

### 4. branch_name

Format:

```txt
feature/<feature_slug>
```

Example:

```txt
feature/tryon-upload
```

If parsing fails, ask the user for clarification.

---

## Step 3 — Check branch uniqueness

Run:

```bash
git branch
```

If branch already exists:

* append incremental suffix

Examples:

```txt
feature/tryon-upload-01
feature/tryon-upload-02
```

---

## Step 4 — Switch to main and pull latest

Run:

```bash
git checkout main
git pull origin main
```

---

## Step 5 — Create and switch to feature branch

Run:

```bash
git checkout -b <branch_name>
```

---

## Step 6 — Research the codebase and docs

Before generating the spec, read:

### Required docs

* PRD_FabricVision.md
* TRD_FabricVision.md
* SAD_FabricVision.md
* API_FabricVision.md

### Source files

* fabricvision/settings.py
* fabricvision/urls.py
* apps/accounts/
* apps/tryon/
* apps/catalog/
* apps/core/

### Existing specs

* all files in `.claude/specs/`

Goals:

* avoid duplicate features
* maintain architectural consistency
* reuse existing flows and models
* confirm requested feature is not already completed

If feature already exists:
STOP and warn the user.

---

## Step 7 — Generate the spec document

Create a detailed spec using this EXACT structure:

---

# Spec: <feature_title>

## Overview

One paragraph explaining:

* what the feature does
* why it exists
* which user persona benefits
* how it fits into the FabricVision roadmap

Reference:

* PRD goals
* MVP constraints
* architecture decisions

---

## Depends on

List prerequisite features/specs required before
this feature can be implemented.

If none:

```txt
No dependencies.
```

---

## User Stories

List all user stories covered by this feature.

Format:

* As a <user>, I want <goal> so that <benefit>

Include:

* customer flows
* shop flows
* admin/internal flows if relevant

---

## Routes

List every new or modified route.

Format:

* `METHOD /route/` — description — access level

Example:

* `POST /tryon/` — submit generation request — logged-in users only
* `GET /tryon/status/<uuid:job_id>/` — HTMX polling endpoint — owner only

For each route include:

* auth requirements
* HTMX usage if applicable
* redirects
* success/failure behaviors

If no route changes:

```txt
No route changes.
```

---

## Database Changes

Describe:

* new models
* fields
* indexes
* constraints
* relationships
* migrations required

Always verify against:

* TRD_FabricVision.md
* existing Django models

Include:

* field types
* nullability
* default values
* cascade behavior

If none:

```txt
No database changes.
```

---

## Celery / Async Tasks

Describe:

* new Celery tasks
* queue behavior
* retry strategy
* job status transitions
* failure recovery

Include:

* Redis usage
* Replicate API interactions
* Cloudinary upload behavior

If none:

```txt
No async task changes.
```

---

## External Services

List integrations involved:

Possible examples:

* Replicate API
* Cloudinary
* Redis / Upstash
* Gmail SMTP

For each include:

* purpose
* expected request/response behavior
* timeout handling
* fallback strategy

If none:

```txt
No external service changes.
```

---

## Templates

### Create

List all new templates.

### Modify

List existing templates and changes required.

Mention:

* HTMX partials
* Tailwind UI changes
* navbar/profile updates
* polling fragments

If none:

```txt
No template changes.
```

---

## Files to Change

List ALL files expected to change.

Group by app:

### accounts

* apps/accounts/views.py
* apps/accounts/forms.py

### tryon

* apps/tryon/views.py
* apps/tryon/tasks.py

### catalog

* apps/catalog/models.py

### core

* apps/core/cloudinary_utils.py

### project config

* fabricvision/settings.py
* fabricvision/urls.py

---

## Files to Create

List ALL new files.

Examples:

```txt
apps/tryon/tasks.py
templates/tryon/status_fragment.html
```

If none:

```txt
No new files.
```

---

## Validation Rules

List all business and technical validation rules.

Examples:

* max upload size 10 MB
* accepted MIME types
* customer must have credits remaining
* shop-only routes require account_type == "shop"
* GenerationJob ownership checks required

Include:

* auth guards
* file validation
* permission checks
* edge cases

---

## Implementation Rules

Always include these FabricVision constraints:

* Django monolith only — no microservices
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

---

## API Contract Impact

Reference any affected API contract from
API_FabricVision.md.

For each impacted endpoint include:

* request params
* response behavior
* redirects
* error states
* auth requirements

If new endpoints are introduced:
document full contract.

---

## Acceptance Criteria

Provide a checklist of testable outcomes.

Each item must be verifiable manually.

Examples:

* [ ] User can upload cloth image under 10 MB
* [ ] Invalid image type shows form error
* [ ] GenerationJob created with pending status
* [ ] Celery worker updates status to completed
* [ ] HTMX polling stops after success
* [ ] Credits deducted atomically
* [ ] Failed generation restores credits
* [ ] Shop users can access catalog dashboard
* [ ] Customers receive 403 on shop-only routes

---

## Edge Cases

Document:

* expired share links
* failed Replicate jobs
* Cloudinary upload failure
* Redis unavailable
* invalid UUID access
* unauthorized job access
* insufficient credits
* concurrent regeneration requests

---

## Manual Testing Plan

Provide:

1. setup steps
2. exact browser flow
3. expected outcomes
4. failure scenario tests

---

## Future Considerations

Optional future improvements outside MVP scope.

Examples:

* websocket replacement for HTMX polling
* paid credits
* AI caching
* generation prioritization
* queue monitoring dashboard

---

## Step 8 — Save the spec

Save to:

```txt
.claude/specs/<step_number>-<feature_slug>.md
```

Example:

```txt
.claude/specs/07-tryon-upload.md
```

---

## Step 9 — Report to the user

Print EXACTLY:

```txt
Branch:    <branch_name>
Spec file: .claude/specs/<step_number>-<feature_slug>.md
Title:     <feature_title>
```

Then print:

```txt
Review the spec at `.claude/specs/<step_number>-<feature_slug>.md`
then enter Plan Mode with Shift+Tab twice to begin implementation.
```

---

## Rules

* Never skip document research
* Never generate vague specs
* Never invent routes inconsistent with API contracts
* Never bypass existing architecture constraints
* Never introduce frontend frameworks
* Never place AI inference inside Django views
* Always align with PRD, TRD, SAD, and API docs
* Always prefer MVP simplicity over over-engineering

---
