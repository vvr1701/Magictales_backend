"""
StoryGift Enchanted Forest Theme - Converted to Magictales format.

Complete 10-page story: "The Enchanted Forest"
Converted from StoryGift's 5 scenes × 2 panels structure
Preserves all original prompts, dialogue, and story narrative
"""

from app.stories.templates import StoryTemplate, PageTemplate


STORYGIFT_ENCHANTED_FOREST_THEME = StoryTemplate(
    theme_id="storygift_enchanted_forest",
    title_template="{name} and the Enchanted Forest",
    description="A magical journey through whispering woods and singing streams",
    default_costume="wearing comfortable outdoor clothes",
    protagonist_description="bright curious eyes, sense of wonder and adventure",
    # Cover page settings for typography-ready composition
    cover_costume="wearing an elegant forest adventurer outfit with a flowing green cape, leather satchel, and nature-inspired accessories",
    cover_header_atmosphere="Mystical enchanted forest canopy with ancient towering trees, soft golden sunlight filtering through leaves, magical mist and ethereal glow",
    cover_magical_elements="Glowing fireflies, floating leaves, and gentle magical sparkles dance around the child's body (not face). A friendly deer watches from the shadows. Waterfalls shimmer in the background.",
    cover_footer_description="Mossy forest floor with wildflowers, a winding magical path, and soft ferns",
    pages=[
        # === SCENE 1 - THE SECRET MAP ===

        # PAGE 1 (Scene 1 - Left Panel)
        PageTemplate(
            page_number=1,
            scene_description="Finding the secret map",
            scene_type="discovery",
            realistic_prompt="""Wide warm indoor shot. A sunny bedroom with toys scattered on the floor. The child named {name} is sitting on a soft rug holding a large colorful map open. Sunlight streams through the window. A teddy bear is nearby. The child is wearing comfortable indoor clothes.""",
            story_text="The morning sunshine danced through the bedroom window as {name} discovered something amazing hidden under a fuzzy rug. 'Look!' {name} shouted with excitement, 'An adventure is waiting!'",
            costume="wearing comfortable indoor clothes"
        ),

        # PAGE 2 (Scene 1 - Right Panel)
        PageTemplate(
            page_number=2,
            scene_description="Examining the magical map",
            scene_type="discovery",
            realistic_prompt="""Close up detail. The map shows a winding path through a forest, a purple stream, and pillow mountains. The child's finger is pointing at the 'X' mark. The map looks hand-drawn and magical. The child is wearing comfortable indoor clothes.""",
            story_text="The map was unlike anything {name} had ever seen before. It showed a winding path through an enchanted forest, a purple singing stream, and mountains that looked like soft pillows. There was even an 'X' marking the treasure spot!",
            costume="wearing comfortable indoor clothes"
        ),

        # === SCENE 2 - THE SILVER TRAIL ===

        # PAGE 3 (Scene 2 - Left Panel)
        PageTemplate(
            page_number=3,
            scene_description="Entering the magical forest",
            scene_type="journey",
            realistic_prompt="""Wide eye-level shot in a magical forest. Giant trees with heart-shaped leaves that sparkle. A glowing silver dust trail winds through the grass. The child named {name} is walking along the path, looking amazed. The child is wearing comfortable outdoor clothes.""",
            story_text="Stepping into the enchanted forest felt like entering a dream. Giant trees with heart-shaped leaves sparkled in the sunlight, and a shimmering silver trail of magical dust wound through the emerald grass. 'So shiny!' {name} whispered in wonder.",
            costume="wearing comfortable outdoor clothes"
        ),

        # PAGE 4 (Scene 2 - Right Panel)
        PageTemplate(
            page_number=4,
            scene_description="Meeting Pip the squirrel",
            scene_type="encounter",
            realistic_prompt="""Mid-shot interaction. A cute brown squirrel (Pip) with a fluffy tail is standing on a log, gesturing forward with tiny paws. The child named {name} is looking at the squirrel with a smile. Fireflies are dancing around them. The child is wearing comfortable outdoor clothes.""",
            story_text="Suddenly, a friendly brown squirrel hopped down from a nearby tree. 'Hello there!' squeaked Pip, waving a tiny paw. 'I'm Pip! Follow the silver trail, {name}, and I'll show you the way to the most magical places in the forest!'",
            costume="wearing comfortable outdoor clothes"
        ),

        # === SCENE 3 - THE SINGING STREAM ===

        # PAGE 5 (Scene 3 - Left Panel)
        PageTemplate(
            page_number=5,
            scene_description="Crossing the singing stream",
            scene_type="challenge",
            realistic_prompt="""Wide action shot. A beautiful blue stream flows through the woods. The stones in the water are purple and round, perfectly spaced for stepping. The child named {name} is carefully stepping from one stone to another. Musical notes float in the air above the water. The child is wearing comfortable outdoor clothes.""",
            story_text="The silver trail led to the most amazing discovery yet - the Singing Stream! The crystal-clear water bubbled and gurgled in perfect harmony, and purple stepping stones created a path across. 'Hop! Hop!' laughed {name}, dancing from stone to stone.",
            costume="wearing comfortable outdoor clothes"
        ),

        # PAGE 6 (Scene 3 - Right Panel)
        PageTemplate(
            page_number=6,
            scene_description="The magical musical water",
            scene_type="wonder",
            realistic_prompt="""Low angle close-up. The child's foot is landing on a purple stone. Ripples in the water form musical clefs and notes. The water glows softly with magical light. Musical sparkles dance in the air. The child is wearing comfortable outdoor clothes.""",
            story_text="Each time {name} stepped on a stone, the water sang a different note! The ripples formed magical musical symbols that danced across the surface, creating the most beautiful melody the forest had ever heard.",
            costume="wearing comfortable outdoor clothes"
        ),

        # === SCENE 4 - THE WHISPERING MOUNTAINS ===

        # PAGE 7 (Scene 4 - Left Panel)
        PageTemplate(
            page_number=7,
            scene_description="Discovering the pillow mountains",
            scene_type="awe",
            realistic_prompt="""Wide epic landscape. In the distance, the mountains are not made of rock, but of giant soft purple and pink pillows. The sun is smiling in the sky with a cheerful face. The child named {name} is looking up at them in awe. The child is wearing comfortable outdoor clothes.""",
            story_text="Beyond the stream rose the most incredible sight - the Whispering Mountains! But these weren't ordinary mountains made of rock and stone. They were enormous, fluffy pillows of purple and pink velvet that reached toward the smiling sun. 'Giant pillows!' gasped {name}.",
            costume="wearing comfortable outdoor clothes"
        ),

        # PAGE 8 (Scene 4 - Right Panel)
        PageTemplate(
            page_number=8,
            scene_description="Climbing the soft mountains",
            scene_type="adventure",
            realistic_prompt="""Mid-shot. The child named {name} is climbing up a soft slope that looks like a giant duvet. Feathers float around like soft snow. The lighting is pastel and dreamy, with magical sparkles. The child is wearing comfortable outdoor clothes.""",
            story_text="Climbing the pillow mountains was like bouncing on the world's softest, most magical bed. With each step, feathers danced through the air like gentle snowflakes, and the whole mountainside whispered secrets of ancient adventures.",
            costume="wearing comfortable outdoor clothes"
        ),

        # === SCENE 5 - THE SUMMIT VIEW ===

        # PAGE 9 (Scene 5 - Left Panel)
        PageTemplate(
            page_number=9,
            scene_description="Reaching the summit",
            scene_type="triumph",
            realistic_prompt="""Wide hero shot from behind. The child named {name} sits on the soft peak, looking out over the magical land. The sun sets, casting golden light. Pip the squirrel with a fluffy tail sits next to them. The view shows the enchanted forest, singing stream, and soft valleys below. The child is wearing comfortable outdoor clothes.""",
            story_text="At the summit, the view was breathtaking. The entire enchanted world spread out below like a living fairytale - the sparkling forest, the musical stream, and valleys filled with wonder. 'Best adventure ever,' whispered {name}, sitting beside faithful Pip.",
            costume="wearing comfortable outdoor clothes"
        ),

        # PAGE 10 (Scene 5 - Right Panel)
        PageTemplate(
            page_number=10,
            scene_description="A magical friendship",
            scene_type="resolution",
            realistic_prompt="""Close up portrait. The child named {name} is smiling with eyes closed, gently hugging Pip the squirrel with a fluffy tail. Soft magical sparkles surround them in the golden sunset light. A feeling of warmth, friendship, and happiness fills the scene. The child is wearing comfortable outdoor clothes.""",
            story_text="As the golden sun painted the sky in magical colors, {name} knew this was just the beginning of many adventures to come. With a gentle hug, Pip whispered, 'See you next time, brave explorer!' And {name} smiled, knowing the enchanted forest would always be there, waiting for the next magical journey.",
            costume="wearing comfortable outdoor clothes"
        ),
    ]
)