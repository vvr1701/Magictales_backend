# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

# PROJECT OVERVIEW

**Zelavo Kids** - AI-powered personalized children's storybook platform

## Tech Stack
- **Backend:** FastAPI (Python 3.11+)
- **Database:** Supabase (PostgreSQL)
- **Storage:** Cloudflare R2 (S3-compatible)
- **Background Jobs:** FastAPI BackgroundTasks (no external queue for MVP)
- **AI Services:** Fal.ai (Flux.1 [dev], Flux PuLID, Face Swap)
- **PDF Generation:** WeasyPrint
- **Payments:** Shopify webhooks

---

# CORE ARCHITECTURE

## Image Generation Flow (CRITICAL)

**The platform generates ALL 10 high-res images UPFRONT when user creates a preview:**

```
User submits form → Validate face → Generate ALL 10 pages (high-res)
→ Create 5 watermarked previews → User views preview (7 days valid)
→ User pays via Shopify → Generate PDF only (images already exist)
→ Download link provided → Cleanup preview files
```

**Important:** After payment, we ONLY generate PDF - all images already exist from preview generation.

## Two Product Pipelines

### Artistic Style (default: Flux.1 [dev] + Fal Face Swap)
- Step 1: Generate base illustration using Flux.1 [dev] (generic child)
- Step 2: Swap face onto illustration using Fal Face Swap
- Cost: ~₹33 per 10-page book

### Photorealistic Style (default: Flux PuLID)
- Single step: Generate image with face embedded using Flux PuLID
- Cost: ~₹38 per 10-page book

---

# STORAGE STRUCTURE

```
Cloudflare R2:
/uploads/{preview_id}/photo.jpg       → Original child photo
/final/{preview_id}/page_01.jpg       → HIGH-RES images (all 10)
/previews/{preview_id}/page_01.jpg    → LOW-RES watermarked (first 5)
/final/{preview_id}/book.pdf          → PDF (generated after payment)
```

## Retention Rules
- **Active preview (unpaid):** All folders kept for 7 days
- **After payment:** /final/ kept for 30 days, /previews/ deleted immediately
- **Expired (no payment):** All folders deleted

---

# PROJECT STRUCTURE

```
app/
├── ai/
│   ├── base.py                      # Abstract interfaces for AI models
│   ├── model_registry.py            # Model configurations (add new models here)
│   ├── factory.py                   # Model factory (creates instances)
│   ├── implementations/             # Model implementations
│   │   ├── flux.py                  # Flux schnell/dev/pro
│   │   ├── pulid.py                 # Flux PuLID
│   │   └── face_swap.py             # Fal Face Swap
│   └── pipelines/
│       ├── artistic.py              # Base generation + Face Swap
│       └── realistic.py             # Face embedding pipeline
│
├── api/
│   ├── endpoints/
│   │   ├── upload.py                # POST /api/upload-photo
│   │   ├── preview.py               # POST /api/preview, GET /api/preview/{id}
│   │   ├── status.py                # GET /api/preview-status/{job_id}
│   │   └── download.py              # GET /api/download/{order_id}
│   └── webhooks/
│       └── shopify.py               # POST /webhooks/shopify/order-paid
│
├── background/
│   └── tasks.py                     # FastAPI background tasks
│
├── core/
│   ├── security.py                  # HMAC verification, signed URLs
│   └── exceptions.py                # Custom exceptions
│
├── models/
│   ├── database.py                  # Supabase client
│   ├── schemas.py                   # Pydantic models
│   └── enums.py                     # Status enums
│
├── services/
│   ├── face_validation.py           # MediaPipe face detection
│   ├── storage.py                   # Cloudflare R2 operations
│   └── pdf_generator.py             # WeasyPrint PDF creation
│
├── stories/
│   ├── templates.py                 # Story template base classes
│   └── themes/
│       └── magic_castle.py          # Magic school theme (10 pages)
│
├── config.py                        # Settings (loaded from .env)
└── main.py                          # FastAPI app initialization
```

---

# KEY COMMANDS

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Run with docker-compose (includes Redis for future)
docker-compose up
```

## Database

```bash
# The database schema is in BACKEND_IMPLEMENTATION_PLAN.md (Section 5)
# Execute the SQL in Supabase SQL Editor

