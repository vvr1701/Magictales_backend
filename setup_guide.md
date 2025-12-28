# Supabase Database Setup Guide for Magictales

## Quick Setup (Recommended)

1. **Go to Supabase Dashboard**: https://seyivldfwemqvskdjkha.supabase.co
2. **Click "SQL Editor"** in the left sidebar
3. **Click "New query"**
4. **Copy the entire `supabase_schema.sql` file** and paste it
5. **Click "Run"**

## Verification

After setup, run this to verify:
```bash
python create_database.py
```

You should see:
```
✅ Table 'previews' exists
✅ Table 'orders' exists
✅ Table 'generation_jobs' exists
✅ Table 'rate_limits' exists
📊 Found 4/4 tables
🎉 All tables already exist! Database is ready.
```

## What Gets Created

### Tables:
- **previews** - Main storybook data with child info and generated images
- **orders** - Purchase tracking and PDF generation status
- **generation_jobs** - Background task progress (AI generation, PDF creation)
- **rate_limits** - API abuse prevention

### Custom Types:
- **preview_status** - preview lifecycle states
- **order_status** - order processing states
- **job_status** - background task states
- **job_type** - types of background jobs
- **book_style** - artistic vs photorealistic

### Features:
- **Auto-updating timestamps** - tracks when records are modified
- **UUID primary keys** - for secure public-facing IDs
- **JSONB storage** - for flexible image arrays and metadata
- **Performance indexes** - on frequently queried columns
- **Foreign key relationships** - linking orders to previews

## Troubleshooting

If you get errors:
1. **"type already exists"** - Safe to ignore, means it's already created
2. **"table already exists"** - Safe to ignore, means it's already created
3. **Permission errors** - Make sure you're the project owner
4. **Syntax errors** - Make sure you copied the entire file

## Testing the Setup

Once created, restart your FastAPI server and test:
```bash
curl -X GET "http://localhost:8000/health"
curl -X GET "http://localhost:8000/api/dev/info"
```

The server should now use the real database instead of the mock client!