# FabricVision Project Roadmap

This roadmap is derived from the PRD, TRD, SAD, and API contracts in `docs/`. It sequences features by dependency and aligns with the MVP-first architecture: Django monolith, Celery for AI, HTMX for UI, Cloudinary for storage, Replicate for inference, PostgreSQL via ORM.

## Feature Delivery Workflow (repeat for each feature)

1. Run the **create-spec** skill to generate a spec file for the next feature.
2. Enter Plan Mode and confirm the implementation plan.
3. Implement the feature in a dedicated branch.
4. Write tests (use the **fabricvision-test-writer** agent if needed).
5. Run tests (use the **test-feature** skill or **fabricvision-test-runner** agent).
6. Run security + quality review (use **code-review-feature**; it invokes security and quality subagents).
7. Ship the feature (use **ship-feature** skill).

## Phase 0 — Project Foundation (Week 0–1)

1. **Repository and environment bootstrap**
   - Django project setup, settings split (base + prod), dotenv support.
   - Procfile, Celery config, Redis/Upstash wiring, Cloudinary/Replicate credentials (env only).
2. **Core app scaffolding**
   - `apps/core/` utilities: Cloudinary helpers, Replicate client wrapper.
   - Base templates (`base.html`, `navbar.html`) and Tailwind setup.
3. **Global routing**
   - Root redirect and health check endpoint per API contracts.

## Phase 1 — MVP Core (Weeks 1–6)

1. **Accounts + Credits (P0)**
   - Registration, login, logout, profile page.
   - UserProfile with `account_type` and `credits_remaining`.
   - Password reset flow (email via SMTP).
2. **Catalog Data Models (P0)**
   - Shop and FabricItem models.
   - Shop registration details captured for shop accounts.
3. **Try‑On Core Flow (P0)**
   - GenerationJob model and TryOnForm validation.
   - Upload to Cloudinary, create job, deduct credits atomically.
   - Celery task pipeline (DWPose → IDM‑VTON → IP‑Adapter Face).
   - HTMX polling status endpoint (every 3s max).
4. **Result Actions (P0)**
   - Download endpoint with signed Cloudinary URL.
   - Regenerate endpoint (new job, credit check).
5. **Generation History (P1)**
   - Paginated history page for logged‑in users.
6. **Shop Catalog Portal (P0)**
   - CRUD for FabricItem.
   - Catalog dashboard listing and HTMX toggle.
7. **Public Shop Catalog (P1)**
   - `/shop/<slug>/` public catalog page.

## Phase 2 — Growth (Weeks 7–12)

1. **Reference Image Style Conditioning (P1)**
   - Accept optional reference image and pass CLIP features to Stage 2.
2. **Shareable Result Links (P1)**
   - Share token generation + public shared result page.
3. **Send‑to‑Shop Inquiry Flow (P2)**
   - Inquiry creation and shop inbox view.
   - Email notifications (Phase 2).
4. **Shop Analytics Dashboard (P1)**
   - Try‑on counts, most popular fabrics, inquiry count.
5. **Paid Credits (P2)**
   - Razorpay integration and credit pack purchase.

## Phase 3 — Scale (Months 4–6)

1. **AI cost optimization**
   - Migrate from Replicate to self‑hosted RunPod.
2. **Embeddable widget**
   - Lightweight widget for shop websites.
3. **WhatsApp Business integration**
   - Automated sharing/inquiry flow.
4. **Advanced analytics**
   - CRM‑style insights and cohort metrics.

## Architectural Guardrails (always enforced)

* Django monolith only; no microservices.
* Django templates + HTMX only; no SPA frameworks.
* All Replicate calls happen in Celery tasks, never in views.
* Cloudinary for all image persistence.
* PostgreSQL via Django ORM only.
* All protected routes require authentication; shop routes require `account_type == "shop"`.
* HTMX polling every 3 seconds maximum.
* Validate uploads server‑side (MIME + size <= 10 MB).

## Suggested Spec Order (feature by feature)

1. Foundation: project settings, Celery, core utils, base templates.
2. Accounts + credits.
3. Catalog models and shop profile data.
4. Try‑on GenerationJob + upload flow + Celery pipeline.
5. HTMX status polling + result page.
6. Download + regenerate.
7. History page.
8. Catalog CRUD + public shop catalog.
9. Reference image conditioning.
10. Shareable links.
11. Inquiry flow + shop inbox.
12. Analytics dashboard.
13. Paid credits.
14. Scale features.
