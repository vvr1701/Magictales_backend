# ZELAVO KIDS - IMAGE GENERATION & STORAGE FLOW
## Addendum to Backend Implementation Plan

**Purpose:** Define the exact image generation, storage, and access flow
**Version:** 2.0 (Final)
**Approach:** Generate All 10 Images Upfront

---

# GENERATION STRATEGY

## The Flow (User's Requirements)

```
1. User submits form with photo + preferences
2. Generate ALL 10 pages in HIGH-RES immediately
3. Store high-res images in /final/{preview_id}/
4. Create watermarked LOW-RES versions of first 5 pages
5. Store watermarked versions in /previews/{preview_id}/
6. Show 5 watermarked preview pages to user
7. User has 7 days to purchase
8. After payment → Grant access to /final/{preview_id}/ (already exists)
9. No payment in 7 days → Delete both /final/ and /previews/ folders
```

## Benefits of This Approach

| Benefit | Description |
|---------|-------------|
| **Instant delivery after payment** | Images already exist, no waiting |
| **Simpler logic** | No partial generation, no continuation |
| **Better preview** | User sees 5 pages, more compelling |
| **Single generation job** | One task handles everything |

## Cost Analysis

| Scenario | AI Cost |
|----------|---------|
| Every preview generated | ₹38.00 (10 images × ₹3.80) |
| User purchases | ₹38.00 total |
| User doesn't purchase | ₹38.00 lost |

**Note:** This approach works best with good conversion rates. The upfront investment creates urgency and better preview quality.

---

# STORAGE STRUCTURE

```
Cloudflare R2 Bucket:
/
├── uploads/
│   └── {preview_id}/
│       └── photo.jpg                    # Original child photo
│
├── final/
│   └── {preview_id}/
│       ├── page_01.jpg                  # HIGH-RES page 1
│       ├── page_02.jpg                  # HIGH-RES page 2
│       ├── page_03.jpg                  # HIGH-RES page 3
│       ├── page_04.jpg                  # HIGH-RES page 4
│       ├── page_05.jpg                  # HIGH-RES page 5
│       ├── page_06.jpg                  # HIGH-RES page 6
│       ├── page_07.jpg                  # HIGH-RES page 7
│       ├── page_08.jpg                  # HIGH-RES page 8
│       ├── page_09.jpg                  # HIGH-RES page 9
│       ├── page_10.jpg                  # HIGH-RES page 10
│       └── book.pdf                     # Generated after payment
│
└── previews/
    └── {preview_id}/
        ├── page_01_preview.jpg          # LOW-RES + WATERMARK
        ├── page_02_preview.jpg          # LOW-RES + WATERMARK
        ├── page_03_preview.jpg          # LOW-RES + WATERMARK
        ├── page_04_preview.jpg          # LOW-RES + WATERMARK
        └── page_05_preview.jpg          # LOW-RES + WATERMARK
```

---

