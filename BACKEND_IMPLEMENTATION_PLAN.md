# ZELAVO KIDS - BACKEND IMPLEMENTATION PLAN
## AI-Powered Personalized Children's Storybook Platform

**Document Purpose:** Complete backend implementation specification for Claude Code
**Tech Stack:** FastAPI + Python 3.11 + Supabase + Cloudflare R2 + FastAPI BackgroundTasks
**Last Updated:** December 2024

---

# TABLE OF CONTENTS

1. Project Overview
2. Technology Stack & Dependencies
3. Project Structure
4. Environment Variables
5. Database Schema
6. API Endpoints Specification
7. Core Services Implementation
8. AI Pipeline Services
9. Background Tasks (FastAPI)
10. Storage Service (Cloudflare R2)
11. Webhook Handlers
12. Error Handling & Retry Logic
13. Testing Requirements
14. Deployment Configuration

---

# 1. PROJECT OVERVIEW

## 1.1 What We're Building

A FastAPI backend that:
1. Accepts child photos and validates faces
2. Generates personalized storybook images using AI
3. Supports TWO styles:
   - **Artistic:** Google Imagen 3 + Fal.ai Face Swap
   - **Photorealistic:** Fal.ai Flux PuLID
4. Handles Shopify webhooks for payments
5. Generates PDFs and manages downloads
6. Uses background job processing for AI generation

## 1.2 Core User Flow

```
User uploads photo → Face validation → Generate ALL 10 pages (high-res)
→ Create 5 watermarked previews → User views preview (7 days valid)
→ User pays via Shopify → Webhook received → Generate PDF from existing images
→ Download link emailed → Cleanup preview files
```

**IMPORTANT:** All 10 images are generated UPFRONT when user submits the form. After payment, we only generate the PDF since images already exist.

## 1.3 Two Product Pipelines

| Product | Pipeline | API Calls per Image | Total per Book |
|---------|----------|---------------------|----------------|
| Artistic Storybook | Imagen 3 → Face Swap | 2 calls | 20 calls |
| Photorealistic Storybook | Flux PuLID | 1 call | 10 calls |

## 1.4 Storage Flow

```
/uploads/{preview_id}/photo.jpg     → Original child photo
/final/{preview_id}/page_01.jpg     → HIGH-RES images (all 10)
/previews/{preview_id}/page_01.jpg  → LOW-RES watermarked (first 5)
/final/{preview_id}/book.pdf        → PDF (generated after payment)
```

## 1.5 Retention Rules

| Scenario | /uploads/ | /final/ | /previews/ |
|----------|-----------|---------|------------|
| Preview active (unpaid) | 7 days | 7 days | 7 days |
| After payment | 30 days | 30 days | DELETE immediately |
| Expired (no payment) | DELETE | DELETE | DELETE |

---

# 2. TECHNOLOGY STACK & DEPENDENCIES

## 2.1 requirements.txt

```
# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6
pydantic==2.5.3
pydantic-settings==2.1.0

# Database
supabase==2.3.4
asyncpg==0.29.0

# Background Tasks (using FastAPI built-in)
# No external queue system needed for MVP

# Storage (Cloudflare R2 - S3 compatible)
boto3==1.34.14

# AI Services
httpx==0.26.0
aiohttp==3.9.1

# Face Detection
mediapipe==0.10.9
opencv-python-headless==4.9.0.80
numpy==1.26.3
Pillow==10.2.0

# PDF Generation
weasyprint==60.2
jinja2==3.1.3

# Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
cryptography==41.0.7

# Utilities
python-dotenv==1.0.0
tenacity==8.2.3
structlog==24.1.0

# Development
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0
```

## 2.2 External Services Required

| Service | Purpose | API Key Env Variable |
|---------|---------|---------------------|
| Google AI Studio | Imagen 3 for artistic images | `GOOGLE_AI_API_KEY` |
| Fal.ai | Face Swap + Flux PuLID | `FAL_API_KEY` |
| Supabase | PostgreSQL database | `SUPABASE_URL`, `SUPABASE_KEY` |
| Cloudflare R2 | Image/PDF storage | `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY` |
| Shopify | Webhooks | `SHOPIFY_WEBHOOK_SECRET` |

---

# 3. PROJECT STRUCTURE

