# ZELAVO KIDS - STORY PROMPTS & TEMPLATES
## Complete Prompts for AI Image Generation

**Purpose:** Story templates with prompts for both Artistic and Photorealistic styles
**Usage:** Copy these into the backend implementation

---

# PROMPT CONSTANTS

## Style Blocks (Add to EVERY prompt)

### Artistic Style Block
```python
ARTISTIC_STYLE_BLOCK = """
Professional children's comic book illustration style, bold black ink outlines 2px thickness,
cel-shaded flat coloring with subtle gradients, vibrant saturated colors 
(primary palette: royal purple, gold, forest green, sky blue),
Marvel-meets-Pixar aesthetic, dramatic lighting with rim lights on characters,
whimsical and enchanting atmosphere, storybook quality, warm inviting mood.
"""
```

### Photorealistic Style Block
```python
REALISTIC_STYLE_BLOCK = """
Ultra-realistic cinematic photography, professional DSLR quality with Canon EOS R5,
natural lighting with golden hour warmth, shallow depth of field f/2.8,
8K resolution, movie still aesthetic, National Geographic quality,
lifelike details and textures, photojournalistic style, magical atmosphere.
"""
```

### Negative Prompt (Use for both styles)
```python
NEGATIVE_PROMPT = """
blurry, low quality, distorted, deformed, ugly, bad anatomy, extra limbs,
extra fingers, mutated hands, poorly drawn face, mutation, watermark,
text overlay, signature, cropped, out of frame, duplicate, multiple heads,
anime style, manga style, chibi, dark horror scary, gore violence,
adult mature content, realistic photo (for artistic only)
"""
```

---

# THEME 1: MAGIC CASTLE

## Theme Metadata
```python
MAGIC_CASTLE = {
    "theme_id": "magic_castle",
    "title_template": "{name}'s First Day of Magic",
    "description": "A magical adventure at the Grand Academy of Arcane Arts",
    "age_range": "4-10",
    "default_costume": "purple wizard robe with gold star embroidery and a pointed hat",
    "protagonist_base": "a {age}-year-old {gender} child with the exact face from the reference photo"
}
```

## Page 1: The Arrival

### Story Text
```
The morning mist clung to the cobblestones as {name} finally arrived at the Grand Academy of Arcane Arts. Standing before the massive iron gates, heart pounding with excitement, {name} couldn't believe this was really happening.

"Only the worthy may pass," hooted Professor Hoot from his pedestal, peering down through his enormous spectacles.
```

### Artistic Prompt
```python
PAGE_1_ARTISTIC = """
A breathtaking wide establishing shot of a magical scene. {protagonist} stands in the 
lower left of the frame, looking up in wonder at massive gothic castle gates made of 
dark iron with glowing purple magical runes. The child wears {costume}. Their expression 
shows excitement and wonder with wide sparkling eyes and mouth slightly open in awe.

On a tall stone pedestal to the right of the gate perches Professor Hoot - a giant 
4-foot-tall majestic brown owl with large round brass reading glasses and a small 
black graduation cap with gold tassel. The owl looks down wisely at the child.

The massive iron gates are 50 feet tall with twisted spires disappearing into morning 
mist. Golden sunlight streams through from behind creating god rays. Magical sparkles 
float in the air like fireflies. Ancient oak trees frame the scene. Cobblestone path 
leads to the gates.

{artistic_style_block}
"""
```

### Photorealistic Prompt
```python
PAGE_1_REALISTIC = """
Cinematic wide shot photograph. {protagonist} stands before massive ornate iron gates 
of an ancient magical castle, wearing {costume}. The child looks up with genuine wonder 
and excitement, eyes sparkling with reflected light from the glowing runes on the gates.

A large majestic owl with round brass spectacles perches on a weathered stone pillar 
beside the gates, looking down with wise, evaluating eyes.

Morning golden hour lighting, mist swirling at ground level, sun rays breaking through 
ancient oak trees, cobblestone path leading to the gates, magical atmosphere with 
floating dust particles catching the light.

{realistic_style_block}
"""
```

### Costume
```
heavy velvet traveling cloak in deep purple with gold trim and a slightly oversized pointed wizard hat
```

---

## Page 2: The Test

### Story Text
```
"These gates open only for those with TRUE magical potential," Professor Hoot declared, 
his voice echoing across the courtyard. "Show me what you've got, young wizard."

{name} took a deep breath, gripped the wooden wand tightly, and shouted with all 
the courage in their heart: "ALOHOMORA!"
```

