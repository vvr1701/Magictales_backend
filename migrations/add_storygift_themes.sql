-- ============================================================================
-- Migration: Add new StoryGift themes to theme check constraint
-- ============================================================================
-- Run this migration to allow the new premium StoryGift themes in the database.
-- The old constraint only allowed: magic_castle, space_adventure, underwater, forest_friends
-- ============================================================================

-- Drop the old theme check constraint
ALTER TABLE previews DROP CONSTRAINT IF EXISTS previews_theme_check;

-- Add the new constraint with all themes
ALTER TABLE previews 
ADD CONSTRAINT previews_theme_check 
CHECK (theme IN (
    -- New StoryGift premium themes
    'storygift_magic_castle',
    'storygift_enchanted_forest',
    'storygift_spy_mission',
    'storygift_cosmic_dreamer',
    'storygift_mighty_guardian',
    'storygift_ocean_explorer',
    'storygift_birthday_magic',
    -- Legacy themes (for backward compatibility)
    'magic_castle',
    'space_adventure',
    'underwater',
    'forest_friends'
));

-- Verify the constraint was applied
DO $$
BEGIN
    RAISE NOTICE 'Migration complete: Theme constraint updated to include StoryGift themes';
END $$;