```
zelavo-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI app initialization
│   ├── config.py                   # Settings and environment variables
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py               # Main API router
│   │   ├── endpoints/
│   │   │   ├── __init__.py
│   │   │   ├── upload.py           # POST /api/upload-photo
│   │   │   ├── preview.py          # POST /api/preview, GET /api/preview/{id}
│   │   │   ├── status.py           # GET /api/preview-status/{job_id}
│   │   │   ├── download.py         # GET /api/download/{order_id}
│   │   │   └── health.py           # GET /health
│   │   └── webhooks/
│   │       ├── __init__.py
│   │       └── shopify.py          # POST /webhooks/shopify/*
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py             # HMAC verification, signed URLs
│   │   ├── exceptions.py           # Custom exceptions
│   │   └── rate_limiter.py         # Rate limiting logic
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py             # Supabase client
│   │   ├── schemas.py              # Pydantic models (request/response)
│   │   └── enums.py                # Status enums
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── face_validation.py      # MediaPipe face detection
│   │   ├── storage.py              # Cloudflare R2 operations
│   │   ├── pdf_generator.py        # WeasyPrint PDF creation
│   │   └── email.py                # Email notifications (optional)
│   │
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── base.py                 # Base AI service class
│   │   ├── google_imagen.py        # Google Imagen 3 API wrapper
│   │   ├── fal_face_swap.py        # Fal.ai Face Swap wrapper
│   │   ├── fal_pulid.py            # Fal.ai Flux PuLID wrapper
│   │   ├── artistic_pipeline.py    # Imagen 3 + Face Swap pipeline
│   │   └── realistic_pipeline.py   # Flux PuLID pipeline
│   │
│   ├── background/
│   │   ├── __init__.py
│   │   └── tasks.py                # FastAPI background tasks
│   │
│   └── stories/
│       ├── __init__.py
│       ├── templates.py            # Story templates/prompts
│       └── themes/
│           ├── magic_castle.py     # Magic school theme
│           ├── space_adventure.py  # Space theme
│           ├── underwater.py       # Ocean theme
│           └── forest_friends.py   # Forest theme
│
├── templates/
│   └── pdf/
│       └── storybook.html          # PDF template
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_upload.py
│   ├── test_preview.py
│   ├── test_pipelines.py
│   └── test_webhooks.py
│
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── render.yaml                     # Render deployment config
└── README.md
```

---

# 4. ENVIRONMENT VARIABLES

## 4.1 .env.example

```env
# ===================
# APP CONFIGURATION
# ===================
APP_ENV=development
APP_DEBUG=true
APP_SECRET_KEY=your-secret-key-min-32-chars-here

# ===================
# DATABASE (Supabase)
# ===================
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-supabase-service-role-key
DATABASE_URL=postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres

# ===================
# BACKGROUND TASKS (MVP)
# ===================
# Using FastAPI BackgroundTasks - no external queue needed

# ===================
# STORAGE (Cloudflare R2)
# ===================
R2_ACCOUNT_ID=your-cloudflare-account-id
R2_ACCESS_KEY_ID=your-r2-access-key
R2_SECRET_ACCESS_KEY=your-r2-secret-key
R2_BUCKET_NAME=zelavo-storage
R2_PUBLIC_URL=https://pub-xxxxx.r2.dev

# ===================
# AI SERVICES
# ===================
GOOGLE_AI_API_KEY=your-google-ai-api-key
FAL_API_KEY=your-fal-ai-api-key

# ===================
# SHOPIFY
# ===================
SHOPIFY_SHOP_DOMAIN=your-store.myshopify.com
SHOPIFY_WEBHOOK_SECRET=your-webhook-secret

# ===================
# RATE LIMITING
# ===================
RATE_LIMIT_PREVIEWS_PER_DAY=3
RATE_LIMIT_UPLOADS_PER_HOUR=10

# ===================
# GENERATION SETTINGS
# ===================
PREVIEW_PAGES=2
FULL_BOOK_PAGES=10
IMAGE_QUALITY=high
DEFAULT_SEED=42
```

## 4.2 config.py Implementation

```python
"""
FILE: app/config.py
PURPOSE: Application settings loaded from environment variables
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_env: str = "development"
    app_debug: bool = False
    app_secret_key: str
    
    # Database
    supabase_url: str
    supabase_key: str
    database_url: str
    
    # Storage
    r2_account_id: str
    r2_access_key_id: str
    r2_secret_access_key: str
    r2_bucket_name: str = "zelavo-storage"
    r2_public_url: str
    
    # AI Services
    google_ai_api_key: str
    fal_api_key: str
    
    # Shopify
    shopify_shop_domain: str
    shopify_webhook_secret: str
    
    # Rate Limiting
    rate_limit_previews_per_day: int = 3
    rate_limit_uploads_per_hour: int = 10
    
    # Generation
    preview_pages: int = 2
    full_book_pages: int = 10
    default_seed: int = 42
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

---

# 5. DATABASE SCHEMA

## 5.1 Supabase SQL Schema

Execute this SQL in Supabase SQL Editor:

```sql
-- ===================
-- ENUMS
-- ===================

CREATE TYPE preview_status AS ENUM (
    'pending',
    'validating',
    'generating',
    'completed',
    'failed',
    'expired',
    'purchased'
);

CREATE TYPE order_status AS ENUM (
    'paid',
    'generating',
    'completed',
    'failed',
    'refunded'
);

CREATE TYPE job_status AS ENUM (
    'queued',
    'processing',
    'completed',
    'failed'
);

CREATE TYPE job_type AS ENUM (
    'preview_generation',
    'full_book_generation',
    'pdf_creation'
);

CREATE TYPE book_style AS ENUM (
    'artistic',
    'photorealistic'
);

-- ===================
-- TABLES
-- ===================

-- Previews table
CREATE TABLE previews (
    id SERIAL PRIMARY KEY,
    preview_id UUID DEFAULT gen_random_uuid() UNIQUE NOT NULL,
    
    -- Session/Customer
    session_id VARCHAR(255),
    customer_id VARCHAR(255),
    
    -- Child details
    child_name VARCHAR(50) NOT NULL,
    child_age INTEGER NOT NULL CHECK (child_age >= 2 AND child_age <= 12),
    child_gender VARCHAR(10) NOT NULL CHECK (child_gender IN ('male', 'female')),
    
    -- Book configuration
    theme VARCHAR(50) NOT NULL,
    style book_style NOT NULL DEFAULT 'artistic',
    
    -- Photo
    photo_url VARCHAR(500) NOT NULL,
    photo_validated BOOLEAN DEFAULT FALSE,
    
    -- Status
    status preview_status DEFAULT 'pending',
    
    -- Generated content
    pages JSONB DEFAULT '[]'::jsonb,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '7 days'),
    
    -- Indexes
    CONSTRAINT valid_theme CHECK (theme IN ('magic_castle', 'space_adventure', 'underwater', 'forest_friends'))
);

