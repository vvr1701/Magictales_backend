"""
StoryGift Mighty Guardian Theme - Superhero Adventure.

Complete 10-page story: "[NAME] The Mighty Guardian"
Premium theme featuring superhero transformation, heroic deeds, and inner strength.
Optimized for both photorealistic and 3D cartoon pipelines.
"""

from app.stories.templates import StoryTemplate, PageTemplate


STORYGIFT_MIGHTY_GUARDIAN_THEME = StoryTemplate(
    theme_id="storygift_mighty_guardian",
    title_template="{name} The Mighty Guardian",
    description="Every child is a hero—now they can see it",
    default_costume="wearing a custom superhero costume in metallic blue and red with gold accents and a flowing cape",
    protagonist_description="confident heroic expression, bright determined eyes",
    # Cover page settings for typography-ready composition
    cover_costume="wearing a metallic blue and red superhero suit with gold accents, flowing cape billowing dramatically behind, gold emblem on chest",
    cover_header_atmosphere="Dramatic city skyline at sunset with lens flare, epic clouds in orange and purple hues",
    cover_magical_elements="Energy auras radiating from the body in gold and blue, motion lines suggesting speed and power. Dynamic flying pose with one fist forward in classic superhero stance.",
    cover_footer_description="City rooftops below with twinkling lights, dynamic perspective looking up at the hero",
    pages=[
        # === PAGE 1 - THE DISCOVERY ===
        PageTemplate(
            page_number=1,
            scene_description="Discovering the magical crystal",
            scene_type="discovery",
            realistic_prompt="""Magical discovery moment. The child named {name} in everyday clothes stands in a park or backyard, looking up with surprise and wonder as a glowing crystalline object with geometric shape and pulsing rainbow energy descends from a beam of light and hovers just above their outstretched hands. The moment just before contact. Golden afternoon light, leaves and grass gently blown by mystical wind, child's hair flowing. Other kids playing in far background, unaware of the magic. The object casts colorful reflections on child's amazed face. Sense of destiny and magic, warm atmosphere.""",
            story_text="{name} was having an ordinary day—playing, laughing, being amazing—when something extraordinary happened. A mysterious glowing object fell from the sky and landed right in {name}'s hands!",
            costume="wearing everyday clothes, t-shirt and jeans"
        ),

        # === PAGE 2 - THE TRANSFORMATION ===
        PageTemplate(
            page_number=2,
            scene_description="Superhero transformation",
            scene_type="transformation",
            realistic_prompt="""Epic transformation sequence. The child named {name} surrounded by swirling energy vortex as the crystal in their hands explodes into ribbons of light that wrap around them, forming a superhero costume. Mid-transformation view showing lower body with the new blue and red suit with gold boots materializing, upper body still in regular clothes but surrounded by glowing energy. Child's expression is exhilarated surprise, arms outstretched, floating slightly off the ground. Energy particles, light trails, dynamic movement. Background blurred by the energy burst. Dramatic backlighting, vibrant colors, sense of power awakening. Split-second frozen moment of magical change.""",
            story_text="The moment {name} touched it, the crystal began to glow even brighter! It transformed into a magnificent superhero costume made specially for someone as brave and kind as {name}. It was time to become... THE MIGHTY GUARDIAN!",
            costume="mid-transformation from regular clothes to superhero suit"
        ),

        # === PAGE 3 - DISCOVERING POWERS ===
        PageTemplate(
            page_number=3,
            scene_description="Powers showcase",
            scene_type="action",
            realistic_prompt="""Powers showcase composition. The child named {name} in full superhero costume with metallic blue and red suit, gold accents, and flowing cape, performing multiple feats in artistic composition. Foreground shows child mid-flight with cape flowing and arms forward, leaving a trail of golden energy. Background layers show echo images of the same child: lifting a car with ease demonstrating strength, running with speed blur effects creating streaks, surrounded by protective energy shield. Central focus on child's determined but joyful face. Urban park setting with impressed onlookers in background. Dynamic diagonal composition, motion blur on movement elements, energy effects in gold and blue, dramatic lighting from multiple angles. Movie poster quality.""",
            story_text="{name} discovered amazing powers—super strength to lift anything, super speed to run faster than the wind, and the ability to fly through the clouds! But the greatest power of all was {name}'s brave and caring heart.",
            costume="wearing full superhero costume with metallic blue and red suit, gold accents, flowing cape"
        ),

        # === PAGE 4 - THE CALL FOR HELP ===
        PageTemplate(
            page_number=4,
            scene_description="Responding to a call for help",
            scene_type="heroic",
            realistic_prompt="""Heroic response moment. Low angle shot looking up at enormous oak tree with a tiny frightened kitten visible on the highest branch, meowing for help, sunlight filtering through leaves. In foreground, the child named {name} in superhero costume looking up with determination and compassion, one hand shielding eyes from sun, other hand on hip in confident pose. Below, a worried child who owns the kitten is pointing up with tears. The composition emphasizes the height and challenge. Guardian is about to leap into action. Golden afternoon light, detailed tree bark and leaves, emotional storytelling through body language.""",
            story_text="Suddenly, {name} heard a call for help! A kitten was stuck at the very top of the tallest tree, too scared to climb down. 'Don't worry, little friend,' called {name}, 'I'm on my way!'",
            costume="wearing superhero costume with cape"
        ),

        # === PAGE 5 - THE RESCUE ===
        PageTemplate(
            page_number=5,
            scene_description="Triumphant kitten rescue",
            scene_type="bonding",
            realistic_prompt="""Triumphant rescue scene. The child named {name} in superhero costume descending gracefully through the air in protective pose, cradling a small orange kitten against their chest with both arms. The kitten is nuzzling into child's neck, tiny paw on child's cheek, both looking peaceful and safe. Child's cape billows upward from the descent, golden energy particles trail from boots. Dappled sunlight through tree leaves creates beautiful lighting, grateful crowd of kids below looking up and cheering with raised arms. Gentle landing moment, dust particles just starting to disturb on ground. Warm, heartwarming atmosphere, emotional connection between hero and rescued animal. Soft focus background, sharp detailed foreground.""",
            story_text="With a mighty leap, {name} soared up, up, up! Gently cradling the grateful kitten, our hero flew back down, landing softly on the ground. The kitten purred and nuzzled {name}'s cheek. Mission accomplished!",
            costume="wearing superhero costume with cape billowing"
        ),

        # === PAGE 6 - SAVING THE TOWN ===
        PageTemplate(
            page_number=6,
            scene_description="Epic storm battle",
            scene_type="climax",
            realistic_prompt="""Epic sky battle. Dramatic wide shot of the child named {name} flying high in stormy sky, both arms extended forward, energy beams shooting from hands toward massive dark purple storm clouds, physically pushing them back. Child's cape whips dramatically in wind, rain droplets frozen mid-air around them, lightning illuminates scene from within clouds. Below, small town visible with lights turning on as people look up in hope. Child's face shows intense concentration and determination, glowing with protective power. Cinematic storm lighting with dark dramatic clouds contrasted with golden hero glow. Wind effects on costume and hair, rain streaming past. Scale shows child as small but mighty against enormous weather system.""",
            story_text="But the day wasn't over! Dark storm clouds gathered, and {name} heard that a big storm was heading toward the town. Using incredible powers, {name} flew high into the sky and used super strength to gently push the storm clouds away from the town!",
            costume="wearing superhero costume, cape whipping in wind"
        ),

        # === PAGE 7 - VICTORY CELEBRATION ===
        PageTemplate(
            page_number=7,
            scene_description="Town celebrates the hero",
            scene_type="celebration",
            realistic_prompt="""Victory celebration. The child named {name} in superhero costume hovering or standing in town square, surrounded by cheering crowd of diverse adults and children throwing confetti, waving banners with child's initial, holding balloons. Enormous vibrant rainbow arcs across clearing sky behind hero. Sun rays breaking through clouds create dramatic god rays. The child is waving with humble smile, slightly embarrassed but proud expression. Mayor offering a golden key to the city. Reporters with cameras, kids asking for autographs. Banner reads 'Thank you Guardian!' Festive, joyful atmosphere, warm golden hour lighting, confetti catching light. Wide celebration shot with hero as focal point. Rich details throughout.""",
            story_text="The sun broke through the clouds, and a beautiful rainbow appeared. The whole town came out to cheer for {name} THE MIGHTY GUARDIAN! Flags waved, confetti flew, and everyone celebrated their amazing hero!",
            costume="wearing superhero costume, standing heroically"
        ),

        # === PAGE 8 - RETURNING HOME ===
        PageTemplate(
            page_number=8,
            scene_description="Power returning to crystal",
            scene_type="transformation",
            realistic_prompt="""Peaceful transformation return. Twilight scene in home's backyard as the child named {name} lands gently. The superhero costume dissolves into streams of golden light that flow into a crystal pendant on a delicate chain around their neck. Half transformed showing boots and cape already turned to light particles, regular clothes visible underneath the fading costume. Child looking down at the glowing crystal with soft, peaceful smile, one hand touching it gently. Family home visible with warm lights in windows, parents' silhouettes watching from window with pride. Purple-orange sunset sky, first stars appearing. Magical atmosphere with particle effects. Sense of secret identity and double life. Quiet emotional moment after action.""",
            story_text="As the day ended, {name} flew home. The superhero costume began to glow and transformed back into the crystal, which now hung on a special chain around {name}'s neck. The powers would always be there when needed.",
            costume="mid-transformation from superhero costume back to regular clothes, crystal pendant forming"
        ),

        # === PAGE 9 - THE SECRET ===
        PageTemplate(
            page_number=9,
            scene_description="Family dinner with a secret",
            scene_type="intimate",
            realistic_prompt="""Heartwarming family dinner scene. Warm dining room with golden overhead light creating intimate atmosphere. The child named {name} in regular clothes sitting at dinner table, hand subtly touching the glowing crystal pendant barely visible under their shirt collar, small knowing smile on face. Parents and siblings talking animatedly, sharing food, laughing warmly. Through window behind them, night sky shows a single bright star twinkling. On the wall, child's drawings include a small superhero sketch that only observant viewers would notice. The crystal emits a very subtle glow that only the viewer can see. Normal family moment but charged with secret knowledge. Cozy, love-filled atmosphere. Sharp focus on child's secret smile and glowing crystal, soft focus on background family. Emotional, frame-worthy final image about inner heroism.""",
            story_text="That night at dinner, {name}'s family talked about their day. When they asked what {name} did, our hero just smiled and touched the crystal under their shirt. Being a hero isn't about powers—it's about being brave, kind, and helping others. And {name}? {name} was ALWAYS a hero.",
            costume="wearing regular clothes, crystal pendant hidden under shirt"
        ),

        # === PAGE 10 - LOOKING TO TOMORROW ===
        PageTemplate(
            page_number=10,
            scene_description="Ready for tomorrow's adventures",
            scene_type="resolution",
            realistic_prompt="""Perfect ending. The child named {name} standing at bedroom window at night in pajamas, looking out at the city skyline in the distance. The crystal pendant glows softly around their neck. In the night sky, a shooting star streaks across. Child's reflection in the window glass shows a subtle superhero silhouette overlay, hinting at their secret identity. Room is cozy with superhero posters on wall, toys scattered. Outside, the city is peaceful and safe. Child's expression shows quiet confidence and readiness for whatever adventure comes next. Magical, hopeful atmosphere. The sense that this is just the beginning of many more heroic adventures.""",
            story_text="Before bed, {name} looked out the window at the peaceful town below. Somewhere out there, someone might need help tomorrow. And the Mighty Guardian would be ready. Because true heroes never stop being brave, kind, and ready to help—just like {name}.",
            costume="wearing pajamas, crystal pendant glowing around neck"
        ),
    ]
)
