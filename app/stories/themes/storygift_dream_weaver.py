"""
StoryGift Dream Weaver Theme - Village of Dreams Adventure.

Complete 10-page story: "[NAME] and the Village of Dreams"
Premium theme featuring magical transformations into different heroes (Chef, Doctor, Pilot, Builder, Firefighter),
the Dream Keeper Lumis, adorable Wisps, the lonely Storm Giant, and the powerful message that every hero lives within.
Optimized for both photorealistic and 3D cartoon pipelines.

CONVERSION OPTIMIZATION:
- Pages 1-5 (Preview): Magical arrival, village reveal, THREE transformation sequences (Chef, Doctor, Pilot - ends mid-flight!)
- Pages 6-10 (Paid): More transformations, Storm Giant emotional reveal, "you were the hero all along" payoff

This is NOT a generic "professions" book - it's a story-driven narrative with emotional depth and a meaningful message.
"""

from app.stories.templates import StoryTemplate, PageTemplate


STORYGIFT_DREAM_WEAVER_THEME = StoryTemplate(
    theme_id="storygift_dream_weaver",
    title_template="{name} and the Village of Dreams",
    description="Every hero you'll ever be already lives inside you",
    default_costume="wearing the magical Cloak of Many Colors that shimmers and shifts with rainbow light",
    protagonist_description="bright hopeful eyes, expression of wonder and determination",
    # Cover page settings for typography-ready composition
    cover_costume="wearing the magnificent Cloak of Many Colors - a flowing magical garment that shimmers with every color of the rainbow, constantly shifting and swirling with starlight patterns",
    cover_header_atmosphere="Dreamy night sky with swirling purple and blue clouds, stars arranged in constellation patterns, multiple moons of different colors, aurora-like ribbons of light",
    cover_magical_elements="Around the child, translucent silhouettes of different heroes emerge from the cloak's magic: a chef with a glowing ladle, a doctor with a stethoscope, a pilot with goggles, a firefighter with water wings, a builder with tools. Small glowing Wisp creatures (adorable cloud-like beings with big eyes) float around happily. The Dream Keeper Lumis (made of starlight and gentle clouds) hovers protectively behind. Sparkles, stardust, and magical transformation particles everywhere.",
    cover_footer_description="Fluffy cloud surface of the Village of Dreams with tiny glowing cottages visible below, soft pink and golden light",
    pages=[
        # === PAGE 1 - THE DREAM KEEPER ARRIVES === (PREVIEW - Magical)
        PageTemplate(
            page_number=1,
            scene_description="Lumis the Dream Keeper appears at the window",
            scene_type="discovery",
            realistic_prompt="""Magical midnight scene. The child {name} in pajamas sitting up in bed, eyes wide with wonder. At the window appears LUMIS the Dream Keeper - a tall ethereal figure made of starlight and cloud wisps, with twin star eyes, flowing misty form, holding a crescent moon staff that glows golden. Stardust trails from Lumis into the starry night sky. Child reaching toward the magical visitor. Bedroom illuminated by Lumis's ethereal glow casting beautiful patterns. Dreamy soft lighting, detailed textures, cinematic lighting.""",
            story_text="{name} was almost asleep when the stars at the window began to swirl and dance. And then HE appeared - Lumis, the Dream Keeper, made of starlight and moonbeams! 'Wake up, brave one,' Lumis said in a voice like wind chimes. 'The Village of Dreams needs a hero tonight. Will you come?'",
            costume="wearing pajamas"
        ),

        # === PAGE 2 - JOURNEY TO THE VILLAGE OF DREAMS === (PREVIEW - Visual Spectacle)
        PageTemplate(
            page_number=2,
            scene_description="Flying through clouds to the magical village",
            scene_type="wonder",
            realistic_prompt="""Breathtaking flight scene. The child {name} in pajamas flying alongside LUMIS (starlight figure with crescent moon staff) through a dreamscape of pink cotton candy and purple lavender clouds. Below them, the VILLAGE OF DREAMS - cottages built on clouds with glowing crystalline walls, stardust streets, tiny bridges. Dark storm clouds swirl above part of the village. WISPS (small adorable cloud-like creatures with big eyes, soft pastel colors) run in panic below. Child holding Lumis's starlight hand, expression of wonder and concern. Epic wide shot, volumetric god rays, detailed textures, cinematic lighting.""",
            story_text="{name} took Lumis's hand and floated right out the window! They flew through clouds that tasted like cotton candy, past stars close enough to touch, all the way to a magical village IN the sky! But {name}'s heart sank - part of the village was in trouble, with storm clouds and scared little creatures running everywhere!",
            costume="wearing pajamas, holding Lumis's starlight hand, flying"
        ),

        # === PAGE 3 - FIRST TRANSFORMATION: THE CHEF === (PREVIEW - Wow Factor!)
        PageTemplate(
            page_number=3,
            scene_description="Transforming into a magical Chef to help",
            scene_type="action",
            realistic_prompt="""Spectacular transformation scene. The child {name} wearing the CLOAK OF MANY COLORS (flowing rainbow fabric with starlight sparkles) mid-transformation into a CHEF. Rainbow light vortex swirling around child. Chef's hat materializing, golden apron with stars appearing, magical glowing ladle in hand. Cold wet WISPS (adorable cloud creatures with big eyes, pastel colors) looking up hopefully, some holding steaming soup cups. Flooded bakery in background with magical sparkly water. Child's face shows exhilarated delight. Dynamic swirling composition, motion blur on transformation, detailed textures, cinematic lighting.""",
            story_text="'The Wisps are cold and hungry!' cried Lumis. 'Here - put this on!' Lumis wrapped a magical CLOAK OF MANY COLORS around {name}'s shoulders. WHOOOOSH! The cloak swirled with rainbow light, and suddenly {name} was wearing a chef's hat and holding a magical golden ladle! Without even thinking, {name} began cooking the most delicious soup the Wisps had ever tasted!",
            costume="mid-transformation into chef outfit - chef hat, golden apron, magical ladle"
        ),

        # === PAGE 4 - SECOND TRANSFORMATION: THE DOCTOR === (PREVIEW - Emotional)
        PageTemplate(
            page_number=4,
            scene_description="Transforming into a Doctor to heal a sick Wisp",
            scene_type="bonding",
            realistic_prompt="""Heartwarming healing scene. The child {name} transformed into DOCTOR by the Cloak of Many Colors, now wearing white coat with rainbow trim. Holding magical glowing stethoscope with heart-shaped end that pulses pink healing light. Gently placing stethoscope on a tiny sick WISP (cloud creature with big eyes, dim glow) in a cloud-bed. Healing golden light spreading through the Wisp. Wisp parents (same style, pastel colors) hovering nearby with hopeful tears. Cozy cottage made of solidified cloud. Intimate warm lighting, emotional connection visible, detailed textures, cinematic lighting.""",
            story_text="A small Wisp was very sick, barely glowing at all. Its parents were so worried! {name} felt the cloak shimmer again, and suddenly was wearing a doctor's coat and holding a magical stethoscope that glowed with healing light. Gently, {name} placed it on the little Wisp's chest, and watched in amazement as the healing warmth spread through the tiny creature. The Wisp opened its eyes and smiled!",
            costume="white doctor coat with rainbow trim, magical glowing stethoscope"
        ),

        # === PAGE 5 - THIRD TRANSFORMATION: THE PILOT === (PREVIEW - CLIFFHANGER!)
        PageTemplate(
            page_number=5,
            scene_description="Transforming into a Pilot for a daring rescue - CLIFFHANGER",
            scene_type="adventure",
            realistic_prompt="""Epic action cliffhanger. The child {name} transformed into PILOT by the Cloak of Many Colors - wearing aviator goggles on forehead, flight jacket with star patches. In cockpit of a magnificent dream-plane (grown from paper airplane, rainbow edges, glowing). Plane just taking off toward a floating cloud-island drifting into dark storm. Stranded WISPS (cloud creatures, big eyes, pastel colors) waving desperately on the island. Lightning illuminates the scene. Child's determined expression, hand on controls. Dramatic contrast between hero's warm glow and storm's darkness. Dynamic diagonal composition, premium action rendering.""",
            story_text="'HELP!' Tiny voices called from far away. A group of Wisps was trapped on a cloud floating toward the terrible storm! {name} grabbed a small paper airplane and felt the cloak's magic surge. WHOOSH! Suddenly {name} was a PILOT with goggles and a flight jacket, and the paper airplane had become a real plane made of dreams! {name} pushed the throttle forward and soared into the sky toward the storm...",
            costume="pilot outfit - aviator goggles on forehead, flight jacket with star patches"
        ),

        # === PAGE 6 - THE RESCUE AND THE BUILDER === (PAID - Action + Teamwork)
        PageTemplate(
            page_number=6,
            scene_description="Successful rescue, then becoming a Builder",
            scene_type="triumph",
            realistic_prompt="""Triumphant dual scene. Upper: The child {name} as PILOT in dream-plane flying from storm, rescued WISPS (cloud creatures, big eyes, pastel colors) cheering in back. Lower: Back in village, child transformed into BUILDER by Cloak of Many Colors - wearing star-decorated hard hat, magical tool belt, holding sparkling blueprints. Broken bridge between cloud-islands. Rainbow building materials floating. WISPS helping with tiny tools. Rainbow bridge forming in background. Dynamic multi-action composition, vibrant colors, detailed textures, cinematic lighting.""",
            story_text="{name} swooped through the edge of the storm and scooped up all the Wisps just in time! But back in the village, the bridge was destroyed! Immediately, the cloak shimmered again. Now {name} was a BUILDER with a magical tool belt, and together with the Wisps, began constructing the most beautiful rainbow bridge anyone had ever seen!",
            costume="builder outfit - star-decorated hard hat, magical tool belt, holding blueprints"
        ),

        # === PAGE 7 - THE FIREFIGHTER WITH WATER WINGS === (PAID - Spectacular Action)
        PageTemplate(
            page_number=7,
            scene_description="Becoming a Firefighter to save the Dream Library",
            scene_type="action",
            realistic_prompt="""Spectacular firefighting action. The Dream Library (stacked glowing dream-books) ablaze with magical purple and orange flames. The child {name} transformed into FIREFIGHTER by Cloak of Many Colors - wearing golden helmet with star, water-shimmer coat, and incredible WATER WINGS extending from back. Flying mid-air, directing water streams from wing-tips at flames. Expression of fierce determination. Dream-books flying to escape. WISPS (cloud creatures, pastel colors) operating small cloud-hoses below. Steam and spray, dramatic fire-water contrast. Dynamic superhero action pose, detailed textures, cinematic lighting.""",
            story_text="Oh no! The Dream Library was on FIRE! Precious dream-books needed saving! The cloak swirled one more time, and {name} became a FIREFIGHTER with wings made of ACTUAL WATER! Flying through the air, {name} directed streams of magical water at the flames while rescuing books left and right. The Wisps cheered as their library was saved!",
            costume="firefighter outfit - golden helmet with star, water-shimmer coat, WINGS MADE OF FLOWING WATER"
        ),

        # === PAGE 8 - MEETING THE STORM GIANT === (PAID - Emotional Revelation)
        PageTemplate(
            page_number=8,
            scene_description="Discovering the Storm Giant is actually lonely and sad",
            scene_type="bonding",
            realistic_prompt="""Emotional revelation scene. The child {name} (firefighter outfit fading back to Cloak of Many Colors) approaching a STORM GIANT sitting on a distant cloud-mountain, head in hands, crying. Giant made of dark clouds and lightning but not scary - deeply sad. Each tear becomes lightning, each sob rumbles as thunder. Giant looking up with surprise and desperate hope at the approaching child. Child's compassionate expression, walking through storm unafraid. Cloak glowing protectively. LUMIS (starlight figure, crescent moon staff) watching knowingly behind. Soft light breaking through near child. Intimate emotional peak.""",
            story_text="{name} flew toward the heart of the storm, expecting something scary. Instead, there sat an enormous Storm Giant made of clouds and lightning... and he was CRYING. Each tear became a thunderbolt, each sob became wind. 'Why does nobody want to be my friend?' the giant sniffled. {name}'s heart melted. The storm wasn't mean - it was just lonely.",
            costume="firefighter outfit fading back to Cloak of Many Colors, glowing with gentle light"
        ),

        # === PAGE 9 - BECOMING THEMSELVES === (PAID - Message Payoff)
        PageTemplate(
            page_number=9,
            scene_description="The most powerful transformation: becoming themselves",
            scene_type="triumph",
            realistic_prompt="""The most powerful moment. The child {name} in pajamas (Cloak dissolved) standing before the STORM GIANT, now GLOWING with inner golden light. Around the child, ghostly golden silhouettes of all heroes (Chef, Doctor, Pilot, Builder, Firefighter) swirl and MERGE INTO child's glowing heart. Reaching up to hold the giant's hand - offering friendship. Giant's expression transforming from sad to hopeful, storm clouds lightening. Lightning becoming sparkles. LUMIS speaking wisely nearby. No costume needed - the heroes are WITHIN. Transcendent lighting, emotional peak, frame-worthy spiritual quality.""",
            story_text="Something magical happened. The cloak began to glow brighter and brighter, and all the heroes {name} had become - the Chef, the Doctor, the Pilot, the Builder, the Firefighter - swirled around and flowed right INTO {name}'s heart! The cloak faded away, and {name} stood there in just pajamas, but GLOWING. 'You see,' smiled Lumis, 'the cloak didn't give you powers. It only showed you what was ALWAYS inside you.' {name} reached up and took the giant's hand. 'Would you like to be friends?'",
            costume="pajamas, but glowing with inner golden light, all hero silhouettes merged within"
        ),

        # === PAGE 10 - THE STAR OF MANY HEARTS === (PAID - Resolution)
        PageTemplate(
            page_number=10,
            scene_description="Celebration, the pendant gift, and waking up with magic",
            scene_type="resolution",
            realistic_prompt="""Perfect fairytale ending. Dual scene. UPPER: Village celebration - storm cleared, stars shining, WISPS (cloud creatures, pastel colors) dancing with sparkle confetti. STORM GIANT (now friendly, soft white clouds, gentle smile) playing with young Wisps. LUMIS placing the STAR OF MANY HEARTS pendant around child {name}'s neck - star-shaped with colored gems (red, pink, blue, orange, gold) for each hero. LOWER: Child waking in bed, morning sunlight, the pendant REAL on the pillow, glowing softly. Small Wisp waving from behind a cloud outside window. Warm satisfying conclusion. Frame-worthy split-scene, detailed textures, cinematic lighting.""",
            story_text="The Storm Giant smiled for the first time in centuries. The village celebrated, and even the giant was invited to the party! Before Lumis took {name} home, the Wisps gave a special gift - the Star of Many Hearts, a pendant with gems for every hero {name} had been. When {name} woke up in bed, it could have been a dream... except the pendant was RIGHT THERE on the pillow, softly glowing. {name} smiled. The heroes would always be inside, ready whenever someone needed help.",
            costume="pajamas, wearing the Star of Many Hearts pendant with multiple colored gems"
        ),
    ]
)