CREATE INDEX idx_previews_preview_id ON previews(preview_id);
CREATE INDEX idx_previews_session_id ON previews(session_id);
CREATE INDEX idx_previews_status ON previews(status);
CREATE INDEX idx_previews_expires_at ON previews(expires_at);


-- Orders table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(100) UNIQUE NOT NULL,
    order_number VARCHAR(50),
    
    -- Customer
    customer_id VARCHAR(255),
    customer_email VARCHAR(255) NOT NULL,
    
    -- Link to preview
    preview_id UUID REFERENCES previews(preview_id),
    
    -- Status
    status order_status DEFAULT 'paid',
    
    -- Generated content
    hq_images JSONB DEFAULT '[]'::jsonb,
    pdf_url VARCHAR(500),
    
    -- Shipping (for physical books)
    shipping_address JSONB,
    tracking_number VARCHAR(100),
    
    -- Error handling
    generation_attempts INTEGER DEFAULT 0,
    last_error TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days')
);

CREATE INDEX idx_orders_order_id ON orders(order_id);
CREATE INDEX idx_orders_preview_id ON orders(preview_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_customer_email ON orders(customer_email);


-- Generation Jobs table
CREATE TABLE generation_jobs (
    id SERIAL PRIMARY KEY,
    job_id UUID DEFAULT gen_random_uuid() UNIQUE NOT NULL,
    
    -- Job details
    job_type job_type NOT NULL,
    reference_id VARCHAR(255) NOT NULL,  -- preview_id or order_id
    
    -- Status
    status job_status DEFAULT 'queued',
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    
    -- Timing
    queued_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Error handling
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    error_message TEXT,
    
    -- Result
    result_data JSONB
);

CREATE INDEX idx_jobs_job_id ON generation_jobs(job_id);
CREATE INDEX idx_jobs_reference_id ON generation_jobs(reference_id);
CREATE INDEX idx_jobs_status ON generation_jobs(status);


-- Rate Limiting table
CREATE TABLE rate_limits (
    id SERIAL PRIMARY KEY,
    identifier VARCHAR(255) NOT NULL,  -- IP address or session_id
    action_type VARCHAR(50) NOT NULL,  -- 'upload', 'preview'
    count INTEGER DEFAULT 1,
    window_start TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(identifier, action_type)
);

CREATE INDEX idx_rate_limits_identifier ON rate_limits(identifier);


-- ===================
-- FUNCTIONS
-- ===================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_previews_updated_at
    BEFORE UPDATE ON previews
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- Cleanup expired previews (run daily via cron)
CREATE OR REPLACE FUNCTION cleanup_expired_previews()
RETURNS void AS $$
BEGIN
    UPDATE previews 
    SET status = 'expired' 
    WHERE expires_at < NOW() 
    AND status NOT IN ('purchased', 'expired');
END;
$$ LANGUAGE plpgsql;
```

---

# 6. API ENDPOINTS SPECIFICATION

## 6.1 Endpoints Overview

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| GET | `/health` | Health check | None |
| POST | `/api/upload-photo` | Upload and validate child photo | Rate limited |
| POST | `/api/preview` | Start preview generation | Rate limited |
| GET | `/api/preview-status/{job_id}` | Check generation status | None |
| GET | `/api/preview/{preview_id}` | Get preview data | None |
| GET | `/api/download/{order_id}` | Get download link | Order verified |
| POST | `/webhooks/shopify/order-paid` | Handle payment webhook | HMAC verified |

## 6.2 Detailed Endpoint Specifications

### POST /api/upload-photo

**Purpose:** Upload child photo and validate face

**Request:**
```
Content-Type: multipart/form-data

Fields:
- photo: File (required, max 10MB, jpg/png)
- session_id: string (optional)
```

**Response (200 - Success):**
```json
{
    "success": true,
    "data": {
        "photo_id": "uuid",
        "photo_url": "https://r2.../uploads/uuid.jpg",
        "face_valid": true,
        "face_count": 1
    }
}
```

**Response (400 - Validation Error):**
```json
{
    "success": false,
    "error": {
        "code": "FACE_VALIDATION_FAILED",
        "message": "No face detected. Please upload a clear photo of your child's face.",
        "details": {
            "reason": "no_face_detected"
        }
    }
}
```

**Validation Rules:**
- File size: max 10MB
- File types: jpg, jpeg, png
- Face validation:
  - Exactly 1 face detected
  - Face size > 10% of image area
  - Face is front-facing (not extreme angles)
  - Image not blurry

---

### POST /api/preview

**Purpose:** Start preview generation job

**Request:**
```json
{
    "photo_url": "https://r2.../uploads/uuid.jpg",
    "child_name": "Arjun",
    "child_age": 6,
    "child_gender": "male",
    "theme": "magic_castle",
    "style": "artistic",
    "session_id": "session_uuid"
}
```

**Response (202 - Accepted):**
```json
{
    "success": true,
    "data": {
        "job_id": "job_uuid",
        "preview_id": "preview_uuid",
        "status": "queued",
        "estimated_time_seconds": 120,
        "message": "Your preview is being generated"
    }
}
```

**Validation Rules:**
- `child_name`: 2-50 characters, letters and spaces only
- `child_age`: 2-12
- `child_gender`: "male" or "female"
- `theme`: one of ["magic_castle", "space_adventure", "underwater", "forest_friends"]
- `style`: "artistic" or "photorealistic"

---

### GET /api/preview-status/{job_id}

**Purpose:** Poll for generation status

**Response (200 - In Progress):**
```json
{
    "success": true,
    "data": {
        "job_id": "job_uuid",
        "status": "processing",
        "progress": 45,
        "current_step": "Generating page 1 of 2",
        "preview_id": null
    }
}
```

**Response (200 - Completed):**
```json
{
    "success": true,
    "data": {
        "job_id": "job_uuid",
        "status": "completed",
        "progress": 100,
        "preview_id": "preview_uuid",
        "redirect_url": "/preview/preview_uuid"
    }
}
```

**Response (200 - Failed):**
```json
{
    "success": false,
    "data": {
        "job_id": "job_uuid",
        "status": "failed",
        "error": "Generation failed. Please try again.",
        "can_retry": true
    }
}
```

---

### GET /api/preview/{preview_id}

**Purpose:** Get preview data for display

**Response (200):**
```json
{
    "success": true,
    "data": {
        "preview_id": "preview_uuid",
        "story_title": "Arjun's Magical Adventure",
        "child_name": "Arjun",
        "theme": "magic_castle",
        "style": "artistic",
        "pages": [
            {
                "page_number": 1,
                "image_url": "https://r2.../previews/uuid/page1.jpg",
                "story_text": "One magical morning, Arjun received a mysterious letter...",
                "is_watermarked": true
            },
            {
                "page_number": 2,
                "image_url": "https://r2.../previews/uuid/page2.jpg",
                "story_text": "The gates of the Grand Academy swung open...",
                "is_watermarked": true
            }
        ],
        "total_pages": 10,
        "preview_pages_shown": 2,
        "expires_at": "2024-01-15T00:00:00Z",
        "checkout_url": "https://your-store.myshopify.com/cart/add?id=xxx&properties[preview_id]=preview_uuid"
    }
}
```

---

### GET /api/download/{order_id}

**Purpose:** Get signed download URL for completed book

**Response (200 - Ready):**
```json
{
    "success": true,
    "data": {
        "download_url": "https://r2.../final/order_id.pdf?signature=xxx&expires=3600",
        "filename": "Arjuns_Magical_Adventure.pdf",
        "expires_in_seconds": 3600,
        "file_size_mb": 15.2
    }
}
```

**Response (202 - Still Generating):**
```json
{
    "success": true,
    "data": {
        "status": "generating",
        "progress": 70,
        "message": "Your book is still being created. Please check back in a few minutes."
    }
}
```

**Response (403 - Not Authorized):**
```json
{
    "success": false,
    "error": {
        "code": "ORDER_NOT_FOUND",
        "message": "Order not found or not paid."
    }
}
```

---

### POST /webhooks/shopify/order-paid

**Purpose:** Handle Shopify payment webhook

**Headers Required:**
```
X-Shopify-Hmac-Sha256: {hmac_signature}
X-Shopify-Shop-Domain: your-store.myshopify.com
X-Shopify-Topic: orders/paid
```

**Verification Steps:**
1. Verify HMAC signature using raw body
2. Verify shop domain matches configured domain
3. Check idempotency (order not already processed)

**Response (200):**
```json
{
    "success": true,
    "message": "Webhook received"
}
```

**Note:** Always return 200 quickly, process order asynchronously.

---

# 7. CORE SERVICES IMPLEMENTATION

## 7.1 Face Validation Service

**File:** `app/services/face_validation.py`

**Functionality:**
- Use MediaPipe Face Detection
- Validate exactly 1 face present
- Check face size (>10% of image)
- Check face angle (front-facing)
- Check image quality (not blurry)

**Interface:**
```python
class FaceValidationService:
    def validate(self, image_bytes: bytes) -> FaceValidationResult:
        """
        Validate uploaded image for face requirements.
        
        Returns:
            FaceValidationResult with:
            - is_valid: bool
            - face_count: int
            - error_code: str (if invalid)
            - error_message: str (if invalid)
        """
        pass
```

**Error Codes:**
- `no_face_detected` - No face found in image
- `multiple_faces` - More than one face detected
- `face_too_small` - Face is less than 10% of image
- `face_angle_invalid` - Face not front-facing
- `image_blurry` - Image quality too low

---

## 7.2 Storage Service (Cloudflare R2)

**File:** `app/services/storage.py`

**Functionality:**
- Upload images to R2
- Generate signed URLs
- Organize by bucket paths:
  - `/uploads/{preview_id}/` - Original photos
  - `/previews/{preview_id}/` - Watermarked previews
  - `/final/{order_id}/` - HQ images and PDFs

**Interface:**
```python
class StorageService:
    async def upload_image(
        self, 
        image_bytes: bytes, 
        path: str,
        content_type: str = "image/jpeg"
    ) -> str:
        """Upload image and return public URL"""
        pass
    
    async def upload_pdf(
        self, 
        pdf_bytes: bytes, 
        path: str
    ) -> str:
        """Upload PDF and return URL"""
        pass
    
    def generate_signed_url(
        self, 
        path: str, 
        expires_in: int = 3600
    ) -> str:
        """Generate time-limited signed URL"""
        pass
    
    async def delete_path(self, path_prefix: str) -> None:
        """Delete all objects under a path prefix"""
        pass
```

---

## 7.3 PDF Generator Service

**File:** `app/services/pdf_generator.py`

**Functionality:**
- Generate print-ready PDFs using WeasyPrint
- Include all story pages with images and text
- Support 8"x8" book format
- Add cover page and back page

**Interface:**
```python
class PDFGeneratorService:
    async def generate_storybook_pdf(
        self,
        pages: list[dict],  # [{image_url, story_text, page_number}]
        title: str,
        child_name: str,
        theme: str
    ) -> bytes:
        """Generate complete storybook PDF"""
        pass
```

---

# 8. AI PIPELINE SERVICES

## 8.1 Google Imagen 3 Service

**File:** `app/ai/google_imagen.py`

**API Details:**
```
Endpoint: https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:generateImages
Method: POST
Auth: x-goog-api-key header
```

**Interface:**
```python
class GoogleImagenService:
    async def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "3:4",
        negative_prompt: str = None
    ) -> bytes:
        """
        Generate image using Imagen 3.
        
        Returns: Image bytes (PNG)
        Raises: ImageGenerationError on failure
        """
        pass