# Enable pg_cron extension for cleanup jobs:
# 1. Go to Supabase Dashboard → Database → Extensions
# 2. Enable "pg_cron"
# 3. Run the scheduled function setup from IMAGE_GENERATION_FLOW_V2.md
```

## Testing AI Models

```bash
# Test with different models via environment variables:
export ARTISTIC_BASE_MODEL=flux_schnell  # Fast model for testing
export ARTISTIC_BASE_MODEL=flux_dev      # Default
export REALISTIC_MODEL=flux_pulid        # Default
```

---

# MODEL-AGNOSTIC ARCHITECTURE

## Switching AI Models

The system is designed to easily switch between AI models without code changes:

### Via Environment Variables (.env)
```env
# Artistic Pipeline
ARTISTIC_BASE_MODEL=flux_dev          # Options: flux_schnell, flux_dev, flux_pro, recraft_v3
ARTISTIC_FACE_MODEL=fal_face_swap     # Options: fal_face_swap

# Photorealistic Pipeline
REALISTIC_MODEL=flux_pulid            # Options: flux_pulid, instant_id

# Fallbacks
FALLBACK_BASE_MODEL=flux_schnell
FALLBACK_REALISTIC_MODEL=instant_id
```

### Adding a New Model
1. Add configuration to `app/ai/model_registry.py` (MODELS dict)
2. Create implementation in `app/ai/implementations/` (implement abstract interface)
3. Register in `app/ai/factory.py` (IMPLEMENTATIONS dict)
4. Update .env to use the new model

### Model Registry Location
All model configurations (endpoints, costs, latency, params) are in `app/ai/model_registry.py`. This is the single source of truth for model metadata.

---

# DATABASE SCHEMA

## Main Tables

### `previews`
- Stores ALL preview/order data
- `hires_images` (JSONB): All 10 high-res image URLs (stored in /final/)
- `preview_images` (JSONB): 5 watermarked preview URLs (stored in /previews/)
- `story_pages` (JSONB): Story text for all 10 pages
- `status`: pending → generating → active → purchased/expired

### `orders`
- Created when Shopify webhook received
- Links to `previews` via `preview_id`
- `pdf_url`: Generated after payment
- `status`: paid → generating_pdf → completed

### `generation_jobs`
- Tracks background job progress
- `job_type`: preview_generation, pdf_creation
- `status`: queued → processing → completed/failed
- `progress`: 0-100 for status polling

---

# API ENDPOINTS

## Public Endpoints

```
POST   /api/upload-photo              Upload child photo, validate face
POST   /api/preview                   Start preview generation (returns job_id)
GET    /api/preview-status/{job_id}   Poll generation status (0-100%)
GET    /api/preview/{preview_id}      Get preview data (5 watermarked + all text)
GET    /api/download/{order_id}       Get signed download URL for PDF
```

## Webhook Endpoints

```
POST   /webhooks/shopify/order-paid   Handle payment webhook (HMAC verified)
```

## Health Check

```
GET    /health                        Simple health check
```

---

# BACKGROUND TASKS

## Using FastAPI BackgroundTasks (MVP)

For MVP, we use FastAPI's built-in `BackgroundTasks` instead of Celery to avoid external dependencies.

### Main Tasks

**`generate_full_preview()`** - Runs when user submits form
- Generates ALL 10 high-res pages → /final/{preview_id}/
- Creates 5 watermarked low-res → /previews/{preview_id}/
- Updates database with all URLs
- Updates job status for polling

**`generate_pdf()`** - Runs after payment webhook
- Downloads existing high-res images from /final/
- Generates PDF with WeasyPrint
- Uploads to /final/{preview_id}/book.pdf
- Deletes /previews/ folder (no longer needed)

### Scheduled Cleanup

Uses Supabase `pg_cron` extension (no external scheduler needed):
- Runs daily at midnight UTC
- Marks expired previews (>7 days unpaid)
- Cleanup endpoint: `POST /admin/cleanup` (manual trigger)

---

# SECURITY

## Webhook Verification

```python
# Shopify webhooks must:
1. Verify HMAC-SHA256 signature (using raw body)
2. Verify shop domain matches configured domain
3. Check idempotency (order not already processed)
```

## Signed URLs

```python
# Download URLs are time-limited signed URLs from R2:
- Valid for 1 hour (3600 seconds)
- Generated using Cloudflare R2 presigned URL mechanism
```

## Rate Limiting

```
- Uploads: 10 per hour per IP/session
- Previews: 3 per day per IP/session
```

---

# STORY TEMPLATES

## Available Themes

### Magic Castle (Implemented)
- 10-page story about first day at magic school
- Characters: Professor Hoot (owl), Sparky (baby dragon), Midnight (cat)
- Full prompts in `STORY_PROMPTS_AND_TEMPLATES.md`

### Coming Soon
- Space Adventure
- Underwater Kingdom
- Forest Friends

## Prompt Structure

Each page has:
- **Artistic prompt** - For Flux.1 [dev] generation (comic book style)
- **Photorealistic prompt** - For Flux PuLID (cinematic photography)
- **Story text** - Template with {name} placeholder
- **Costume** - Specific outfit for that scene

---

# IMPORTANT IMPLEMENTATION NOTES

## Face Validation (MediaPipe)

Must validate BEFORE queuing generation:
- Exactly 1 face detected
- Face size > 10% of image area
- Face is front-facing
- Image not blurry

## Error Handling

Custom exceptions in `app/core/exceptions.py`:
- `FaceValidationError` - Face detection failed
- `ImageGenerationError` - AI generation failed
- `WebhookVerificationError` - HMAC verification failed
- `RateLimitExceededError` - Rate limit exceeded

## Retry Logic

Automatic retries configured for:
- Image generation: 3 retries with backoff (30s, 60s, 120s)
- Face swap: 2 retries with backoff (15s, 30s)
- Storage upload: 3 retries with backoff (5s, 10s, 20s)

---

# ENVIRONMENT VARIABLES

See `.env.example` for complete list. Critical variables:

```env
# Database
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-service-role-key

