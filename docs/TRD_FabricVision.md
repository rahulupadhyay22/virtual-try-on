**TECHNICAL REQUIREMENTS DOCUMENT**

**FabricVision - AI Virtual Try-On Platform**

Full technical specification for Django + Celery + Replicate AI stack

Version 1.0 | May 2026 | Internal Engineering Reference

# **1\. System Architecture Overview**

FabricVision is a monolithic Django application served via Railway, with Celery handling asynchronous AI generation jobs. The frontend is rendered entirely via Django templates with HTMX for dynamic updates. There is no separate frontend service - everything is in one Django project, one Git repository, and one Railway deployment group.

## **1.1 Architecture Diagram - Component Overview**

Browser (Django Templates + HTMX + Tailwind) --> Django App (Views, Forms, Models, URLs) --> Celery Worker (AI pipeline tasks) --> Replicate API (GPU inference) --> Cloudinary (image storage) --> PostgreSQL (data persistence) --> Redis/Upstash (job queue broker)

## **1.2 Key Architectural Decisions**

- Monolith over microservices - single Django project reduces operational overhead for MVP
- Celery over Django-Q or RQ - mature ecosystem, best Replicate integration examples available
- HTMX over React - no build step, no separate deployment, polling via hx-trigger every 3s
- Django templates over Next.js - one repo, one deploy, sessions work natively, zero CORS issues
- Replicate over self-hosted GPU - no infrastructure to manage, pay per prediction, scales automatically
- Cloudinary over S3 - 25 GB free tier, Django SDK (cloudinary-storage), signed URLs built-in

# **2\. Django Project Structure**

## **2.1 Folder Layout**

fabricvision/ # Django project root

fabricvision/ # Project config package

settings.py # Base settings

settings_prod.py # Production overrides

urls.py # Root URL config

celery.py # Celery app instance

apps/

accounts/ # User auth, profiles, credits

models.py # UserProfile, CreditBalance

views.py # Register, login, profile

forms.py # RegistrationForm, LoginForm

urls.py

templates/accounts/

tryon/ # Core try-on feature

models.py # GenerationJob

views.py # Upload, status, history

forms.py # TryOnForm

tasks.py # Celery tasks (AI pipeline)

urls.py

templates/tryon/

catalog/ # Shop fabric catalog

models.py # Shop, FabricItem

views.py # Catalog CRUD, public view

forms.py # FabricItemForm

urls.py

templates/catalog/

core/ # Shared utils, base templates

cloudinary_utils.py # Upload/delete helpers

replicate_client.py # Replicate API wrapper

templates/ # Global base templates

base.html

navbar.html

static/ # CSS, JS

manage.py

requirements.txt

Procfile # Railway process definitions

# **3\. Database Models**

## **3.1 accounts - UserProfile**

| **Field**         | **Type**      | **Constraints**         | **Description**            |
| ----------------- | ------------- | ----------------------- | -------------------------- |
| id                | AutoField PK  | PK                      | Auto increment primary key |
| user              | OneToOneField | User FK, CASCADE        | Django auth User           |
| account_type      | CharField(10) | choices: customer, shop | Differentiates user modes  |
| credits_remaining | IntegerField  | default=5               | Free generations left      |
| phone             | CharField(15) | null, blank             | Optional contact number    |
| created_at        | DateTimeField | auto_now_add            | Registration timestamp     |

## **3.2 catalog - Shop**

| **Field**     | **Type**       | **Constraints**  | **Description**          |
| ------------- | -------------- | ---------------- | ------------------------ |
| id            | AutoField PK   | PK               | Primary key              |
| owner         | OneToOneField  | User FK, CASCADE | Shop owner Django user   |
| business_name | CharField(120) | unique           | Display name of shop     |
| slug          | SlugField(140) | unique           | URL-safe shop identifier |
| city          | CharField(80)  |                  | City of operation        |
| contact_phone | CharField(15)  | null, blank      | WhatsApp contact         |
| gst_number    | CharField(20)  | null, blank      | Optional GST number      |
| created_at    | DateTimeField  | auto_now_add     | Shop registration date   |

## **3.3 catalog - FabricItem**

| **Field**             | **Type**           | **Constraints**  | **Description**                   |
| --------------------- | ------------------ | ---------------- | --------------------------------- |
| id                    | AutoField PK       | PK               | Primary key                       |
| shop                  | ForeignKey         | Shop FK, CASCADE | Owning shop                       |
| name                  | CharField(200)     |                  | Fabric display name               |
| fabric_type           | CharField(80)      |                  | Salwar suit, lehenga, etc.        |
| cloth_image_url       | URLField           |                  | Cloudinary URL of fabric image    |
| cloth_image_public_id | CharField(200)     |                  | Cloudinary public ID for deletion |
| price_min             | DecimalField(10,2) | null, blank      | Minimum price (INR)               |
| price_max             | DecimalField(10,2) | null, blank      | Maximum price (INR)               |
| available_colours     | CharField(300)     | null, blank      | Comma-separated colour names      |
| is_active             | BooleanField       | default=True     | Show/hide from catalog            |
| tryon_count           | IntegerField       | default=0        | Total try-ons on this item        |
| created_at            | DateTimeField      | auto_now_add     | Created timestamp                 |