```

**Request Format:**
```json
{
    "prompt": "string",
    "number_of_images": 1,
    "aspect_ratio": "3:4",
    "safety_filter_level": "block_few",
    "person_generation": "allow_all"
}
```

**Response Format:**
```json
{
    "generated_images": [
        {
            "image": {
                "image_bytes": "base64_encoded_data"
            }
        }
    ]
}
```

---

## 8.2 Fal.ai Face Swap Service

**File:** `app/ai/fal_face_swap.py`

**API Details:**
```
Endpoint: https://queue.fal.run/fal-ai/face-swap
Method: POST
Auth: Authorization: Key {FAL_API_KEY}
```

**Interface:**
```python
class FalFaceSwapService:
    async def swap_face(
        self,
        base_image_url: str,
        face_image_url: str
    ) -> str:
        """
        Swap face onto base image.
        
        Args:
            base_image_url: URL of generated illustration
            face_image_url: URL of child's photo
            
        Returns: URL of result image
        Raises: FaceSwapError on failure
        """
        pass
```

**Request Format:**
```json
{
    "base_image_url": "https://...",
    "swap_image_url": "https://..."
}
```

**Response Format:**
```json
{
    "image": {
        "url": "https://...",
        "content_type": "image/png"
    }
}
```

---

## 8.3 Fal.ai Flux PuLID Service

**File:** `app/ai/fal_pulid.py`

**API Details:**
```
Endpoint: https://queue.fal.run/fal-ai/flux-pulid
Method: POST
Auth: Authorization: Key {FAL_API_KEY}
```

**Interface:**
```python
class FalPulidService:
    async def generate_with_face(
        self,
        prompt: str,
        reference_image_url: str,
        seed: int = 42,
        guidance_scale: float = 7.5,
        num_steps: int = 30,
        id_weight: float = 0.85
    ) -> str:
        """
        Generate image with embedded face from reference.
        
        Returns: URL of generated image
        Raises: GenerationError on failure
        """
        pass
