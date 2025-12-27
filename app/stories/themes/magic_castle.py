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
            artistic_prompt="""
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
            """,
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
            artistic_prompt="""
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
            """,
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
            artistic_prompt="""
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
            """,
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
            artistic_prompt="""
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
            """,
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
            artistic_prompt="""
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
            """,
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
            artistic_prompt="""
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
            """,
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
            artistic_prompt="""
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
            """,
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
            artistic_prompt="""
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
            """,
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
            artistic_prompt="""
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
            """,
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
            artistic_prompt="""
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
            """,
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