# Zelavo Kids Backend

AI-powered personalized children's storybook platform backend.

## 🚀 Features

- **Face Validation**: MediaPipe-powered face detection and validation
- **Model-Agnostic AI**: Easy switching between AI models (Flux.1, PuLID, Face Swap)
- **Two Art Styles**: Artistic (illustration) and Photorealistic styles
- **Complete Story Generation**: All 10 pages generated upfront
- **PDF Creation**: High-quality print-ready PDFs
- **Shopify Integration**: Payment webhooks with HMAC verification
- **Cloud Storage**: Cloudflare R2 for scalable file storage

## 🏗️ Architecture

### Core Flow
```
Photo Upload → Face Validation → Generate ALL 10 Pages → Create 5 Watermarked Previews
→ User Views Preview → Payment via Shopify → Generate PDF → Download
```

### Tech Stack
- **Framework**: FastAPI (Python 3.11+)
- **Database**: Supabase (PostgreSQL)
- **Storage**: Cloudflare R2
- **AI Services**: Fal.ai (Flux.1, PuLID, Face Swap)
- **PDF**: WeasyPrint
- **Background Tasks**: FastAPI BackgroundTasks

## 📦 Installation

### Prerequisites
- Python 3.11+
- Supabase account
- Cloudflare R2 account
- Fal.ai API key

### Local Development

1. **Clone and setup**:
```bash
git clone <repository>
cd zelavo-backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

2. **Environment setup**:
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. **Database setup**:
- Execute the SQL schema from `BACKEND_IMPLEMENTATION_PLAN.md` in Supabase
- Enable `pg_cron` extension for cleanup jobs

4. **Run development server**:
```bash
uvicorn app.main:app --reload
```

### Docker Development

```bash
docker-compose up
```

## 🔧 Configuration

### Environment Variables

Key configuration in `.env`:

```env
# Database
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-service-role-key

# Storage
R2_ACCESS_KEY_ID=your-r2-access-key
R2_SECRET_ACCESS_KEY=your-r2-secret-key
R2_BUCKET_NAME=zelavo-storage

# AI Services
FAL_API_KEY=your-fal-ai-api-key

# AI Models (easy switching)
ARTISTIC_BASE_MODEL=flux_dev
REALISTIC_MODEL=flux_pulid

# Shopify
SHOPIFY_WEBHOOK_SECRET=your-webhook-secret
```

### Model Switching

Switch AI models easily via environment variables:

```bash
# Fast model for testing
export ARTISTIC_BASE_MODEL=flux_schnell

# High quality model
export ARTISTIC_BASE_MODEL=flux_dev

# Different realistic model
export REALISTIC_MODEL=instant_id
```

## 📚 API Documentation

### Main Endpoints

- `POST /api/upload-photo` - Upload and validate child photo
- `POST /api/preview` - Start preview generation (returns job_id)
- `GET /api/preview-status/{job_id}` - Poll generation status
- `GET /api/preview/{preview_id}` - Get preview data
- `GET /api/download/{order_id}` - Get download links
- `POST /webhooks/shopify/order-paid` - Payment webhook

### Interactive Docs
Visit `http://localhost:8000/docs` when running locally.

## 🎨 Adding New AI Models

The platform uses a model-agnostic architecture:

1. **Add model config** in `app/ai/model_registry.py`:
```python
"new_model": ModelConfig(
    model_id="new_model",
    endpoint="provider/model",
    model_type=ModelType.BASE_GENERATION,
    cost_per_image=0.03,
    avg_latency_seconds=5,
)
```

2. **Create implementation** in `app/ai/implementations/`:
```python
class NewModelService(BaseGenerationService):
    async def generate(self, prompt: str, **kwargs) -> GenerationResult:
        # Implementation here
```

3. **Register in factory** (`app/ai/factory.py`):
```python
IMPLEMENTATIONS = {
    "new_model": NewModelService,
    # ... existing models
}
```

4. **Switch to new model**:
```bash
export ARTISTIC_BASE_MODEL=new_model
```

## 📖 Adding New Story Themes

1. **Create theme file** in `app/stories/themes/your_theme.py`:
```python
YOUR_THEME = StoryTemplate(
    theme_id="your_theme",
    title_template="{name}'s Adventure",
    description="Description",
    pages=[
        PageTemplate(
            page_number=1,
            artistic_prompt="...",
            realistic_prompt="...",
            story_text="..."
        ),
        # ... 9 more pages
    ]
)
```

2. **Register theme** in `app/stories/themes/__init__.py`:
```python
AVAILABLE_THEMES = {
    "your_theme": YOUR_THEME,
    # ... existing themes
}
```

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Job Status
Monitor generation progress:
```bash
curl http://localhost:8000/api/preview-status/{job_id}
```

### Logs
The application uses structured logging with `structlog`.

## 🚀 Deployment

### Render.com (Recommended)

1. Connect repository to Render
2. Set environment variables in dashboard
3. Deploy using `render.yaml` configuration

### Manual Deployment

1. Build Docker image:
```bash
docker build -t zelavo-backend .
```

2. Run with environment:
```bash
docker run -p 8000:8000 --env-file .env zelavo-backend
```

## 🔐 Security

- **HMAC verification** for Shopify webhooks
- **Signed URLs** for file downloads (1-hour expiry)
- **Rate limiting** (configurable per endpoint)
- **Input validation** with Pydantic
- **Face validation** before processing

## 💰 Cost Structure

| Configuration | Per Book (10 pages) | Notes |
|---------------|-------------------|-------|
| Flux.1 [dev] + Face Swap | ₹33 | Default artistic |
| Flux PuLID | ₹38 | Default realistic |
| Flux Schnell + Face Swap | ₹15 | Fast/testing |

## 🛠️ Development

### Project Structure
```
app/
├── ai/                 # AI services and pipelines
├── api/               # API endpoints
├── background/        # Background tasks
├── core/             # Core utilities
├── models/           # Data models and schemas
├── services/         # Business services
├── stories/          # Story templates
└── main.py          # FastAPI app
```

### Key Files
- `CLAUDE.md` - Guide for Claude Code
- `BACKEND_IMPLEMENTATION_PLAN.md` - Complete specification
- `AI_MODEL_CONFIGURATION.md` - Model configuration guide

## 🐛 Troubleshooting

### Common Issues

1. **Face validation failing**:
   - Check image quality and lighting
   - Ensure exactly one face in photo
   - Verify MediaPipe installation

2. **AI generation errors**:
   - Check Fal.ai API key and credits
   - Verify model availability
   - Check network connectivity

3. **Storage issues**:
   - Verify R2 credentials and permissions
   - Check bucket exists and is accessible
   - Verify endpoint URLs

4. **Webhook issues**:
   - Verify HMAC secret matches Shopify
   - Check webhook URL is accessible
   - Verify shop domain configuration

### Debug Mode
Enable debug logging:
```bash
export APP_DEBUG=true
export ENABLE_MODEL_LOGGING=true
```

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs with debug enabled
3. Consult the specification documents
4. Check model registry for available models

---

**Generated with ❤️ for Zelavo Kids**