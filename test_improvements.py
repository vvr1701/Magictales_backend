#!/usr/bin/env python3
"""
Comprehensive test script to validate all PDF improvements work correctly
without breaking existing workflow.
"""

import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from stories.templates import StoryTemplate, PageTemplate
from stories.themes.magic_castle import MAGIC_CASTLE_THEME
from services.pdf_generator import PDFGeneratorService
from config import get_settings
from pathlib import Path
import tempfile

def test_story_template_backward_compatibility():
    """Test that story templates still work with existing API."""
    print("🧪 Testing story template backward compatibility...")

    # Test basic template functionality
    template = MAGIC_CASTLE_THEME
    assert template.theme_id == "magic_castle", "Theme ID should be preserved"
    assert template.get_title("Alice") == "Alice's First Day of Magic", "Title formatting should work"

    # Test page access
    assert len(template.pages) == 10, "Should have 10 pages"
    page1 = template.pages[0]
    assert page1.page_number == 1, "Page numbering should be correct"
    assert hasattr(page1, 'scene_type'), "Pages should have scene_type attribute"

    # Test prompt generation (existing API)
    prompt_data = template.get_page_prompt(
        page_number=1,
        style="photorealistic",
        child_name="Alice",
        child_age=6,
        child_gender="girl",
        enable_cinematic=False  # Test without cinematic enhancements
    )

    assert "prompt" in prompt_data, "Should return prompt data"
    assert "negative_prompt" in prompt_data, "Should include negative prompt"

    # Debug: print actual prompt
    print(f"DEBUG: Generated prompt: {prompt_data['prompt'][:200]}...")

    # Note: Image prompts use face embedding, so child name is NOT in image prompts
    # Instead, check for age and gender which ARE included
    assert "6-year-old" in prompt_data["prompt"], "Should include child age"
    assert "girl" in prompt_data["prompt"], "Should include child gender"

    print("✅ Story template backward compatibility: PASSED")

def test_cinematic_enhancements():
    """Test that new cinematic features work correctly."""
    print("🧪 Testing cinematic enhancements...")

    template = MAGIC_CASTLE_THEME

    # Test with cinematic enhancements enabled
    prompt_with_cinematic = template.get_page_prompt(
        page_number=1,
        style="photorealistic",
        child_name="Bob",
        child_age=7,
        child_gender="boy",
        enable_cinematic=True
    )

    # Test without cinematic enhancements
    prompt_without_cinematic = template.get_page_prompt(
        page_number=1,
        style="photorealistic",
        child_name="Bob",
        child_age=7,
        child_gender="boy",
        enable_cinematic=False
    )

    # Prompts should be different when cinematic is enabled
    assert prompt_with_cinematic["prompt"] != prompt_without_cinematic["prompt"], \
        "Cinematic enhancements should modify prompts"

    # Both should contain basic story elements
    for prompt_data in [prompt_with_cinematic, prompt_without_cinematic]:
        assert "7-year-old" in prompt_data["prompt"], "Should contain age"
        assert "boy" in prompt_data["prompt"], "Should contain gender"

    print("✅ Cinematic enhancements: PASSED")

def test_pdf_generator_integration():
    """Test that PDF generator works with all new features."""
    print("🧪 Testing PDF generator integration...")

    # Create temporary directory for test output
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Initialize PDF generator
        generator = PDFGeneratorService()

        # Test layout detection
        layout_hero = generator._detect_page_layout(1, MAGIC_CASTLE_THEME, "Standing before the gates...")
        layout_action = generator._detect_page_layout(6, MAGIC_CASTLE_THEME, "Flying through the sky...")

        assert layout_hero in ["layout-hero", "layout-establishing"], \
            f"Page 1 should use hero/establishing layout, got: {layout_hero}"
        assert layout_action == "layout-action", \
            f"Page 6 should use action layout, got: {layout_action}"

        # Test sound effect generation
        sound_effect = generator._generate_dynamic_sound_effect(
            page_number=2,
            story_text="The gate EXPLODED open with a CLANG!",
            scene_type="test",
            story_template=MAGIC_CASTLE_THEME
        )

        assert sound_effect, "Should generate sound effect"
        assert any(effect in sound_effect.lower() for effect in ["clang", "boom", "crash"]), \
            f"Sound effect should be relevant to content: {sound_effect}"

        # Test content complexity analysis
        complexity = generator._analyze_content_complexity(
            "The gate EXPLODED open! 'Welcome!' shouted the professor. 'Are you ready?' asked Alice."
        )

        assert "dialogue_count" in complexity, "Should analyze dialogue"
        assert "action_intensity" in complexity, "Should analyze action"
        assert complexity["dialogue_count"] >= 2, "Should detect multiple dialogue instances"

        # Test premium cover generation
        cover_design = generator._generate_premium_cover_design(
            title="Alice's First Day of Magic",
            child_name="Alice",
            theme="magic_castle",
            story_template=MAGIC_CASTLE_THEME
        )

        assert "title_class" in cover_design, "Should include title styling"
        assert "background_class" in cover_design, "Should include background styling"
        assert "magical" in cover_design["title_class"], "Magic theme should use magical styling"

        print("✅ PDF generator integration: PASSED")