## **3.4 tryon - GenerationJob**

| **Field**                 | **Type**       | **Constraints**     | **Description**                         |
| ------------------------- | -------------- | ------------------- | --------------------------------------- |
| id                        | UUIDField      | PK, default=uuid4   | UUID primary key (safe for public URLs) |
| user                      | ForeignKey     | User FK, CASCADE    | Requesting user                         |
| fabric_item               | ForeignKey     | FabricItem FK, null | If from shop catalog (optional)         |
| user_photo_url            | URLField       |                     | Cloudinary URL of user photo            |
| user_photo_public_id      | CharField(200) |                     | Cloudinary public ID                    |
| cloth_image_url           | URLField       |                     | Cloudinary URL of cloth image           |
| cloth_image_public_id     | CharField(200) |                     | Cloudinary public ID                    |
| reference_image_url       | URLField       | null, blank         | Optional reference design image         |
| reference_image_public_id | CharField(200) | null, blank         | Cloudinary public ID                    |
| output_image_url          | URLField       | null, blank         | Cloudinary URL of generated result      |
| output_image_public_id    | CharField(200) | null, blank         | Cloudinary public ID                    |
| status                    | CharField(20)  | choices below       | pending/processing/completed/failed     |
| body_type_detected        | CharField(20)  | full/half           | Detected from user photo                |
| garment_type              | CharField(80)  | null, blank         | User-specified garment type             |
| error_message             | TextField      | null, blank         | Error details on failure                |
| replicate_job_id          | CharField(200) | null, blank         | Replicate prediction ID                 |
| duration_seconds          | FloatField     | null, blank         | Total generation time                   |
| share_token               | CharField(64)  | unique, null        | Token for shareable link                |
| share_expires_at          | DateTimeField  | null, blank         | Link expiry (7 days)                    |
| created_at                | DateTimeField  | auto_now_add        | Job created timestamp                   |
| updated_at                | DateTimeField  | auto_now            | Last status update                      |

# **4\. AI Pipeline - Technical Specification**

## **4.1 Overview**

The AI pipeline runs inside a Celery task (tryon.tasks.run_generation_pipeline). It is a 3-stage sequential pipeline. Intermediate outputs are NOT stored to Cloudinary - only the final output image is saved. All Replicate API calls are synchronous within the task (Replicate's Python SDK handles polling internally).

## **4.2 Stage 1 - Body Type Detection + Pose Estimation**

- Model: DWPose via Replicate (or MediaPipe as fallback, runs in-process)
- Input: user_photo_url from Cloudinary
- Output: pose keypoints JSON + segmentation mask
- Body type heuristic: if detected height / width ratio > 1.8 AND full-body keypoints present (ankles visible) -> full_body, else half_body
- Result stored in job.body_type_detected field

## **4.3 Stage 2 - Cloth Draping (Virtual Try-On)**

- Model: IDM-VTON on Replicate (primary) / OOTDiffusion (fallback)
- Inputs: user_photo_url, cloth_image_url, pose keypoints from Stage 1
- If reference_image_url is present: CLIP features extracted and passed as style_conditioning to the model
- Output: generated try-on image URL (temporary Replicate URL, valid for 1 hour)
- This stage is the most time-consuming: ~8-14 seconds

## **4.4 Stage 3 - Face & Body Preservation**

- Model: IP-Adapter Face via Replicate
- Input: Stage 2 output image + original user_photo_url (face reference)
- Purpose: correct any face distortion introduced by the diffusion model in Stage 2
- Output: final image with original face identity restored
- Final image downloaded from Replicate URL and uploaded to Cloudinary
- job.output_image_url and job.output_image_public_id saved to DB
- job.status set to completed, job.duration_seconds calculated and saved

## **4.5 Error Handling**

- If any stage fails: job.status = failed, job.error_message = exception string
- User credit is NOT deducted on failure
- HTMX polling detects failed status and shows error message with retry button
- Replicate timeouts set to 120 seconds per stage

# **5\. Celery Configuration**

## **5.1 Setup**

\# fabricvision/celery.py

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fabricvision.settings')

app = Celery('fabricvision')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

## **5.2 Settings**

CELERY_BROKER_URL = env('REDIS_URL') # Upstash Redis TLS URL

CELERY_RESULT_BACKEND = env('REDIS_URL')

CELERY_TASK_SERIALIZER = 'json'

CELERY_RESULT_EXPIRES = 3600 # 1 hour

CELERY_WORKER_CONCURRENCY = 2 # 2 parallel AI jobs

CELERY_TASK_TIME_LIMIT = 180 # 3 minute hard timeout

## **5.3 Procfile (Railway)**

web: gunicorn fabricvision.wsgi:application --bind 0.0.0.0:\$PORT

worker: celery -A fabricvision worker --loglevel=info --concurrency=2

# **6\. HTMX Polling - Frontend Pattern**

## **6.1 How It Works**

After the user submits the try-on form, Django creates a GenerationJob and returns a redirect to the result page. The result page has an HTMX polling div that calls the job status endpoint every 3 seconds. When the job status becomes completed or failed, the endpoint returns a final HTML fragment that replaces the polling div, stopping further polling automatically.

## **6.2 Template Pattern**

&lt;!-- tryon/result.html --&gt;

<div id="result-panel"

hx-get="/tryon/status/{{ job.id }}/"

hx-trigger="every 3s"

hx-target="#result-panel"

hx-swap="outerHTML">

&lt;p&gt;Generating your try-on... please wait&lt;/p&gt;

&lt;/div&gt;

## **6.3 Status View Response**

The /tryon/status/&lt;uuid&gt;/ view returns an HTML fragment (not JSON). If status is pending or processing, it returns the polling div again. If completed, it returns the result image HTML. If failed, it returns an error message with retry button. This means HTMX stops polling automatically when a final state is returned.

# **7\. Cloudinary Integration**

## **7.1 Django Settings**

CLOUDINARY_STORAGE = {

'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME'),

'API_KEY': env('CLOUDINARY_API_KEY'),

'API_SECRET': env('CLOUDINARY_API_SECRET'),

}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

