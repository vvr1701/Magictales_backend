"""
Panel-Based Story Templates for Photorealistic Comic Book Generation
"""

from dataclasses import dataclass
from typing import Optional, List
from app.ai.pipelines.photorealistic_comic import Dialogue, ComicPanel, StoryScene


@dataclass
class PanelStoryTemplate:
    """Complete story template with panel-based structure for photorealistic comic books."""
    theme_id: str
    title_template: str       # "{name}'s Magical Adventure"
    description: str
    default_costume: str
    protagonist_description: str
    scenes: List[StoryScene]

    def get_title(self, child_name: str) -> str:
        """Get formatted title for this story."""
        return self.title_template.format(name=child_name)

    def get_scene_count(self) -> int:
        """Get total number of scenes."""
        return len(self.scenes)

    def get_panel_count(self) -> int:
        """Get total number of panels (2 per scene)."""
        return len(self.scenes) * 2

    def get_scenes_for_preview(self, preview_count: int = 5) -> List[StoryScene]:
        """Get scenes that will generate the desired number of preview panels."""
        scenes_needed = (preview_count + 1) // 2  # 2 panels per scene
        return self.scenes[:scenes_needed]

    def get_all_characters(self) -> List[str]:
        """Get list of all unique characters in the story."""
        characters = set()
        for scene in self.scenes:
            characters.update(scene.left_panel.characters_in_panel)
            characters.update(scene.right_panel.characters_in_panel)
        return list(characters)

    def get_dialogue_for_scene(self, scene_index: int) -> List[Dialogue]:
        """Get all dialogue for a specific scene."""
        if 0 <= scene_index < len(self.scenes):
            scene = self.scenes[scene_index]
            return scene.left_panel.dialogue + scene.right_panel.dialogue
        return []

    def format_dialogue_for_child(self, child_name: str) -> 'PanelStoryTemplate':
        """Replace {name} placeholders in all dialogue with child's name."""
        formatted_scenes = []

        for scene in self.scenes:
            # Format left panel dialogue
            left_dialogue = []
            for d in scene.left_panel.dialogue:
                formatted_speaker = d.speaker.format(name=child_name) if "{name}" in d.speaker else d.speaker
                formatted_text = d.text.format(name=child_name) if "{name}" in d.text else d.text
                left_dialogue.append(Dialogue(formatted_speaker, formatted_text, d.position))

            # Format right panel dialogue
            right_dialogue = []
            for d in scene.right_panel.dialogue:
                formatted_speaker = d.speaker.format(name=child_name) if "{name}" in d.speaker else d.speaker
                formatted_text = d.text.format(name=child_name) if "{name}" in d.text else d.text
                right_dialogue.append(Dialogue(formatted_speaker, formatted_text, d.position))

            # Create formatted panels
            left_panel = ComicPanel(
                scene.left_panel.image_prompt,
                left_dialogue,
                scene.left_panel.characters_in_panel
            )

            right_panel = ComicPanel(
                scene.right_panel.image_prompt,
                right_dialogue,
                scene.right_panel.characters_in_panel
            )

            formatted_scene = StoryScene(
                scene.narrative,
                left_panel,
                right_panel,
                scene.costume
            )

            formatted_scenes.append(formatted_scene)

        return PanelStoryTemplate(
            self.theme_id,
            self.title_template,
            self.description,
            self.default_costume,
            self.protagonist_description,
            formatted_scenes
        )


# Style blocks for photorealistic comic book generation
PHOTOREALISTIC_COMIC_STYLE_BLOCK = """
Photorealistic comic book panel, cinematic photography meets graphic novel art,
8K resolution, Unreal Engine 5 render quality, volumetric lighting,
comic ink line overlays, hyperrealistic textures, Marvel cover art style,
dramatic shadows and highlights, sharp character focus, expressive facial features,
professional studio lighting, depth of field, masterpiece quality.
"""

NEGATIVE_PROMPT_COMIC = """
bad anatomy, blurry faces, cartoonish low quality, low resolution,
bad layout, deformed hands, multiple heads, duplicate characters,
cropped faces, out of frame, draft quality, watermark, signature,
text overlay in image, speech bubbles in image, inconsistent character design,
bad proportions, amateur comic art, flat lighting.
"""