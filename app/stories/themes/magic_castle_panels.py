"""
Magic Castle Theme - Panel-Based Photorealistic Comic Book Version
Designed for high-quality face consistency and cinematic comic book style
"""

from app.stories.panel_templates import PanelStoryTemplate
from app.ai.pipelines.photorealistic_comic import Dialogue, ComicPanel, StoryScene

MAGIC_CASTLE_PANELS_THEME = PanelStoryTemplate(
    theme_id="magic_castle_panels",
    title_template="{name}'s First Day of Magic",
    description="A photorealistic comic book adventure at the Grand Academy of Arcane Arts",
    default_costume="wearing a purple wizard robe with gold star embroidery",
    protagonist_description="with bright expressive eyes, curious and brave expression, consistent facial features throughout all panels",
    scenes=[
        # SCENE 1: The Arrival and Test
        StoryScene(
            narrative="The morning mist clung to the cobblestones as the Grand Academy of Arcane Arts finally came into view. Standing before the massive iron gates was the school's oldest guardian.",
            left_panel=ComicPanel(
                image_prompt=(
                    "Wide establishing shot of a massive gothic castle with ornate iron gates "
                    "shrouded in morning mist. Small child wizard stands before the imposing entrance, "
                    "dwarfed by the ancient architecture. Professor Hoot, a giant brown owl with "
                    "spectacles, perches on a weathered stone pillar. Cinematic atmosphere with "
                    "golden morning light filtering through mist."
                ),
                dialogue=[],
                characters_in_panel=["owl"]
            ),
            right_panel=ComicPanel(
                image_prompt=(
                    "Dramatic low angle close-up. Child wizard points a glowing wooden wand at "
                    "the massive iron gate lock, magical sparks and energy bursting from the wand tip. "
                    "Determined expression on the child's face, eyes focused with concentration. "
                    "Professor Hoot watches approvingly from his stone perch above. "
                    "Magical runes on the gate beginning to glow with activation."
                ),
                dialogue=[
                    Dialogue("Professor Hoot", "Only the worthy may pass.", "left"),
                    Dialogue("{name}", "ALOHOMORA!", "right")
                ],
                characters_in_panel=["owl"]
            ),
            costume="wearing a heavy velvet traveling cloak and pointed wizard hat"
        ),

        # SCENE 2: Beast Taming Class
        StoryScene(
            narrative="The courtyard buzzed with excitement as Beast Taming class began. In the center sat a wooden crate that shook violently, promising an unexpected surprise.",
            left_panel=ComicPanel(
                image_prompt=(
                    "Medium shot of a stone courtyard with a reinforced wooden crate "
                    "shaking violently in the center. Purple magical smoke leaks from the cracks. "
                    "Child wizard stands at a safe distance, wand at ready, watching with "
                    "cautious curiosity. Other students visible in background, some backing away. "
                    "Ancient castle walls and gothic windows frame the scene."
                ),
                dialogue=[
                    Dialogue("Student", "It's going to explode!", "left")
                ],
                characters_in_panel=[]
            ),
            right_panel=ComicPanel(
                image_prompt=(
                    "Intimate close-up interaction shot. The wooden crate is now open, revealing "
                    "Sparky the baby red dragon sitting inside looking sad and hungry. "
                    "Child wizard kneels down compassionately, offering a magical cookie. "
                    "Sparky sniffs the offering with large, hopeful eyes. A small puff of harmless "
                    "smoke drifts from the dragon's tiny nostrils. Warm, emotional lighting."
                ),
                dialogue=[
                    Dialogue("{name}", "You're just hungry, aren't you?", "left"),
                    Dialogue("Sparky", "*Hiccup*", "right")
                ],
                characters_in_panel=["dragon"]
            ),
            costume="wearing casual wizard robes with rolled up sleeves"
        ),

        # SCENE 3: Flight Training
        StoryScene(
            narrative="By afternoon, the winds picked up for Advanced Flight. The broomstick vibrated with magical energy, alive with enchantment and possibility.",
            left_panel=ComicPanel(
                image_prompt=(
                    "Dynamic low angle action shot. Child wizard straddles a magical wooden "
                    "broomstick, just launching from the grassy field. Feet kicking off the ground, "
                    "dust and magical particles swirling around. Both hands gripping the broom handle "
                    "with determination. Other students visible in background at various heights. "
                    "Motion lines showing upward movement."
                ),
                dialogue=[
                    Dialogue("{name}", "Time to fly!", "right")
                ],
                characters_in_panel=[]
            ),
            right_panel=ComicPanel(
                image_prompt=(
                    "Spectacular high altitude aerial shot. Child wizard flies confidently "
                    "through the sky, sitting securely on the wooden broomstick with twigs at the back. "
                    "Zooming through a magical stone ring target suspended in midair. "
                    "Clouds surround the scene, castle grounds visible far below. "
                    "Child leaning forward for speed, face showing pure joy and accomplishment."
                ),
                dialogue=[
                    Dialogue("{name}", "I did it!", "right")
                ],
                characters_in_panel=[]
            ),
            costume="wearing leather flight gear, goggles on head, and a scarf flapping in wind"
        ),

        # SCENE 4: Library Chaos
        StoryScene(
            narrative="The Ancient Library was a place of quiet study until an innocent touch of a forbidden book changed everything into magical chaos.",
            left_panel=ComicPanel(
                image_prompt=(
                    "Wide angle interior shot of the magical library with towering wooden "
                    "bookshelves reaching into shadows. Midnight the sleek black cat sleeps "
                    "peacefully on a wooden reading table in the foreground. Child wizard "
                    "reaches curiously for a dusty, glowing red book on a high shelf. "
                    "Warm sunbeams create dramatic lighting through tall windows, "
                    "illuminating floating dust particles."
                ),
                dialogue=[
                    Dialogue("{name}", "Just one peek...", "left")
                ],
                characters_in_panel=["cat"]
            ),
            right_panel=ComicPanel(
                image_prompt=(
                    "Explosive action scene of complete magical chaos. Dozens of leather-bound books "
                    "fly through the air like birds with pages flapping wildly. Child wizard "
                    "ducks under an overturned wooden table, laughing at the absurd situation. "
                    "Midnight the black cat leaps athletically through the air, catching a "
                    "flying blue book with perfect feline grace. Papers and scrolls scatter everywhere. "
                    "Dynamic motion lines and magical energy effects throughout."
                ),
                dialogue=[
                    Dialogue("Midnight", "MEOW! (Got it!)", "left"),
                    Dialogue("{name}", "Down, books! Down!", "right")
                ],
                characters_in_panel=["cat"]
            ),
            costume="wearing a cozy knitted sweater with wizard academy crest"
        ),

        # SCENE 5: Peaceful Ending
        StoryScene(
            narrative="As the twin moons rose over the academy, a perfect moment of peace and belonging settled over the magical world. This wasn't just a school; it was home.",
            left_panel=ComicPanel(
                image_prompt=(
                    "Atmospheric silhouette shot from behind. Child wizard stands on ornate "
                    "stone balcony railing of the Astronomy Tower, gazing out at a giant full moon "
                    "in the star-filled sky. Midnight the black cat sits gracefully beside them "
                    "on the ledge, also looking out at the view. Dark blue night sky with "
                    "twinkling stars and magical aurora effects. Castle grounds twinkle with "
                    "warm lights far below."
                ),
                dialogue=[],
                characters_in_panel=["cat"]
            ),
            right_panel=ComicPanel(
                image_prompt=(
                    "Intimate close-up side profile portrait. Child wizard smiles softly with "
                    "peaceful contentment while gazing up at the starry sky. Magical moonlight "
                    "creates silver rim lighting on their face, highlighting gentle, hopeful expression. "
                    "Midnight the cat rubs affectionately against their shoulder, purring. "
                    "Stars reflected in the child's eyes. Sense of wonder and belonging. "
                    "Perfect ending moment with emotional depth."
                ),
                dialogue=[
                    Dialogue("{name}", "I'm ready for tomorrow.", "bottom")
                ],
                characters_in_panel=["cat"]
            ),
            costume="wearing formal royal silk robes with a starry magical cape"
        )
    ]
)

def get_magic_castle_panels_theme() -> PanelStoryTemplate:
    """Get the Magic Castle panels theme for photorealistic comic generation."""
    return MAGIC_CASTLE_PANELS_THEME