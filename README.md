# MagicTales Backend

> AI-powered personalized children's storybook platform - Backend API

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com)
[![Deployed on Render](https://img.shields.io/badge/Deployed%20on-Render-purple.svg)](https://render.com)

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Story Themes](#story-themes)
- [AI Pipeline](#ai-pipeline)
- [Background Tasks](#background-tasks)
- [Shopify Integration](#shopify-integration)
- [Database Schema](#database-schema)
- [Deployment](#deployment)
- [Development Guide](#development-guide)
- [Troubleshooting](#troubleshooting)

---

## Overview

MagicTales Backend is the core API service for generating personalized AI-powered children's storybooks. It handles:

- **Photo Upload & Validation**: Face detection using MediaPipe
- **AI Image Generation**: Creates personalized story illustrations using Fal.ai
- **Story Generation**: 10-page personalized stories with the child as the hero
- **PDF Generation**: High-quality printable storybooks using ReportLab
- **Shopify Integration**: Payment processing and order management
- **Background Processing**: Async image generation with progress tracking

### Key Features

| Feature | Description |
|---------|-------------|
| Face-in-Image AI | Child's face seamlessly integrated into story illustrations |
| 8 Story Themes | Enchanted Forest, Magic Castle, Ocean Explorer, etc. |
| 2 Art Styles | Photorealistic and 3D Cartoon |
| Real-time Progress | Polling-based generation status updates |
| Watermarked Previews | First 5 pages free, unlock remaining with purchase |
| PDF Export | Print-ready 10x10 inch square format |

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │   React     │  │  Shopify    │  │  Shopify    │                 │
│  │   Frontend  │  │  Storefront │  │  Admin      │                 │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                 │
└─────────┼────────────────┼────────────────┼─────────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         API LAYER (FastAPI)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │  /api/*     │  │ /webhooks/* │  │  /proxy/*   │  │  /health   │ │
│  │  REST API   │  │  Shopify    │  │  App Proxy  │  │  Health    │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └────────────┘ │
└─────────┼────────────────┼────────────────┼─────────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       SERVICE LAYER                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │    Face     │  │     AI      │  │    PDF      │  │  Storage   │ │
│  │  Validation │  │  Pipeline   │  │  Generator  │  │  (R2)      │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
          │                │                │                │
          ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SERVICES                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │  Supabase   │  │   Fal.ai    │  │ Cloudflare  │  │  Resend    │ │
│  │  Database   │  │   AI API    │  │     R2      │  │   Email    │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Request Flow - Story Generation

```
1. USER UPLOADS PHOTO
   POST /api/upload-photo
   └── Validate file type/size
   └── Face detection (MediaPipe)
   └── Store in R2
   └── Return photo_url

2. USER CREATES PREVIEW
   POST /api/preview
   └── Validate request
   └── Create preview record (DB)
   └── Create job record (DB)
   └── Start background task
   └── Return job_id + preview_id

3. BACKGROUND TASK GENERATES IMAGES
   generate_full_preview()
   └── Update job: status="processing"
   └── Generate cover image (Fal.ai)
   └── For each page 1-10:
       └── Build prompt from theme
       └── Call Fal.ai Flux PuLID
       └── Apply watermark (pages 1-5)
       └── Upload to R2
       └── Update progress (X/10)
   └── Update preview with URLs
   └── Update job: status="completed"

4. USER POLLS STATUS
   GET /api/preview-status/{job_id}
   └── Return progress %, current step, completed pages

5. USER VIEWS PREVIEW
   GET /api/preview/{preview_id}
   └── Return watermarked pages 1-5
   └── Return locked pages 6-10 (teaser only)

6. USER PURCHASES (Shopify)
   Checkout → Payment → Webhook
   POST /webhooks/shopify/order-paid
   └── Verify HMAC signature
   └── Extract preview_id from line items
   └── Create order record
   └── Mark preview as PURCHASED
   └── Generate remaining pages (if needed)
   └── Generate PDF
   └── Email download link

7. USER DOWNLOADS
   GET /api/download/{order_id}
   └── Verify order ownership
   └── Return PDF URL
```

---

## Tech Stack

| Category | Technology | Purpose |
|----------|------------|---------|
| **Framework** | FastAPI 0.109 | Async REST API |
| **Server** | Gunicorn + Uvicorn | Production WSGI/ASGI server |
| **Database** | Supabase (PostgreSQL) | Data persistence |
| **Storage** | Cloudflare R2 | Image & PDF storage (S3-compatible) |
| **AI** | Fal.ai (Flux PuLID) | Identity-preserving image generation |
| **Face Detection** | MediaPipe | Photo validation |
| **PDF** | ReportLab | PDF generation |
| **Email** | Resend | Transactional emails |
| **E-commerce** | Shopify | Payment & order management |
| **Logging** | structlog | Structured JSON logging |
| **Rate Limiting** | slowapi | API rate limiting |

---

## Project Structure

```
magictales_backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point, middleware, exception handlers
│   ├── config.py               # Pydantic settings, environment configuration
│   │
│   ├── api/                    # === API LAYER ===
│   │   ├── router.py           # Main router - aggregates all endpoints
│   │   │
│   │   ├── endpoints/          # REST API endpoints
│   │   │   ├── upload.py       # POST /api/upload-photo - Photo upload & validation
│   │   │   ├── preview.py      # POST /api/preview - Start generation
│   │   │   │                   # GET /api/preview/{id} - Get preview data
│   │   │   │                   # POST /api/preview/{id}/retry - Retry failed
│   │   │   ├── status.py       # GET /api/preview-status/{job_id} - Poll progress
│   │   │   ├── download.py     # GET /api/download/{order_id} - Get PDF
│   │   │   ├── health.py       # GET /health - Health check with DB status
│   │   │   ├── my_creations.py # GET /api/my-creations - User's stories
│   │   │   ├── development.py  # Dev endpoints (disabled in production)
│   │   │   └── test_shopify.py # Test endpoints (disabled in production)
│   │   │
│   │   └── webhooks/
│   │       └── shopify.py      # POST /webhooks/shopify/order-paid
│   │                           # POST /webhooks/shopify/order-cancelled
│   │
│   ├── ai/                     # === AI GENERATION LAYER ===
│   │   ├── base.py             # Abstract base classes for AI services
│   │   ├── factory.py          # Pipeline factory - creates appropriate pipeline
│   │   │
│   │   ├── implementations/    # Concrete AI model implementations
│   │   │   ├── flux_pulid.py   # Flux PuLID - identity preservation
│   │   │   ├── nano_banana.py  # NanoBanana pipeline (VLM + generation)
│   │   │   └── inpainting.py   # Face inpainting service
│   │   │
│   │   ├── pipelines/          # High-level generation pipelines
│   │   │   ├── storybook_pipeline.py   # Main photorealistic pipeline
│   │   │   └── cartoon3d_pipeline.py   # 3D cartoon style pipeline
│   │   │
│   │   └── utils/
│   │       └── face_utils.py   # Face processing utilities
│   │
│   ├── services/               # === BUSINESS LOGIC LAYER ===
│   │   ├── storage.py          # R2 storage operations (upload, download, signed URLs)
│   │   ├── face_validation.py  # MediaPipe face detection service
│   │   ├── pdf_generator.py    # PDF service (delegates to storygift)
│   │   ├── storygift_pdf_generator.py  # ReportLab PDF generation (10x10 format)
│   │   ├── email_service.py    # Resend email integration
│   │   └── shopify_auth.py     # Shopify HMAC verification
│   │
│   ├── stories/                # === STORY CONTENT ===
│   │   └── themes/             # Story theme definitions
│   │       ├── __init__.py     # Theme registry and helpers
│   │       ├── storygift_enchanted_forest.py   # Theme: Magical forest adventure
│   │       ├── storygift_magic_castle.py       # Theme: Royal castle
│   │       ├── storygift_ocean_explorer.py     # Theme: Underwater journey
│   │       ├── storygift_cosmic_dreamer.py     # Theme: Space exploration
│   │       ├── storygift_mighty_guardian.py    # Theme: Superhero origin
│   │       ├── storygift_birthday_magic.py     # Theme: Birthday celebration
│   │       ├── storygift_safari_adventure.py   # Theme: African safari
│   │       └── storygift_dream_weaver.py       # Theme: Dream world
│   │
│   ├── background/             # === BACKGROUND TASKS ===
│   │   └── tasks.py            # Async generation tasks
│   │                           # - generate_full_preview()
│   │                           # - generate_remaining_pages()
│   │                           # - generate_pdf()
│   │
│   ├── models/                 # === DATA MODELS ===
│   │   ├── database.py         # Supabase client (with REST fallback)
│   │   ├── schemas.py          # Pydantic request/response models
│   │   └── enums.py            # Status enums (PreviewStatus, JobStatus, etc.)
│   │
│   ├── core/                   # === CORE UTILITIES ===
│   │   ├── exceptions.py       # Custom exception classes
│   │   └── rate_limiter.py     # Rate limiting configuration
│   │
│   └── routers/
│       └── proxy.py            # Shopify App Proxy - serves React frontend
│
├── migrations/                 # SQL migration files
│   ├── add_cartoon_3d_style.sql
│   ├── add_cover_url.sql
│   └── ...
│
├── tests/                      # Test suite (pytest)
│
├── .claude/                    # Claude Code agent configurations
│   └── agents/
│       ├── backend-api.md
│       ├── ai-pipeline.md
│       ├── database.md
│       ├── shopify-integration.md
│       └── testing.md
│
├── Dockerfile                  # Container definition
├── docker-compose.yml          # Local development with Docker
├── requirements.txt            # Python dependencies
├── render.yaml                 # Render.com deployment config
├── CLAUDE.md                   # Claude Code project guide
└── .env.example               # Environment template
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- pip
- Supabase account (free tier works)
- Cloudflare R2 bucket
- Fal.ai API key

### Local Development Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-org/magictales_backend.git
cd magictales_backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Copy environment template
cp .env.example .env

# 6. Configure environment variables
# Edit .env with your credentials (see Configuration section)

# 7. Run development server
uvicorn app.main:app --reload --port 8000

# 8. Access the API
# API: http://localhost:8000
# Docs: http://localhost:8000/docs (Swagger UI)
# ReDoc: http://localhost:8000/redoc
```

### Running with Docker

```bash
# Build image
docker build -t magictales-backend .

# Run container
docker run -p 8000:8000 --env-file .env magictales-backend

# Or use docker-compose for full stack
docker-compose up
```

---

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# ╔═══════════════════════════════════════════════════════════════════╗
# ║                      APP CONFIGURATION                             ║
# ╚═══════════════════════════════════════════════════════════════════╝
APP_ENV=development              # development | staging | production
APP_DEBUG=true                   # Enable debug mode & API docs
APP_SECRET_KEY=your-secret-key-minimum-32-characters-long

# ╔═══════════════════════════════════════════════════════════════════╗
# ║                      DATABASE (Supabase)                           ║
# ╚═══════════════════════════════════════════════════════════════════╝
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
DATABASE_URL=postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres

# ╔═══════════════════════════════════════════════════════════════════╗
# ║                      STORAGE (Cloudflare R2)                       ║
# ╚═══════════════════════════════════════════════════════════════════╝
R2_ACCOUNT_ID=your-cloudflare-account-id
R2_ACCESS_KEY_ID=your-r2-access-key
R2_SECRET_ACCESS_KEY=your-r2-secret-key
R2_BUCKET_NAME=magictales-storage
R2_PUBLIC_URL=https://pub-xxxxx.r2.dev
R2_ENDPOINT_URL=https://xxxxx.r2.cloudflarestorage.com

# ╔═══════════════════════════════════════════════════════════════════╗
# ║                      AI SERVICES (Fal.ai)                          ║
# ╚═══════════════════════════════════════════════════════════════════╝
FAL_API_KEY=your-fal-api-key

# ╔═══════════════════════════════════════════════════════════════════╗
# ║                      SHOPIFY INTEGRATION                           ║
# ╚═══════════════════════════════════════════════════════════════════╝
# Required in production, optional in development
SHOPIFY_SHOP_DOMAIN=your-store.myshopify.com
SHOPIFY_WEBHOOK_SECRET=whsec_xxxxx
SHOPIFY_API_SECRET=shpss_xxxxx

# ╔═══════════════════════════════════════════════════════════════════╗
# ║                      EMAIL (Resend)                                ║
# ╚═══════════════════════════════════════════════════════════════════╝
RESEND_API_KEY=re_xxxxx
FROM_EMAIL=MagicTales <noreply@yourdomain.com>

# ╔═══════════════════════════════════════════════════════════════════╗
# ║                      FEATURE FLAGS                                 ║
# ╚═══════════════════════════════════════════════════════════════════╝
TESTING_MODE_ENABLED=false       # Enable dev/test endpoints
```

### Environment-Specific Settings

| Setting | Development | Production |
|---------|-------------|------------|
| `APP_ENV` | development | production |
| `APP_DEBUG` | true | false |
| `TESTING_MODE_ENABLED` | true | false |
| API Docs | Enabled (/docs) | Disabled |
| Dev Endpoints | Enabled | Disabled |
| Logging | Console + File | Console only |
| Shopify Verification | Relaxed | Strict |

---

## API Reference

### Endpoints Summary

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/health` | Health check with DB status | None |
| `POST` | `/api/upload-photo` | Upload and validate child photo | None |
| `POST` | `/api/preview` | Start story generation | Session |
| `GET` | `/api/preview-status/{job_id}` | Poll generation progress | None |
| `GET` | `/api/preview/{preview_id}` | Get preview data | None |
| `POST` | `/api/preview/{job_id}/retry` | Retry failed generation | None |
| `GET` | `/api/download/{order_id}` | Download purchased PDF | Order ownership |
| `GET` | `/api/my-creations` | List user's stories | Session/Customer ID |
| `POST` | `/webhooks/shopify/order-paid` | Shopify payment webhook | HMAC |
| `POST` | `/webhooks/shopify/order-cancelled` | Shopify cancellation webhook | HMAC |

### Detailed Endpoint Documentation

#### Upload Photo

```http
POST /api/upload-photo
Content-Type: multipart/form-data
```

**Request:**
```
file: <binary image data>
```

**Response (200 OK):**
```json
{
  "success": true,
  "photo_id": "fed301ba-5e60-47f0-8a08-e1ab71656dbf",
  "photo_url": "https://pub-xxx.r2.dev/uploads/fed301ba.../photo.jpg",
  "face_detected": true,
  "face_confidence": 0.95,
  "face_area_percent": 19.97
}
```

**Error Responses:**
- `400` - No face detected, multiple faces, face too small
- `413` - File too large (max 10MB)
- `415` - Invalid file type

---

#### Create Preview

```http
POST /api/preview
Content-Type: application/json
```

**Request:**
```json
{
  "photo_url": "https://storage.com/uploads/.../photo.jpg",
  "child_name": "Emma",
  "child_age": 6,
  "child_gender": "female",
  "theme": "storygift_enchanted_forest",
  "style": "photorealistic",
  "session_id": "optional-session-id"
}
```

**Response (200 OK):**
```json
{
  "job_id": "abc123-def456",
  "preview_id": "xyz789-uvw012",
  "status": "queued",
  "estimated_time_seconds": 180,
  "message": "Your personalized storybook is being generated..."
}
```

---

#### Poll Status

```http
GET /api/preview-status/{job_id}
```

**Response (200 OK):**
```json
{
  "job_id": "abc123-def456",
  "status": "processing",
  "progress": 45,
  "current_step": "Generating page 5 of 10...",
  "pages_completed": 4,
  "total_pages": 10,
  "preview_id": "xyz789-uvw012",
  "estimated_remaining_seconds": 90
}
```

**Status Values:**
- `queued` - Waiting to start
- `processing` - Currently generating
- `completed` - All pages ready
- `failed` - Generation failed (check error_message)

---

#### Get Preview

```http
GET /api/preview/{preview_id}
```

**Response (200 OK):**
```json
{
  "preview_id": "xyz789-uvw012",
  "status": "active",
  "generation_phase": "preview",
  "story_title": "Emma's Enchanted Forest Adventure",
  "child_name": "Emma",
  "theme": "storygift_enchanted_forest",
  "style": "photorealistic",
  "cover_url": "https://storage.com/covers/xyz789.jpg",
  "preview_pages": [
    {
      "page_number": 0,
      "image_url": "https://storage.com/covers/xyz789.jpg",
      "story_text": "",
      "is_watermarked": true,
      "is_locked": false,
      "is_cover": true
    },
    {
      "page_number": 1,
      "image_url": "https://storage.com/previews/page1.jpg",
      "story_text": "Once upon a time, Emma discovered a hidden path...",
      "is_watermarked": true,
      "is_locked": false,
      "is_cover": false
    }
    // ... pages 2-5
  ],
  "locked_pages": [
    {
      "page_number": 6,
      "image_url": "",
      "story_text": "Deep in the forest, Emma found...",
      "is_watermarked": false,
      "is_locked": true
    }
    // ... pages 7-10
  ],
  "total_pages": 11,
  "preview_pages_count": 6,
  "locked_pages_count": 5,
  "expires_at": "2024-01-29T12:00:00Z",
  "days_remaining": 7,
  "pdf_url": null,
  "purchase": {
    "price": 599,
    "currency": "INR",
    "price_formatted": "₹599",
    "checkout_url": "https://store.myshopify.com/cart/add?..."
  }
}
```

---

## Story Themes

### Available Themes

| Theme ID | Title | Age Range | Pages |
|----------|-------|-----------|-------|
| `storygift_enchanted_forest` | Enchanted Forest | 3-8 | 10 |
| `storygift_magic_castle` | Magic Castle | 4-9 | 10 |
| `storygift_ocean_explorer` | Ocean Explorer | 3-8 | 10 |
| `storygift_cosmic_dreamer` | Cosmic Adventure | 5-10 | 10 |
| `storygift_mighty_guardian` | Mighty Guardian | 4-9 | 10 |
| `storygift_birthday_magic` | Birthday Magic | 3-8 | 10 |
| `storygift_safari_adventure` | Safari Adventure | 3-8 | 10 |
| `storygift_dream_weaver` | Dream Weaver | 4-9 | 10 |

### Theme Structure

Each theme is defined in `app/stories/themes/`:

```python
# Example: storygift_enchanted_forest.py

from app.stories.themes import StoryTheme, StoryPage

ENCHANTED_FOREST_THEME = StoryTheme(
    id="storygift_enchanted_forest",
    title="The Enchanted Forest",
    title_template="{name}'s Enchanted Forest Adventure",
    description="A magical woodland adventure with talking animals",
    age_range="3-8",

    # Cover generation settings
    cover_prompt="A magical forest entrance with glowing fireflies...",

    # 10 story pages
    pages=[
        StoryPage(
            page_number=1,
            scene_prompt="""
                A {age}-year-old {gender} child with {face_description}
                standing at the entrance of a magical glowing forest,
                wearing {costume}, looking with wonder at floating fireflies...
            """,
            story_text="Once upon a time, {name} discovered a hidden path that led to an enchanted forest...",
            costume="a cozy explorer outfit with a small backpack",
            setting="forest entrance with ancient trees and glowing mushrooms"
        ),
        # ... pages 2-10
    ]
)
```

### Adding a New Theme

1. **Create theme file**: `app/stories/themes/storygift_your_theme.py`

2. **Define the theme**:
```python
YOUR_THEME = StoryTheme(
    id="storygift_your_theme",
    title="Your Theme Title",
    title_template="{name}'s Your Theme Adventure",
    description="Theme description",
    age_range="3-8",
    cover_prompt="Cover image prompt...",
    pages=[
        StoryPage(
            page_number=1,
            scene_prompt="AI generation prompt with {name}, {age}, {gender}, {face_description}...",
            story_text="Story text with {name} placeholder...",
            costume="character outfit description",
            setting="scene setting description"
        ),
        # Add all 10 pages
    ]
)
```

3. **Register in `__init__.py`**:
```python
from .storygift_your_theme import YOUR_THEME

THEMES = {
    # ... existing themes
    "storygift_your_theme": YOUR_THEME,
}
```

4. **Add to frontend** theme selection

---

## AI Pipeline

### Generation Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI GENERATION PIPELINE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ Child Photo  │───▶│  MediaPipe   │───▶│ Face Crop    │      │
│  │   (Input)    │    │  Detection   │    │ & Validate   │      │
│  └──────────────┘    └──────────────┘    └──────┬───────┘      │
│                                                  │               │
│                                                  ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ Theme Page   │───▶│   Prompt     │◀───│  VLM Face    │      │
│  │   Data       │    │   Builder    │    │  Analysis    │      │
│  └──────────────┘    └──────┬───────┘    └──────────────┘      │
│                             │                                    │
│                             ▼                                    │
│                      ┌──────────────┐                           │
│                      │  Fal.ai      │                           │
│                      │  Flux PuLID  │                           │
│                      └──────┬───────┘                           │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  Watermark   │◀───│  Generated   │───▶│   Upload     │      │
│  │   (Preview)  │    │    Image     │    │   to R2      │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Models Used

| Model | Provider | Purpose | Cost |
|-------|----------|---------|------|
| **Flux PuLID** | Fal.ai | Identity-preserving image generation | ~$0.04/image |
| **LLaVA Next** | Fal.ai | Vision-language face description | ~$0.01/call |
| **MediaPipe** | Google | Local face detection | Free |

### Art Styles

| Style | Description | Prompt Modifications |
|-------|-------------|---------------------|
| `photorealistic` | Realistic, cinematic look | Higher detail, realistic lighting |
| `cartoon_3d` | Pixar/Disney-style 3D | Stylized, softer features, vibrant colors |

### Pipeline Code Flow

```python
# app/ai/pipelines/storybook_pipeline.py

class StorybookPipeline:
    async def generate_page(
        self,
        scene_prompt: str,
        child_photo_url: str,
        child_name: str,
        child_age: int,
        child_gender: str,
        **kwargs
    ) -> GenerationResult:

        # 1. Analyze face with VLM
        face_description = await self.vlm_service.describe_face(child_photo_url)

        # 2. Build final prompt
        final_prompt = self.build_prompt(
            scene_prompt=scene_prompt,
            face_description=face_description,
            name=child_name,
            age=child_age,
            gender=child_gender
        )

        # 3. Generate image with identity preservation
        result = await self.flux_pulid.generate(
            prompt=final_prompt,
            face_image_url=child_photo_url,
            id_weight=0.9  # How much to preserve identity
        )

        return result
```

---

## Background Tasks

### Task System

We use FastAPI's built-in `BackgroundTasks` - no external queue needed:

```python
# In endpoint
background_tasks.add_task(
    generate_full_preview,
    job_id=job_id,
    preview_id=preview_id,
    photo_url=photo_url,
    # ... other params
)
```

### Main Tasks

#### `generate_full_preview`
Generates all 10 story pages + cover image.

```python
async def generate_full_preview(
    job_id: str,
    preview_id: str,
    photo_url: str,
    child_name: str,
    child_age: int,
    child_gender: str,
    theme: str,
    style: str
):
    # 1. Update job status
    update_job(job_id, status="processing", progress=0)

    # 2. Get theme template
    theme_template = get_theme(theme)

    # 3. Generate cover
    cover_url = await generate_cover(...)
    update_progress(job_id, 5)

    # 4. Generate each page
    for i, page in enumerate(theme_template.pages):
        image_url = await pipeline.generate_page(...)

        # Apply watermark for preview pages (1-5)
        if i < 5:
            watermarked_url = await apply_watermark(image_url)

        update_progress(job_id, 10 + (i * 9))  # 10% to 100%

    # 5. Update preview with all URLs
    update_preview(preview_id, images=all_images)

    # 6. Mark complete
    update_job(job_id, status="completed", progress=100)
```

#### `generate_remaining_pages`
Called after purchase to generate pages 6-10 without watermarks.

#### `generate_pdf`
Creates the final PDF using ReportLab.

### Retry Mechanism

- Max 3 attempts per job
- Exponential backoff between retries
- Failed pages tracked separately
- User can trigger manual retry

---

## Shopify Integration

### Webhook Configuration

Configure in Shopify Admin → Settings → Notifications → Webhooks:

| Event | URL | Format |
|-------|-----|--------|
| Order paid | `https://api.yourapp.com/webhooks/shopify/order-paid` | JSON |
| Order cancelled | `https://api.yourapp.com/webhooks/shopify/order-cancelled` | JSON |

### Webhook Security

All webhooks are verified using HMAC-SHA256:

```python
def verify_shopify_webhook(request_body: bytes, signature: str, secret: str) -> bool:
    computed = base64.b64encode(
        hmac.new(
            secret.encode(),
            request_body,
            hashlib.sha256
        ).digest()
    ).decode()

    return hmac.compare_digest(computed, signature)
```

### Order Flow

```
┌─────────────────────────────────────────────────────────────┐
│                  SHOPIFY ORDER FLOW                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Customer adds to cart with preview_id in line item props │
│     └── properties[preview_id] = "xyz789"                   │
│                                                              │
│  2. Customer completes checkout                              │
│                                                              │
│  3. Shopify sends order-paid webhook                         │
│     POST /webhooks/shopify/order-paid                        │
│     └── Verify HMAC signature                                │
│     └── Extract preview_id from line_items                   │
│     └── Check idempotency (order already processed?)         │
│                                                              │
│  4. Create order record in database                          │
│     └── Link to preview_id                                   │
│     └── Store customer email                                 │
│                                                              │
│  5. Update preview status                                    │
│     └── status = "purchased"                                 │
│     └── generation_phase = "generating_full"                 │
│                                                              │
│  6. Generate remaining pages (if needed)                     │
│     └── Pages 6-10 without watermark                         │
│                                                              │
│  7. Generate PDF                                             │
│     └── All 10 pages + cover                                 │
│     └── Upload to R2                                         │
│                                                              │
│  8. Send email with download link                            │
│     └── Via Resend                                           │
│     └── Link expires in 30 days                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### App Proxy

The backend serves the React frontend via Shopify App Proxy:

**Shopify Partner Dashboard Configuration:**
- Subpath prefix: `storygift`
- Proxy URL: `https://api.yourapp.com/proxy`

**Result:**
```
https://your-store.myshopify.com/apps/storygift/create
                    ↓
https://api.yourapp.com/proxy/create
                    ↓
React SPA with Liquid wrapper
```

---

## Database Schema

### ERD Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    previews     │     │ generation_jobs │     │     orders      │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ preview_id (PK) │◀────│ reference_id    │     │ order_id (PK)   │
│ session_id      │     │ job_id (PK)     │     │ preview_id (FK) │───┐
│ customer_id     │     │ job_type        │     │ customer_email  │   │
│ child_name      │     │ status          │     │ status          │   │
│ theme           │     │ progress        │     │ pdf_url         │   │
│ style           │     │ current_step    │     │ created_at      │   │
│ photo_url       │     │ error_message   │     │ expires_at      │   │
│ status          │     │ queued_at       │     └─────────────────┘   │
│ cover_url       │     │ completed_at    │                           │
│ hires_images    │     └─────────────────┘                           │
│ preview_images  │                                                    │
│ story_pages     │◀───────────────────────────────────────────────────┘
│ pdf_url         │
│ created_at      │
│ expires_at      │
└─────────────────┘
```

### Table Definitions

```sql
-- ═══════════════════════════════════════════════════════════════
-- PREVIEWS: Story generation records
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE previews (
    preview_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT,                    -- Browser session for guests
    customer_id TEXT,                   -- Shopify customer ID
    customer_email TEXT,

    -- Child info
    child_name TEXT NOT NULL,
    child_age INTEGER,
    child_gender TEXT,                  -- 'male' or 'female'

    -- Story config
    theme TEXT NOT NULL,                -- e.g., 'storygift_enchanted_forest'
    style TEXT DEFAULT 'photorealistic', -- 'photorealistic' or 'cartoon_3d'
    photo_url TEXT NOT NULL,

    -- Status tracking
    status TEXT DEFAULT 'generating',   -- generating, active, purchased, expired, failed
    generation_phase TEXT,              -- preview, generating_full, complete

    -- Generated content
    cover_url TEXT,
    hires_images JSONB DEFAULT '[]',    -- [{page: 1, url: "..."}, ...]
    preview_images JSONB DEFAULT '[]',  -- Watermarked versions
    story_pages JSONB DEFAULT '[]',     -- [{page: 1, text: "..."}, ...]
    pdf_url TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '7 days')
);

-- ═══════════════════════════════════════════════════════════════
-- GENERATION_JOBS: Track async generation tasks
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE generation_jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type TEXT NOT NULL,             -- 'preview_generation', 'pdf_generation'
    reference_id UUID NOT NULL,         -- preview_id or order_id

    -- Status
    status TEXT DEFAULT 'queued',       -- queued, processing, completed, failed
    progress INTEGER DEFAULT 0,         -- 0-100
    current_step TEXT,                  -- Human-readable status
    error_message TEXT,
    result_data JSONB,

    -- Timestamps
    queued_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Retry tracking
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3
);

-- ═══════════════════════════════════════════════════════════════
-- ORDERS: Purchase records (linked to Shopify)
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,          -- Shopify order ID
    order_number TEXT,                  -- Human-readable order number
    preview_id UUID REFERENCES previews(preview_id),

    customer_email TEXT,
    status TEXT DEFAULT 'paid',         -- paid, generating_pdf, completed, failed
    pdf_url TEXT,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days')
);

-- ═══════════════════════════════════════════════════════════════
-- INDEXES
-- ═══════════════════════════════════════════════════════════════
CREATE INDEX idx_previews_session ON previews(session_id);
CREATE INDEX idx_previews_customer ON previews(customer_id);
CREATE INDEX idx_previews_status ON previews(status);
CREATE INDEX idx_jobs_reference ON generation_jobs(reference_id);
CREATE INDEX idx_jobs_status ON generation_jobs(status);
CREATE INDEX idx_orders_preview ON orders(preview_id);
```

---

## Deployment

### Render.com (Recommended)

1. **Connect Repository**
   - Go to Render Dashboard
   - New → Web Service
   - Connect GitHub repo

2. **Configure Service**
   - Name: `magictales-backend`
   - Region: Oregon (US West) or closest to users
   - Branch: `main`
   - Build Command: (uses Dockerfile)
   - Instance Type: **Starter ($7/mo)** minimum
     - Free tier spins down and breaks webhooks!

3. **Set Environment Variables**
   - Copy all variables from `.env`
   - Set `APP_ENV=production`
   - Set `APP_DEBUG=false`
   - Set `TESTING_MODE_ENABLED=false`

4. **Configure Health Check**
   - Health Check Path: `/health`

5. **Deploy**

### Docker Deployment (Manual)

```bash
# Build
docker build -t magictales-backend .

# Run
docker run -d \
  --name magictales-api \
  -p 8000:8000 \
  --env-file .env \
  --restart unless-stopped \
  magictales-backend
```

### Production Checklist

- [ ] `APP_ENV=production`
- [ ] `APP_DEBUG=false`
- [ ] `TESTING_MODE_ENABLED=false`
- [ ] All Shopify credentials configured
- [ ] Resend domain verified
- [ ] R2 bucket permissions set
- [ ] Health check working
- [ ] Webhooks receiving (test with Shopify)
- [ ] SSL/HTTPS enabled
- [ ] Logs accessible

---

## Development Guide

### Code Style

```bash
# Format code
black app/

# Sort imports
isort app/

# Type checking
mypy app/

# Lint
flake8 app/
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_preview.py

# Run with verbose output
pytest -v
```

### Adding a New Endpoint

1. **Create endpoint file**: `app/api/endpoints/your_endpoint.py`

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import structlog

logger = structlog.get_logger()
router = APIRouter()

class YourRequest(BaseModel):
    field: str

class YourResponse(BaseModel):
    result: str

@router.post("/your-endpoint", response_model=YourResponse)
async def your_endpoint(request: YourRequest):
    """
    Endpoint description.
    """
    logger.info("Processing request", field=request.field)

    # Your logic here

    return YourResponse(result="success")
```

2. **Register in router**: `app/api/router.py`

```python
from app.api.endpoints import your_endpoint

api_router.include_router(your_endpoint.router, tags=["your-tag"])
```

3. **Add tests**: `tests/test_your_endpoint.py`

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes and commit
git add .
git commit -m "feat: add your feature"

# Push and create PR
git push -u origin feature/your-feature
```

**Branch Naming:**
- `feature/add-new-theme`
- `fix/pdf-generation-error`
- `refactor/ai-pipeline`
- `docs/update-readme`

**Commit Messages:**
- `feat: add new feature`
- `fix: resolve bug`
- `refactor: improve code structure`
- `docs: update documentation`
- `test: add tests`

---

## Troubleshooting

### Common Issues

#### "No module named 'requests'"
```bash
pip install requests
```
The REST Supabase fallback client requires this package.

#### Database Connection Fails
- Verify `SUPABASE_URL` and `SUPABASE_KEY`
- Check network connectivity
- Ensure Supabase project is active

#### Image Generation Fails
- Check `FAL_API_KEY` is valid
- Verify Fal.ai account has credits
- Ensure photo URL is publicly accessible

#### Health Check Fails on Render
- Increase `--start-period` in Dockerfile
- Check startup logs for errors
- Verify database connection

#### Shopify Webhooks Not Received
- Verify webhook URL is publicly accessible (HTTPS)
- Check `SHOPIFY_WEBHOOK_SECRET` matches Shopify config
- Test with Shopify's webhook tester

#### Face Not Detected
- Photo should have clear, front-facing face
- Face should be at least 10% of image area
- Good lighting, no obstructions

### Viewing Logs

**Local:**
```bash
# If file logging enabled
tail -f logs/app.log
```

**Render:**
- Dashboard → Your Service → Logs
- Or: `render logs -s magictales-backend`

### Debug Mode

Enable detailed logging:
```bash
APP_DEBUG=true
```

Access API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Health Check Details

```bash
curl https://your-api.com/health
```

Response:
```json
{
  "status": "healthy",      // or "degraded"
  "database": "connected",  // or "disconnected"
  "timestamp": "2024-01-22T12:00:00Z",
  "service": "magictales-backend"
}
```

---

## Support

- **Issues**: GitHub Issues
- **Documentation**: This README + `/docs` endpoint
- **Claude Code**: Use `.claude/agents/` for specialized help

---

## License

Proprietary - All Rights Reserved

---

**Built with FastAPI, powered by AI**
