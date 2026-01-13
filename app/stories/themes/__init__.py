"""
Story themes.
"""

# Import old theme for backward compatibility (temporarily)
from app.stories.themes.magic_castle import MAGIC_CASTLE_THEME

# Import new StoryGift-style themes
from app.stories.themes.storygift_magic_castle import STORYGIFT_MAGIC_CASTLE_THEME
from app.stories.themes.storygift_enchanted_forest import STORYGIFT_ENCHANTED_FOREST_THEME
from app.stories.themes.storygift_spy_mission import STORYGIFT_SPY_MISSION_THEME

AVAILABLE_THEMES = {
    # Primary themes: StoryGift collection (10 pages each, superior quality)
    "storygift_magic_castle": STORYGIFT_MAGIC_CASTLE_THEME,
    "storygift_enchanted_forest": STORYGIFT_ENCHANTED_FOREST_THEME,
    "storygift_spy_mission": STORYGIFT_SPY_MISSION_THEME,

    # Legacy theme: Keep for backward compatibility
    "magic_castle": MAGIC_CASTLE_THEME,
}

def get_theme(theme_id: str):
    """Get story template by theme ID."""
    if theme_id not in AVAILABLE_THEMES:
        raise ValueError(f"Unknown theme: {theme_id}. Available: {list(AVAILABLE_THEMES.keys())}")
    return AVAILABLE_THEMES[theme_id]