### Artistic Prompt
```python
PAGE_2_ARTISTIC = """
Dynamic action shot split scene. {protagonist} is in a power stance - feet planted wide, 
both hands gripping a simple wooden wand (oak, 10 inches, slightly crooked). The wand tip 
EXPLODES with brilliant golden-purple magical energy, swirling sparks and lightning 
crackling toward the massive iron gate lock.

The child's face shows intense concentration - eyes focused, determined expression, 
hair and cloak billowing from magical wind. They wear {costume}.

Professor Hoot the giant owl with brass glasses watches from his pedestal, one eyebrow 
raised, evaluating the young wizard's potential.

The iron lock on the gate is beginning to glow, ancient runes activating in sequence. 
Magical energy swirls throughout the scene. Dramatic lighting from the spell creates 
strong shadows.

{artistic_style_block}
"""
```

### Photorealistic Prompt
```python
PAGE_2_REALISTIC = """
Dramatic action photograph. {protagonist} stands in a determined pose, both hands 
gripping a rustic wooden wand pointed at massive iron gates. Brilliant golden-purple 
light bursts from the wand tip, illuminating the child's concentrated face.

The child wears {costume}, cloak flowing in the magical wind. Expression shows pure 
determination and focus.

A large owl with spectacles observes from a stone pedestal, backlit by morning sun. 
The gate's iron lock glows with activating magical energy. Sparks and light particles 
fill the air.

High-speed photography capturing motion, dramatic rim lighting from magical burst, 
shallow depth of field on child's face.

{realistic_style_block}
"""
```

### Costume
```
purple velvet traveling cloak with gold star embroidery, pointed wizard hat slightly askew from the magical wind
```

---

## Page 3: Gateway Opened

### Story Text
```
With a thunderous CLANG, the ancient gates swung wide open. Beyond them lay a world 
{name} had only dreamed about - a courtyard filled with floating lanterns, students 
in colorful robes, and a magnificent castle that seemed to touch the clouds.

"Welcome to the Grand Academy," Professor Hoot smiled. "Your adventure begins now."
```

### Artistic Prompt
```python
PAGE_3_ARTISTIC = """
Cinematic reveal shot. The massive iron gates are swinging wide open toward the viewer, 
creating a natural frame. Magical energy crackles along the gate edges in purple and 
gold lightning. Ancient runes on the gates pulse with fading light.

Walking through the center of the frame, viewed from behind in 3/4 back view, is 
{protagonist}. Their face is partially visible in profile showing an awed, joyful 
expression. They wear {costume}, cloak flowing majestically. Small footsteps on 
ancient cobblestones.

REVEALED BEYOND THE GATES: A breathtaking magical courtyard bathed in warm sunlight. 
A grand fountain shoots water that transforms into flying fish mid-air. Floating 
lanterns drift lazily. Students in various colored robes walk between gothic buildings. 
A clock tower has hands that move backwards. Trees have leaves in silver, gold, and purple.

Professor Hoot flies overhead, wings spread magnificently, announcing the new arrival.

{artistic_style_block}
"""
```

### Photorealistic Prompt
```python
PAGE_3_REALISTIC = """
Cinematic reveal photograph from behind. {protagonist} walks through massive opening 
iron gates, seen from 3/4 back view. Profile shows wonder and joy on their face. 
They wear {costume}, cloak catching the breeze.

Beyond the gates, a stunning magical courtyard is revealed - an ornate fountain with 
water catching prismatic light, students in flowing robes, gothic architecture with 
towers reaching into soft clouds, floating lanterns, impossibly beautiful gardens.

A large owl soars overhead, wings spread against the bright sky.

Golden hour lighting flooding through the gates, lens flare from sun, shallow depth 
of field with child sharp and background dreamy, sense of stepping into another world.

{realistic_style_block}
"""
```

### Costume
```
purple velvet cloak flowing behind, pointed hat held in one hand at their side
```

---

## Page 4: Beast Taming Class

### Story Text
```
The first class was Beast Taming, and it started with chaos. A wooden crate in the 
center of the courtyard shook violently, smoke pouring from the cracks. Other students 
ran screaming, but {name} stepped closer.

"Everyone back!" shouted Professor Flamel. But {name} wasn't afraid. Something in 
that crate needed help, not fear.
```

