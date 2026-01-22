"""
StoryGift Safari Adventure Theme - African Savanna Adventure.

Complete 10-page story: "[NAME]'s Wild Safari Adventure"
Premium theme featuring African wildlife, elephant guide Zara, Lion King encounter, and becoming the Safari Guardian.
Optimized for both photorealistic and 3D cartoon pipelines.

CONVERSION OPTIMIZATION:
- Pages 1-5 (Preview): Maximum wow factor, ends with Lion King cliffhanger
- Pages 6-10 (Paid): Resolution, parade, emotional farewell
"""

from app.stories.templates import StoryTemplate, PageTemplate


STORYGIFT_SAFARI_ADVENTURE_THEME = StoryTemplate(
    theme_id="storygift_safari_adventure",
    title_template="{name}'s Wild Safari Adventure",
    description="Where the wild things know your name - become the chosen Safari Guardian",
    default_costume="wearing khaki safari explorer outfit with adventure vest, boots, and explorer hat",
    protagonist_description="bright adventurous eyes, expression of wonder and courage",
    # Cover page settings for typography-ready composition
    cover_costume="wearing premium khaki safari outfit with golden compass pendant glowing on chest, adventure vest with pockets, sturdy boots, and explorer hat tilted heroically",
    cover_header_atmosphere="Golden African sunset with dramatic orange and purple clouds, acacia tree silhouettes against the sky, birds flying in formation",
    cover_magical_elements="Majestic elephant Zara with colorful Maasai beads standing protectively behind the child. A proud lion with golden mane on one side. Giraffes, zebras, and colorful birds creating a frame. The magical Heartstone Compass glowing golden on child's chest. Warm rim lighting creates epic silhouette.",
    cover_footer_description="Golden savanna grass swaying, dust particles catching sunset light, animal footprints in red earth",
    pages=[
        # === PAGE 1 - THE HEARTSTONE COMPASS === (PREVIEW - Wonder)
        PageTemplate(
            page_number=1,
            scene_description="Discovering the magical Heartstone Compass",
            scene_type="discovery",
            realistic_prompt="""Magical morning discovery scene. The child named {name} in pajamas kneeling on bedroom floor, golden morning light streaming through window. Before them sits an ancient wooden box with African tribal carvings that has mysteriously appeared. The box is open, revealing a magnificent glowing compass made of amber and gold - the Heartstone Compass - hovering slightly and pulsing with warm golden light. Tiny golden particles float around it like fireflies. Child's hands reaching toward it with wonder, face illuminated by the magical glow, expression of pure amazement. Safari-themed room decorations visible - animal posters, globe. The compass casts animal-shaped shadows on the walls. Dreamy, warm lighting with magical golden glow effects. Detailed textures, soft focus background.""",
            story_text="{name} woke up to find a mysterious wooden box at the foot of the bed. Inside was the most beautiful compass {name} had ever seen - and it was glowing! The moment {name} touched it, it felt warm, like it had been waiting for someone special.",
            costume="wearing pajamas"
        ),

        # === PAGE 2 - MAGICAL TRANSPORT === (PREVIEW - Excitement)
        PageTemplate(
            page_number=2,
            scene_description="The compass activates magical teleportation",
            scene_type="wonder",
            realistic_prompt="""Magical teleportation scene. The child {name} in pajamas standing in bedroom, holding the Heartstone Compass which blazes with intense golden light. A spectacular magical whirlwind of golden particles, African patterns, and animal silhouettes swirls around the child. The room transforms - walls fade into golden savanna light. Child's expression shows wonder and excitement, hair and clothes blown by magical wind. Glowing compass at center of the vortex. Everything spinning into golden light. Cinematic magical transformation moment, detailed textures, soft focus background.""",
            story_text="The compass grew brighter and brighter until {name} could barely look at it! When {name} held it tight and whispered 'I want to help,' the whole room began to spin in a whirlwind of golden light and animal shadows. Heart pounding with excitement, {name} felt the floor disappear...",
            costume="wearing pajamas, holding blazing compass"
        ),

        # === PAGE 3 - ARRIVAL IN SAVANNA === (PREVIEW - Spectacle)
        PageTemplate(
            page_number=3,
            scene_description="Child appears in the African savanna, meets Zara",
            scene_type="adventure",
            realistic_prompt="""Spectacular arrival scene. The child {name} now wearing khaki safari outfit, standing in golden African savanna grass, looking around in amazement. Before them stands ZARA - a majestic African elephant with colorful Maasai beads around her neck, wise kind eyes, trunk raised in greeting. Acacia trees silhouetted against dramatic orange sunset sky. Giraffes and zebras visible in the distance. The Heartstone Compass still glowing on child's chest. Child's expression shows joyful disbelief. Warm golden hour lighting, dust particles in sunlight. Epic first meeting, BBC Earth quality.""",
            story_text="...and suddenly {name} was standing in the most incredible place! Golden grass stretched forever under a huge African sky. And there, waiting with a knowing smile in her eyes, was the most beautiful elephant {name} had ever seen. 'Welcome, brave one,' she said warmly. 'I am Zara. The Heartstone knew you would come. The animals need your help!'",
            costume="wearing khaki safari explorer outfit with vest and hat"
        ),

        # === PAGE 4 - THE GREAT GATHERING === (PREVIEW - Heart + Stakes)
        PageTemplate(
            page_number=4,
            scene_description="Meeting the animals at the Great Acacia Tree",
            scene_type="bonding",
            realistic_prompt="""Emotional gathering scene. The child {name} in safari outfit standing at the base of the Great Acacia Tree (enormous ancient tree with golden leaves), surrounded by African animals forming a hopeful circle. Baby zebra pressing against child's leg. Meerkats on hind legs. Wise old tortoise looking up. Giraffes bending necks down. ZARA (elephant with colorful Maasai beads, wise eyes) standing protectively nearby. Dry cracked watering hole visible behind. The Heartstone Compass glowing with golden threads connecting to each animal. Child's expression shows compassion and determination. Golden hour light, detailed textures, soft focus background.""",
            story_text="At the Great Acacia Tree, animals of every kind had gathered. A baby zebra who had lost its mother pressed close to {name}. 'The rains haven't come,' said a wise old tortoise sadly. 'The watering hole is almost empty.' {name} felt the compass grow warm and knew: 'I'll help you. I promise.'",
            costume="wearing safari outfit with glowing Heartstone Compass pendant"
        ),

        # === PAGE 5 - THE LION KING === (PREVIEW - CLIFFHANGER!)
        PageTemplate(
            page_number=5,
            scene_description="Face to face with the mighty Lion King",
            scene_type="triumph",
            realistic_prompt="""Epic cliffhanger moment. The child {name} in safari outfit standing brave but small before the LION KING - magnificent male lion with enormous golden mane glowing with inner fire, amber eyes piercing and ancient. Animals parted and silent. Lion's expression unreadable, testing. Child standing firm, chin up with courage. Heartstone Compass blazing golden light between them. Dust particles in dramatic sunbeams. Low angle emphasizing lion's power but child's bravery central. Golden hour rim light on mane. Tense, beautiful, museum-quality dramatic composition, detailed textures, soft focus background.""",
            story_text="Suddenly, the animals fell silent. From the tall grass emerged the Lion King himself - the most magnificent creature {name} had ever seen. His golden eyes studied the small human before him. {name}'s heart pounded, but instead of running, our brave hero stood tall and looked right into the lion's eyes. The compass blazed with light. The Lion King spoke: 'So... YOU are the one the Heartstone chose.'",
            costume="wearing safari outfit, compass blazing with golden light"
        ),

        # === PAGE 6 - EARNING RESPECT === (PAID - Triumph)
        PageTemplate(
            page_number=6,
            scene_description="The Lion King bows to the new Safari Guardian",
            scene_type="triumph",
            realistic_prompt="""Triumphant recognition moment. The LION KING has lowered his great golden-maned head in bow of respect to the child {name}. Child's small hand gently placed on lion's massive forehead. Golden light radiates from Heartstone Compass creating halo around both. Behind them, animals celebrating - elephants trumpeting, zebras rearing, birds spiraling, meerkats jumping. ZARA (elephant with Maasai beads, wise eyes) watching proudly. Dramatic sun creating golden rim light, dust sparkling like glitter. Child's expression shows awe and rising confidence. Wide epic shot, cinematic emotional quality.""",
            story_text="The great lion studied {name} for a long moment... then slowly, majestically, he bowed his golden head. 'Courage is not about being unafraid,' he rumbled. 'It is about standing tall when you ARE afraid. You have the heart of a true Safari Guardian, {name}.' All around them, the animals erupted in joyful celebration!",
            costume="wearing safari outfit with glowing compass"
        ),

        # === PAGE 7 - SAVING THE WATERING HOLE === (PAID - Teamwork)
        PageTemplate(
            page_number=7,
            scene_description="Working together to restore the watering hole",
            scene_type="action",
            realistic_prompt="""Action-packed teamwork scene. The child {name} in safari outfit standing on rock directing animals, compass pointing the way, expression of determined leadership. Meerkats digging channels with impressive speed, dirt flying. ZARA and elephants (Maasai beads) using trunks to move boulders. Hippos clearing mud. Birds carrying plants. Zebras stomping earth flat. Water beginning to flow into dry watering hole, creating first reflecting pools. Dusty, active, everyone working together. Heartstone Compass sending golden guiding threads. Late afternoon light, dynamic diagonal action composition, detailed textures, soft focus background.""",
            story_text="There was no time to waste! {name} and the animals worked together like never before. The meerkats dug new channels with lightning speed. The elephants moved heavy boulders. The birds planted seeds. And slowly, wonderfully, fresh water began to flow back into the watering hole! {name} had done it - with the help of new friends!",
            costume="wearing safari outfit, dusty from work, compass glowing"
        ),

        # === PAGE 8 - THE GREAT ANIMAL PARADE === (PAID - Celebration)
        PageTemplate(
            page_number=8,
            scene_description="Sunset celebration parade across the savanna",
            scene_type="celebration",
            realistic_prompt="""Iconic celebration image. The Great Animal Parade at golden sunset. Wide cinematic shot. The child {name} riding on ZARA's back (elephant with colorful Maasai beads, wise kind eyes), arms raised in joyful celebration. Parade of African animals against spectacular orange-pink-purple sunset. Lion King walking alongside. Giraffes arching gracefully. Zebras prancing. Flamingos flying in pink ribbons. Full watering hole reflecting sunset. Great Acacia Tree silhouetted. Dust catching golden light like glitter. Heartstone Compass creating golden glow around child. Frame-worthy, epic composition, BBC Planet Earth meets Lion King parade, detailed textures, soft focus background.""",
            story_text="As the sun began to set, something magical happened. Every animal in the savanna joined together in the Great Animal Parade - a celebration that hadn't happened in a hundred years! {name} rode proudly on Zara's back as the parade crossed the golden grasslands. It was the most beautiful sight in the world.",
            costume="wearing safari outfit, sitting proudly on elephant"
        ),

        # === PAGE 9 - THE GOLDEN FEATHER === (PAID - Emotional Gift)
        PageTemplate(
            page_number=9,
            scene_description="Receiving the sacred golden feather",
            scene_type="bonding",
            realistic_prompt="""Intimate emotional ceremony at twilight. The LION KING gently placing a magnificent golden feather (shimmering like captured sunshine) into the hair of child {name}, who is kneeling respectfully. ZARA (elephant with Maasai beads) standing nearby, tears of joy in wise eyes. Animals gathered in a reverent circle. Baby zebra pressing close. Meerkats at attention. First stars in purple twilight sky. Heartstone Compass glowing softly. Lion's expression warm, fatherly, proud. Child's face showing overwhelming gratitude and bittersweet farewell emotion. Golden hour fading to blue hour, intimate lighting, frame-worthy tearjerker, detailed textures, soft focus background.""",
            story_text="The Lion King approached with something precious - a golden feather that shimmered like captured sunshine. 'This marks you as a Safari Guardian forever, {name},' he said, placing it gently in the child's hair. 'Whenever an animal needs kindness anywhere in the world, you will feel it in your heart.' {name}'s eyes filled with happy tears.",
            costume="wearing safari outfit, receiving golden feather"
        ),

        # === PAGE 10 - HOME WITH THE WILD IN HEART === (PAID - Resolution)
        PageTemplate(
            page_number=10,
            scene_description="Home again, but forever connected to the wild",
            scene_type="resolution",
            realistic_prompt="""Perfect storybook ending. The child {name} back in bedroom at night, sitting at window in pajamas, looking up at spectacular star-filled sky. Heartstone Compass on windowsill glowing softly. Golden feather tucked behind ear, also glowing. Stars arranged into African animal constellations - lion, elephant, giraffe across the Milky Way. Small stuffed elephant toy (gift from Zara) on bed pillow. Child with peaceful knowing smile, one hand on compass, other touching feather. Soft nightlight glow, magical starlight from window. Cozy but magical, emotionally satisfying conclusion, detailed textures, soft focus background.""",
            story_text="The Heartstone Compass glowed one last time, and in a whirlwind of golden light, {name} was back home, safe in bed as the stars came out. Looking out the window, {name} gasped - the stars had formed into animal shapes, just for a moment! The compass glowed on the windowsill, the golden feather tucked safely behind one ear. {name} smiled. The savanna would always be there, and the animals would always be friends.",
            costume="wearing pajamas, golden feather in hair, compass nearby"
        ),
    ]
)
