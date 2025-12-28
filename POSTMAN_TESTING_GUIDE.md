# Magictales API - Postman Testing Guide

## Overview

This comprehensive Postman collection provides complete testing capabilities for the Magictales API, covering the entire flow from photo upload to PDF download.

## Files Included

- `Magictales_API_Collection.postman_collection.json` - Main collection with all API endpoints
- `Magictales_Environment.postman_environment.json` - Environment variables and configuration
- This guide (`POSTMAN_TESTING_GUIDE.md`)

## Quick Start

### 1. Import into Postman

1. Open Postman
2. Click **Import** in the top-left corner
3. Import both files:
   - `Magictales_API_Collection.postman_collection.json`
   - `Magictales_Environment.postman_environment.json`
4. Select the "Magictales API Environment" in the environment dropdown

### 2. Configure Environment

The environment comes pre-configured with test values, but you can customize:

| Variable | Default | Description |
|----------|---------|-------------|
| `baseUrl` | `http://localhost:8000` | API server URL |
| `test_child_name` | `Emma` | Child's name for testing |
| `test_child_age` | `6` | Child's age (2-12) |
| `test_child_gender` | `female` | Child's gender (`male`/`female`) |
| `test_theme` | `magic_castle` | Story theme |
| `test_email` | `test@magictales.com` | Customer email |

### 3. Start Testing

Ensure your Magictales API server is running on `http://localhost:8000`, then follow the **Complete Testing Flow** below.

## Complete Testing Flow

### 🏥 Step 0: Health Check
**Request:** `Health Check`
- Verifies the API server is running
- **Expected:** Status 200 with `"status": "healthy"`

### 📸 Step 1: Upload Photo
**Request:** `Upload Child Photo`
- Upload a child's photo (JPEG/PNG, max 10MB)
- Photo must contain exactly one clearly visible child's face
- **Auto-populated:** `photo_id`, `photo_url`
- **Expected:** Status 200 with face validation success

### 🎨 Step 2: Create Preview
**Request:** `Create Storybook Preview`
- Uses the `photo_url` from Step 1
- Starts AI generation of personalized storybook
- **Auto-populated:** `job_id`, `preview_id`
- **Expected:** Status 200 with job queued

### ⏳ Step 3: Monitor Preview Generation
**Request:** `Get Preview Generation Status`
- Poll this endpoint every 10-15 seconds
- Monitor progress until `status: "completed"`
- **Expected:** Progress from 0% to 100%
- **Completion time:** ~2-3 minutes

### 🔧 Step 4: Generate PDF (Development)
**Request:** `Generate PDF (Development)`
- **⚠️ Development only** - bypasses payment verification
- Creates order and starts PDF generation
- **Auto-populated:** `order_id`
- **Expected:** Status 200 with order created

### 📊 Step 5: Monitor PDF Generation
**Request:** `Get Order Status (Development)`
- Poll this endpoint to check PDF generation progress
- Wait for `order.status: "completed"`
- **Expected:** Order status progresses to completed

### 📥 Step 6: Download PDF
**Request:** `Download Generated PDF`
- Downloads the final personalized PDF storybook
- **Expected:** Status 200 with download URL and file details

## Collection Features

### 🔄 Auto-Variable Population
The collection automatically extracts and stores values from responses:
- Photo upload → `photo_id`, `photo_url`
- Preview creation → `job_id`, `preview_id`
- PDF generation → `order_id`

### 📊 Progress Monitoring
Built-in console logging shows:
- Request progress and status
- Current step information
- Success/failure indicators
- Variable values for debugging

### ✅ Automated Testing
Each request includes comprehensive tests:
- Response status validation
- Required field presence
- Business logic validation
- Error condition handling

### 🧪 Development Tools
Special development endpoints for testing:
- `/api/dev/info` - API documentation and flow info
- `/api/dev/generate-pdf` - Bypass payment for testing
- `/api/dev/order-status/{order_id}` - Order status tracking

## Available Story Themes

The API supports these themes (update `test_theme` variable):
- `magic_castle` - Magical castle adventure
- `space_adventure` - Space exploration story
- `underwater` - Underwater adventure
- `forest_friends` - Forest animal friends

## Available Styles

- `artistic` (default) - Artistic illustration style
- `photorealistic` - More realistic photo style

## Troubleshooting

### Common Issues

1. **"No photo_url found"**
   - Ensure Step 1 (Upload Photo) completed successfully
   - Check collection variables for `photo_url` value

2. **"Preview not found"**
   - Ensure Step 2 (Create Preview) completed successfully
   - Wait for preview generation to complete in Step 3

3. **"Development endpoints disabled"**
   - Server must be running in development mode
   - Check server environment configuration

4. **Face validation fails**
   - Use clear photos with exactly one child's face
   - Ensure good lighting and face visibility
   - File size must be under 10MB

### Debugging

1. **Check Console Output**
   - Open Postman Console (View → Show Postman Console)
   - Review detailed request/response logging

2. **Verify Variables**
   - Check Environment tab for current variable values
   - Use "Complete Flow Tester" request to see all variables

3. **Server Logs**
   - Check your API server logs for detailed error information

## Request Timing

| Step | Endpoint | Expected Time |
|------|----------|---------------|
| 1 | Upload Photo | 2-5 seconds |
| 2 | Create Preview | 1-2 seconds |
| 3 | Preview Generation | 2-3 minutes |
| 4 | Generate PDF | 1-2 seconds |
| 5 | PDF Generation | 1-2 minutes |
| 6 | Download | 1-2 seconds |

## Production vs Development

### Development Mode
- Uses `/api/dev/generate-pdf` (bypasses payment)
- Uses `/api/dev/order-status` for tracking
- Marked with `is_development_order: true`

### Production Mode
- Would use Shopify webhook integration
- Payment verification required
- Standard order processing flow

## Support

If you encounter issues:
1. Check the server is running and accessible
2. Verify environment variables are set correctly
3. Review console output for detailed error messages
4. Check server logs for backend issues

---

**Happy Testing!** 🎉

This collection provides everything you need to test the complete Magictales API flow. The automated variable management and comprehensive testing make it easy to verify all functionality works as expected.