# COMPLETE FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        USER SUBMITS FORM                                 │
│         (photo, child_name, age, gender, theme, style)                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     STEP 1: VALIDATE & QUEUE                             │
│                                                                          │
│  • Validate face in uploaded photo (MediaPipe)                           │
│  • Create preview record in database (status: 'generating')              │
│  • Upload photo to /uploads/{preview_id}/photo.jpg                       │
│  • Create job record (status: 'queued')                                  │
│  • Start FastAPI BackgroundTask: generate_full_preview                   │
│  • Return job_id to frontend for polling                                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│            STEP 2: GENERATE ALL 10 HIGH-RES PAGES (Worker)               │
│                                                                          │
│  For page_num in 1 to 10:                                                │
│    • Get prompt from story template for this page                        │
│    • Call AI pipeline (Artistic OR Photorealistic based on style)        │
│    • Save HIGH-RES image to /final/{preview_id}/page_{NN}.jpg            │
│    • Update job progress (10%, 20%, 30%... 100%)                         │
│                                                                          │
│  Time: ~2-3 minutes for all 10 pages                                     │
│  AI Cost: 10 × ₹3.80 = ₹38.00                                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│          STEP 3: CREATE WATERMARKED PREVIEWS (Worker - Same Job)         │
│                                                                          │
│  For page_num in 1 to 5:                                                 │
│    • Download high-res from /final/{preview_id}/page_{NN}.jpg            │
│    • Resize to 800px width (low resolution)                              │
│    • Apply diagonal watermark: "PREVIEW - zelavokids.com"                │
│    • Add subtle opacity overlay                                          │
│    • Save to /previews/{preview_id}/page_{NN}_preview.jpg                │
│                                                                          │
│  Cost: FREE (just image processing, no AI)                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   STEP 4: UPDATE DATABASE                                │
│                                                                          │
│  UPDATE previews SET                                                     │
│    status = 'active',                                                    │
│    hires_images = JSON array of all 10 high-res URLs,                    │
│    preview_images = JSON array of 5 watermarked preview URLs,            │
│    expires_at = NOW() + INTERVAL '7 days'                                │
│                                                                          │
│  UPDATE jobs SET                                                         │
│    status = 'completed',                                                 │
│    progress = 100                                                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    STEP 5: USER VIEWS PREVIEW                            │
│                                                                          │
│  Frontend calls GET /api/preview/{preview_id}                            │
│  Response includes:                                                      │
│    • 5 watermarked preview image URLs (low-res)                          │
│    • Story text for all 10 pages (text is free to show)                  │
│    • Total pages: 10                                                     │
│    • Message: "Purchase to unlock all 10 pages in full quality"          │
│    • Shopify checkout URL with preview_id                                │
│    • Expiry warning: "Preview expires in X days"                         │
│                                                                          │
│  User can revisit this preview for 7 days                                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
┌─────────────────────────────────┐ ┌─────────────────────────────────────┐
│     USER DOESN'T PAY            │ │          USER PAYS                  │
│     (within 7 days)             │ │                                     │
│                                 │ │  Shopify sends webhook              │
│  Daily cron job checks:         │ │                                     │
│  • Find expired previews        │ │                                     │
│  • Delete /final/{preview_id}/  │ │                                     │
│  • Delete /previews/{preview_id}│ │                                     │
│  • Delete /uploads/{preview_id}/│ │                                     │
│  • Update status = 'expired'    │ │                                     │
│                                 │ │                                     │
│  Loss: ₹38.00                   │ │                                     │
└─────────────────────────────────┘ └──────────────┬──────────────────────┘
                                                   │
                                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  STEP 6: PROCESS PAYMENT WEBHOOK                         │
│                                                                          │
│  POST /webhooks/shopify/order-paid                                       │
│                                                                          │
│  1. Verify HMAC signature (security)                                     │
│  2. Verify shop domain matches                                           │
│  3. Extract preview_id from line item properties                         │
│  4. Check preview exists and is not expired                              │
│  5. Check idempotency (order not already processed)                      │
│  6. Create order record:                                                 │
│     • order_id = Shopify order ID                                        │
│     • preview_id = linked preview                                        │
│     • customer_email = from webhook                                      │
│     • status = 'paid'                                                    │
│  7. Queue PDF generation task                                            │
│  8. Return 200 immediately                                               │
└─────────────────────────────────────────────────────────────────────────┘
                                                   │
                                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   STEP 7: GENERATE PDF (Worker)                          │
│                                                                          │
│  1. Get preview record and all 10 high-res image URLs                    │
│  2. Download all images from /final/{preview_id}/                        │
│  3. Get story text for all 10 pages                                      │
│  4. Generate PDF using WeasyPrint:                                       │
│     • Cover page with title and child's name                             │
│     • 10 story pages with image + text                                   │
│     • Back cover with credits                                            │
│  5. Upload PDF to /final/{preview_id}/book.pdf                           │
│  6. Update order record:                                                 │
│     • status = 'completed'                                               │
│     • pdf_url = signed URL                                               │
│     • completed_at = NOW()                                               │
│  7. Update preview status = 'purchased'                                  │
│  8. Extend expiry to 30 days (for re-downloads)                          │
└─────────────────────────────────────────────────────────────────────────┘
                                                   │
                                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   STEP 8: NOTIFY CUSTOMER                                │
│                                                                          │
│  • Send email with download link                                         │
│  • Include: PDF download, individual image downloads                     │
│  • Links valid for 30 days                                               │
│  • Customer can also access from "My Orders" page                        │
└─────────────────────────────────────────────────────────────────────────┘
                                                   │
                                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   STEP 9: CLEANUP PREVIEW FILES                          │
