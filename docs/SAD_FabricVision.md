**SYSTEM ARCHITECTURE DOCUMENT**

**FabricVision - AI Virtual Try-On Platform**

Complete system architecture, data flows, deployment topology, and scaling strategy

Version 1.0 | May 2026

# **1\. System Overview**

FabricVision is a monolithic web application built on Django, deployed on Railway as a single project with three process types: a web server (gunicorn), an async worker (Celery), and an in-process broker connection (Redis via Upstash). All business logic, template rendering, and job orchestration live in the same codebase. External AI inference is delegated to Replicate's serverless GPU platform, and all persistent image storage is handled by Cloudinary.

The architecture is deliberately simple for MVP: no microservices, no separate frontend deployment, no container orchestration. The goal is to ship a working product with one engineer, one Git repository, and one Railway dashboard.

## **1.1 Architecture Principles**

- Monolith first - single Django project until there is a proven need to split
- Async by default for AI - all Replicate API calls run in Celery workers, never in request/response cycle
- Managed services over self-hosted - Replicate for GPU, Upstash for Redis, Cloudinary for storage, Railway for hosting
- Zero cold-start infrastructure - Celery workers are always-on processes, not serverless functions
- HTMX over JavaScript frameworks - server-rendered HTML with targeted DOM updates only where needed

# **2\. Component Architecture**

## **2.1 Components and Responsibilities**

| **Component**  | **Technology**                     | **Responsibility**                                                       |
| -------------- | ---------------------------------- | ------------------------------------------------------------------------ |
| Web Server     | Django + Gunicorn                  | HTTP request handling, template rendering, form processing, session auth |
| Task Queue     | Celery 5.x                         | Async execution of AI pipeline tasks, job status updates                 |
| Message Broker | Redis (Upstash)                    | Job queue between Django and Celery, task result storage                 |
| Database       | PostgreSQL (Railway)               | All persistent data: users, jobs, catalogs, sessions                     |
| Image Storage  | Cloudinary                         | User photos, cloth images, AI output images                              |
| AI Inference   | Replicate API                      | IDM-VTON cloth draping, DWPose, IP-Adapter face restoration              |
| Frontend Layer | Django Templates + HTMX + Tailwind | Server-rendered HTML, async job polling, responsive UI                   |
| Static Files   | Whitenoise                         | Serve CSS/JS directly from gunicorn in production                        |
| Email          | Gmail SMTP                         | Password reset, (Phase 2) notifications                                  |

# **3\. Data Flow - Try-On Generation**

## **3.1 Happy Path Flow**

Step 1 - User submits try-on form (POST /tryon/) with user photo, cloth image, optional reference image.

Step 2 - Django view validates the form. If valid: uploads all images to Cloudinary, saves URLs to a new GenerationJob record (status: pending), deducts 1 credit from UserProfile, queues Celery task run_generation_pipeline.delay(job_id), returns HTTP 302 redirect to /tryon/result/&lt;job_id&gt;/.

Step 3 - Browser loads /tryon/result/&lt;job_id&gt;/. Django view renders result page with HTMX polling div pointing to /tryon/status/&lt;job_id&gt;/ with hx-trigger='every 3s'.

Step 4 - Celery worker picks up task from Redis queue. Sets job.status = processing. Calls Replicate API Stage 1: DWPose pose estimation on user photo URL. Receives pose keypoints.

Step 5 - Celery calls Replicate Stage 2: IDM-VTON with user photo URL, cloth image URL, and pose keypoints. If reference image present, CLIP features extracted and passed as style conditioning. Receives temporary try-on image URL.

Step 6 - Celery calls Replicate Stage 3: IP-Adapter Face with Stage 2 output and original user photo as face reference. Receives final image URL (preserved face).

Step 7 - Celery downloads final image from Replicate's temporary URL, uploads to Cloudinary under outputs/&lt;user_id&gt;/, saves output_image_url and output_image_public_id to GenerationJob, sets job.status = completed, records job.duration_seconds.

