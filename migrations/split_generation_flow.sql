-- Migration: Add columns for split generation flow
-- Run this in Supabase SQL Editor

-- Add generation_phase to track preview vs complete state
ALTER TABLE previews ADD COLUMN IF NOT EXISTS generation_phase TEXT DEFAULT 'preview';
-- Values: 'preview' (5 pages generated), 'generating_full' (in progress), 'complete' (10 pages done)

-- Store analyzed_features for consistency across split generation
ALTER TABLE previews ADD COLUMN IF NOT EXISTS analyzed_features TEXT;

-- Track page counts
ALTER TABLE previews ADD COLUMN IF NOT EXISTS preview_page_count INTEGER DEFAULT 5;
ALTER TABLE previews ADD COLUMN IF NOT EXISTS total_page_count INTEGER DEFAULT 10;

-- Add index for querying by generation phase
CREATE INDEX IF NOT EXISTS idx_previews_generation_phase ON previews(generation_phase);

-- Update existing previews to mark them as complete (they have all pages)
UPDATE previews 
SET generation_phase = 'complete' 
WHERE generation_phase IS NULL OR generation_phase = 'preview';

COMMENT ON COLUMN previews.generation_phase IS 'preview=5 pages, generating_full=in progress, complete=all 10 pages';
COMMENT ON COLUMN previews.analyzed_features IS 'VLM face analysis result - reused for consistency across split generation';
