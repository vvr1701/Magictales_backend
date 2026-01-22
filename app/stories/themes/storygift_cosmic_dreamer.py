"""
StoryGift Cosmic Dreamer Theme - Space Adventure.

Complete 10-page story: "[NAME]'s Cosmic Adventure"
Premium theme featuring space exploration, alien friendship, and heroic journey.
Optimized for both photorealistic and 3D cartoon pipelines.
"""

from app.stories.templates import StoryTemplate, PageTemplate


STORYGIFT_COSMIC_DREAMER_THEME = StoryTemplate(
    theme_id="storygift_cosmic_dreamer",
    title_template="{name}'s Cosmic Adventure",
    description="Watch your child reach for the stars on an epic space journey",
    default_costume="wearing a premium white and silver NASA-style astronaut suit with gold accents",
    protagonist_description="bright curious eyes, expression of wonder and excitement",
    # Cover page settings for typography-ready composition
    cover_costume="wearing a premium white and silver NASA-style astronaut suit with gold visor reflecting stars and galaxies, heroic stance",
    cover_header_atmosphere="Deep space with vibrant purple and blue nebula clouds, twinkling stars, and a shooting star trail across the cosmic sky",
    cover_magical_elements="Glowing asteroid surface beneath feet, stardust particles floating around the body (not face). A distant Earth glows blue in the background. Golden rim lighting creates an epic silhouette.",
    cover_footer_description="Glowing asteroid surface with crystalline formations and cosmic dust",
    pages=[
        # === PAGE 1 - THE MAGICAL ROCKET ===
        PageTemplate(
            page_number=1,
            scene_description="Discovering the magical rocket",
            scene_type="discovery",
            realistic_prompt="""Magical backyard scene at twilight. The child named {name} in pajamas stands in awe before a magnificent silver and blue rocket ship with the name glowing in neon letters on the side. The rocket has a translucent glass dome showing a cozy interior with stars projected inside. Fireflies dance around, the child's house is warmly lit in background, purple and pink sunset sky. Child's face shows pure wonder and excitement. Dreamy, warm lighting with magical glow effects. Detailed grass and garden, soft focus background.""",
            story_text="{name} had always dreamed of exploring space. One magical night, a shimmering rocket appeared in the backyard, with {name}'s name glowing on the side. It was time for the adventure of a lifetime!",
            costume="wearing pajamas"
        ),

        # === PAGE 2 - BLAST OFF ===
        PageTemplate(
            page_number=2,
            scene_description="Rocket launch sequence",
            scene_type="action",
            realistic_prompt="""Dynamic launch sequence. The child named {name} visible through transparent rocket dome, wearing shiny white astronaut suit with colorful mission patches, big smile on face, hands on controls. Rocket blasting off with realistic fire and smoke effects mixed with magical rainbow sparkles and stardust trails. View from slight low angle showing rocket ascending through clouds, stars beginning to appear. Motion blur on exhaust, child's excited expression crystal clear. Cinematic lighting, vibrant colors, sense of speed and adventure.""",
            story_text="Wearing a special astronaut suit made just for someone as brave as {name}, our hero climbed into the rocket. With a roar of engines and a burst of colorful sparkles, the rocket zoomed up, up, up into the starry sky!",
            costume="wearing a shiny white astronaut suit with colorful mission patches"
        ),

        # === PAGE 3 - JOURNEY THROUGH SPACE ===
        PageTemplate(
            page_number=3,
            scene_description="Floating through the cosmos",
            scene_type="wonder",
            realistic_prompt="""Awe-inspiring space vista. Interior view showing the child named {name} in astronaut suit floating gently inside the rocket cabin, pressed against a large curved window with hands and face lit by the cosmic glow outside. Through the window: Saturn with glowing rings, colorful planets in cotton-candy pink and electric blue, asteroids with friendly expressions, shooting stars with sparkle trails. Earth is a beautiful blue marble in the distance. Child's reflection visible in glass, expression of pure amazement. Zero-gravity hair floating slightly. Soft interior cabin lighting contrasts with vibrant space colors.""",
            story_text="Through the window, {name} watched Earth get smaller and smaller. The rocket zoomed past glowing planets, spinning asteroids, and shooting stars that waved hello!",
            costume="wearing astronaut suit with clear helmet"
        ),

        # === PAGE 4 - MOON LANDING ===
        PageTemplate(
            page_number=4,
            scene_description="Iconic moon landing moment",
            scene_type="triumph",
            realistic_prompt="""Iconic moon landing moment. The child named {name} in detailed white and gold astronaut suit with clear helmet showing joyful face, mid-bounce on the lunar surface with moon dust particles suspended in air around their boots. One arm raised triumphantly, the other holding a flag with their name. Footprints trail behind them in silver moon dust. Enormous Earth rises on the horizon, glowing blue and green and white against the black star-filled space. Dramatic lighting with sun creating long shadows and golden rim light on the suit. Craters and lunar rocks frame the composition. Frame-worthy, epic cinematic scene.""",
            story_text="The rocket landed gently on the Moon with a soft POOF of moon dust. {name} took one small step onto the silvery surface—and started bouncing in the low gravity! It felt like flying!",
            costume="wearing detailed white and gold astronaut suit with clear helmet"
        ),

        # === PAGE 5 - MEETING THE ALIEN ===
        PageTemplate(
            page_number=5,
            scene_description="First contact with friendly alien",
            scene_type="bonding",
            realistic_prompt="""Heartwarming first contact scene. The child named {name} in astronaut suit kneeling down on moon surface to be at eye level with an adorable small alien creature. The alien has translucent skin with bioluminescent patterns, large expressive opalescent eyes full of hope, softly glowing antenna, holding a tiny broken star-map device. The alien is peeking shyly from behind an iridescent moon rock. Child's gloved hand extended in friendship, kind smile visible through helmet. Gentle lighting creates an intimate moment. Background shows their shadows cast on lunar surface, stars twinkling, soft glow from Earth. Emotional connection visible between characters. Cute and heartwarming, not scary.""",
            story_text="Suddenly, {name} heard a gentle beeping sound. Peeking out from behind a moon rock was a friendly alien with big sparkly eyes! The alien was lost and needed help finding the way home.",
            costume="wearing astronaut suit with clear helmet"
        ),

        # === PAGE 6 - GUIDING THE WAY ===
        PageTemplate(
            page_number=6,
            scene_description="Epic space journey with alien friend",
            scene_type="adventure",
            realistic_prompt="""Epic space journey. The child named {name} and small alien friend visible through rocket dome, both looking at a holographic 3D star map floating between them with glowing constellation lines. Outside the windows: spectacular asteroid field with crystals growing on asteroids, comets with rainbow tails streaming past, a stunning planet made of purple and pink crystals coming into view ahead. The alien is pointing excitedly, child is piloting with focused determination. Interior lit by the hologram's blue glow and the cosmic light from outside. Sense of teamwork and adventure. Rich color palette, dynamic composition with diagonal lines leading to crystal planet.""",
            story_text="Being the kind and clever astronaut that {name} is, our hero used the rocket's special star-map to guide the alien friend through glittering asteroid fields and past dancing comets, all the way to a beautiful planet made of crystals.",
            costume="wearing astronaut suit"
        ),

        # === PAGE 7 - CELEBRATION ON CRYSTAL PLANET ===
        PageTemplate(
            page_number=7,
            scene_description="Joyful alien celebration",
            scene_type="celebration",
            realistic_prompt="""Joyful celebration scene. The child named {name} in astronaut suit standing on crystalline planet surface, surrounded by a crowd of diverse cute aliens of various sizes and colors, all with bioluminescent features, waving, cheering, some holding the child's hands. The alien friend from before is hugging the child's leg happily. An elder alien is placing a magical glowing star pendant around child's neck that radiates warm golden light. Crystal formations frame the scene like natural architecture. In the sky: multiple moons, nebula clouds, the child's rocket in background. Confetti-like stardust falling. Wide shot that captures scale and emotion. Child's face shows joy and pride. Warm, celebratory lighting.""",
            story_text="The alien's family came out to thank {name}—hundreds of friendly aliens waving and cheering! They gave our brave hero a special gift: a glowing star that would light the way home and remind {name} that friends can be found anywhere in the universe.",
            costume="wearing astronaut suit"
        ),

        # === PAGE 8 - JOURNEY HOME ===
        PageTemplate(
            page_number=8,
            scene_description="Triumphant journey home",
            scene_type="return",
            realistic_prompt="""Triumphant journey home. Wide cinematic shot of child's silver rocket flying through space toward Earth, now larger and clearly the destination. A magical glowing star mounted on the rocket's nose like a guiding light. Behind the rocket, the crystal planet is growing distant with tiny alien silhouettes waving. On either side of the rocket, shooting stars and comets create an honor guard formation, leaving glittering trails. Through the rocket's dome window, the child named {name} is visible at the controls, looking confident and happy, the star pendant glowing on their chest. Deep space blues and purples transition to warmer colors as they approach Earth. Sense of completion and homecoming. Epic cinematic composition, volumetric lighting, lens flare from the guiding star.""",
            story_text="With the glowing star guiding the way, {name} flew the rocket back toward Earth. The aliens waved goodbye, and shooting stars seemed to escort the hero home, leaving trails of sparkles across the cosmos.",
            costume="wearing astronaut suit with glowing star pendant"
        ),

        # === PAGE 9 - COMING HOME ===
        PageTemplate(
            page_number=9,
            scene_description="Perfect sunrise homecoming",
            scene_type="peaceful",
            realistic_prompt="""Perfect storybook ending. Golden sunrise scene in the backyard. The rocket is parked on the grass with morning dew sparkling. The child named {name} stepping out in astronaut suit with helmet off tucked under one arm, the magical glowing star pendant still glowing softly around their neck. Child's face shows peaceful happiness and wonder, looking up at the dawn sky where a few stars are still faintly visible. Parents' house in background with warm lights turning on, bedroom window visible. Garden looks slightly magical with flowers sparkling and birds gathering. Footprints from the previous night still visible on dewy grass. Soft golden hour lighting, warm and safe atmosphere. The child looks changed by the adventure, more confident, full of dreams.""",
            story_text="The rocket landed gently in the backyard just as the sun rose. {name} stepped out, still wearing the glowing star. Some adventures take you to the edge of the universe—but the best part is always coming home. What will {name} dream of tonight?",
            costume="wearing astronaut suit with helmet off, glowing star pendant around neck"
        ),

        # === PAGE 10 - DREAMING OF TOMORROW ===
        PageTemplate(
            page_number=10,
            scene_description="Looking up at the stars",
            scene_type="resolution",
            realistic_prompt="""Peaceful bedtime scene. The child named {name} in cozy pajamas sitting at bedroom window, looking up at the night sky filled with stars. The magical glowing star pendant rests on the windowsill, still emitting a soft golden glow. In the sky, a faint outline of the crystal planet and friendly alien can be seen among the constellations, like a secret only the child knows. Child's reflection visible in the window glass, peaceful smile on face. Room is warmly lit with soft nightlight. Stuffed animals and space-themed decorations visible. Feeling of contentment, wonder, and anticipation for future adventures. Intimate, cozy atmosphere with magical undertones.""",
            story_text="That night, {name} sat by the window, watching the stars twinkle in the sky. Somewhere out there, new friends were waving hello. And {name} knew that this was just the beginning of many more cosmic adventures to come.",
            costume="wearing cozy pajamas"
        ),
    ]
)
