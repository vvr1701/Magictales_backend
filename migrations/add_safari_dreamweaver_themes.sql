-- ============================================================================
-- Migration: Add Safari Adventure and Dream Weaver themes
-- ============================================================================
-- Run this migration to allow the two new premium themes in the database.
-- New themes:
--   - storygift_safari_adventure (Safari Guardian adventure)
--   - storygift_dream_weaver (Profession transformations adventure)
-- ============================================================================

-- Drop the old theme check constraint
ALTER TABLE previews DROP CONSTRAINT IF EXISTS previews_theme_check;

-- Add the new constraint with all themes including the two new ones
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
    -- NEW THEMES ADDED
    'storygift_safari_adventure',
    'storygift_dream_weaver',
    -- Legacy themes (for backward compatibility)
    'magic_castle',
    'space_adventure',
    'underwater',
    'forest_friends'
));

-- Verify the constraint was applied
DO $$
BEGIN
    RAISE NOTICE 'Migration complete: Added storygift_safari_adventure and storygift_dream_weaver themes';
END $$;