def test_css_framework():
    """Test that CSS framework is properly structured."""
    print("🧪 Testing CSS framework...")

    css_file = Path("app/static/css/comic-book-layouts.css")
    assert css_file.exists(), "CSS file should exist"

    css_content = css_file.read_text()

    # Test that all required classes exist
    required_classes = [
        ".layout-hero", ".layout-action", ".layout-sequence", ".layout-intimate",
        ".speech-bubble", ".sound-effect", ".magical-title-glow", ".cosmic-title-glow",
        ".premium-cover", ".floating-sparkles", ".panel-grid"
    ]

    for css_class in required_classes:
        assert css_class in css_content, f"CSS should contain {css_class}"

    # Test that animations are defined
    animations = ["@keyframes sparkle-float", "@keyframes magical-pulse", "@keyframes cosmic-pulse"]
    for animation in animations:
        assert animation in css_content, f"CSS should contain {animation}"

    print("✅ CSS framework: PASSED")

def test_fallback_mechanisms():
    """Test that all fallback mechanisms work correctly."""
    print("🧪 Testing fallback mechanisms...")

    generator = PDFGeneratorService()

    # Test layout fallback with invalid scene type
    layout = generator._detect_page_layout(1, None, "")
    assert layout == "layout-hero", f"Should fallback to hero layout, got: {layout}"

    # Test sound effect fallback with minimal content
    sound_effect = generator._generate_dynamic_sound_effect(1, "", "unknown", None)
    assert sound_effect, "Should generate fallback sound effect"

    # Test cover design fallback with unknown theme
    cover_design = generator._generate_premium_cover_design(
        title="Test Story",
        child_name="Test",
        theme="unknown_theme"
    )
    assert "title_class" in cover_design, "Should provide fallback cover design"

    print("✅ Fallback mechanisms: PASSED")

def test_backward_compatibility_full_pipeline():
    """Test complete pipeline maintains backward compatibility."""
    print("🧪 Testing full pipeline backward compatibility...")

    # Test that old API calls still work exactly as before
    template = MAGIC_CASTLE_THEME

    # This should work exactly as it did before our changes
    for page_num in range(1, 11):
        prompt_data = template.get_page_prompt(
            page_number=page_num,
            style="photorealistic",
            child_name="TestChild",
            child_age=5,
            child_gender="child"
        )

        assert "prompt" in prompt_data, f"Page {page_num} should return prompt"
        assert "negative_prompt" in prompt_data, f"Page {page_num} should return negative_prompt"
        assert "5-year-old" in prompt_data["prompt"], f"Page {page_num} should include age"
        assert "child" in prompt_data["prompt"], f"Page {page_num} should include gender"

        # Test story text generation
        story_text = template.get_story_text(page_num, "TestChild")
        assert "TestChild" in story_text, f"Page {page_num} story should include child name"

    print("✅ Full pipeline backward compatibility: PASSED")

def main():
    """Run all tests."""
    print("🚀 Starting comprehensive improvement tests...\n")

    try:
        test_story_template_backward_compatibility()
        test_cinematic_enhancements()
        test_pdf_generator_integration()
        test_css_framework()
        test_fallback_mechanisms()
        test_backward_compatibility_full_pipeline()

        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("✅ All improvements work correctly without breaking existing workflow")
        print("✅ Backward compatibility maintained")
        print("✅ New features integrate seamlessly")
        print("✅ Fallback mechanisms protect against errors")
        print("✅ Ready for production use!")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()