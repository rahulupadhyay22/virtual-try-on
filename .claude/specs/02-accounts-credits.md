# Spec: Accounts + Credits

## Overview
Implement the FabricVision accounts system with registration, login, logout, profile, and password reset flows, plus the MVP credits model that grants free generations to customers and shops. This enables end customers and shop owners to access their correct portal experiences while ensuring credit balances are visible and consistent with PRD requirements. The feature supports the MVP roadmap by establishing authenticated access and credit awareness before try-on generation is delivered.

## Depends on
* 01-project-foundation.md

## User Stories
* As a customer, I want to register and log in so that I can access the try-on flow.
* As a shop owner, I want to register with a shop account type so that I can use shop-only features later.
* As a user, I want to see my remaining credits so that I know how many try-ons I can run.
* As a user, I want to reset my password so that I can regain access if I forget it.
* As a user, I want to log out securely so that my account stays protected.

## Routes
* `GET /accounts/register/` -- show registration form with account type selection -- public
* `POST /accounts/register/` -- create User + UserProfile, set initial credits by account type, log in user -- public; on success redirect to `/tryon/`, on failure re-render with form errors
* `GET /accounts/login/` -- show login form -- public
* `POST /accounts/login/` -- authenticate and create session -- public; redirects to `next` param or `/tryon/`
* `POST /accounts/logout/` -- end user session -- login required; redirect to `/accounts/login/`
* `GET /accounts/profile/` -- show profile with account type and credits -- login required
* `GET /accounts/password-reset/` -- show password reset email form -- public
* `POST /accounts/password-reset/` -- trigger password reset email -- public; redirect to `/accounts/password-reset/done/`
* `GET /accounts/password-reset/done/` -- password reset email sent confirmation -- public
* `GET /accounts/reset/<uidb64>/<token>/` -- show new password form -- public
* `POST /accounts/reset/<uidb64>/<token>/` -- set new password -- public; redirect to `/accounts/reset/done/`
* `GET /accounts/reset/done/` -- password reset complete -- public

## Database Changes
* **accounts.UserProfile**
  * `user` -- OneToOneField(User, on_delete=CASCADE), unique
  * `account_type` -- CharField(max_length=10, choices=[customer, shop])
  * `credits_remaining` -- IntegerField(default=5)
  * `phone` -- CharField(max_length=15, null=True, blank=True)
  * `created_at` -- DateTimeField(auto_now_add=True)
* Migration required to create the UserProfile table.
* Initial credits:
  * customer: 5
  * shop: 20 (override default on registration for shop accounts)

## Celery / Async Tasks
No async task changes.

## External Services
* **Gmail SMTP** -- used by Django password reset flow to send reset emails; handle SMTP errors by showing Django form errors and not leaking whether an email exists.

## Templates

### Create
* `templates/accounts/register.html`
* `templates/accounts/login.html`
* `templates/accounts/profile.html`
* `templates/accounts/password_reset.html`
* `templates/accounts/password_reset_done.html`
* `templates/accounts/password_reset_confirm.html`
* `templates/accounts/password_reset_complete.html`

### Modify
* `templates/navbar.html` -- show current user credits and account type when authenticated.

## Files to Change

### accounts
* `apps/accounts/apps.py`
* `apps/accounts/models.py`
* `apps/accounts/forms.py`
* `apps/accounts/views.py`
* `apps/accounts/urls.py`

### tryon
No changes.

### catalog
No changes.

### core
No changes.

### project config
* `fabricvision/settings.py` -- add `apps.accounts` to INSTALLED_APPS
* `fabricvision/urls.py` -- include accounts routes

## Files to Create
* `apps/accounts/__init__.py`
* `apps/accounts/apps.py`
* `apps/accounts/models.py`
* `apps/accounts/forms.py`
* `apps/accounts/views.py`
* `apps/accounts/urls.py`
* `templates/accounts/register.html`
* `templates/accounts/login.html`
* `templates/accounts/profile.html`
* `templates/accounts/password_reset.html`
* `templates/accounts/password_reset_done.html`
* `templates/accounts/password_reset_confirm.html`
* `templates/accounts/password_reset_complete.html`

## Validation Rules
* Registration requires username, email, password1, password2, and account_type.
* Passwords must match and satisfy Django password validators.
* account_type must be one of `customer` or `shop`.
* credits_remaining must never be negative.
* Profile and logout routes require authentication.
* Password reset should not reveal whether an email exists.

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
* `GET /accounts/register/` -- no params -- 200 OK registration form -- public
* `POST /accounts/register/` -- username, email, password1, password2, account_type -- 302 to `/tryon/` on success, 200 with form errors on failure -- public
* `GET /accounts/login/` -- no params -- 200 OK login form -- public
* `POST /accounts/login/` -- username, password, next (optional) -- 302 to `next` or `/tryon/` on success, 200 with error on failure -- public
* `POST /accounts/logout/` -- no params -- 302 to `/accounts/login/` -- login required
* `GET /accounts/profile/` -- no params -- 200 OK profile page with credits -- login required
* `GET /accounts/password-reset/` -- no params -- 200 OK password reset form -- public
* `POST /accounts/password-reset/` -- email -- 302 to `/accounts/password-reset/done/` -- public

## Acceptance Criteria
* [x] Customer can register and is assigned 5 credits on creation.
* [x] Shop account can register and is assigned 20 credits on creation.
* [x] Login establishes a session and redirects to `/tryon/` by default.
* [x] Logout invalidates the session and redirects to `/accounts/login/`.
* [x] Profile page shows account type and credits remaining.
* [x] Password reset email flow works without leaking account existence.
* [x] Navbar shows credits for authenticated users.

## Edge Cases
* Duplicate username or email returns a form error.
* Invalid account_type is rejected.
* Password reset for unknown email behaves the same as known email.
* Logout requested via GET should return 405 or redirect via POST-only route.
* Credits must never drop below zero when later decremented by try-on flows.

## Manual Testing Plan
1. Register a customer account and verify redirect to `/tryon/` and credits = 5 in navbar and profile.
2. Register a shop account and verify credits = 20.
3. Log out and confirm redirect to `/accounts/login/`.
4. Log in with `next` parameter and confirm redirect to `next`.
5. Use password reset with a valid email and confirm the reset email workflow completes.
6. Use password reset with an unknown email and confirm identical response.

## Future Considerations
* Credit purchase packs (Phase 2) with Razorpay integration.
* Credit transaction ledger for audit and refunds.
* Admin credit adjustments and reporting.