│                                                                          │
│  After successful purchase:                                              │
│  • Delete /previews/{preview_id}/ (watermarked no longer needed)         │
│  • Keep /final/{preview_id}/ for 30 days (customer downloads)            │
│  • Keep /uploads/{preview_id}/ for 30 days (support issues)              │
│                                                                          │
│  After 30 days:                                                          │
│  • Delete everything                                                     │
│  • Customer can request regeneration if needed (support ticket)          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

# DATABASE SCHEMA UPDATES

## Previews Table (Updated)

```sql
CREATE TABLE previews (
    id SERIAL PRIMARY KEY,
    preview_id UUID DEFAULT gen_random_uuid() UNIQUE NOT NULL,
    
    -- Session/Customer
    session_id VARCHAR(255),
    customer_id VARCHAR(255),
    customer_email VARCHAR(255),
    
    -- Child details
    child_name VARCHAR(50) NOT NULL,
    child_age INTEGER NOT NULL CHECK (child_age >= 2 AND child_age <= 12),
    child_gender VARCHAR(10) NOT NULL CHECK (child_gender IN ('male', 'female')),
    
    -- Book configuration
    theme VARCHAR(50) NOT NULL,
    style VARCHAR(20) NOT NULL DEFAULT 'artistic',
    
    -- Photo
    photo_url VARCHAR(500) NOT NULL,
    photo_validated BOOLEAN DEFAULT FALSE,
    
    -- Status: pending, generating, active, purchased, expired
    status VARCHAR(20) DEFAULT 'pending',
    
    -- HIGH-RES images (all 10 pages) - stored in /final/
    hires_images JSONB DEFAULT '[]'::jsonb,
    -- Example: [
    --   {"page": 1, "url": "https://.../final/preview_id/page_01.jpg"},
    --   {"page": 2, "url": "https://.../final/preview_id/page_02.jpg"},
    --   ...
    -- ]
    
    -- PREVIEW images (first 5 pages, watermarked) - stored in /previews/
    preview_images JSONB DEFAULT '[]'::jsonb,
    -- Example: [
    --   {"page": 1, "url": "https://.../previews/preview_id/page_01_preview.jpg", "text": "..."},
    --   ...
    -- ]
    
    -- Story text for all pages
    story_pages JSONB DEFAULT '[]'::jsonb,
    -- Example: [
    --   {"page": 1, "text": "The morning mist clung to..."},
    --   {"page": 2, "text": "Only the worthy may pass..."},
    --   ...
    -- ]
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '7 days'),
    
    -- Constraints
    CONSTRAINT valid_theme CHECK (theme IN ('magic_castle', 'space_adventure', 'underwater', 'forest_friends')),
    CONSTRAINT valid_style CHECK (style IN ('artistic', 'photorealistic'))
);

-- Indexes
CREATE INDEX idx_previews_preview_id ON previews(preview_id);
CREATE INDEX idx_previews_session_id ON previews(session_id);
CREATE INDEX idx_previews_customer_id ON previews(customer_id);
CREATE INDEX idx_previews_status ON previews(status);
CREATE INDEX idx_previews_expires_at ON previews(expires_at);
```

## Orders Table (Updated)

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(100) UNIQUE NOT NULL,  -- Shopify order ID
    order_number VARCHAR(50),                -- Human readable order #
    
    -- Link to preview (this contains all the generated images)
    preview_id UUID REFERENCES previews(preview_id) NOT NULL,
    
    -- Customer
    customer_email VARCHAR(255) NOT NULL,
    customer_name VARCHAR(100),
    
    -- Status: paid, generating_pdf, completed, failed
    status VARCHAR(20) DEFAULT 'paid',
    
    -- PDF
    pdf_url VARCHAR(500),
    pdf_generated_at TIMESTAMP WITH TIME ZONE,
    
    -- For physical book orders
    shipping_address JSONB,
    tracking_number VARCHAR(100),
    shipped_at TIMESTAMP WITH TIME ZONE,
    
    -- Error handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days')
);

