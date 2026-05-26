**API CONTRACTS DOCUMENT**

**FabricVision - AI Virtual Try-On Platform**

All Django URL endpoints with request/response contracts

Version 1.0 | May 2026 | Base URL: <https://fabricvision.up.railway.app>

# **1\. Conventions**

## **1.1 Base URL & Versioning**

All endpoints are served from the Django application root. No API versioning prefix for MVP - all routes are at the root level. HTML views return rendered templates. HTMX status endpoints return HTML fragments.

## **1.2 Authentication**

- Session-based - Django login sets a session cookie
- All protected views use @login_required decorator
- Shop-only views additionally check request.user.userprofile.account_type == 'shop'
- Public endpoints (catalog view, shared result) require no auth

## **1.3 Response Format**

- HTML views: return rendered Django template (Content-Type: text/html)
- HTMX fragments: return partial HTML (hx-trigger or hx-swap targets)
- Error responses: Django messages framework + redirect, or 400/403/404 HTTP status

## **1.4 File Uploads**

- multipart/form-data encoding for all image uploads
- Max file size: 10 MB enforced in Django form validation
- Accepted MIME types: image/jpeg, image/png, image/webp

# **2\. Authentication Endpoints**

**\[GET\]** **/accounts/register/**

_Show registration page with account type selection (customer or shop)_

**Auth:** None

**Responses:** 200 OK - registration form HTML

**\[POST\]** **/accounts/register/**

_Submit registration form - creates User + UserProfile_

**Auth:** None

**Params/Body:** username, email, password1, password2, account_type (customer|shop)

**Responses:** 302 redirect to /tryon/ on success | 200 with form errors on failure

**\[GET\]** **/accounts/login/**

_Show login page_

**Auth:** None

**Responses:** 200 OK - login form HTML

**\[POST\]** **/accounts/login/**

_Submit login credentials - creates Django session_

**Auth:** None

**Params/Body:** username, password, next (optional redirect)

**Responses:** 302 redirect to next or /tryon/ on success | 200 with error on failure

**\[POST\]** **/accounts/logout/**

_Logout user - destroys session_

**Auth:** Login required

**Responses:** 302 redirect to /accounts/login/

**\[GET\]** **/accounts/profile/**

_Show user profile page with credits, history link, account type_

**Auth:** Login required

**Responses:** 200 OK - profile template with user data

**\[GET\]** **/accounts/password-reset/**

_Show password reset form_

**Auth:** None

**Responses:** 200 OK - email input form

**\[POST\]** **/accounts/password-reset/**

_Send password reset email via Django built-in flow_

**Auth:** None

**Params/Body:** email

**Responses:** 302 redirect to /accounts/password-reset/done/

# **3\. Try-On Endpoints**

**\[GET\]** **/tryon/**

_Show the main try-on upload form (home page for logged in users)_

**Auth:** Login required

**Responses:** 200 OK - upload form with credit balance shown

**\[POST\]** **/tryon/**

_Submit try-on request - validates inputs, uploads to Cloudinary, creates GenerationJob, queues Celery task_

**Auth:** Login required

**Params/Body:** user_photo (file), cloth_image (file), reference_image (file, optional), garment_type (str, optional)

**Responses:** 302 redirect to /tryon/result/&lt;job_id&gt;/ on success | 200 with form errors | 402 if no credits

**\[GET\]** **/tryon/result/&lt;uuid:job_id&gt;/**

_Show try-on result page - contains HTMX polling div_

**Auth:** Login required, must own job

**Responses:** 200 OK - result page with HTMX poller | 404 if job not found | 403 if not owner

**\[GET\]** **/tryon/status/&lt;uuid:job_id&gt;/**

_HTMX polling endpoint - returns HTML fragment with current job state. Called every 3 seconds by HTMX. Returns final HTML when job is completed or failed (HTMX stops polling automatically)_

**Auth:** Login required, must own job

**Responses:** 200 OK - HTML fragment: spinner if pending/processing | result image if completed | error + retry if failed

**\[GET\]** **/tryon/history/**

_Show paginated generation history for logged in user_

**Auth:** Login required

**Params/Body:** page (query param, default 1)

**Responses:** 200 OK - history page with job list, thumbnails, status badges

**\[POST\]** **/tryon/regenerate/&lt;uuid:job_id&gt;/**

_Re-queue generation for existing job with same inputs. Deducts 1 credit. Creates a new GenerationJob copying inputs from original._

**Auth:** Login required, must own job

**Responses:** 302 redirect to new job result page | 402 if no credits

**\[GET\]** **/tryon/download/&lt;uuid:job_id&gt;/**

_Redirect to Cloudinary output image URL for download. Adds Content-Disposition header._

**Auth:** Login required, must own job

**Responses:** 302 redirect to Cloudinary signed download URL | 404 if job not completed

**\[POST\]** **/tryon/share/&lt;uuid:job_id&gt;/**

_Generate shareable link - sets share_token and share_expires_at on job (7 days)_

**Auth:** Login required, must own job

**Responses:** 200 OK - JSON {share_url: string} | 404 if job not completed

**\[GET\]** **/tryon/shared/&lt;str:share_token&gt;/**

_Public shareable result page - no auth required. Shows output image with cloth and user photo thumbnails._

**Auth:** None (public)

**Responses:** 200 OK - public result page | 404 if token invalid or expired

# **4\. Catalog Endpoints (Shop Portal)**

**\[GET\]** **/catalog/**

_Shop dashboard - shows shop's fabric catalog list with try-on counts_

**Auth:** Login required, shop account only

**Responses:** 200 OK - catalog management page | 403 if customer account

**\[GET\]** **/catalog/add/**

_Show add fabric item form_

**Auth:** Login required, shop account only

**Responses:** 200 OK - FabricItemForm HTML

**\[POST\]** **/catalog/add/**

_Submit new fabric item - uploads cloth image to Cloudinary, creates FabricItem_

**Auth:** Login required, shop account only

**Params/Body:** name (str), fabric_type (str), cloth_image (file), price_min (decimal, optional), price_max (decimal, optional), available_colours (str, optional)

**Responses:** 302 redirect to /catalog/ on success | 200 with form errors on failure

**\[GET\]** **/catalog/edit/&lt;int:item_id&gt;/**

_Show edit form for existing fabric item_

**Auth:** Login required, must own item

**Responses:** 200 OK - pre-filled FabricItemForm | 403 if not owner | 404 if not found

**\[POST\]** **/catalog/edit/&lt;int:item_id&gt;/**

_Update fabric item details. If new cloth image uploaded, old Cloudinary image is deleted._

**Auth:** Login required, must own item

**Params/Body:** name, fabric_type, cloth_image (optional), price_min, price_max, available_colours, is_active

**Responses:** 302 redirect to /catalog/ on success | 200 with form errors

**\[POST\]** **/catalog/delete/&lt;int:item_id&gt;/**

_Delete fabric item and its Cloudinary image_

**Auth:** Login required, must own item

**Responses:** 302 redirect to /catalog/ with success message

**\[GET\]** **/catalog/toggle/&lt;int:item_id&gt;/**

_Toggle is_active status of a fabric item (HTMX-friendly)_

**Auth:** Login required, must own item

**Responses:** 200 OK - updated item row HTML fragment for HTMX swap

**\[GET\]** **/shop/&lt;slug:shop_slug&gt;/**

_Public catalog page for a shop - shows all active fabric items. No auth required. Customers can click an item to go to try-on pre-filled with that cloth._

**Auth:** None (public)

**Responses:** 200 OK - public catalog page | 404 if shop not found

**\[GET\]** **/catalog/analytics/**

_Shop analytics dashboard - try-on counts, most popular fabrics, total inquiries_

**Auth:** Login required, shop account only

**Responses:** 200 OK - analytics page with chart data

# **5\. Inquiry Endpoints**

**\[POST\]** **/inquiry/send/&lt;uuid:job_id&gt;/**

_Customer sends their try-on result as an inquiry to the cloth shop. Creates an Inquiry record. Sends email notification to shop (Phase 2)._

**Auth:** Login required

**Params/Body:** message (str, optional)

**Responses:** 302 redirect back with success message | 404 if job not found or not linked to a FabricItem

**\[GET\]** **/inquiry/**

_Shop inbox - list of all inquiries received with try-on result images_

**Auth:** Login required, shop account only

**Responses:** 200 OK - inquiry list page

# **6\. Internal / Utility Endpoints**

**\[GET\]** **/**

