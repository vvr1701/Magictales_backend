# Practical Postman Examples - Exact Test Data Used

Based on our successful end-to-end testing, here are the exact endpoints and data you can use in Postman.

## Server Setup
Make sure your FastAPI server is running:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 1. 🏥 Health Check

**GET** `http://localhost:8000/health`

**Headers:**
```
Content-Type: application/json
```

**Expected Response:**
```json
{
    "status": "healthy",
    "timestamp": "2025-12-28T14:46:24.123456Z"
}
```

---

## 2. 📸 Photo Upload

**POST** `http://localhost:8000/api/upload-photo`

**Headers:**
```
(None - Postman auto-sets Content-Type: multipart/form-data)
```

**Body:** Form-data
- Key: `photo` (File type)
- Value: Upload your child photo (we used `/mnt/c/Users/santh/Pictures/Screenshots/Screenshot 2025-12-21 123352.png`)

**Successful Response:**
```json
{
    "photo_id": "acdd7eb2-0d7f-46ce-99c6-bb02d12d5c7b",
    "message": "Photo uploaded and validated successfully",
    "faces_detected": 1,
    "face_area_percentage": 15.2
}
```

**Save this `photo_id` for the next step!**

---

## 3. 🎨 Create Preview

**POST** `http://localhost:8000/api/preview`

**Headers:**
```
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
    "photo_id": "acdd7eb2-0d7f-46ce-99c6-bb02d12d5c7b",
    "child_name": "Alex",
    "theme": "magic_castle",
    "style": "photorealistic"
}
```

**Successful Response:**
```json
{
    "job_id": "preview_generation_acdd7eb2-0d7f-46ce-99c6-bb02d12d5c7b_1735392204",
    "preview_id": "d9b66c39-86d5-4649-8844-836dd9c9c287",
    "estimated_time_minutes": 10,
    "message": "Preview generation started"
}
```

**Save both `job_id` and `preview_id`!**

---

## 4. ⏳ Monitor Preview Generation

**GET** `http://localhost:8000/api/preview-status/{job_id}`

**Example:** `http://localhost:8000/api/preview-status/preview_generation_acdd7eb2-0d7f-46ce-99c6-bb02d12d5c7b_1735392204`

**Headers:**
```
Content-Type: application/json
```

**Response (In Progress):**
```json
{
    "job_id": "preview_generation_acdd7eb2-0d7f-46ce-99c6-bb02d12d5c7b_1735392204",
    "status": "processing",
    "progress": 60,
    "current_step": "Generating page 6/10",
    "estimated_remaining_minutes": 3
}
```

**Response (Completed):**
```json
{
    "job_id": "preview_generation_acdd7eb2-0d7f-46ce-99c6-bb02d12d5c7b_1735392204",
    "status": "completed",
    "progress": 100,
    "preview_id": "d9b66c39-86d5-4649-8844-836dd9c9c287",
    "message": "Preview generated successfully"
}
```

**Keep polling every 10-15 seconds until status = "completed"**

---

## 5. 👀 View Generated Preview

**GET** `http://localhost:8000/api/preview/{preview_id}`

**Example:** `http://localhost:8000/api/preview/d9b66c39-86d5-4649-8844-836dd9c9c287`

**Headers:**
```
Content-Type: application/json
```

**Response Preview:**
```json
{
    "preview_id": "d9b66c39-86d5-4649-8844-836dd9c9c287",
    "status": "active",
    "story_title": "Alex's First Day of Magic",
    "child_name": "Alex",
    "theme": "magic_castle",
    "style": "photorealistic",
    "preview_pages": [
        {
            "page_number": 1,
            "image_url": "https://pub-eab76058d817412b9c6c9726ff8ae49e.r2.dev/previews/d9b66c39-86d5-4649-8844-836dd9c9c287/page_01_preview.jpg",
            "story_text": "The morning mist clung to the cobblestones as Alex finally arrived at the Grand Academy of Arcane Arts...",
            "is_watermarked": true,
            "is_locked": false
        }
        // ... 4 more preview pages
    ],
    "locked_pages": [
        {
            "page_number": 6,
            "story_text": "After lunch came the class Alex had been waiting for...",
            "is_locked": true
        }
        // ... 4 more locked pages (6-10)
    ],
    "purchase": {
        "price": 499,
        "currency": "INR",
        "checkout_url": "https://magictales-2.myshopify.com/cart/add?id=PRODUCT_VARIANT_ID&properties[preview_id]=d9b66c39-86d5-4649-8844-836dd9c9c287"
    }
}
```

---

## 6. 💳 Simulate Shopify Payment (Webhook)

**POST** `http://localhost:8000/webhooks/shopify/order-paid`