### Artistic Prompt
```python
PAGE_4_ARTISTIC = """
Action scene in a stone courtyard classroom. A large reinforced wooden crate (4 feet tall) 
is VIOLENTLY SHAKING, jumping off the ground. Cracks appear in the wood. Purple and 
orange smoke billows from the gaps. Small flames lick the edges.

{protagonist} walks TOWARD the shaking crate while other students flee in panic behind 
them. The child wears {costume}, sleeves rolled up, showing they're ready to work. 
Their expression shows calm determination mixed with curiosity - slight confident smile, 
eyes focused on the crate.

Background: Five other student wizards in various colored robes scramble backward in 
panic. An elderly wizard teacher with a long white beard looks on with interest.

The crate is cracking, about to burst open. Motion lines show the violent shaking.

{artistic_style_block}
"""
```

### Photorealistic Prompt
```python
PAGE_4_REALISTIC = """
Dramatic photograph in a stone courtyard. A large wooden crate shakes violently, 
smoke and small flames emerging from the gaps. The wood is splintering.

{protagonist} walks calmly toward the dangerous crate, wearing {costume} with sleeves 
rolled up. Expression shows brave curiosity rather than fear. They approach with 
one hand slightly raised in a calming gesture.

Other students blur past in the background, running away. An elderly professor 
watches with raised eyebrows.

Motion blur on shaking crate, child sharp and in focus, dramatic side lighting from 
the flames, smoke swirling in the air.

{realistic_style_block}
"""
```

### Costume
```
casual purple wizard robes with rolled-up sleeves, ready for practical work
```

---

## Page 5: Meeting Sparky

### Story Text
```
The crate EXPLODED open - but instead of a terrifying monster, out tumbled the 
smallest, saddest baby dragon {name} had ever seen. Red scales, tiny wings, and 
the most pitiful hiccup that sent a tiny smoke ring floating into the air.

"You're not scary at all," {name} whispered, kneeling down. "You're just hungry 
and lonely, aren't you?"
```

### Artistic Prompt
```python
PAGE_5_ARTISTIC = """
Heartwarming close-up scene. {protagonist} is kneeling down to eye level with SPARKY - 
a small adorable baby dragon (size of a large cat). Sparky has red scales, tiny orange 
wings that are too small for his body, big watery golden eyes, and smoke puffing from 
his nostrils with each hiccup.

The child wears {costume} and has the most gentle, kind expression - soft eyes, warm 
smile, one hand slowly reaching out offering a glowing magical cookie (golden, star-shaped).

Sparky leans forward cautiously, sniffing the cookie. His expression transforms from 
scared to hopeful - eyes widening, tiny tail starting to wag. A small heart-shaped 
puff of smoke comes from his nose.

Background is softly blurred with warm golden light, creating an intimate bonding moment. 
Broken crate pieces scattered around them.

{artistic_style_block}
"""
```

### Photorealistic Prompt
```python
PAGE_5_REALISTIC = """
Intimate close-up photograph. {protagonist} kneels on stone ground, face-to-face with 
a small baby dragon creature. The child wears {costume}, expression showing pure 
gentleness and compassion. They offer something from their hand.

The baby dragon is endearingly small with reddish scales, stubby wings, and large 
expressive eyes. It looks cautiously hopeful, leaning slightly toward the child.

Broken wooden crate pieces scattered around them. Warm golden backlighting creates 
a halo effect. Sharp focus on both faces with blurred background.

Portrait photography style, emotional connection between child and creature, 
soft warm lighting.

{realistic_style_block}
"""
```

### Costume
```
casual purple wizard robes, now with a bit of soot from the crate explosion
```

---

## Page 6: Flight Class

### Story Text
```
After lunch came the class {name} had been waiting for: Flight Training! The broomstick 
vibrated with magical energy. At first it bucked like a wild horse, but {name} held on 
tight.

"UP!" {name} commanded, and suddenly - WHOOSH! The ground fell away, and the sky 
opened up like a doorway to freedom.
```