## **7.2 Folder Structure in Cloudinary**

fabricvision/

user_photos/&lt;user_id&gt;/ # User uploaded photos

cloth_images/&lt;user_id&gt;/ # Cloth images uploaded by users

cloth_images/shop/&lt;shop_id&gt;/ # Shop catalog fabric images

reference_images/&lt;user_id&gt;/ # Optional reference images

outputs/&lt;user_id&gt;/ # Final generated try-on images

## **7.3 Storage Policy**

- Intermediate AI images (pose maps, Stage 2 raw output) are NEVER saved to Cloudinary
- Only the final Stage 3 output is uploaded to Cloudinary
- User photos are stored under private folders - Cloudinary signed URLs used for AI model access
- Outputs are public URLs for easy download and sharing

# **8\. Third-Party Services & Environment Variables**

| **Variable**          | **Service**        | **Description**                     |
| --------------------- | ------------------ | ----------------------------------- |
| DJANGO_SECRET_KEY     | Django             | Secret key for signing sessions     |
| DATABASE_URL          | Railway PostgreSQL | Auto-set by Railway                 |
| REDIS_URL             | Upstash Redis      | TLS URL for Celery broker           |
| CLOUDINARY_CLOUD_NAME | Cloudinary         | Cloud name from dashboard           |
| CLOUDINARY_API_KEY    | Cloudinary         | API key from dashboard              |
| CLOUDINARY_API_SECRET | Cloudinary         | API secret from dashboard           |
| REPLICATE_API_TOKEN   | Replicate          | API token for AI inference          |
| EMAIL_HOST_USER       | Gmail SMTP         | For password reset emails           |
| EMAIL_HOST_PASSWORD   | Gmail SMTP         | App password (not account password) |
| ALLOWED_HOSTS         | Django             | Railway domain + custom domain      |

# **9\. Security Requirements**

- All uploads validated server-side: file type (mime sniffing), max size 10 MB, image dimensions check
- User can only access their own GenerationJobs - queryset filtered by request.user
- Shop owners can only manage their own FabricItems - queryset filtered by shop.owner
- CSRF protection enabled on all forms (Django default)
- Cloudinary signed URLs used for user photo access by Replicate - never expose raw S3 URLs
- Django DEBUG=False in production, ALLOWED_HOSTS explicitly set
- All secrets stored as Railway environment variables - never in code
- Rate limiting on generation endpoint: max 10 requests per hour per user (via django-ratelimit)

# **10\. Performance Requirements**

| **Component**               | **Target**   | **Notes**                           |
| --------------------------- | ------------ | ----------------------------------- |
| Total generation time (P50) | < 15 seconds | 3-stage pipeline                    |
| Total generation time (P95) | < 25 seconds | Under high Replicate load           |
| Page load time              | < 2 seconds  | Django templates, whitenoise static |
| Celery job queue lag        | < 3 seconds  | Time from submit to worker pickup   |
| Cloudinary upload time      | < 2 seconds  | Final output image ~2-3 MB          |
| HTMX poll interval          | 3 seconds    | Balances responsiveness and load    |

# **11\. Dependencies - requirements.txt**

django>=4.2,<5.0

djangorestframework>=3.14

celery>=5.3

redis>=5.0

cloudinary>=1.36

django-cloudinary-storage>=0.3

replicate>=0.25

Pillow>=10.0

gunicorn>=21.0

django-environ>=0.11

django-ratelimit>=4.0

whitenoise>=6.6

psycopg2-binary>=2.9