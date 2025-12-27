"""
Story themes.
"""

from app.stories.themes.magic_castle import MAGIC_CASTLE_THEME

AVAILABLE_THEMES = {
    "magic_castle": MAGIC_CASTLE_THEME,
}

def get_theme(theme_id: str):
    """Get story template by theme ID."""
    if theme_id not in AVAILABLE_THEMES:
        raise ValueError(f"Unknown theme: {theme_id}. Available: {list(AVAILABLE_THEMES.keys())}")
    return AVAILABLE_THEMES[theme_id]