"""
StoryGift Spy Mission Theme - Converted to Magictales format.

Complete 10-page story: "Operation: Lunchbox"
Converted from StoryGift's 5 scenes × 2 panels structure
Preserves all original prompts, dialogue, and story narrative
"""

from app.stories.templates import StoryTemplate, PageTemplate


STORYGIFT_SPY_MISSION_THEME = StoryTemplate(
    theme_id="storygift_spy_mission",
    title_template="{name}: Operation Lunchbox",
    description="A high-stakes spy adventure on the ultimate playground mission",
    default_costume="wearing tactical spy gear",
    protagonist_description="focused, determined spy agent with keen eyes and quick reflexes",
    # Cover page settings for typography-ready composition
    cover_costume="wearing sleek tactical spy gear with a utility belt, spy sunglasses pushed up on forehead, and cool gadget watch",
    cover_header_atmosphere="High-tech spy headquarters holographic displays and sleek dark metallic sky with digital grid patterns, cinematic spy movie atmosphere",
    cover_magical_elements="Agent Zero the robot companion stands loyally beside the child. High-tech gadgets and gizmos surround the scene. Laser grid patterns in the background (not crossing face). Cool spy movie lighting effects.",
    cover_footer_description="Futuristic metallic floor with glowing tech patterns, spy equipment scattered around",
    pages=[
        # === SCENE 1 - MISSION BRIEFING ===

        # PAGE 1 (Scene 1 - Left Panel)
        PageTemplate(
            page_number=1,
            scene_description="Secret mission briefing",
            scene_type="briefing",
            realistic_prompt="""Wide establishing shot. A futuristic playground with high-tech jungle gyms. The child spy named {name} is crouching behind a slide, looking at a map. Agent Zero (a clumsy robot with one wheel and a bowtie) is trembling behind them. Cinematic spy movie lighting. The child is wearing tactical spy gear.""",
            story_text="The mission briefing was crystal clear: retrieve the Golden Lunchbox before recess ended. For top-tier spy {name}, the playground was a jungle of obstacles, but this was just another Tuesday. Agent Zero beeped nervously, his single wheel wobbling with fear.",
            costume="wearing tactical spy gear"
        ),

        # PAGE 2 (Scene 1 - Right Panel)
        PageTemplate(
            page_number=2,
            scene_description="Aerial reconnaissance",
            scene_type="action",
            realistic_prompt="""Wide angle action shot. The child spy named {name} is sliding down a zip-line high above the playground. Below, other children (background characters) are playing on swings. Agent Zero (a robot with one wheel and a bowtie) is rolling frantically on the ground trying to keep up. The playground extends into the distance. The child is wearing tactical spy gear.""",
            story_text="Without hesitation, Agent {name} deployed the zip-line technique for aerial reconnaissance. Flying high above the playground battlefield, the target came into view. 'Target acquired,' {name} reported coolly, while poor Agent Zero rolled frantically below, trying to keep pace.",
            costume="wearing tactical spy gear"
        ),

        # === SCENE 2 - SANDBOX SECTOR ===

        # PAGE 3 (Scene 2 - Left Panel)
        PageTemplate(
            page_number=3,
            scene_description="Dr. Fluff's fortress",
            scene_type="stealth",
            realistic_prompt="""Low angle shot looking up at a sandcastle. Dr. Fluff (a fluffy white Persian cat wearing a monocle) is sitting at the top like a fortress commander. Red strings (representing laser beams) are crisscrossing the sandbox. The scene has dramatic spy movie lighting. The child spy is wearing tactical spy gear.""",
            story_text="The Sandbox Sector was under the control of the notorious Dr. Fluff. The fluffy white Persian cat, monocle gleaming menacingly, sat atop his Sand Castle of Doom like an evil mastermind. Laser beams of red yarn crisscrossed the entire area - one wrong move would spell disaster.",
            costume="wearing tactical spy gear"
        ),

        # PAGE 4 (Scene 2 - Right Panel)
        PageTemplate(
            page_number=4,
            scene_description="Navigating the laser maze",
            scene_type="infiltration",
            realistic_prompt="""Wide overhead shot. The entire sandbox looks like a giant maze. The child spy named {name} is crawling through trench-like paths in the sand. Multiple red strings (laser beams) form a complex web across the entire sandbox. Dr. Fluff (white Persian cat with monocle) is watching from the far corner. The child is wearing tactical spy gear.""",
            story_text="Agent {name} employed advanced infiltration techniques, army-crawling through the sandy trenches. The laser maze was complex, but years of spy training had prepared {name} for exactly this moment. 'Easy peasy,' {name} whispered confidently, despite Dr. Fluff's watchful glare.",
            costume="wearing tactical spy gear"
        ),

        # === SCENE 3 - GENERAL NUTKINS CONFRONTATION ===

        # PAGE 5 (Scene 3 - Left Panel)
        PageTemplate(
            page_number=5,
            scene_description="Enemy henchman appears",
            scene_type="confrontation",
            realistic_prompt="""Mid shot confrontation. A squirrel wearing a mini eyepatch (General Nutkins) is standing on a bucket, blocking the path with an aggressive stance. The child spy named {name} is reaching into their utility belt, ready for action. Intense standoff atmosphere with dramatic lighting. The child is wearing tactical spy gear.""",
            story_text="Suddenly, a shadow blocked the path to victory! It was General Nutkins, Dr. Fluff's most trusted henchman. The acorn-hoarding squirrel chittered aggressively, his tiny eyepatch glinting as he blocked the route to the castle gate. Time to deploy the secret weapon!",
            costume="wearing tactical spy gear"
        ),

        # PAGE 6 (Scene 3 - Right Panel)
        PageTemplate(
            page_number=6,
            scene_description="Secret weapon deployment",
            scene_type="action",
            realistic_prompt="""Wide action shot. The child spy named {name} acts quickly, firing a pink 'Sticky Gum Blaster' weapon. The gum flies across the frame toward General Nutkins (squirrel with eyepatch) who gets stuck to a wooden post. The path ahead is now clear, leading towards the castle gate in the background. The child is wearing tactical spy gear.""",
            story_text="Agent {name} moved with lightning speed, drawing the legendary Sticky Gum Blaster from the utility belt. 'Chew on this!' {name} declared, firing a perfectly aimed pink projectile. General Nutkins found himself firmly stuck to a wooden post, clearing the path to victory.",
            costume="wearing tactical spy gear"
        ),

        # === SCENE 4 - THE SPINNING BRIDGE ===

        # PAGE 7 (Scene 4 - Left Panel)
        PageTemplate(
            page_number=7,
            scene_description="Final obstacle revealed",
            scene_type="challenge",
            realistic_prompt="""Wide shot. A spinning log bridge over a puddle of water (imagined as a shark tank with toy sharks). The Golden Lunchbox is glowing like a treasure on the other side. Dr. Fluff (white Persian cat with monocle) is watching from a high tower. Agent Zero (robot with one wheel and bowtie) is looking worried. The child spy is wearing tactical spy gear.""",
            story_text="With the guards neutralized, the path to the Golden Lunchbox was finally clear. But Dr. Fluff had saved his most diabolical trick for last - the dreaded spinning log bridge over the shark-infested moat! Agent Zero calculated frantically: 'Probability of falling: 99%!'",
            costume="wearing tactical spy gear"
        ),

        # PAGE 8 (Scene 4 - Right Panel)
        PageTemplate(
            page_number=8,
            scene_description="Crossing the impossible bridge",
            scene_type="heroic",
            realistic_prompt="""Wide angle action shot. The child spy named {name} is running across a spinning log bridge with perfect balance. Below, the puddle acts as a moat filled with toy sharks. On the far side, the Golden Lunchbox sits on a pedestal like the ultimate prize. Dr. Fluff (white Persian cat with monocle) is watching from a high vantage point in the background. The child is wearing tactical spy gear.""",
            story_text="But Agent {name} was no ordinary spy. With the confidence of a true professional, {name} sprinted across the spinning bridge, maintaining perfect balance despite the impossible odds. 'Never tell me the odds,' {name} called back heroically, eyes fixed on the golden prize ahead.",
            costume="wearing tactical spy gear"
        ),

        # === SCENE 5 - MISSION ACCOMPLISHED ===

        # PAGE 9 (Scene 5 - Left Panel)
        PageTemplate(
            page_number=9,
            scene_description="Victory achieved",
            scene_type="triumph",
            realistic_prompt="""Low angle hero shot. The child spy named {name} holds the Golden Lunchbox high above their head like a trophy of victory. Sunlight beams catch the metal, creating a glorious moment. Agent Zero (robot with one wheel and bowtie) is doing a happy victory dance. The child is wearing tactical spy gear.""",
            story_text="VICTORY! The Golden Lunchbox was finally secured. As the recess bell rang in the distance, Agent {name} held the prize high above their head like a champion. The taste of success was sweet, and Agent Zero performed his signature victory dance, beeping with joy.",
            costume="wearing tactical spy gear"
        ),

        # PAGE 10 (Scene 5 - Right Panel)
        PageTemplate(
            page_number=10,
            scene_description="Friendship and peace",
            scene_type="resolution",
            realistic_prompt="""Wide celebratory shot. The child spy named {name} is sitting on a park bench with Agent Zero (robot with one wheel and bowtie) and Dr. Fluff (white Persian cat with monocle, now friendly). They are all sharing a peanut butter sandwich together. The sun is setting behind the playground, casting long golden shadows. A feeling of friendship, victory, and contentment. The child is wearing a school uniform with sunglasses.""",
            story_text="Mission accomplished! As the imaginary spy world faded back to reality, {name} discovered the greatest treasure of all - new friends. Agent Zero, Dr. Fluff, and {name} shared a peanut butter sandwich as the sun set over their playground kingdom. 'Same time tomorrow?' asked {name} with a grin.",
            costume="wearing a school uniform with sunglasses"
        ),
    ]
)