**Headers:**
```
Content-Type: application/json
X-Shopify-Hmac-Sha256: 2hvVcW+64vqeNbkCOKhSO7YKk1bODJQ8GlAo1PfG4ns=
X-Shopify-Shop-Domain: magictales-2.myshopify.com
```

**Body (raw JSON) - Use EXACT preview_id from step 5:**
```json
{
    "id": "12345678901234567890",
    "order_number": 1001,
    "created_at": "2025-12-28T10:00:00Z",
    "customer": {
        "id": "123456789",
        "email": "test@example.com",
        "first_name": "John",
        "last_name": "Doe"
    },
    "shipping_address": {
        "first_name": "John",
        "last_name": "Doe",
        "address1": "123 Main St",
        "city": "Test City",
        "province": "Test State",
        "country": "India",
        "zip": "123456"
    },
    "line_items": [
        {
            "id": "987654321",
            "product_id": "123456",
            "title": "Personalized Storybook",
            "quantity": 1,
            "price": "499.00",
            "properties": [
                {
                    "name": "preview_id",
                    "value": "d9b66c39-86d5-4649-8844-836dd9c9c287"
                }
            ]
        }
    ],
    "total_price": "499.00",
    "currency": "INR",
    "financial_status": "paid"
}
```

**Successful Response:**
```json
{
    "success": true,
    "message": "Webhook received and processed"
}
```

**This creates an order and starts PDF generation in the background!**

---

## 7. 📥 Download PDF & Images

**GET** `http://localhost:8000/api/download/{order_id}`

**Example:** `http://localhost:8000/api/download/12345678901234567890`

**Headers:**
```
Content-Type: application/json
```

**Response:**
```json
{
    "status": "ready",
    "downloads": {
        "pdf": {
            "url": "https://8ed51ab5ca6bbb846c3a251f28a86d29.r2.cloudflarestorage.com/magictales-storage/final/d9b66c39-86d5-4649-8844-836dd9c9c287/book.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&...",
            "filename": "Alex_Storybook.pdf",
            "size_mb": 7.6,
            "expires_in_seconds": 3600
        },
        "images": [
            {
                "page": 1,
                "url": "https://8ed51ab5ca6bbb846c3a251f28a86d29.r2.cloudflarestorage.com/magictales-storage/final/d9b66c39-86d5-4649-8844-836dd9c9c287/page_01.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&...",
                "filename": "page_01.jpg"
            }
            // ... all 10 pages
        ]
    },
    "expires_at": "2026-01-27T14:42:59Z",
    "days_remaining": 29
}
```

**You can now download the PDF and individual images using those signed URLs!**

---

## 8. 🧪 Test Webhook (No HMAC)

**POST** `http://localhost:8000/webhooks/shopify/test`

**Headers:**
```
Content-Type: application/json
```

**Body (any JSON):**
```json
{
    "test": "webhook",
    "message": "Testing webhook endpoint"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Test webhook received"
}
```

---

## Complete Testing Flow in Order:

1. **Health Check** ✓
2. **Upload Photo** → Save `photo_id` ✓
3. **Create Preview** → Save `job_id` and `preview_id` ✓
4. **Poll Status** → Wait for completion (8-10 min) ✓
5. **View Preview** → See watermarked pages ✓
6. **Simulate Payment** → Use exact `preview_id` ✓
7. **Download Files** → Get PDF (7.6MB) + 10 images ✓

---

## Important Notes:

### 🔐 HMAC Signature
For the webhook, the HMAC is calculated as:
```
HMAC-SHA256(webhook_secret, raw_json_body)
```
Our test uses a pre-calculated HMAC that works with the test secret.

### ⏱️ Timing
- **Preview Generation**: ~8-10 minutes (generates all 10 high-res images)
- **PDF Generation**: ~2-3 minutes (after payment webhook)
- **Download URLs**: Valid for 1 hour, order valid for 30 days

### 🎨 Model Options
You can test different styles:
- `"style": "artistic"` - Uses Flux.1 + Face Swap
- `"style": "photorealistic"` - Uses Flux PuLID (recommended)

### 🎭 Theme Options
- `"theme": "magic_castle"` - Magic school adventure (fully implemented)
- Other themes in development

---

**💡 Pro Tip:** Use Postman's environment variables to automatically save IDs between requests:

```javascript
// In the "Tests" tab of Upload Photo:
pm.environment.set("photo_id", pm.response.json().photo_id);

// In the "Tests" tab of Create Preview:
pm.environment.set("preview_id", pm.response.json().preview_id);
pm.environment.set("job_id", pm.response.json().job_id);
```

Then use `{{photo_id}}`, `{{preview_id}}`, etc. in subsequent requests!