```

**Request Format:**
```json
{
    "prompt": "string",
    "reference_images": ["https://..."],
    "num_inference_steps": 30,
    "guidance_scale": 7.5,
    "seed": 42,
    "id_weight": 0.85,
    "num_images": 1
}
```

**Response Format:**
```json
{
    "images": [
        {
            "url": "https://...",
            "content_type": "image/png"
        }
    ]
}
```

---

## 8.4 Artistic Pipeline (Imagen 3 + Face Swap)

**File:** `app/ai/artistic_pipeline.py`

**Pipeline Flow:**
```
1. Generate base illustration with Imagen 3 (generic child)
2. Upload base illustration to R2
3. Swap face using Fal.ai Face Swap
4. Download and store final image
5. Apply watermark (if preview)
```

**Interface:**
```python
class ArtisticPipeline:
    def __init__(
        self,
        imagen_service: GoogleImagenService,
        face_swap_service: FalFaceSwapService,
        storage_service: StorageService
    ):
        pass
    
    async def generate_page(
        self,
        prompt: str,
        child_photo_url: str,
        output_path: str,
        apply_watermark: bool = False
    ) -> dict:
        """
        Generate single page with artistic style.
        
        Returns: {
            "image_url": "https://...",
            "generation_time_ms": 5000
        }
        """
        pass
    
    async def generate_book(
        self,
        pages_config: list[dict],  # [{prompt, story_text, page_number}]
        child_photo_url: str,
        preview_id: str,
        is_preview: bool = True
    ) -> list[dict]:
        """
        Generate all pages for a book.
        
        Returns: List of page results
        """
        pass
