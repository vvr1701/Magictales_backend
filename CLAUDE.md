# CLAUDE.md

This file provides guidance to Claude Code when working with this codebase.

## Project Overview
MagicTales - AI-powered personalized children's storybook platform

## Available Agents
When working on specific areas, reference these specialized agents for detailed guidance:

| Area | Agent File |
|------|------------|
| API Development | `.claude/agents/backend-api.md` |
| AI/Image Generation | `.claude/agents/ai-pipeline.md` |
| Shopify Integration | `.claude/agents/shopify-integration.md` |
| Testing | `.claude/agents/testing.md` |
| Database | `.claude/agents/database.md` |

## Quick Commands
```bash
# Start development server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest

# Check logs
Get-Content logs/app.log -Tail 50
```

## Key Directories
- `app/api/endpoints/` - REST API endpoints
- `app/ai/` - AI model implementations and pipelines
- `app/services/` - Business logic services
- `app/stories/themes/` - Story templates and prompts

## When to Use Each Agent

**Use Backend API Agent when:**
- Adding or modifying API endpoints
- Debugging request/response issues
- Working with middleware or CORS

**Use AI Pipeline Agent when:**
- Debugging image generation
- Tuning prompts for better quality
- Adding new AI models

**Use Shopify Agent when:**
- Debugging webhook issues
- Fixing App Proxy problems
- Working with cart integration

**Use Testing Agent when:**
- Writing unit or integration tests
- Debugging test failures
- Improving test coverage

**Use Database Agent when:**
- Modifying schema
- Optimizing queries
- Working with Supabase