_Root URL - redirects to /tryon/ if logged in, else to /accounts/login/_

**Auth:** None

**Responses:** 302 redirect

**\[GET\]** **/health/**

_Health check endpoint for Railway uptime monitoring_

**Auth:** None

**Responses:** 200 OK - plain text 'ok'

# **7\. Complete URL Map Summary**

| **Method** | **URL**                         | **Auth**       | **Description**              |
| ---------- | ------------------------------- | -------------- | ---------------------------- |
| GET/POST   | /accounts/register/             | Public         | User registration            |
| GET/POST   | /accounts/login/                | Public         | User login                   |
| POST       | /accounts/logout/               | Login required | Logout                       |
| GET        | /accounts/profile/              | Login required | Profile page                 |
| GET/POST   | /accounts/password-reset/       | Public         | Password reset               |
| GET/POST   | /tryon/                         | Login required | Try-on upload form           |
| GET        | /tryon/result/&lt;uuid&gt;/     | Login required | Result page with HTMX poller |
| GET        | /tryon/status/&lt;uuid&gt;/     | Login required | HTMX status fragment         |
| GET        | /tryon/history/                 | Login required | Generation history           |
| POST       | /tryon/regenerate/&lt;uuid&gt;/ | Login required | Re-run generation            |
| GET        | /tryon/download/&lt;uuid&gt;/   | Login required | Download output image        |
| POST       | /tryon/share/&lt;uuid&gt;/      | Login required | Generate share link          |
| GET        | /tryon/shared/&lt;token&gt;/    | Public         | Shared result page           |
| GET        | /catalog/                       | Shop only      | Shop catalog management      |
| GET/POST   | /catalog/add/                   | Shop only      | Add fabric item              |
| GET/POST   | /catalog/edit/&lt;id&gt;/       | Shop only      | Edit fabric item             |
| POST       | /catalog/delete/&lt;id&gt;/     | Shop only      | Delete fabric item           |
| GET        | /catalog/toggle/&lt;id&gt;/     | Shop only      | Toggle item active (HTMX)    |
| GET        | /shop/&lt;slug&gt;/             | Public         | Public shop catalog page     |
| GET        | /catalog/analytics/             | Shop only      | Shop analytics dashboard     |
| POST       | /inquiry/send/&lt;uuid&gt;/     | Login required | Send try-on inquiry to shop  |
| GET        | /inquiry/                       | Shop only      | Shop inquiry inbox           |
| GET        | /health/                        | Public         | Health check                 |