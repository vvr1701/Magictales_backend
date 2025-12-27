# CLAUDE CODE SETUP FOR ZELAVO KIDS
## Complete Configuration & MCP Setup Guide

---

# 1. CLAUDE CODE CONFIGURATION FILE

Save this as `~/.config/claude-code/config.json` (Linux/Mac) or `%APPDATA%\claude-code\config.json` (Windows):

```json
{
  "mcpServers": {
    
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/home/user/projects/zelavo-backend",
        "/home/user/projects/zelavo-frontend"
      ]
    },

    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "<YOUR_GITHUB_TOKEN>"
      }
    },

    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "<YOUR_SUPABASE_DATABASE_URL>"
      }
    },

    "fetch": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"]
    },

    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },

    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

---

# 2. REQUIRED ENVIRONMENT VARIABLES

Create a `.env.claude` file in your project root for Claude Code to reference:

```env
# ===========================================
# ZELAVO KIDS - ENVIRONMENT CONFIGURATION
# ===========================================

# -----------------
# APP SETTINGS
# -----------------
APP_ENV=development
APP_DEBUG=true
APP_SECRET_KEY=generate-a-secure-32-char-key-here

# -----------------
# DATABASE (Supabase)
# -----------------
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
DATABASE_URL=postgresql://postgres:[password]@db.xxxxx.supabase.co:5432/postgres

# -----------------
# BACKGROUND TASKS (MVP)
# -----------------
# Using FastAPI BackgroundTasks - no external queue needed

# -----------------
# STORAGE (Cloudflare R2)
# -----------------
R2_ACCOUNT_ID=your-cloudflare-account-id
R2_ACCESS_KEY_ID=your-r2-access-key
R2_SECRET_ACCESS_KEY=your-r2-secret-key
R2_BUCKET_NAME=zelavo-storage
R2_PUBLIC_URL=https://pub-xxxxx.r2.dev

# -----------------
# AI SERVICES (Fal.ai)
# -----------------
FAL_API_KEY=your-fal-api-key

# -----------------
# AI MODEL CONFIGURATION
# -----------------
# Artistic Pipeline
ARTISTIC_BASE_MODEL=flux_dev
ARTISTIC_FACE_MODEL=fal_face_swap
ARTISTIC_STYLE=digital_illustration

# Photorealistic Pipeline
REALISTIC_MODEL=flux_pulid

# Fallback Models
FALLBACK_BASE_MODEL=flux_schnell
FALLBACK_FACE_MODEL=fal_face_swap
FALLBACK_REALISTIC_MODEL=instant_id

# Model Settings
DEFAULT_SEED=42
GUIDANCE_SCALE=7.5
NUM_INFERENCE_STEPS=28

# Feature Flags
ENABLE_MODEL_FALLBACK=true
ENABLE_MODEL_LOGGING=true

# -----------------
# SHOPIFY
# -----------------
SHOPIFY_SHOP_DOMAIN=your-store.myshopify.com
SHOPIFY_WEBHOOK_SECRET=your-webhook-secret
SHOPIFY_API_KEY=your-shopify-api-key
SHOPIFY_API_SECRET=your-shopify-api-secret

# -----------------
# RATE LIMITING
# -----------------
RATE_LIMIT_PREVIEWS_PER_DAY=3
RATE_LIMIT_UPLOADS_PER_HOUR=10

# -----------------
# GENERATION SETTINGS
# -----------------
PREVIEW_PAGES=5
FULL_BOOK_PAGES=10
IMAGE_WIDTH=1024
IMAGE_HEIGHT=1365
```

---

# 3. SERVICES SETUP GUIDE

## 3.1 Supabase Setup

1. Go to https://supabase.com and create new project
2. Get credentials from Settings → API:
   - `SUPABASE_URL`: Project URL
   - `SUPABASE_KEY`: service_role key (not anon key)
3. Get Database URL from Settings → Database:
   - `DATABASE_URL`: Connection string (use connection pooler for production)

## 3.2 Background Tasks (MVP)

For MVP, we use FastAPI's built-in BackgroundTasks instead of Celery + Redis.
- No external queue service needed
- No additional setup required
- Background tasks run in the FastAPI process
- Can migrate to Celery + Redis later for scale

## 3.3 Cloudflare R2 Setup

1. Go to Cloudflare Dashboard → R2
2. Create new bucket named "zelavo-storage"
3. Create R2 API token with read/write permissions
4. Enable public access and get public URL

## 3.4 Fal.ai Setup

1. Go to https://fal.ai and create account
2. Get API key from dashboard
3. Add billing info for production usage

## 3.5 GitHub Token

1. Go to GitHub → Settings → Developer Settings → Personal Access Tokens
2. Create token with scopes: `repo`, `workflow`

---

# 4. INSTALLATION COMMANDS

Run these commands to set up the development environment:

```bash
# Create project directory
mkdir -p ~/projects/zelavo-backend
cd ~/projects/zelavo-backend

# Initialize Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Claude Code (if not already installed)
npm install -g @anthropic-ai/claude-code

# Install MCP servers globally
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-postgres
npm install -g @modelcontextprotocol/server-fetch
npm install -g @modelcontextprotocol/server-sequential-thinking
npm install -g @modelcontextprotocol/server-memory

# Create config directory
mkdir -p ~/.config/claude-code

