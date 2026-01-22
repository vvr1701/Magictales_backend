"""
StoryGift Birthday Magic Theme - Magical Birthday Wish.

Complete 10-page story: "[NAME]'s Magical Birthday Wish"
Premium theme featuring birthday celebration, wish fulfillment, and family love.
Optimized for both photorealistic and 3D cartoon pipelines.
"""

from app.stories.templates import StoryTemplate, PageTemplate


STORYGIFT_BIRTHDAY_MAGIC_THEME = StoryTemplate(
    theme_id="storygift_birthday_magic",
    title_template="{name}'s Magical Birthday Wish",
    description="The birthday gift that makes their wildest birthday wishes come true",
    default_costume="wearing a special birthday outfit with a golden birthday crown",
    protagonist_description="bright joyful eyes, expression of pure happiness and wonder",
    # Cover page settings for typography-ready composition
    cover_costume="wearing a golden birthday crown and festive party outfit, hands clasped in wish-making pose",
    cover_header_atmosphere="Magical sparkles and confetti swirling in pink, purple, and gold against a dreamy bokeh background of party lights",
    cover_magical_elements="Sitting before an elaborate multi-tiered birthday cake with lit candles creating warm glow on face. Eyes closed in wish-making moment. Swirling magical sparkles and confetti emerging from the candles. Presents wrapped in shimmering paper stacked around.",
    cover_footer_description="Colorful balloons floating with glowing strings, magical golden hour party atmosphere",
    pages=[
        # === PAGE 1 - THE SPECIAL DAY ===
        PageTemplate(
            page_number=1,
            scene_description="Magical birthday morning",
            scene_type="discovery",
            realistic_prompt="""Magical morning awakening. The child named {name} waking up in cozy bedroom, sitting up in bed with big excited smile, sunlight streaming through window creating god rays filled with dancing dust particles that look like tiny sparkles. Room decorated with birthday decorations including banner saying 'Happy Birthday!' and balloons tied to bedpost, presents on a table. Child wearing birthday pajamas, stretching arms up in joy. Through window, the world outside looks especially beautiful with bluebird on windowsill, flowers in bloom, sunshine golden and warm. Calendar on wall has today's date circled with hearts. Magical warm lighting, sense of excitement and specialness, everything has a subtle celebratory glow. Cozy bedroom with soft morning light.""",
            story_text="Today was the most special day of the year—{name}'s birthday! The sun seemed to shine a little brighter, the birds sang a little sweeter, and even the morning air felt like it was full of magic, just for {name}.",
            costume="wearing birthday pajamas"
        ),

        # === PAGE 2 - BIRTHDAY BREAKFAST ===
        PageTemplate(
            page_number=2,
            scene_description="Family birthday breakfast",
            scene_type="bonding",
            realistic_prompt="""Warm family breakfast scene. Bright kitchen with morning light through window. The child named {name} sitting at breakfast table wearing golden paper birthday crown with gems, hands clasped together, eyes scrunched closed making a wish. In front of them: stack of fluffy pancakes with strawberries, whipped cream, chocolate chips, single lit candle on top casting warm glow. Parents standing behind with loving expressions, hands on child's shoulders, other family members around table smiling warmly. Kitchen decorated with homemade birthday decorations, 'Happy Birthday' banner visible. Golden sparkles beginning to swirl around the candle flame subtly. Cozy, love-filled family atmosphere, warm golden light, sense of intimacy and tradition.""",
            story_text="At breakfast, {name}'s family had prepared a special birthday surprise—pancakes stacked high with {name}'s favorite toppings, and right on top was a single candle. 'Make a wish before breakfast!' said Mom with a warm smile. {name} closed their eyes and wished with all their heart.",
            costume="wearing birthday crown and party outfit"
        ),

        # === PAGE 3 - THE BIRTHDAY FAIRY ===
        PageTemplate(
            page_number=3,
            scene_description="Twinkle the birthday fairy appears",
            scene_type="revelation",
            realistic_prompt="""Fairy appearance magic. The child named {name} at breakfast table, mouth formed in surprised 'O', looking at a small adorable fairy hovering above the pancakes where the candle smoke is transforming into the magical being. Twinkle the fairy is made of golden and pink sparkles, tiny with delicate iridescent wings, wearing a dress made of wishes and confetti, carrying a small wand topped with a star. Trails of glitter and magical smoke curl around her. Family members in background equally amazed, pointing with delighted expressions. Kitchen lighting now has magical quality with floating sparkles everywhere, rainbow light refractions on surfaces. The pancake candle is out, smoke still rising and partially formed into magic. Whimsical, joyful energy, beautiful particle effects.""",
            story_text="When {name} opened their eyes and blew out the candle, something incredible happened! The wish didn't just vanish—it transformed into a shimmering, giggling fairy made of birthday sparkles! 'Hello {name}! I'm Twinkle, your Birthday Wish Fairy, and today, your wishes REALLY come true!'",
            costume="wearing birthday crown"
        ),

        # === PAGE 4 - HOUSE TRANSFORMATION ===
        PageTemplate(
            page_number=4,
            scene_description="House transforms into party palace",
            scene_type="transformation",
            realistic_prompt="""House transformation spectacle. Wide shot of living room mid-magical transformation. Furniture rearranging itself with sparkle trails, walls expanding and decorating themselves with streamers and lights, ceiling rising to accommodate an enormous indoor bouncy castle in rainbow colors. Chocolate fountain erupting in corner with actual chocolate flowing, presents of all sizes floating and spinning gently in the air wrapped in shimmering paper. The child named {name} in center with arms spread wide, spinning with joy, Twinkle the fairy flying circles around them leaving sparkle trails. Family members reacting with delight and amazement. Dynamic composition showing transformation in action, motion blur on moving objects, magical particle effects everywhere, vibrant party colors, dramatic lighting from multiple magic sources. Feels like a movie transformation sequence.""",
            story_text="Twinkle sprinkled fairy dust everywhere, and suddenly {name}'s house began to transform! The living room turned into a magnificent party palace with floating presents, a chocolate fountain taller than Dad, and a bouncy castle that reached the ceiling!",
            costume="wearing birthday outfit with crown"
        ),

        # === PAGE 5 - FRIENDS APPEAR ===
        PageTemplate(
            page_number=5,
            scene_description="Friends appear and pets can talk",
            scene_type="celebration",
            realistic_prompt="""Party coming to life. Chaotic joyful scene with the child named {name}'s diverse group of friends materializing in bursts of colorful confetti and sparkles, each arrival creating a small explosion of their favorite color. Friends mid-laugh, some hugging the child, all wearing party hats and fun outfits. In foreground, family dog and cat with subtle magical glow around them, mouths open as if talking animatedly, expressions funny and expressive. In background, goldfish bowl with goldfish wearing tiny top hat, bubbles forming into speech bubble shapes. Twinkle flying above orchestrating the magic with wand leaving rainbow trails. Balloons, streamers, presents everywhere. Sense of controlled chaos and pure fun, everyone's faces showing genuine joy. Vibrant party colors, dynamic multiple focal points composition.""",
            story_text="But Twinkle wasn't done! 'What else did you wish for, {name}?' With a wave of her wand, {name}'s friends appeared in a burst of confetti and laughter, ready to celebrate! And look—the family pets could talk for the day! Even the shy goldfish was telling jokes!",
            costume="wearing birthday outfit surrounded by friends"
        ),

        # === PAGE 6 - THE BEST PARTY EVER ===
        PageTemplate(
            page_number=6,
            scene_description="Dance party peak moment",
            scene_type="action",
            realistic_prompt="""Dance party peak moment. The child named {name} in center of dance floor which is the transformed living room, in mid-dance pose with big smile, surrounded by dancing friends, everyone jumping, spinning, and celebrating. Twinkle the fairy conducting the party magic, wand raised, creating a light show with rainbow beams and floating musical notes made of sparkles. Table visible with partially eaten magical cake that shows rainbow layers inside, each slice a different flavor. Decorations are at peak party chaos with balloons bouncing, confetti perpetually falling, streamers swirling magically. DJ booth made of magical presents with lights flashing. Pet dog dancing on hind legs adorably. Action and celebration at maximum energy. Vibrant party atmosphere with dynamic movement throughout.""",
            story_text="The party was amazing! {name} and friends played every game imaginable. They danced with the fairy, ate magical birthday cake that tasted like every flavor they wished for, and when {name} made one more secret wish... Twinkle smiled knowingly and said, 'This one is extra special. Come with me!'",
            costume="wearing birthday outfit with crown, dancing"
        ),

        # === PAGE 7 - FAMILY MEMORIES ===
        PageTemplate(
            page_number=7,
            scene_description="Family shares favorite memories",
            scene_type="intimate",
            realistic_prompt="""Emotional family moment. Intimate scene in softly lit room away from party noise with muffled celebration sounds visible through doorway. The child named {name} sitting on couch surrounded by family members in a close circle including parents, siblings, grandparents. Each family member is sharing, and their spoken words literally appear in the air as beautiful glowing text and images. Floating photographs of memories, words like 'kind', 'brave', 'creative' in golden script, little scenes playing in magical bubbles showing moments from the past year. Child's face shows overwhelmed happiness, eyes shining with happy tears. Twinkle hovering above, wand creating the memory visualization magic. Warm, soft lighting like golden hour indoors, intimate composition, everyone leaning in close. This is the emotional heart of the story.""",
            story_text="Twinkle led {name} to a quiet room, and with the gentlest magic, created something no gift could ever buy—a perfect moment. There, {name}'s family stood together, and one by one, they each shared their favorite memory of {name} from the past year. Every word sparkled in the air like stars.",
            costume="wearing birthday outfit, sitting with family"
        ),

        # === PAGE 8 - MAGICAL TAPESTRY ===
        PageTemplate(
            page_number=8,
            scene_description="Memories woven into magical tapestry",
            scene_type="wonder",
            realistic_prompt="""Magical tapestry creation. Living room at twilight, party winding down peacefully. Above everyone's heads, Twinkle is weaving together magical ribbons of light in different colors. Each ribbon contains miniature scenes from the day's celebration including pancake breakfast, friends arriving, dancing, family moment, playing like a moving photo album. The ribbons weave into an elaborate glowing tapestry floating like aurora borealis, casting beautiful multi-colored light on everyone below. The child named {name} standing in center looking up with wonder and contentment, arms slightly raised in awe. Friends and family gathered around also looking up, faces illuminated by the magic, some holding each other. Presents and party remnants visible but peaceful now. Through windows, stars are appearing in the evening sky. Sense of day well spent, magic being preserved. Beautiful volumetric lighting, spectacular but peaceful.""",
            story_text="As the day turned to evening, Twinkle gathered all the magical moments from {name}'s birthday and wove them into a beautiful glowing tapestry that floated above. 'This,' she said, 'is made of love, laughter, and wishes. It will keep this day alive in your heart forever, {name}.'",
            costume="wearing birthday outfit, looking up in wonder"
        ),

        # === PAGE 9 - GOODBYE TWINKLE ===
        PageTemplate(
            page_number=9,
            scene_description="Twinkle says farewell",
            scene_type="farewell",
            realistic_prompt="""Perfect bedtime ending. The child named {name} in pajamas sitting on edge of bed in peaceful bedroom with party decorations still visible but quiet now. Twinkle the fairy hovering at eye level in front of them, both hands holding child's hands, looking into each other's eyes with love and understanding. Fairy is beginning to dissolve into golden sparkles from feet upward, creating beautiful particle effect of her departure. Soft nightlight glow in the room, stars visible through window. On nightstand: birthday crown, some party favors, and a framed family photo from earlier today. Parents visible in doorway watching the farewell with soft, loving smiles. Child's expression is peaceful, content, a little sad but mostly full of gratitude. The room has a gentle glow from the fading fairy magic. Bittersweet beauty captured in the moment: magic ending but love remaining. Emotional, frame-worthy image.""",
            story_text="As {name} got ready for bed that night, Twinkle prepared to leave. 'Will I see you again?' asked {name}. The fairy smiled. 'Every birthday, if you believe. But remember—the real magic isn't the wishes that come true. It's knowing how loved you are.' She kissed {name}'s forehead, and in a puff of sparkles, she was gone. But {name} could still feel the magic... because love IS magic, and {name} had so much of it.",
            costume="wearing pajamas, holding hands with fairy"
        ),

        # === PAGE 10 - THE MAGIC OF LOVE ===
        PageTemplate(
            page_number=10,
            scene_description="Peaceful sleep full of love",
            scene_type="resolution",
            realistic_prompt="""Perfect resolution. The child named {name} peacefully asleep in bed, covers tucked up, soft smile on sleeping face. On the pillow next to them, a single golden sparkle glows gently, the last trace of Twinkle's magic. Around the room, subtle evidence of the magical day: the birthday crown on the nightstand, a floating balloon settled in the corner, family photos now including one from today's celebration. Through the window, a shooting star crosses the night sky. The moonlight creates soft patterns on the bed. The child is surrounded by love, even in sleep. The room feels warm, safe, and full of happy memories. Above the bed, barely visible, the magical tapestry of memories has transformed into a gentle dream, showing tiny images of the day's adventures. A perfect ending that captures the magic of being loved.""",
            story_text="That night, {name} slept better than ever before, dreaming of dancing fairies and magical wishes. On the nightstand, a single sparkle glowed softly—Twinkle's promise that the magic of birthdays never really ends. Because the best gift of all isn't something you can unwrap. It's being surrounded by people who love you. And {name} had plenty of that.",
            costume="wearing pajamas, peacefully sleeping"
        ),
    ]
)
