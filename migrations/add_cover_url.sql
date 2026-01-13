-- Add cover_url column to previews table
ALTER TABLE previews ADD COLUMN IF NOT EXISTS cover_url TEXT;

-- Verify the column was added (optional, for manual checking)
-- SELECT * FROM information_schema.columns WHERE table_name = 'previews' AND column_name = 'cover_url';