### Artistic Prompt
```python
PAGE_6_ARTISTIC = """
Dynamic vertical action shot showing triumphant flight. {protagonist} ROCKETS upward 
into the sky on a wooden broomstick with twigs at the tail. The composition is 
dramatically vertical with strong upward motion lines.

The child's expression shows pure JOY - huge smile, eyes bright with exhilaration, 
hair streaming upward, {costume} flowing behind like a banner. They grip the broom 
confidently, leaning forward into the speed.

Below, rapidly shrinking, are other students pointing up in amazement on a grassy 
training field. Sparky the baby dragon jumps up and down excitedly, shooting tiny 
celebratory fire puffs.

The sky opens up brilliantly - blue with fluffy white clouds. A flock of magical 
birds with sparkle trails flies alongside.

Speed lines and sparkle effects throughout. Sense of freedom and achievement.

{artistic_style_block}
"""
```

### Photorealistic Prompt
```python
PAGE_6_REALISTIC = """
Action photograph capturing the moment of flight. {protagonist} soars upward on a 
rustic wooden broomstick, wearing {costume}. Their face shows pure exhilaration - 
genuine smile, wind-swept hair, eyes sparkling with joy.

The scarf streams dramatically behind them. Below, a grassy field with other students 
grows small. A small red dragon-like creature watches from the ground.

Blue sky with scattered clouds above. Motion blur on the ground, child sharp against 
the sky. Golden sunlight catches their face.

Sports action photography style, high shutter speed capturing motion, dramatic 
upward angle.

{realistic_style_block}
"""
```

### Costume
```
fitted brown leather flight jacket, vintage flying goggles pushed up on forehead, red scarf streaming behind
```

---

## Page 7: Above the Clouds

### Story Text
```
Higher and higher {name} flew, until the castle became a toy below and the clouds 
became a soft, endless ocean around them. Three moons hung in the magical sky, 
and for one perfect moment, {name} felt like anything was possible.

Even Sparky had somehow followed, his tiny wings working overtime to keep up.
```

### Artistic Prompt
```python
PAGE_7_ARTISTIC = """
Breathtaking wide shot of endless magical sky. {protagonist} soars on their broomstick 
through a sea of fluffy white and pink-tinged clouds. They wear {costume}, goggles 
now over eyes reflecting the clouds.

The child's posture is confident and graceful - one hand on the broom, one arm stretched 
out touching the clouds as they pass. Expression shows peaceful bliss and wonder.

THREE MOONS of different sizes hang in the deep blue-purple sky - one large silver, 
one medium gold, one small rose-pink. Countless stars form shifting constellations. 
A shooting star streaks across the corner.

Sparky the baby dragon flies alongside, tiny wings working hard, tongue out in doglike 
happiness.

Magical elements: Rainbow trails follow the broomstick, cloud creatures (whales made 
of cloud) swim in the distance, floating islands visible on the horizon.

{artistic_style_block}
"""
```

### Photorealistic Prompt
```python
PAGE_7_REALISTIC = """
Stunning aerial photograph above the clouds. {protagonist} flies through a dreamscape 
of clouds and sky, wearing {costume}. Expression shows pure peace and wonder, a gentle 
smile as they stretch one hand to touch the passing clouds.

Multiple moons visible in a twilight purple-blue sky filled with stars. The child and 
broomstick are silhouetted against the cosmic backdrop.

A small winged creature flies nearby. Cloud formations below look like a soft ocean. 
Golden light catches the edges of everything.

Drone-style aerial photography meets fantasy, ethereal lighting, shallow depth of field, 
sense of infinite possibility and freedom.

{realistic_style_block}
"""
```

### Costume
```
leather flight jacket, goggles over eyes reflecting the magical sky, red scarf flowing
```

---

## Page 8: The Library Incident

### Story Text
```
The Ancient Library held thousands of magical books - and one very forbidden section. 
{name} couldn't resist reaching for a glowing red book, despite Midnight the cat's 
warning meow.

The moment {name}'s finger touched the spine, every book in the library came ALIVE!
```

### Artistic Prompt
```python
PAGE_8_ARTISTIC = """
Chaotic action scene in a magical library. Impossibly tall dark wooden bookshelves 
stretch upward. DOZENS of books have come to life and FLY through the air like birds, 
pages flapping as wings!

{protagonist} has ducked under a heavy reading table, laughing despite the chaos - 
this is FUN chaos. They wear {costume}. Papers swirl like a blizzard around them.

MIDNIGHT the cat (sleek black cat with glowing yellow eyes and silver collar) leaps 
through the air in an athletic pounce, catching a flying blue book in her mouth. 
Her body is stretched elegantly mid-air.

Books everywhere: a dictionary chases a thesaurus, a cookbook flaps near the ceiling, 
a map book has unfolded into a paper airplane shape. One angry book seems to be 
shouting at everything.

Warm candlelight mixed with chaos. Floating candles wobble in the book-wind.

{artistic_style_block}
"""
```

