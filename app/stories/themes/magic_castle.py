"""
Magic Castle theme - 10 page story about first day at magic school.
"""

from app.stories.templates import StoryTemplate, PageTemplate

MAGIC_CASTLE_THEME = StoryTemplate(
    theme_id="magic_castle",
    title_template="{name}'s First Day of Magic",
    description="A magical adventure at the Grand Academy of Arcane Arts",
    default_costume="purple wizard robe with gold star embroidery",
    protagonist_description="bright expressive eyes, curious and brave expression",
    pages=[
        # PAGE 1: The Arrival
        PageTemplate(
            page_number=1,
            scene_description="Arrival at the magic school gates",
            scene_type="arrival",  # Cinematic: establishing shot with golden lighting
            realistic_prompt="""
            Cinematic wide shot photograph. {protagonist} stands before massive ornate iron gates
            of an ancient magical castle, wearing {costume}. The child looks up with genuine wonder
            and excitement, eyes sparkling with reflected light from the glowing runes on the gates.

            A large majestic owl with round brass spectacles perches on a weathered stone pillar
            beside the gates, looking down with wise, evaluating eyes.

            Morning golden hour lighting, mist swirling at ground level, sun rays breaking through
            ancient oak trees, cobblestone path leading to the gates, magical atmosphere with
            floating dust particles catching the light.

            {realistic_style_block}
            """,
            story_text="""The morning mist clung to the cobblestones as {name} finally arrived at the Grand Academy of Arcane Arts. Standing before the massive iron gates, heart pounding with excitement, {name} couldn't believe this was really happening.

"Only the worthy may pass," hooted Professor Hoot from his pedestal, peering down through his enormous spectacles.""",
            costume="heavy velvet traveling cloak in deep purple with gold trim and a slightly oversized pointed wizard hat"
        ),

        # PAGE 2: The Test
        PageTemplate(
            page_number=2,
            scene_description="The magical test to open the gates",
            scene_type="test",  # Cinematic: dramatic lighting with magical effects

            realistic_prompt="""
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
            """,
            story_text="""These gates open only for those with TRUE magical potential," Professor Hoot declared, his voice echoing across the courtyard. "Show me what you've got, young wizard."

{name} took a deep breath, gripped the wooden wand tightly, and shouted with all the courage in their heart: "ALOHOMORA!""",
            costume="purple velvet traveling cloak with gold star embroidery, pointed wizard hat slightly askew from the magical wind"
        ),

        # PAGE 3: Gateway Opened
        PageTemplate(
            page_number=3,
            scene_description="Walking through the opened gates",
            scene_type="revelation",  # Cinematic: epic establishing shot with sense of wonder

            realistic_prompt="""
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
            """,
            story_text="""With a thunderous CLANG, the ancient gates swung wide open. Beyond them lay a world {name} had only dreamed about - a courtyard filled with floating lanterns, students in colorful robes, and a magnificent castle that seemed to touch the clouds.

"Welcome to the Grand Academy," Professor Hoot smiled. "Your adventure begins now.""",
            costume="purple velvet cloak flowing behind, pointed hat held in one hand at their side"
        ),

        # PAGE 4: Beast Taming Class
        PageTemplate(
            page_number=4,
            scene_description="Beast taming class chaos",
            scene_type="chaos",  # Cinematic: dynamic action shot with dramatic lighting

            realistic_prompt="""
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
            """,
            story_text="""The first class was Beast Taming, and it started with chaos. A wooden crate in the center of the courtyard shook violently, smoke pouring from the cracks. Other students ran screaming, but {name} stepped closer.

"Everyone back!" shouted Professor Flamel. But {name} wasn't afraid. Something in that crate needed help, not fear.""",
            costume="casual purple wizard robes with rolled-up sleeves, ready for practical work"
        ),

        # PAGE 5: Meeting Sparky
        PageTemplate(
            page_number=5,
            scene_description="Meeting Sparky the baby dragon",
            scene_type="bonding",  # Cinematic: intimate close-up with natural lighting

            realistic_prompt="""
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
            """,
            story_text="""The crate EXPLODED open - but instead of a terrifying monster, out tumbled the smallest, saddest baby dragon {name} had ever seen. Red scales, tiny wings, and the most pitiful hiccup that sent a tiny smoke ring floating into the air.

"You're not scary at all," {name} whispered, kneeling down. "You're just hungry and lonely, aren't you?""",
            costume="casual purple wizard robes, now with a bit of soot from the crate explosion"
        ),

        # PAGE 6: Flight Class
        PageTemplate(
            page_number=6,
            scene_description="First successful broomstick flight",
            scene_type="action",  # Cinematic: dynamic action shot with dramatic upward angle

            realistic_prompt="""
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
            """,
            story_text="""After lunch came the class {name} had been waiting for: Flight Training! The broomstick vibrated with magical energy. At first it bucked like a wild horse, but {name} held on tight.

"UP!" {name} commanded, and suddenly - WHOOSH! The ground fell away, and the sky opened up like a doorway to freedom.""",
            costume="fitted brown leather flight jacket, vintage flying goggles pushed up on forehead, red scarf streaming behind"
        ),

        # PAGE 7: Above the Clouds
        PageTemplate(
            page_number=7,
            scene_description="Flying above the clouds",
            scene_type="flight",  # Cinematic: heroic angle with epic sky lighting

            realistic_prompt="""
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
            """,
            story_text="""Higher and higher {name} flew, until the castle became a toy below and the clouds became a soft, endless ocean around them. Three moons hung in the magical sky, and for one perfect moment, {name} felt like anything was possible.

Even Sparky had somehow followed, his tiny wings working overtime to keep up.""",
            costume="leather flight jacket, goggles over eyes reflecting the magical sky, red scarf flowing"
        ),

        # PAGE 8: The Library Incident
        PageTemplate(
            page_number=8,
            scene_description="Library incident with flying books",
            scene_type="mischief",  # Cinematic: dynamic chaos with dramatic lighting

            realistic_prompt="""
            Dynamic photograph in an ancient library. Books fly chaotically through the air as if
            alive, pages flapping. {protagonist} ducks behind an overturned wooden chair, wearing
            {costume}, laughing at the absurd situation.

            A sleek black cat leaps athletically through the air, catching a flying book.
            Papers swirl everywhere. Tall wooden bookshelves stretch into shadow above.

            Warm candlelight creates dramatic shadows. Motion blur on flying books, child's
            laughing face sharp. Dust and papers fill the air.

            Action photography in low light, high ISO grain, sense of magical mischief.

            {realistic_style_block}
            """,
            story_text="""The Ancient Library held thousands of magical books - and one very forbidden section. {name} couldn't resist reaching for a glowing red book, despite Midnight the cat's warning meow.

The moment {name}'s finger touched the spine, every book in the library came ALIVE!""",
            costume="cozy cream-colored knitted sweater with a small wizard crest, comfortable for library reading"
        ),

        # PAGE 9: New Friends
        PageTemplate(
            page_number=9,
            scene_description="Bonding with animal friends",
            scene_type="friendship",  # Cinematic: intimate portrait with golden lighting

            realistic_prompt="""
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
            """,
            story_text="""After the library chaos was sorted (and {name} promised never to touch the Restricted Section again), Midnight curled up in {name}'s lap while Sparky pressed his nose against the window, wanting to join.

"I think I've found my people," {name} smiled, scratching Midnight's ears. "And my cat. And my dragon.""",
            costume="cream knitted sweater with wizard crest, slightly disheveled with a few papers stuck in hair"
        ),

        # PAGE 10: Under the Moons
        PageTemplate(
            page_number=10,
            scene_description="Peaceful ending under the moons",
            scene_type="peaceful",  # Cinematic: dramatic silhouette with magical moonlight

            realistic_prompt="""
            Cinematic photograph from a castle tower balcony at night. {protagonist} stands at
            an ornate stone railing, gazing out at an incredible view - castle grounds twinkling
            with lights, multiple moons in a star-filled sky. They wear {costume}.

            Profile shows peaceful contentment and quiet wonder. A black cat sits beside them on
            the railing. A small sleeping dragon curls at their feet.

            Moonlight creates silver rim lighting. Warm glow from windows below. Stars reflected
            in the child's eyes. The world spreads out below, full of possibility.

            Night photography, long exposure for stars, dramatic silhouette against cosmic sky.

            {realistic_style_block}
            """,
            story_text="""As the three moons rose over the Grand Academy, {name} stood on the Astronomy Tower balcony with Midnight by their side and Sparky curled at their feet. The first day was over, but this was just the beginning.

"I'm ready for tomorrow," {name} whispered to the stars. "I'm ready for everything."

THE END... of the Beginning.""",
            costume="formal royal silk robes in deep purple with a starry cape that seems to contain actual moving stars, small silver circlet on head"
        ),
    ]
)