```

---

## 8.5 Photorealistic Pipeline (Flux PuLID)

**File:** `app/ai/realistic_pipeline.py`

**Pipeline Flow:**
```
1. Generate image with face embedded using Flux PuLID
2. Download and store image
3. Apply watermark (if preview)
```

**Interface:**
```python
class RealisticPipeline:
    def __init__(
        self,
        pulid_service: FalPulidService,
        storage_service: StorageService
    ):
        pass
    
    async def generate_page(
        self,
        prompt: str,
        child_photo_url: str,
        output_path: str,
        seed: int = 42,
        apply_watermark: bool = False
    ) -> dict:
        """
        Generate single page with photorealistic style.
        
        Returns: {
            "image_url": "https://...",
            "generation_time_ms": 3000
        }
        """
        pass
    
    async def generate_book(
        self,
        pages_config: list[dict],
        child_photo_url: str,
        preview_id: str,
        is_preview: bool = True,
        seed: int = 42
    ) -> list[dict]:
        """Generate all pages for a book."""
        pass
```

---

# 9. QUEUE SYSTEM (CELERY)

## 9.1 Celery Configuration

**File:** `app/workers/celery_app.py`

```python
from celery import Celery
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "zelavo_workers",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task settings
    task_soft_time_limit=300,  # 5 minutes soft limit
    task_time_limit=600,       # 10 minutes hard limit
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Retry settings
    task_default_retry_delay=60,
    task_max_retries=3,
    
    # Queue settings
    task_routes={
        "app.workers.tasks.generate_preview": {"queue": "preview"},
        "app.workers.tasks.generate_full_book": {"queue": "full_book"},
        "app.workers.tasks.create_pdf": {"queue": "pdf"},
    }
)
```

## 9.2 Task Definitions

**File:** `app/workers/tasks.py`

```python
"""
Celery background tasks for AI generation.
"""

@celery_app.task(bind=True, max_retries=2, soft_time_limit=600)
def generate_full_preview(
    self,
    job_id: str,
    preview_id: str,
    photo_url: str,
    child_name: str,
    child_age: int,
    child_gender: str,
    theme: str,
    style: str  # "artistic" or "photorealistic"
) -> dict:
    """
    Generate ALL 10 HIGH-RES pages upfront + 5 watermarked previews.
    
    This is the main generation task - runs when user submits form.
    All 10 images are generated immediately and stored.
    
    Steps:
    1. Generate pages 1-10 (high-res) → save to /final/{preview_id}/
    2. Create watermarked low-res versions of pages 1-5 → save to /previews/{preview_id}/
    3. Update database with all URLs
    """
    pass


@celery_app.task(bind=True, max_retries=2)
def generate_pdf(
    self,
    order_id: str,
    preview_id: str
) -> dict:
    """
    Generate PDF from EXISTING high-res images after payment.
    
    Images already exist in /final/{preview_id}/ - no new AI generation needed.
    
    Steps:
    1. Download all 10 images from /final/{preview_id}/
    2. Get story text for all pages
    3. Generate PDF with WeasyPrint
    4. Upload PDF to /final/{preview_id}/book.pdf
    5. Delete /previews/{preview_id}/ (no longer needed)
    6. Send download email
    """
    pass


@celery_app.task
def cleanup_expired_previews() -> dict:
    """
    Daily cleanup of expired previews (run via Celery Beat).
    
    Deletes all storage folders for previews that:
    - Expired (past 7 days)
    - Were NOT purchased
    """
    pass


@celery_app.task
def send_download_email(
    order_id: str,
    customer_email: str,
    download_url: str
) -> None:
    """Send download link to customer."""
    pass
```

## 9.3 Running Workers

```bash
# Start preview worker
celery -A app.workers.celery_app worker -Q preview -c 2 --loglevel=info

# Start full book worker
celery -A app.workers.celery_app worker -Q full_book -c 2 --loglevel=info

# Start PDF worker
celery -A app.workers.celery_app worker -Q pdf -c 1 --loglevel=info

# Start all workers (development)
celery -A app.workers.celery_app worker -Q preview,full_book,pdf -c 4 --loglevel=info
```

---

# 10. STORY TEMPLATES

## 10.1 Template Structure

**File:** `app/stories/templates.py`

```python
"""
Story template structure and base classes.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PageTemplate:
    page_number: int
    scene_description: str
    artistic_prompt: str      # For Imagen 3
    realistic_prompt: str     # For Flux PuLID
    story_text: str           # Text with {name} placeholder
    costume: Optional[str] = None


@dataclass
class StoryTemplate:
    theme_id: str
    title_template: str       # "{name}'s Magical Adventure"
    description: str
    default_costume: str
    protagonist_description: str
    pages: list[PageTemplate]
    
    def get_title(self, child_name: str) -> str:
        return self.title_template.format(name=child_name)
    
    def get_page_prompt(
        self, 
        page_number: int, 
        style: str,
        child_name: str,
        child_age: int,
        child_gender: str
    ) -> str:
        """Get formatted prompt for a specific page and style."""
        pass
```

## 10.2 Magic Castle Theme

**File:** `app/stories/themes/magic_castle.py`

```python
"""
Magic Castle theme - 10 page story about first day at magic school.
"""

MAGIC_CASTLE_THEME = StoryTemplate(
    theme_id="magic_castle",
    title_template="{name}'s First Day of Magic",
    description="A magical adventure at the Grand Academy of Arcane Arts",
    default_costume="purple wizard robe with gold star embroidery",
    protagonist_description="bright expressive eyes, curious and brave expression",
    pages=[
        PageTemplate(
            page_number=1,
            scene_description="Arrival at the magic school gates",
            artistic_prompt="""
A breathtaking wide establishing shot of a magical scene. A {age}-year-old {gender} child 
stands in the lower left of the frame, looking up in wonder at massive gothic castle gates 
made of dark iron with glowing purple magical runes. The child wears a {costume}. 
Their expression shows excitement and wonder with wide sparkling eyes.

