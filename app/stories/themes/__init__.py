"""
Story themes.
"""

# Import old theme for backward compatibility (temporarily)
from app.stories.themes.magic_castle import MAGIC_CASTLE_THEME

# Import StoryGift-style themes (Premium collection)
from app.stories.themes.storygift_magic_castle import STORYGIFT_MAGIC_CASTLE_THEME
from app.stories.themes.storygift_enchanted_forest import STORYGIFT_ENCHANTED_FOREST_THEME

# Import new premium themes
from app.stories.themes.storygift_cosmic_dreamer import STORYGIFT_COSMIC_DREAMER_THEME
from app.stories.themes.storygift_mighty_guardian import STORYGIFT_MIGHTY_GUARDIAN_THEME
from app.stories.themes.storygift_ocean_explorer import STORYGIFT_OCEAN_EXPLORER_THEME
from app.stories.themes.storygift_birthday_magic import STORYGIFT_BIRTHDAY_MAGIC_THEME

# Import newest premium themes (Safari & Dream Weaver)
from app.stories.themes.storygift_safari_adventure import STORYGIFT_SAFARI_ADVENTURE_THEME
from app.stories.themes.storygift_dream_weaver import STORYGIFT_DREAM_WEAVER_THEME

AVAILABLE_THEMES = {
    # Primary themes: StoryGift collection (10 pages each, superior quality)
    "storygift_magic_castle": STORYGIFT_MAGIC_CASTLE_THEME,
    "storygift_enchanted_forest": STORYGIFT_ENCHANTED_FOREST_THEME,

    # New premium themes
    "storygift_cosmic_dreamer": STORYGIFT_COSMIC_DREAMER_THEME,
    "storygift_mighty_guardian": STORYGIFT_MIGHTY_GUARDIAN_THEME,
    "storygift_ocean_explorer": STORYGIFT_OCEAN_EXPLORER_THEME,
    "storygift_birthday_magic": STORYGIFT_BIRTHDAY_MAGIC_THEME,

    # Newest premium themes (Safari & Dream Weaver)
    "storygift_safari_adventure": STORYGIFT_SAFARI_ADVENTURE_THEME,
    "storygift_dream_weaver": STORYGIFT_DREAM_WEAVER_THEME,

    # Legacy theme: Keep for backward compatibility
    "magic_castle": MAGIC_CASTLE_THEME,
}

def get_theme(theme_id: str):
    """Get story template by theme ID."""
    if theme_id not in AVAILABLE_THEMES:
        raise ValueError(f"Unknown theme: {theme_id}. Available: {list(AVAILABLE_THEMES.keys())}")
    return AVAILABLE_THEMES[theme_id]