Step 8 - HTMX polls /tryon/status/&lt;job_id&gt;/. Django view sees status = completed. Returns HTML fragment with output image and action buttons. HTMX replaces the polling div. Polling stops automatically.

## **3.2 Failure Flow**

If any Replicate API call fails or times out (120s limit): Celery catches the exception, sets job.status = failed and job.error_message = exception string. Credit is restored to UserProfile (atomic transaction). HTMX poll detects failed status and renders error message with retry button.

# **4\. Deployment Architecture**

## **4.1 Railway Project Structure**

- Service 1 - web: Django app via Gunicorn. Handles all HTTP traffic. Railway auto-assigns domain and SSL.
- Service 2 - worker: Celery worker. Same Docker image as web, different start command. Always-on, 2 concurrent workers.
- Service 3 - PostgreSQL: Railway managed PostgreSQL. DATABASE_URL auto-injected.
- Service 4 - (optional) Redis: Or use Upstash Redis external service for free tier. REDIS_URL set as env var.

## **4.2 Procfile**

web: gunicorn fabricvision.wsgi:application --bind 0.0.0.0:\$PORT --workers 2 --timeout 60

worker: celery -A fabricvision worker --loglevel=info --concurrency=2 --max-tasks-per-child=10

## **4.3 Environment Variables**

DJANGO_SECRET_KEY=&lt;generated&gt;

DJANGO_SETTINGS_MODULE=fabricvision.settings_prod

DATABASE_URL=&lt;auto-set by Railway&gt;

REDIS_URL=&lt;Upstash TLS URL&gt;

CLOUDINARY_CLOUD_NAME=&lt;from Cloudinary dashboard&gt;

CLOUDINARY_API_KEY=&lt;from Cloudinary dashboard&gt;

CLOUDINARY_API_SECRET=&lt;from Cloudinary dashboard&gt;

REPLICATE_API_TOKEN=&lt;from Replicate dashboard&gt;

EMAIL_HOST_USER=&lt;gmail address&gt;

EMAIL_HOST_PASSWORD=&lt;gmail app password&gt;

ALLOWED_HOSTS=fabricvision.up.railway.app,yourdomain.com

# **5\. Django Apps Dependency Map**

## **5.1 App Dependencies**

| **App**  | **Depends On**            | **Provides**                                       |
| -------- | ------------------------- | -------------------------------------------------- |
| core     | Nothing (leaf)            | cloudinary_utils, replicate_client, base templates |
| accounts | core, django.contrib.auth | UserProfile model, auth views, credit management   |
| catalog  | accounts, core            | Shop model, FabricItem model, shop portal views    |
| tryon    | accounts, catalog, core   | GenerationJob model, try-on views, Celery tasks    |

# **6\. Scaling Strategy**

## **6.1 MVP Scale (0-1000 users)**

- Single Railway web service (2 gunicorn workers)
- Single Celery worker service (2 concurrent tasks)
- Replicate handles all GPU scaling automatically - no GPU management needed
- Cloudinary free tier (25 GB) sufficient for ~8,000-12,000 generations
- PostgreSQL Railway free tier sufficient

## **6.2 Growth Scale (1,000-10,000 users)**

- Scale Celery worker to 4+ concurrent tasks on Railway
- Add PostgreSQL connection pooling (PgBouncer or Railway upgrade)
- Upgrade Cloudinary to paid plan if storage exceeded
- Add Redis caching layer for shop catalog pages (django-cacheops)
- Migrate from Replicate to self-hosted IDM-VTON on RunPod for 80% cost reduction

## **6.3 Future Scale (10,000+ users)**

- Extract Celery workers to dedicated Railway service with horizontal scaling
- Add CDN (Cloudflare) in front of Railway for static assets and HTML caching
- Introduce read replicas for PostgreSQL for heavy analytics queries
- Consider extracting shop portal to separate Django app with dedicated DB