### Photorealistic Prompt
```python
PAGE_8_REALISTIC = """
Dynamic photograph in an ancient library. Books fly chaotically through the air as if 
alive, pages flapping. {protagonist} ducks behind an overturned wooden chair, wearing 
{costume}, laughing at the absurd situation.

A sleek black cat leaps athletically through the air, catching a flying book. 
Papers swirl everywhere. Tall wooden bookshelves stretch into shadow above.

Warm candlelight creates dramatic shadows. Motion blur on flying books, child's 
laughing face sharp. Dust and papers fill the air.

Action photography in low light, high ISO grain, sense of magical mischief.

{realistic_style_block}
"""
```

### Costume
```
cozy cream-colored knitted sweater with a small wizard crest, comfortable for library reading
```

---

## Page 9: New Friends

### Story Text
```
After the library chaos was sorted (and {name} promised never to touch the Restricted 
Section again), Midnight curled up in {name}'s lap while Sparky pressed his nose 
against the window, wanting to join.

"I think I've found my people," {name} smiled, scratching Midnight's ears. "And my 
cat. And my dragon."
```

### Artistic Prompt
```python
PAGE_9_ARTISTIC = """
Warm, cozy scene in a library window seat. {protagonist} sits comfortably in a large 
window alcove, late afternoon golden light streaming in. They wear {costume}, slightly 
disheveled from the earlier chaos but happy.

MIDNIGHT the black cat is curled up contentedly in the child's lap, purring, eyes 
half-closed in bliss. The child strokes her fur gently, looking down with pure affection.

SPARKY appears at the window from outside, pressing his little dragon face against 
the glass adorably, making a fog circle with his breath, wanting to join but knowing 
he's not allowed in the library (fire hazard).

The composition is warm, safe, and loving. Golden hour light creates a halo effect. 
Scattered books visible in the background, now peaceful on their shelves.

{artistic_style_block}
"""
```

### Photorealistic Prompt
```python
PAGE_9_REALISTIC = """
Intimate portrait photograph in a library window seat. {protagonist} sits in a cozy 
alcove, wearing {costume}, bathed in warm golden afternoon light streaming through 
the window. Their expression is peaceful and content.

A black cat is curled in their lap, eyes closed in contentment as the child pets 
it gently. A small dragon-like creature presses its face against the window from 
outside, looking in hopefully.

Soft golden hour lighting, shallow depth of field with child and cat sharp, 
window background softly glowing. Sense of found family and belonging.

Portrait photography, natural window light, emotional warmth.

{realistic_style_block}
"""
```

### Costume
```
cream knitted sweater with wizard crest, slightly disheveled with a few papers stuck in hair
```

---

## Page 10: Under the Moons

### Story Text
```
As the three moons rose over the Grand Academy, {name} stood on the Astronomy Tower 
balcony with Midnight by their side and Sparky curled at their feet. The first day 
was over, but this was just the beginning.

"I'm ready for tomorrow," {name} whispered to the stars. "I'm ready for everything."

THE END... of the Beginning.
```

### Artistic Prompt
```python
PAGE_10_ARTISTIC = """
Stunning cinematic finale. The view is from the Astronomy Tower balcony, the highest 
point of the castle. Stone balcony railing carved with celestial symbols that faintly glow.

{protagonist} stands at the railing, viewed from 3/4 angle so we see both their profile 
and the magnificent view. They wear {costume} - formal and regal. Expression is peaceful, 
content, full of quiet excitement for the future.

THREE MOONS hang in the deep blue-purple sky - large silver, medium gold, small rose-pink. 
Countless stars form shifting constellations. The castle grounds twinkle with floating 
lanterns below.

MIDNIGHT sits elegantly on the stone railing, yellow eyes reflecting the moons.
SPARKY is curled at {name}'s feet, sleepy but content, tail wrapped around their ankle 
protectively.

Silver-blue moonlight creates rim lighting on all characters. Warm orange glow from 
castle windows provides contrast. Magical, triumphant, full of promise.

{artistic_style_block}
"""
```