# Copy config file
cp claude_code_config.json ~/.config/claude-code/config.json
```

---

# 5. PROJECT INITIALIZATION PROMPT

Use this prompt to start Claude Code with the project:

```
I'm building a personalized children's storybook platform called "Zelavo Kids".

Please read and implement the backend using these specification documents:
1. BACKEND_IMPLEMENTATION_PLAN.md - Main architecture
2. IMAGE_GENERATION_FLOW_V2.md - Image generation workflow
3. AI_MODEL_CONFIGURATION.md - Model-agnostic AI system
4. STORY_PROMPTS_AND_TEMPLATES.md - Story content

TECH STACK:
- FastAPI (Python 3.11+)
- FastAPI BackgroundTasks (background jobs - no Redis needed for MVP)
- Supabase (PostgreSQL database + pg_cron for scheduled tasks)
- Cloudflare R2 (file storage)
- Fal.ai (AI image generation)

KEY REQUIREMENTS:
1. Model-agnostic architecture - easy to switch AI models via env vars
2. Generate ALL 10 high-res images upfront when user creates preview
3. Create 5 watermarked low-res previews from those images
4. After payment, generate PDF only (images already exist)
5. Preview expires after 7 days if not purchased
6. Shopify webhook integration for payments

DEFAULT AI MODELS:
- Artistic: Flux.1 [dev] + Fal Face Swap
- Photorealistic: Flux PuLID

Please start by:
1. Setting up the project structure
2. Creating the configuration and environment handling
3. Implementing the model registry and factory
4. Then proceed with the rest of the implementation

The .env file is already configured with all necessary credentials.
```

---

# 6. ALTERNATIVE: CLAUDE.MD FILE

Create a `CLAUDE.md` file in your project root that Claude Code will automatically read:

```markdown
# Zelavo Kids Backend

## Project Overview
AI-powered personalized children's storybook platform.

## Tech Stack
- FastAPI + Python 3.11
- FastAPI BackgroundTasks (no Redis for MVP)
- Supabase (PostgreSQL + pg_cron)
- Cloudflare R2 (storage)
- Fal.ai (AI generation)

## Key Architecture Decisions

### AI Model System
- Model-agnostic design with factory pattern
- Switch models via environment variables
- Fallback support for reliability

### Image Generation Flow
1. Generate ALL 10 high-res images upfront
2. Create 5 watermarked previews
3. After payment → Generate PDF only
4. 7-day expiry for unpurchased previews

### Default Models
- Artistic: `flux_dev` + `fal_face_swap`
- Photorealistic: `flux_pulid`

## File Structure
```
app/
├── ai/                    # AI model implementations
│   ├── model_registry.py  # Model configurations
│   ├── factory.py         # Model factory
│   ├── implementations/   # Model implementations
│   └── pipelines/         # Artistic & Realistic pipelines
├── api/                   # FastAPI endpoints
├── services/              # Business logic
├── background/            # FastAPI background tasks
└── stories/               # Story templates
```

## Commands
```bash
# Run API server
uvicorn app.main:app --reload

# Run tests
pytest tests/
```

## Environment Variables
See `.env.example` for all required variables.

## Documentation
- BACKEND_IMPLEMENTATION_PLAN.md
- IMAGE_GENERATION_FLOW_V2.md
- AI_MODEL_CONFIGURATION.md
- STORY_PROMPTS_AND_TEMPLATES.md
```

---

# 7. QUICK START CHECKLIST

## Before Starting Claude Code:

- [ ] Supabase project created and credentials copied
- [ ] Cloudflare R2 bucket created with public access
- [ ] Fal.ai account created with API key
- [ ] GitHub token generated (optional)
- [ ] `.env` file created with all credentials
- [ ] MCP config file saved to correct location
- [ ] All specification documents in project folder

## Start Development:

```bash
# Navigate to project
cd ~/projects/zelavo-backend

# Activate virtual environment
source venv/bin/activate

# Start Claude Code
claude-code

# Or with specific config
claude-code --config ~/.config/claude-code/config.json
```

---

# 8. MCP SERVERS REFERENCE

| Server | Purpose | Required |
|--------|---------|----------|
| `filesystem` | Read/write project files | ✅ Yes |
| `github` | Repo management, commits | Optional |
| `postgres` | Direct database access | Optional |
| `fetch` | Test API endpoints | Optional |
| `sequential-thinking` | Complex reasoning | Recommended |
| `memory` | Remember context | Recommended |

---

# 9. TROUBLESHOOTING

## MCP Server Not Starting

```bash
# Check if npm packages are installed
npm list -g @modelcontextprotocol/server-filesystem

# Reinstall if needed
npm install -g @modelcontextprotocol/server-filesystem
```

## Permission Issues

```bash
# Fix filesystem permissions
chmod -R 755 ~/projects/zelavo-backend
```

## Config Not Found

```bash
# Check config location
ls -la ~/.config/claude-code/

# Create directory if missing
mkdir -p ~/.config/claude-code/
```

---

# 10. SPEC FILES LOCATION

Place all specification documents in the project root:

```
zelavo-backend/
├── BACKEND_IMPLEMENTATION_PLAN.md
├── IMAGE_GENERATION_FLOW_V2.md
├── AI_MODEL_CONFIGURATION.md
├── STORY_PROMPTS_AND_TEMPLATES.md
├── CLAUDE.md
├── .env
├── .env.example
└── requirements.txt
```

---

**Ready to build! Start Claude Code and paste the initialization prompt.**
