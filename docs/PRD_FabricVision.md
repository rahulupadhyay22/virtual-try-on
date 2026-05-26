**PRODUCT REQUIREMENTS DOCUMENT**

**FabricVision - AI Virtual Try-On Platform**

Helping customers visualise unstitched cloth as finished garments on their own body

Version 1.0 | May 2026 | Confidential

# **1\. Product Overview**

## **1.1 Problem Statement**

The unstitched cloth market in India - covering lehengas, salwar suits, kurta fabric, sarees, and related garments - suffers from a fundamental discovery gap. Customers browsing cloth shops, whether in person or online, cannot visualise how a raw fabric will look on them once stitched into a garment. This uncertainty drives purchase hesitation, reduces conversion rates, and creates high return volumes for shops.

Cloth shops rely on static photographs of models to demonstrate fabric, which fails to communicate how the garment will look on a specific customer's body type, skin tone, and proportions. There is no existing tool purpose-built for the unstitched Indian fabric market.

## **1.2 Product Vision**

FabricVision is an AI-powered virtual try-on platform where users upload their photo and a cloth image, and receive a realistic generated image of themselves wearing the garment - with their face, body type, and proportions fully preserved. Users can additionally upload reference design images to guide the AI output. Cloth shops can upload and manage their fabric catalogs through a dedicated business portal.

## **1.3 Goals**

- Enable customers to see themselves wearing any unstitched fabric before purchasing
- Preserve user identity - face and body type must not be altered during generation
- Support reference images so users can specify design patterns, embroidery styles, or colour palettes
- Provide cloth shops a business portal to manage fabric catalogs and share try-on links
- Deliver generated results within 12-20 seconds
- Operate at near-zero cost during MVP phase using free tiers of all services

## **1.4 Non-Goals (MVP)**

- No marketplace - shops upload their own catalogs only
- No mobile app - web only for MVP
- No stitching or tailoring service integration
- No video try-on - static image output only
- No 3D garment simulation

# **2\. User Personas**

## **2.1 End Customer**

| **Attribute** | **Detail**                                                                       |
| ------------- | -------------------------------------------------------------------------------- |
| Name          | Priya, 28, Hyderabad                                                             |
| Behaviour     | Browses fabric shops online and offline, shops for wedding and festive occasions |
| Pain point    | Cannot tell how a fabric will look as a stitched garment on her body             |
| Goal          | See herself wearing the outfit before buying, share the look with family         |
| Tech comfort  | Moderate - uses smartphone apps daily, comfortable with photo uploads            |

## **2.2 Cloth Shop / Business**

| **Attribute** | **Detail**                                                               |
| ------------- | ------------------------------------------------------------------------ |
| Name          | Rajan, boutique owner, Hyderabad                                         |
| Behaviour     | Sells unstitched fabric online and in-store, manages 200-500 fabric SKUs |
| Pain point    | Customers hesitate to buy without seeing how fabric looks on them        |
| Goal          | Increase conversion, share try-on links with WhatsApp customers          |
| Tech comfort  | Basic - can upload images, fill forms; needs simple UI                   |

# **3\. Feature Requirements**

## **3.1 Authentication**

- Email + password registration and login using Django built-in auth
- Separate registration flow for End Customers and Shop accounts
- Session-based authentication - no JWT for MVP
- Password reset via email
- Profile page: name, email, account type, credits remaining

## **3.2 End Customer - Try-On Flow**

### **Image Upload**

- User uploads their own photo - full body or half body both accepted
- System auto-detects body type and adapts generation accordingly
- Accepted formats: JPG, PNG, WEBP - max 10 MB per file
- Client-side preview shown before submission

### **Cloth Image Upload**

- User uploads an image of the unstitched fabric or cloth
- All garment types supported: salwar suits, lehengas, kurtas, sarees, sherwanis, etc.

### **Reference Image (Optional)**

- User can optionally upload a reference image: embroidery pattern, print design, colour reference
- CLIP vision model extracts style features from reference image
- Extracted style conditions the cloth draping generation in Stage 2 of AI pipeline

### **Generation**

- GenerationJob created in DB with status: pending on form submission
- Celery worker runs 3-stage AI pipeline via Replicate API
- HTMX polls job status every 3 seconds and auto-updates result panel
- User sees progress indicator with estimated wait time (12-20 seconds)

