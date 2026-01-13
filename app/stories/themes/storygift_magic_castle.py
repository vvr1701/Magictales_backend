"""
StoryGift Magic Castle Theme - Converted to Magictales format.

Complete 10-page story: "The First Day of Magic School"
Converted from StoryGift's 5 scenes × 2 panels structure
Preserves all original prompts, dialogue, and story narrative
"""

from app.stories.templates import StoryTemplate, PageTemplate


STORYGIFT_MAGIC_CASTLE_THEME = StoryTemplate(
    theme_id="storygift_magic_castle",
    title_template="{name}'s First Day of Magic School",
    description="A detailed magical academy adventure",
    default_costume="wearing wizard robes",
    protagonist_description="bright expressive eyes, curious and brave expression",
    # Cover page settings for typography-ready composition
    cover_costume="wearing elegant purple and gold wizard robes with magical embroidered patterns, a flowing cape, and holding a glowing wand",
    cover_header_atmosphere="Majestic magical castle towers rising into a mystical purple twilight sky with stars and magical aurora, castle spires fading into elegant mist",
    cover_magical_elements="Glowing magical orbs float gently around the child's body (not face). Professor Hoot the wise owl perches on a nearby pillar. Sparky the baby dragon peeks from behind. Magical sparkles and wisps dance in the air.",
    cover_footer_description="Polished marble castle courtyard floor with magical glowing runes, ancient stone steps leading to grand doors",
    pages=[
        # === SCENE 1 - THE ARRIVAL ===

        # PAGE 1 (Scene 1 - Left Panel)
        PageTemplate(
            page_number=1,
            scene_description="Arrival at the magic school gates",
            scene_type="arrival",
            realistic_prompt="""Wide establishing shot. The child wizard named {name} stands small in the foreground looking up at a massive, intimidating gothic castle gate made of dark iron. The castle towers disappear into the mist. To the right of the gate, sitting on a high stone pedestal, is a giant brown wise owl wearing large round reading glasses and a small black graduation cap. Cinematic lighting. The child is wearing wizard robes.""",
            story_text="The morning mist clung to the cobblestones as the Grand Academy of Arcane Arts finally came into view. Standing before the massive iron gates was the school's oldest guardian. Professor Hoot was not merely an owl; he was a giant, ancient sentinel wearing thick spectacles.",
            costume="wearing wizard robes"
        ),

        # PAGE 2 (Scene 1 - Right Panel)
        PageTemplate(
            page_number=2,
            scene_description="Entering the magic school",
            scene_type="arrival",
            realistic_prompt="""Wide angle cinematic shot. The massive iron gate towers overhead. Professor Hoot (a giant brown wise owl wearing large round reading glasses and a small black graduation cap) is perched high on a stone pillar. The child wizard named {name} stands small at the base, casting a spell on the lock with a wand raised high. Magic sparks fly into the mist. The child is wearing wizard robes.""",
            story_text="He adjusted his glasses with a wing tip and peered down. The test had begun before the first step was even taken. 'Only the worthy may pass,' hooted Professor Hoot as {name} shouted 'ALOHOMORA!' and magic sparks illuminated the ancient lock.",
            costume="wearing wizard robes"
        ),

        # === SCENE 2 - BEAST TAMING CLASS ===

        # PAGE 3 (Scene 2 - Left Panel)
        PageTemplate(
            page_number=3,
            scene_description="Beast Taming class begins",
            scene_type="action",
            realistic_prompt="""Eye-level shot. A reinforced wooden crate in the center of a stone courtyard is shaking violently. Purple smoke is leaking from the cracks of the crate. The child wizard named {name} is standing back cautiously, holding a wand. Stone castle walls in background. Other students are visible saying "It's gonna blow!" The child is wearing wizard robes.""",
            story_text="The courtyard was buzzing as the Beast Taming class began. In the center sat a wooden crate that shook violently. Purple smoke leaked from every crack as students backed away nervously. 'It's gonna blow!' someone shouted.",
            costume="wearing wizard robes"
        ),

        # PAGE 4 (Scene 2 - Right Panel)
        PageTemplate(
            page_number=4,
            scene_description="Meeting Sparky the dragon",
            scene_type="bonding",
            realistic_prompt="""Wide shot of the stone courtyard. The child named {name} is kneeling next to the open crate, offering a treat to Sparky (a tiny, cute baby dragon, red with orange wings, breathing a tiny puff of harmless smoke). Other students are watching from a distance in the background. The castle walls loom large around them. The child is wearing wizard robes.""",
            story_text="With a pop, the lid flew open, revealing Sparky—a baby dragon with the hiccups. Every time he hiccuped, a smoke ring puffed from his nose. He wasn't scary; he was just hungry. '{name} offered a treat, realizing 'You're just hungry, aren't you?'",
            costume="wearing wizard robes"
        ),

        # === SCENE 3 - ADVANCED FLIGHT ===

        # PAGE 5 (Scene 3 - Left Panel)
        PageTemplate(
            page_number=5,
            scene_description="Learning to fly on broomstick",
            scene_type="action",
            realistic_prompt="""Low angle action shot. The child named {name} is straddling a wooden magical broomstick, hovering just above the grass. Their feet are kicking off the ground to launch. Dust swirls around them. The child is holding the broom handle tight with both hands, wearing wizard robes. Expression of determination and excitement.""",
            story_text="By afternoon, the winds picked up for Advanced Flight. The broomstick vibrated in hand, alive with enchantment. While others wobbled, a surge of confidence took hold. 'Time to fly!' {name} declared with determination.",
            costume="wearing wizard robes"
        ),

        # PAGE 6 (Scene 3 - Right Panel)
        PageTemplate(
            page_number=6,
            scene_description="Flying through the castle grounds",
            scene_type="flight",
            realistic_prompt="""Extremely wide aerial shot. The child named {name} is zooming through a stone ring high in the sky on a broomstick. Other student flyers are visible in the distance. The castle grounds and clouds are far below. The child is wearing wizard robes and has an expression of pure joy and accomplishment.""",
            story_text="With a command of 'UP!', the broom shot into the sky. The wind rushed past ears like a roaring river. The ground became a quilt of green and grey. 'I did it!' {name} shouted with pure exhilaration as they soared through stone rings in the sky.",
            costume="wearing wizard robes"
        ),

        # === SCENE 4 - THE ANCIENT LIBRARY ===

        # PAGE 7 (Scene 4 - Left Panel)
        PageTemplate(
            page_number=7,
            scene_description="Exploring the magical library",
            scene_type="mischief",
            realistic_prompt="""Wide angle shot of a magical library with tall bookshelves. Midnight (a sleek black cat with glowing yellow eyes and a silver collar) is sleeping on a wooden table in the foreground. The child named {name} is reaching for a dusty red book on a high shelf. Sunbeams hit the dust. The child is wearing wizard robes.""",
            story_text="The Ancient Library was quiet until curiosity took over. Midnight, the library cat, dozed peacefully as {name} reached for an ancient tome. 'Just one peek...' they whispered, not knowing what magic would unfold.",
            costume="wearing wizard robes"
        ),

        # PAGE 8 (Scene 4 - Right Panel)
        PageTemplate(
            page_number=8,
            scene_description="Chaos in the magical library",
            scene_type="chaos",
            realistic_prompt="""Wide interior shot of the magical library. Hundreds of books are flying like a flock of birds across the high-ceilinged room. Midnight (a sleek black cat with glowing yellow eyes and a silver collar) is leaping mid-air to catch one. The child named {name} is ducking near a table, wearing wizard robes.""",
            story_text="A sneeze disturbed the dust, and suddenly the books woke up! Leather-bound covers flapped like heavy wings in a paper storm. Midnight sprang into action, treating the flying literature like birds. 'MEOW! Got it!' seemed to say as {name} called 'Down boy!' It was chaos, but fun.",
            costume="wearing wizard robes"
        ),

        # === SCENE 5 - PEACEFUL ENDING ===

        # PAGE 9 (Scene 5 - Left Panel)
        PageTemplate(
            page_number=9,
            scene_description="Peaceful moment on the tower balcony",
            scene_type="peaceful",
            realistic_prompt="""Back view silhouette. The child named {name} is standing on a stone balcony railing, looking out at a giant full moon. Midnight (a sleek black cat with glowing yellow eyes and a silver collar) is sitting next to them on the ledge. The sky is dark blue with stars. The child is wearing formal robes. Peaceful, contemplative atmosphere.""",
            story_text="As the twin moons rose, the castle quieted down. Standing on the balcony of the Astronomy Tower, looking out over the glittering lights of the village, everything felt magical. Midnight purred contentedly, a faithful companion in this new adventure.",
            costume="wearing formal robes"
        ),

        # PAGE 10 (Scene 5 - Right Panel)
        PageTemplate(
            page_number=10,
            scene_description="Finding home at magic school",
            scene_type="peaceful",
            realistic_prompt="""Wide atmospheric shot. The child named {name} and Midnight (a sleek black cat with glowing yellow eyes and a silver collar) are sitting on the edge of the Astronomy Tower balcony. The village lights twinkle far below. A giant full moon fills the sky behind them. Cinematic silhouette. The child is wearing formal robes. Peaceful, hopeful expression.""",
            story_text="This wasn't just a school; it was home. With Midnight by their side and a world of magic to explore, {name} smiled and whispered, 'I'm ready for tomorrow.' The moon smiled back, casting silver light on a perfect first day.",
            costume="wearing formal robes"
        )
    ]
)