# **7\. Security Architecture**

## **7.1 Authentication & Session Security**

- Django session-based auth - SESSION_COOKIE_SECURE=True, SESSION_COOKIE_HTTPONLY=True in production
- CSRF protection on all POST forms - Django's CsrfViewMiddleware enabled
- Password hashing: Django default PBKDF2 with SHA256

## **7.2 Image Security**

- Cloudinary signed URLs used when passing user photos to Replicate API - prevents direct URL exposure
- User photos stored under private user-scoped folder paths in Cloudinary
- Output images are public Cloudinary URLs - acceptable as they contain no sensitive data

## **7.3 API & Rate Limiting**

- django-ratelimit on /tryon/ POST: 10 requests per hour per user
- django-ratelimit on /accounts/login/ POST: 5 requests per 5 minutes per IP
- File upload validation: MIME type sniffing (not just extension), max 10 MB, image dimension check
- Queryset-level authorization: GenerationJob.objects.filter(user=request.user) - no IDOR possible

## **7.4 Production Hardening**

- DEBUG=False in production
- ALLOWED_HOSTS explicitly set to Railway domain and custom domain only
- All secrets in Railway environment variables - never committed to Git
- SECURE_SSL_REDIRECT=True (Railway provides SSL termination)
- X_FRAME_OPTIONS=DENY
- SECURE_BROWSER_XSS_FILTER=True

# **8\. Monitoring & Observability**

## **8.1 MVP Monitoring**

- Railway built-in logs for web and worker services
- Celery task failure emails via CELERY_SEND_TASK_ERROR_EMAILS = True
- GenerationJob.status field provides complete audit trail of all AI jobs
- GenerationJob.duration_seconds tracks generation performance over time

## **8.2 Phase 2 Additions**

- Sentry (free tier) for Django exception tracking and Celery task errors
- Simple dashboard view for admin: total generations, failure rate, average duration
- Cloudinary usage webhook alerts when approaching 80% of free tier limits

# **9\. AI Model Reference**

| **Model**              | **Replicate ID**         | **Stage**             | **Purpose**                                   |
| ---------------------- | ------------------------ | --------------------- | --------------------------------------------- |
| DWPose                 | yolov8/dwpose            | Stage 1               | Pose estimation and body keypoint detection   |
| SAM (Segment Anything) | meta/sam-2               | Stage 1               | Body segmentation mask generation             |
| IDM-VTON               | cuuupid/idm-vton         | Stage 2               | Primary cloth draping model                   |
| OOTDiffusion           | levihsu/ootdiffusion     | Stage 2 (fallback)    | Alternative cloth draping model               |
| IP-Adapter Face        | zsxkib/ip-adapter-faceid | Stage 3               | Face identity preservation                    |
| CLIP (via Replicate)   | openai/clip-vit-large    | Stage 2 (conditional) | Style feature extraction from reference image |

# **10\. Cost Model - MVP**

| **Service**             | **Free Tier**           | **Cost at 1000 gen/mo** | **Notes**                           |
| ----------------------- | ----------------------- | ----------------------- | ----------------------------------- |
| Railway (web + worker)  | 500 hrs/mo free         | ~\$0-5                  | Upgrade to Hobby \$5/mo when needed |
| Railway PostgreSQL      | Included                | \$0                     | Shared DB on free plan              |
| Upstash Redis           | 10,000 req/day free     | \$0                     | Well within free tier for queue     |
| Cloudinary              | 25 GB storage, 25 GB BW | \$0 for MVP             | ~2-3 MB per generation              |
| Replicate (IDM-VTON)    | Pay per prediction      | ~\$8-15                 | \$0.008-0.015 per full pipeline run |
| Total MVP (1000 gen/mo) |                         | \$8-20/month            | Dominated by Replicate GPU cost     |