-- Indexes
CREATE INDEX idx_orders_order_id ON orders(order_id);
CREATE INDEX idx_orders_preview_id ON orders(preview_id);
CREATE INDEX idx_orders_customer_email ON orders(customer_email);
CREATE INDEX idx_orders_status ON orders(status);
```

---

# API ENDPOINTS

## POST /api/preview (Start Generation)

**Request:**
```json
{
    "photo_url": "https://r2.../uploads/uuid/photo.jpg",
    "child_name": "Arjun",
    "child_age": 6,
    "child_gender": "male",
    "theme": "magic_castle",
    "style": "artistic",
    "session_id": "session_uuid",
    "customer_email": "parent@example.com"
}
```

**Response (202 Accepted):**
```json
{
    "success": true,
    "data": {
        "job_id": "job_uuid",
        "preview_id": "preview_uuid",
        "status": "queued",
        "estimated_time_seconds": 180,
        "message": "Generating your personalized storybook..."
    }
}
```

## GET /api/preview-status/{job_id}

**Response (In Progress):**
```json
{
    "success": true,
    "data": {
        "job_id": "job_uuid",
        "status": "processing",
        "progress": 45,
        "current_step": "Generating page 5 of 10...",
        "pages_completed": 4,
        "total_pages": 10
    }
}
```

**Response (Completed):**
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

## GET /api/preview/{preview_id}

**Response:**
```json
{
    "success": true,
    "data": {
        "preview_id": "preview_uuid",
        "status": "active",
        
        "story_title": "Arjun's First Day of Magic",
        "child_name": "Arjun",
        "theme": "magic_castle",
        "style": "artistic",
        
        "preview_pages": [
            {
                "page_number": 1,
                "image_url": "https://r2.../previews/uuid/page_01_preview.jpg",
                "story_text": "The morning mist clung to the cobblestones...",
                "is_preview": true
            },
            {
                "page_number": 2,
                "image_url": "https://r2.../previews/uuid/page_02_preview.jpg",
                "story_text": "Only the worthy may pass...",
                "is_preview": true
            },
            {
                "page_number": 3,
                "image_url": "https://r2.../previews/uuid/page_03_preview.jpg",
                "story_text": "With a thunderous CLANG...",
                "is_preview": true
            },
            {
                "page_number": 4,
                "image_url": "https://r2.../previews/uuid/page_04_preview.jpg",
                "story_text": "The first class was Beast Taming...",
                "is_preview": true
            },
            {
                "page_number": 5,
                "image_url": "https://r2.../previews/uuid/page_05_preview.jpg",
                "story_text": "The crate EXPLODED open...",
                "is_preview": true
            }
        ],
        
        "locked_pages": [
            {
                "page_number": 6,
                "story_text": "After lunch came the class...",
                "is_locked": true
            },
            {
                "page_number": 7,
                "story_text": "Higher and higher...",
                "is_locked": true
            },
            {
                "page_number": 8,
                "story_text": "The Ancient Library held...",
                "is_locked": true
            },
            {
                "page_number": 9,
                "story_text": "After the library chaos...",
                "is_locked": true
            },
            {
                "page_number": 10,
                "story_text": "As the three moons rose...",
                "is_locked": true
            }
        ],
        
        "total_pages": 10,
        "preview_pages_count": 5,
        "locked_pages_count": 5,
        
        "expires_at": "2024-01-15T00:00:00Z",
        "days_remaining": 6,
        
        "purchase": {
            "price": 499,
            "currency": "INR",
            "price_formatted": "₹499",
            "checkout_url": "https://zelavokids.myshopify.com/cart/add?id=VARIANT_ID&properties[preview_id]=preview_uuid"
        }
    }
}
```

## GET /api/my-previews (For Logged-in Users)

**Response:**
```json
{
    "success": true,
    "data": {
        "previews": [
            {
                "preview_id": "uuid-1",
                "story_title": "Arjun's First Day of Magic",
                "theme": "magic_castle",
                "thumbnail_url": "https://r2.../previews/uuid-1/page_01_preview.jpg",
                "status": "active",
                "expires_at": "2024-01-15T00:00:00Z",
                "days_remaining": 6,
                "created_at": "2024-01-08T10:30:00Z",
                "is_purchased": false
            },
            {
                "preview_id": "uuid-2",
                "story_title": "Arjun's Space Adventure",
                "theme": "space_adventure",
                "thumbnail_url": "https://r2.../previews/uuid-2/page_01_preview.jpg",
                "status": "purchased",
                "created_at": "2024-01-05T14:20:00Z",
                "is_purchased": true,
                "order_id": "order_123"
            }
        ]
    }
}
```

## GET /api/download/{order_id}

**Response (Ready):**
```json
{
    "success": true,
    "data": {
        "status": "ready",
        "downloads": {
            "pdf": {
                "url": "https://r2.../final/preview_id/book.pdf?signature=xxx",
                "filename": "Arjuns_First_Day_of_Magic.pdf",
                "size_mb": 15.2,
                "expires_in_seconds": 3600
            },
            "images": [
                {
                    "page": 1,
                    "url": "https://r2.../final/preview_id/page_01.jpg?signature=xxx",
                    "filename": "page_01.jpg"
                },
                {
                    "page": 2,
                    "url": "https://r2.../final/preview_id/page_02.jpg?signature=xxx",
                    "filename": "page_02.jpg"
                }
                // ... pages 3-10
            ]
        },
        "expires_at": "2024-02-15T00:00:00Z",
        "days_remaining": 28
    }
}
```

---

# FASTAPI BACKGROUND TASKS (MVP)

> **Note:** For MVP, we use FastAPI's built-in BackgroundTasks instead of Celery + Redis.
> This keeps infrastructure simple and cost-free. Can migrate to Celery later if needed.

## Task 1: generate_full_preview

```python
"""
FILE: app/background/tasks.py
FastAPI background tasks for image generation
"""