On a tall stone pedestal to the right of the gate perches a giant majestic brown owl 
with large round brass reading glasses and a small black graduation cap, looking down wisely.

Morning golden hour lighting with sun rays breaking through mist. Magical sparkles float 
in the air. Ancient oak trees frame the scene. Cobblestone path leads to the gates.

Professional children's comic book illustration style, bold black ink outlines, 
cel-shaded flat coloring, vibrant saturated colors, Marvel meets Pixar aesthetic, 
dramatic cinematic lighting, dynamic composition.
            """,
            realistic_prompt="""
Cinematic photograph of a {age}-year-old {gender} child with the exact face from the 
reference photo, standing before massive ornate iron gates of an ancient magical castle. 
The child wears a {costume}, looking up with wonder and excitement.

A large majestic owl with round glasses perches on a stone pillar beside the gates.
Morning golden hour lighting, mist swirling at ground level, sun rays through ancient trees.

Ultra-realistic cinematic photography, professional DSLR quality, shallow depth of field, 
8K resolution, movie still aesthetic, magical atmosphere.
            """,
            story_text="""
The morning mist clung to the cobblestones as {name} finally arrived at the Grand Academy 
of Arcane Arts. Standing before the massive iron gates, heart pounding with excitement, 
{name} couldn't believe this was really happening.