### Photorealistic Prompt
```python
PAGE_10_REALISTIC = """
Cinematic photograph from a castle tower balcony at night. {protagonist} stands at 
an ornate stone railing, gazing out at an incredible view - castle grounds twinkling 
with lights, multiple moons in a star-filled sky. They wear {costume}.

Profile shows peaceful contentment and quiet wonder. A black cat sits beside them on 
the railing. A small sleeping dragon curls at their feet.

Moonlight creates silver rim lighting. Warm glow from windows below. Stars reflected 
in the child's eyes. The world spreads out below, full of possibility.

Night photography, long exposure for stars, dramatic silhouette against cosmic sky.

{realistic_style_block}
"""
```

### Costume
```
formal royal silk robes in deep purple with a starry cape that seems to contain actual moving stars, small silver circlet on head
```

---

# PYTHON IMPLEMENTATION

## Complete Theme Dictionary

```python
"""
FILE: app/stories/themes/magic_castle.py
COMPLETE IMPLEMENTATION
"""

from app.stories.templates import StoryTemplate, PageTemplate

MAGIC_CASTLE_THEME = StoryTemplate(
    theme_id="magic_castle",
    title_template="{name}'s First Day of Magic",
    description="A magical adventure at the Grand Academy of Arcane Arts",
    default_costume="purple wizard robe with gold star embroidery",
    protagonist_description="bright expressive eyes, curious and brave expression",
    pages=[
        PageTemplate(
            page_number=1,
            scene_description="Arrival at the magic school gates",
            artistic_prompt=PAGE_1_ARTISTIC,
            realistic_prompt=PAGE_1_REALISTIC,
            story_text=PAGE_1_TEXT,
            costume="heavy velvet traveling cloak in deep purple with gold trim and a slightly oversized pointed wizard hat"
        ),
        PageTemplate(
            page_number=2,
            scene_description="The magical test to open the gates",
            artistic_prompt=PAGE_2_ARTISTIC,
            realistic_prompt=PAGE_2_REALISTIC,
            story_text=PAGE_2_TEXT,
            costume="purple velvet traveling cloak with gold star embroidery, pointed wizard hat slightly askew from the magical wind"
        ),
        PageTemplate(
            page_number=3,
            scene_description="Walking through the opened gates",
            artistic_prompt=PAGE_3_ARTISTIC,
            realistic_prompt=PAGE_3_REALISTIC,
            story_text=PAGE_3_TEXT,
            costume="purple velvet cloak flowing behind, pointed hat held in one hand at their side"
        ),
        PageTemplate(
            page_number=4,
            scene_description="Beast taming class chaos",
            artistic_prompt=PAGE_4_ARTISTIC,
            realistic_prompt=PAGE_4_REALISTIC,
            story_text=PAGE_4_TEXT,
            costume="casual purple wizard robes with rolled-up sleeves, ready for practical work"
        ),
        PageTemplate(
            page_number=5,
            scene_description="Meeting Sparky the baby dragon",
            artistic_prompt=PAGE_5_ARTISTIC,
            realistic_prompt=PAGE_5_REALISTIC,
            story_text=PAGE_5_TEXT,
            costume="casual purple wizard robes, now with a bit of soot from the crate explosion"
        ),
        PageTemplate(
            page_number=6,
            scene_description="First successful broomstick flight",
            artistic_prompt=PAGE_6_ARTISTIC,
            realistic_prompt=PAGE_6_REALISTIC,
            story_text=PAGE_6_TEXT,
            costume="fitted brown leather flight jacket, vintage flying goggles pushed up on forehead, red scarf streaming behind"
        ),
        PageTemplate(
            page_number=7,
            scene_description="Flying above the clouds",
            artistic_prompt=PAGE_7_ARTISTIC,
            realistic_prompt=PAGE_7_REALISTIC,
            story_text=PAGE_7_TEXT,
            costume="leather flight jacket, goggles over eyes reflecting the magical sky, red scarf flowing"
        ),
        PageTemplate(
            page_number=8,
            scene_description="Library incident with flying books",
            artistic_prompt=PAGE_8_ARTISTIC,
            realistic_prompt=PAGE_8_REALISTIC,
            story_text=PAGE_8_TEXT,
            costume="cozy cream-colored knitted sweater with a small wizard crest, comfortable for library reading"
        ),
        PageTemplate(
            page_number=9,
            scene_description="Bonding with animal friends",
            artistic_prompt=PAGE_9_ARTISTIC,
            realistic_prompt=PAGE_9_REALISTIC,
            story_text=PAGE_9_TEXT,
            costume="cream knitted sweater with wizard crest, slightly disheveled with a few papers stuck in hair"
        ),
        PageTemplate(
            page_number=10,
            scene_description="Peaceful ending under the moons",
            artistic_prompt=PAGE_10_ARTISTIC,
            realistic_prompt=PAGE_10_REALISTIC,
            story_text=PAGE_10_TEXT,
            costume="formal royal silk robes in deep purple with a starry cape that seems to contain actual moving stars, small silver circlet on head"
        ),
    ]
)
```