# Storage
R2_ACCESS_KEY_ID=your-r2-access-key
R2_SECRET_ACCESS_KEY=your-r2-secret-key
R2_BUCKET_NAME=zelavo-storage
R2_PUBLIC_URL=https://pub-xxxxx.r2.dev

# AI Services
FAL_API_KEY=your-fal-ai-api-key

# Shopify
SHOPIFY_WEBHOOK_SECRET=your-webhook-secret

# Models (easy switching)
ARTISTIC_BASE_MODEL=flux_dev
REALISTIC_MODEL=flux_pulid
```

---

# COST STRUCTURE

| Configuration | Per Image | Per 10-Page Book |
|---------------|-----------|------------------|
| Flux.1 [dev] + Face Swap | ₹3.30 | ₹33 |
| Flux PuLID (realistic) | ₹3.80 | ₹38 |
| Flux Schnell + Face Swap (testing) | ₹1.50 | ₹15 |

---

# WORKFLOW SUMMARY

1. **User uploads photo** → Face validation → Store in /uploads/
2. **User submits preferences** → Create preview record → Queue background job
3. **Background job runs** → Generate 10 high-res → Create 5 watermarked previews
4. **User views preview** → Show 5 watermarked pages + all text → Checkout link
5. **User pays (Shopify)** → Webhook received → Create order → Queue PDF generation
6. **PDF generated** → From existing high-res images → Email download link
7. **User downloads** → Signed URL valid for 1 hour → Can re-download for 30 days

---

# DOCUMENTATION REFERENCES

- **BACKEND_IMPLEMENTATION_PLAN.md** - Complete backend specification
- **IMAGE_GENERATION_FLOW_V2.md** - Detailed generation and storage flow
- **AI_MODEL_CONFIGURATION.md** - Model-agnostic architecture and switching
- **STORY_PROMPTS_AND_TEMPLATES.md** - Complete story prompts for all pages

---

# COMMON TASKS

## Adding a New Story Theme

1. Create `app/stories/themes/your_theme.py`
2. Define 10 PageTemplate objects with prompts
3. Create StoryTemplate with metadata
4. Register in `app/stories/__init__.py`

## Debugging Generation Issues

```python
# Enable detailed logging
export ENABLE_MODEL_LOGGING=true

# Check job status in database
SELECT * FROM generation_jobs WHERE job_id = 'xxx';

# Check preview record
SELECT * FROM previews WHERE preview_id = 'xxx';
```

## Testing Webhooks Locally

Use ngrok or similar to expose local server:
```bash
ngrok http 8000
# Use ngrok URL in Shopify webhook settings
```

---

# DEPLOYMENT

## Render (Recommended for MVP)

See `render.yaml` for configuration. Deploys:
- Web service (FastAPI app)
- No separate worker needed (uses BackgroundTasks)

## Environment Setup

1. Set all environment variables in Render dashboard
2. Database runs on Supabase (managed)
3. Storage runs on Cloudflare R2 (managed)
4. No Redis needed for MVP

---

**Last Updated:** December 2024
**Project Status:** Implementation in progress