"Only the worthy may pass," hooted Professor Hoot from his pedestal, adjusting his spectacles.
            """,
            costume="heavy velvet traveling cloak in deep purple with gold trim and a pointed wizard hat"
        ),
        # ... Pages 2-10 follow same structure
    ]
)
```

---

# 11. WEBHOOK HANDLERS

## 11.1 Shopify Webhook Security

**File:** `app/core/security.py`

```python
"""
Security utilities for webhook verification and signed URLs.
"""

import hmac
import hashlib
import base64
from fastapi import Request, HTTPException


async def verify_shopify_webhook(request: Request, secret: str) -> bool:
    """
    Verify Shopify webhook HMAC signature.
    
    CRITICAL: Must read raw body before any parsing.
    """
    # Get signature from header
    shopify_hmac = request.headers.get("X-Shopify-Hmac-Sha256")
    if not shopify_hmac:
        raise HTTPException(status_code=401, detail="Missing HMAC signature")
    
    # Get raw body
    body = await request.body()
    
    # Compute expected signature
    computed_hmac = base64.b64encode(
        hmac.new(
            secret.encode("utf-8"),
            body,
            hashlib.sha256
        ).digest()
    ).decode("utf-8")
    
    # Compare signatures
    if not hmac.compare_digest(computed_hmac, shopify_hmac):
        raise HTTPException(status_code=401, detail="Invalid HMAC signature")
    
    return True


def verify_shop_domain(request: Request, expected_domain: str) -> bool:
    """Verify webhook came from expected shop."""
    shop_domain = request.headers.get("X-Shopify-Shop-Domain")
    if shop_domain != expected_domain:
        raise HTTPException(status_code=401, detail="Invalid shop domain")
    return True
```

## 11.2 Webhook Endpoint

**File:** `app/api/webhooks/shopify.py`

```python
"""
Shopify webhook handlers.
"""

@router.post("/order-paid")
async def handle_order_paid(request: Request):
    """
    Handle Shopify orders/paid webhook.
    
    Flow:
    1. Verify HMAC signature
    2. Verify shop domain
    3. Check idempotency (order not already processed)
    4. Extract preview_id from line item properties
    5. Create order record
    6. Queue full book generation
    7. Return 200 immediately
    """
    pass
```

---

# 12. ERROR HANDLING & RETRY LOGIC

## 12.1 Custom Exceptions

**File:** `app/core/exceptions.py`

```python
"""
Custom exception classes.
"""

class ZelavoBaseException(Exception):
    """Base exception for all Zelavo errors."""
    def __init__(self, message: str, code: str, details: dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)


class FaceValidationError(ZelavoBaseException):
    """Raised when face validation fails."""
    pass


class ImageGenerationError(ZelavoBaseException):
    """Raised when AI image generation fails."""
    pass


class FaceSwapError(ZelavoBaseException):
    """Raised when face swap fails."""
    pass


class StorageError(ZelavoBaseException):
    """Raised when storage operations fail."""
    pass


class WebhookVerificationError(ZelavoBaseException):
    """Raised when webhook verification fails."""
    pass


class RateLimitExceededError(ZelavoBaseException):
    """Raised when rate limit is exceeded."""
    pass


class OrderNotFoundError(ZelavoBaseException):
    """Raised when order is not found."""
    pass
```

## 12.2 Retry Configuration

```python
"""
Retry settings for different operations.
"""

RETRY_CONFIG = {
    "imagen_generation": {
        "max_retries": 3,
        "backoff_seconds": [30, 60, 120],
        "retry_on": ["timeout", "rate_limit", "server_error"]
    },
    "face_swap": {
        "max_retries": 2,
        "backoff_seconds": [15, 30],
        "retry_on": ["timeout", "server_error"]
    },
    "pulid_generation": {
        "max_retries": 3,
        "backoff_seconds": [30, 60, 120],
        "retry_on": ["timeout", "rate_limit", "server_error"]
    },
    "storage_upload": {
        "max_retries": 3,
        "backoff_seconds": [5, 10, 20],
        "retry_on": ["timeout", "connection_error"]
    }
}
```

---

# 13. TESTING REQUIREMENTS

## 13.1 Test Structure

```
tests/
├── conftest.py              # Fixtures and test configuration
├── test_upload.py           # Photo upload tests
├── test_face_validation.py  # Face detection tests
├── test_preview.py          # Preview generation tests
├── test_pipelines.py        # AI pipeline tests
├── test_webhooks.py         # Webhook handler tests
├── test_storage.py          # R2 storage tests
└── test_pdf.py              # PDF generation tests
```

## 13.2 Required Test Cases

### Upload Tests
- [ ] Valid photo uploads successfully
- [ ] Rejects files over 10MB
- [ ] Rejects non-image files
- [ ] Rejects photos with no face
- [ ] Rejects photos with multiple faces
- [ ] Rate limiting works correctly

### Preview Tests
- [ ] Preview generation queues successfully
- [ ] Status endpoint returns correct progress
- [ ] Completed preview data is correct
- [ ] Preview expires after 7 days
- [ ] Watermarks are applied

### Pipeline Tests
- [ ] Artistic pipeline generates 2 pages
- [ ] Photorealistic pipeline generates 2 pages
- [ ] Face is consistent across pages
- [ ] Handles API errors gracefully
- [ ] Retries on transient failures

### Webhook Tests
- [ ] Valid HMAC passes verification
- [ ] Invalid HMAC is rejected
- [ ] Wrong shop domain is rejected
- [ ] Duplicate orders are handled (idempotency)
- [ ] Full book generation is queued

---

# 14. DEPLOYMENT CONFIGURATION

## 14.1 Render Configuration

**File:** `render.yaml`

```yaml
services:
  # Main API
  - type: web
    name: zelavo-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    envVars:
      - key: APP_ENV
        value: production
      # ... other env vars from Render dashboard
    autoDeploy: true
    
  # Celery Worker
  - type: worker
    name: zelavo-worker
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: celery -A app.workers.celery_app worker -Q preview,full_book,pdf -c 4 --loglevel=info
    envVars:
      # ... same env vars as API
```

## 14.2 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for WeasyPrint and MediaPipe
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 14.3 docker-compose.yml (Development)

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - .:/app
    depends_on:
      - redis
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  worker:
    build: .
    env_file:
      - .env
    volumes:
      - .:/app
    depends_on:
      - redis
    command: celery -A app.workers.celery_app worker -Q preview,full_book,pdf -c 2 --loglevel=info

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

---

# 15. IMPLEMENTATION ORDER

## Phase 1: Foundation (Do First)
1. [ ] Set up project structure
2. [ ] Implement `config.py` with settings
3. [ ] Set up Supabase and create tables
4. [ ] Implement basic FastAPI app with health check
5. [ ] Implement storage service (Cloudflare R2)

## Phase 2: Core Features
6. [ ] Implement face validation service
7. [ ] Implement upload endpoint
8. [ ] Implement Google Imagen 3 service
9. [ ] Implement Fal.ai Face Swap service
10. [ ] Implement Fal.ai PuLID service

## Phase 3: Pipelines
11. [ ] Implement Artistic Pipeline
12. [ ] Implement Photorealistic Pipeline
13. [ ] Create story templates (at least magic_castle)
14. [ ] Implement watermark service

## Phase 4: Main Generation Flow
15. [ ] Set up Celery with Redis
16. [ ] Implement `generate_full_preview` task (10 high-res + 5 watermarked)
17. [ ] Implement preview endpoints (POST /api/preview, GET /api/preview/{id})
18. [ ] Implement status endpoint (GET /api/preview-status/{job_id})

## Phase 5: Payment Integration
19. [ ] Implement webhook security (HMAC verification)
20. [ ] Implement Shopify webhook handler
21. [ ] Implement `generate_pdf` task (from existing images)
22. [ ] Implement download endpoint

## Phase 6: User Account Features
23. [ ] Implement GET /api/my-previews endpoint
24. [ ] Implement preview expiry logic

## Phase 7: Cleanup & Polish
25. [ ] Implement `cleanup_expired_previews` scheduled task
26. [ ] Add comprehensive error handling
27. [ ] Add rate limiting
28. [ ] Write tests
29. [ ] Set up deployment configuration

---

# 16. QUICK REFERENCE

## API Base URL
```
Production: https://api.zelavokids.com
Development: http://localhost:8000
```

## Key Endpoints
```
POST   /api/upload-photo          # Upload child photo
POST   /api/preview               # Start preview generation
GET    /api/preview-status/{id}   # Check generation status
GET    /api/preview/{id}          # Get preview data
GET    /api/download/{order_id}   # Get download link
POST   /webhooks/shopify/order-paid  # Payment webhook
```

## External APIs
```
Google Imagen 3:  https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:generateImages
Fal Face Swap:    https://queue.fal.run/fal-ai/face-swap
Fal Flux PuLID:   https://queue.fal.run/fal-ai/flux-pulid
```

## Storage Paths
```
/uploads/{preview_id}/photo.jpg     # Original child photo
/previews/{preview_id}/page_1.jpg   # Watermarked preview images
/final/{order_id}/page_1.jpg        # HQ final images
/final/{order_id}/book.pdf          # Final PDF
```

---

**END OF IMPLEMENTATION PLAN**

*Ready for Claude Code to implement*