### **Output Actions**

- Download - user downloads generated image at full resolution
- Regenerate - re-run generation with same or modified inputs
- Share - copy shareable link valid for 7 days
- Send to Shop - send try-on result and inquiry to the cloth shop

## **3.3 Shop Portal**

- Shop registration with business name, city, contact details
- Fabric catalog management: upload images, name, fabric type, price range, colours
- View all customer try-on requests linked to their catalog items
- Shareable catalog link for WhatsApp sharing
- Dashboard: total try-ons, most tried fabrics, inquiry count

## **3.4 Credits System**

- Each end customer gets 5 free generations on registration
- Each shop account gets 20 free generations on registration
- Credit balance shown in navbar and profile page
- Paid credit packs planned for Phase 2 - not in MVP scope

# **4\. User Stories**

| **ID** | **User Story**                                                 | **Acceptance Criteria**                             | **Priority** |
| ------ | -------------------------------------------------------------- | --------------------------------------------------- | ------------ |
| US-01  | As a customer I want to upload my photo for try-on             | Photo uploads, preview shown, stored in Cloudinary  | P0           |
| US-02  | As a customer I want to upload cloth and see myself wearing it | Generation completes in under 20s, output displayed | P0           |
| US-03  | As a customer I want my face and body preserved in output      | Face identical to input, body proportions unchanged | P0           |
| US-04  | As a customer I want to add a reference design image           | Style from reference reflected in generated output  | P1           |
| US-05  | As a customer I want to download my generated result           | Download saves full-resolution image to device      | P0           |
| US-06  | As a customer I want to see my generation history              | History page shows all past generations             | P1           |
| US-07  | As a shop I want to upload my fabric catalog                   | Catalog items saved, visible on shop public page    | P0           |
| US-08  | As a shop I want to see which fabrics are being tried          | Dashboard shows try-on count per catalog item       | P1           |
| US-09  | As a shop I want to share a catalog link via WhatsApp          | Public catalog URL works without login              | P1           |
| US-10  | As a customer I want to send try-on result to a shop           | Inquiry sent, shop notified, inquiry logged in DB   | P2           |

# **5\. Constraints & Assumptions**

## **5.1 Technical Constraints**

- AI generation is 12-20 seconds - async Celery jobs required, not synchronous HTTP
- Replicate API rate limits - concurrent generation jobs must be queued
- Cloudinary free tier: 25 GB storage, 25 GB bandwidth per month - intermediate AI images must NOT be saved
- Railway: 512 MB RAM shared CPU - Celery worker must run as a separate Railway service

## **5.2 Assumptions**

- Users will upload clear, well-lit photos - low quality input produces low quality output
- Cloth images should be photographed flat or on a mannequin for best results
- Full-body detection is heuristic - may occasionally misclassify

## **5.3 Out of Scope for MVP**

- Payment gateway
- Mobile app
- Multi-language support
- Video try-on
- 3D simulation

# **6\. Success Metrics**

| **Metric**                 | **MVP Target** | **Measurement**                 |
| -------------------------- | -------------- | ------------------------------- |
| Generation success rate    | \> 90%         | Successful jobs / total jobs    |
| Average generation time    | < 20 seconds   | Celery job duration avg         |
| User retention week 2      | \> 30%         | Users with 2+ generations       |
| Shop signups month 1       | 10 shops       | Shop registrations with catalog |
| Face preservation approval | \> 95%         | User thumbs up/down rating      |
| Cloudinary storage at 3mo  | < 20 GB        | Cloudinary dashboard            |

# **7\. Release Roadmap**

## **Phase 1 - MVP (Weeks 1-6)**

- User auth (register, login, profile)
- End customer try-on flow (upload, generate, download)
- 3-stage AI pipeline via Replicate
- Basic generation history
- Shop catalog upload portal
- Credits system (free tier only)

## **Phase 2 - Growth (Weeks 7-12)**

- Reference image style conditioning
- Shop dashboard and analytics
- Shareable result links
- Send-to-shop inquiry flow
- Credit pack payments via Razorpay
- Email notifications

## **Phase 3 - Scale (Months 4-6)**

- Migrate AI from Replicate to self-hosted RunPod
- Embeddable widget for shop websites
- WhatsApp Business API integration
- Mobile responsive improvements
- Advanced analytics and shop CRM