import asyncio
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()


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
    """
    Generate ALL 10 high-res pages + 5 watermarked previews.
    
    This runs as a FastAPI BackgroundTask - no external queue needed.
    """
    try:
        await update_job_progress(job_id, 0, "Starting generation...")
        
        # Get story template
        template = get_story_template(theme)
        
        # Select pipeline
        if style == "artistic":
            pipeline = ArtisticPipeline()
        else:
            pipeline = RealisticPipeline()
        
        hires_images = []
        story_pages = []
        
        # ============================================
        # PHASE 1: Generate all 10 HIGH-RES pages
        # ============================================
        for page_num in range(1, 11):
            progress = int((page_num / 10) * 80)  # 0% to 80%
            await update_job_progress(
                job_id, 
                progress, 
                f"Generating page {page_num} of 10..."
            )
            
            # Build prompt for this page
            prompt_data = build_prompt(
                template=template,
                page_number=page_num,
                style=style,
                child_name=child_name,
                child_age=child_age,
                child_gender=child_gender
            )
            
            # Generate high-res image
            output_path = f"final/{preview_id}/page_{page_num:02d}.jpg"
            
            image_url = await pipeline.generate_page(
                prompt=prompt_data["prompt"],
                negative_prompt=prompt_data["negative_prompt"],
                child_photo_url=photo_url,
                output_path=output_path
            )
            
            hires_images.append({
                "page": page_num,
                "url": image_url
            })
            
            # Get story text
            story_text = build_story_text(template, page_num, child_name)
            story_pages.append({
                "page": page_num,
                "text": story_text
            })
        
        # ============================================
        # PHASE 2: Create 5 watermarked previews
        # ============================================
        await update_job_progress(job_id, 85, "Creating preview images...")
        
        preview_images = []
        
        for page_num in range(1, 6):  # Only first 5 pages
            hires_url = hires_images[page_num - 1]["url"]
            preview_path = f"previews/{preview_id}/page_{page_num:02d}_preview.jpg"
            
            preview_url = await create_watermarked_preview(
                source_url=hires_url,
                output_path=preview_path,
                watermark_text="PREVIEW - magictales.com",
                resize_width=800  # Low resolution
            )
            
            preview_images.append({
                "page": page_num,
                "url": preview_url,
                "text": story_pages[page_num - 1]["text"]
            })
        
        # ============================================
        # PHASE 3: Update database
        # ============================================
        await update_job_progress(job_id, 95, "Saving your storybook...")
        
        await update_preview_record(
            preview_id=preview_id,
            status="active",
            hires_images=hires_images,
            preview_images=preview_images,
            story_pages=story_pages,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        
        await update_job_status(job_id, "completed", progress=100)
        
        logger.info(f"Preview generation completed: {preview_id}")
        
    except Exception as e:
        logger.error(f"Generation failed for {preview_id}: {str(e)}")
        await update_job_status(job_id, "failed", error=str(e))
        await update_preview_status(preview_id, "failed")
        # Note: No automatic retry in MVP - user can retry manually
```

## Task 2: generate_pdf

```python
async def generate_pdf(
    order_id: str,
    preview_id: str
):
    """
    Generate PDF from existing high-res images.
    
    Called after payment is confirmed via webhook.
    Images already exist in /final/{preview_id}/
    """
    try:
        await update_order_status(order_id, "generating_pdf")
        
        # Get preview data
        preview = await get_preview_by_id(preview_id)
        
        # Download all high-res images
        images = []
        for img_data in preview.hires_images:
            image_bytes = await download_image(img_data["url"])
            images.append({
                "page": img_data["page"],
                "bytes": image_bytes
            })
        
        # Generate PDF
        pdf_bytes = await generate_storybook_pdf(
            images=images,
            story_pages=preview.story_pages,
            title=f"{preview.child_name}'s First Day of Magic",
            child_name=preview.child_name,
            theme=preview.theme
        )
        
        # Upload PDF
        pdf_path = f"final/{preview_id}/book.pdf"
        pdf_url = await upload_to_r2(pdf_bytes, pdf_path, "application/pdf")
        
        # Update order
        await update_order_record(
            order_id=order_id,
            status="completed",
            pdf_url=pdf_url,
            completed_at=datetime.utcnow()
        )
        
        # Update preview
        await update_preview_status(preview_id, "purchased")
        await extend_preview_expiry(preview_id, days=30)
        
        # Cleanup preview images (watermarked no longer needed)
        await delete_r2_folder(f"previews/{preview_id}/")
        
        # Send email notification (inline for MVP)
        await send_download_email(
            order_id=order_id,
            customer_email=preview.customer_email,
            download_url=pdf_url
        )
        
        logger.info(f"PDF generation completed: {order_id}")
        
    except Exception as e:
        logger.error(f"PDF generation failed for order {order_id}: {str(e)}")
        await update_order_status(order_id, "failed", error=str(e))
```

## Task 3: cleanup_expired_previews (Scheduled via Supabase pg_cron)

For MVP, we use Supabase's built-in `pg_cron` extension instead of Celery Beat.

### Enable pg_cron in Supabase Dashboard:
1. Go to Database → Extensions
2. Enable `pg_cron`

### Schedule the cleanup function:
```sql
-- Create the cleanup function
CREATE OR REPLACE FUNCTION cleanup_expired_previews()
RETURNS void AS $$
BEGIN
    -- Mark expired previews
    UPDATE previews 
    SET status = 'expired' 
    WHERE expires_at < NOW() 
    AND status NOT IN ('purchased', 'expired');
END;
$$ LANGUAGE plpgsql;

-- Schedule to run daily at midnight UTC
SELECT cron.schedule(
    'cleanup-expired-previews',    -- Job name
    '0 0 * * *',                   -- Daily at midnight
    'SELECT cleanup_expired_previews()'
);
```

### API Endpoint for Manual Cleanup (Optional)
```python
@router.post("/admin/cleanup", include_in_schema=False)
async def trigger_cleanup(background_tasks: BackgroundTasks):
    """Manual trigger for cleanup - useful for testing."""
    background_tasks.add_task(cleanup_expired_files)
    return {"message": "Cleanup started"}


async def cleanup_expired_files():
    """
    Delete R2 files for expired previews.
    Called manually or via scheduled endpoint.
    """
    expired_previews = await db.query("""
        SELECT preview_id 
        FROM previews 
        WHERE status = 'expired'
        AND files_deleted = false
    """)
    
    cleaned_count = 0
    
    for preview in expired_previews:
        preview_id = preview["preview_id"]
        
        try:
            # Delete all files from R2
            await delete_r2_folder(f"final/{preview_id}/")
            await delete_r2_folder(f"previews/{preview_id}/")
            await delete_r2_folder(f"uploads/{preview_id}/")
            
            # Mark as cleaned
            await db.execute("""
                UPDATE previews 
                SET files_deleted = true 
                WHERE preview_id = $1
            """, preview_id)
            
            cleaned_count += 1
            logger.info(f"Cleaned up expired preview: {preview_id}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup {preview_id}: {str(e)}")
    
    return {"cleaned": cleaned_count, "total_expired": len(expired_previews)}
```

---

# WATERMARK IMPLEMENTATION

```python
from PIL import Image, ImageDraw, ImageFont
import io


async def create_watermarked_preview(
    source_url: str,
    output_path: str,
    watermark_text: str = "PREVIEW - zelavokids.com",
    resize_width: int = 800
) -> str:
    """
    Download high-res image, resize, apply watermark, upload.
    
    Returns: URL of watermarked preview image
    """
    # Download original
    image_bytes = await download_from_url(source_url)
    img = Image.open(io.BytesIO(image_bytes))
    
    # Resize to low-res (maintain aspect ratio)
    aspect_ratio = img.height / img.width
    new_height = int(resize_width * aspect_ratio)
    img = img.resize((resize_width, new_height), Image.LANCZOS)
    
    # Create watermark overlay
    watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
    
    # Load font (use default if custom not available)
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # Calculate text size and position (diagonal across image)
    text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # Draw diagonal watermarks
    for y in range(-img.height, img.height * 2, 150):
        for x in range(-img.width, img.width * 2, 300):
            # Create rotated text
            txt_img = Image.new('RGBA', (text_width + 20, text_height + 20), (0, 0, 0, 0))
            txt_draw = ImageDraw.Draw(txt_img)
            txt_draw.text((10, 10), watermark_text, font=font, fill=(255, 255, 255, 80))
            txt_img = txt_img.rotate(45, expand=True)
            
            # Paste onto watermark layer
            watermark.paste(txt_img, (x, y), txt_img)
    
    # Combine original with watermark
    img = img.convert('RGBA')
    img = Image.alpha_composite(img, watermark)
    img = img.convert('RGB')
    
    # Save to bytes
    output_buffer = io.BytesIO()
    img.save(output_buffer, format='JPEG', quality=80)
    output_buffer.seek(0)
    
    # Upload to R2
    preview_url = await upload_to_r2(
        output_buffer.getvalue(),
        output_path,
        "image/jpeg"
    )
    
    return preview_url
```

---

# STORAGE RETENTION RULES

| Storage Path | Status | Retention |
|--------------|--------|-----------|
| `/uploads/{preview_id}/` | Active preview | 7 days |
| `/uploads/{preview_id}/` | Purchased | 30 days |
| `/final/{preview_id}/` | Active preview | 7 days |
| `/final/{preview_id}/` | Purchased | 30 days |
| `/previews/{preview_id}/` | Active preview | 7 days |
| `/previews/{preview_id}/` | Purchased | Delete immediately after PDF generated |

---

# CELERY BEAT SCHEDULE

```python
# In celery_app.py

celery_app.conf.beat_schedule = {
    'cleanup-expired-previews': {
        'task': 'app.workers.tasks.cleanup_expired_previews',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM UTC
    },
    'cleanup-expired-orders': {
        'task': 'app.workers.tasks.cleanup_expired_orders',
        'schedule': crontab(hour=4, minute=0),  # Daily at 4 AM UTC
    },
}
```

---

# SUMMARY

| Step | What Happens | Storage Location |
|------|--------------|------------------|
| 1 | User submits form | - |
| 2 | Generate 10 HIGH-RES pages | `/final/{preview_id}/` |
| 3 | Create 5 watermarked LOW-RES | `/previews/{preview_id}/` |
| 4 | User views 5 preview pages | Served from `/previews/` |
| 5a | User doesn't pay (7 days) | DELETE all folders |
| 5b | User pays | Keep `/final/`, DELETE `/previews/` |
| 6 | Generate PDF | `/final/{preview_id}/book.pdf` |
| 7 | User downloads | Served from `/final/` (30 days) |

**Total AI Cost:** ₹38.00 per preview (10 images × ₹3.80)

---

**END OF DOCUMENT**