## Prompt Builder Function

```python
"""
FILE: app/stories/prompt_builder.py
"""

from app.stories.templates import StoryTemplate
from app.stories.constants import ARTISTIC_STYLE_BLOCK, REALISTIC_STYLE_BLOCK, NEGATIVE_PROMPT


def build_prompt(
    template: StoryTemplate,
    page_number: int,
    style: str,  # "artistic" or "photorealistic"
    child_name: str,
    child_age: int,
    child_gender: str
) -> dict:
    """
    Build the final prompt for a specific page.
    
    Returns:
        dict with 'prompt' and 'negative_prompt'
    """
    page = template.pages[page_number - 1]
    
    # Get base prompt for style
    if style == "artistic":
        base_prompt = page.artistic_prompt
        style_block = ARTISTIC_STYLE_BLOCK
    else:
        base_prompt = page.realistic_prompt
        style_block = REALISTIC_STYLE_BLOCK
    
    # Build protagonist description
    protagonist = f"a {child_age}-year-old {child_gender} child with the exact face from the reference photo, {template.protagonist_description}"
    
    # Get costume for this page
    costume = page.costume or template.default_costume
    
    # Replace placeholders
    final_prompt = base_prompt.format(
        protagonist=protagonist,
        costume=costume,
        age=child_age,
        gender=child_gender,
        artistic_style_block=ARTISTIC_STYLE_BLOCK if style == "artistic" else "",
        realistic_style_block=REALISTIC_STYLE_BLOCK if style == "photorealistic" else ""
    )
    
    # Clean up whitespace
    final_prompt = " ".join(final_prompt.split())
    
    return {
        "prompt": final_prompt,
        "negative_prompt": NEGATIVE_PROMPT.strip()
    }


def build_story_text(
    template: StoryTemplate,
    page_number: int,
    child_name: str
) -> str:
    """
    Build the story text for a specific page.
    """
    page = template.pages[page_number - 1]
    return page.story_text.format(name=child_name)
```

---

# ADDITIONAL THEMES (Stubs for Future Implementation)

## Theme 2: Space Adventure
```python
SPACE_ADVENTURE = {
    "theme_id": "space_adventure",
    "title_template": "{name}'s Journey to the Stars",
    "description": "An epic adventure through the solar system",
    "age_range": "5-12",
    "pages": 10
}
# TODO: Implement full prompts
```

## Theme 3: Underwater Kingdom
```python
UNDERWATER_KINGDOM = {
    "theme_id": "underwater",
    "title_template": "{name} and the Ocean Secret",
    "description": "A magical underwater adventure with sea creatures",
    "age_range": "3-8",
    "pages": 10
}
# TODO: Implement full prompts
```

## Theme 4: Forest Friends
```python
FOREST_FRIENDS = {
    "theme_id": "forest_friends",
    "title_template": "{name}'s Enchanted Forest",
    "description": "A heartwarming adventure in a magical forest",
    "age_range": "3-7",
    "pages": 10
}
# TODO: Implement full prompts
```

---

# PROMPT OPTIMIZATION NOTES

## For Best Results

1. **Keep protagonist description identical** across all pages
2. **Use same seed** (42 recommended) for style consistency
3. **Include style block at the end** of every prompt
4. **Costume changes are okay** - describe them fully each time
5. **Supporting characters** (owl, dragon, cat) should have consistent descriptions

## Character Descriptions (Use Exactly)

```python
PROFESSOR_HOOT = "Professor Hoot - a giant 4-foot-tall majestic brown owl with large round brass reading glasses and a small black graduation cap with gold tassel"

SPARKY = "Sparky - a small adorable baby dragon the size of a large cat, with red scales, tiny orange wings too small for his body, big watery golden eyes"

MIDNIGHT = "Midnight - a sleek elegant black cat with glowing yellow eyes and a silver collar with a tiny bell"
```

---

**END OF PROMPTS FILE**
