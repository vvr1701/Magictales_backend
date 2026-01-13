"""
Magic Castle theme - 10 page story about first day at magic school.
"""

from app.stories.templates import (
    StoryTemplate,
    PageTemplate,
    ComicPageTemplate,
    ComicPanel,
    DialogueBubble
)

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
            artistic_prompt="""
            Comic book illustration panel. {protagonist} stands before massive ornate iron gates
            of an ancient magical castle, wearing {costume}. The child looks up with wonder and
            excitement, in classic comic book hero pose.

            A large majestic owl with round spectacles perches on a stone pillar, with a speech
            bubble saying "Only the worthy may pass." The owl has wise, evaluating eyes.

            Comic book style: dynamic perspective, bold outlines, vibrant colors, magical atmosphere
            with floating sparkles and runes glowing on the gates. Morning golden lighting with
            dramatic shadows. Classic superhero comic art style, detailed linework.

            Include atmospheric text effects: "WHOOSH" for morning breeze through trees.
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
            scene_type="test",  # Cinematic: dramatic lighting with magical effects
            artistic_prompt="""
            Comic book action panel. {protagonist} in dramatic superhero pose, both hands gripping
            a wooden wand pointed at massive iron gates, wearing {costume}. Bold speech bubble:
            "ALOHOMORA!" in large, magical-style lettering.

            Brilliant magical energy bursts from wand tip with comic book "ZAP!" "CRACKLE!" sound
            effects. The owl on pedestal has thought bubble: "Impressive..." Gate lock glows with
            activating runes.

            Classic comic book art style: dynamic action lines, bold colors, dramatic lighting
            effects, speed lines around the magical burst. Heroic comic book composition with
            low angle shot to make character look powerful.

            Include sound effects: "CRACKLE!" "WHOOOM!" "BUZZ!" for magical energy.
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
            scene_type="revelation",  # Cinematic: epic establishing shot with sense of wonder
            artistic_prompt="""
            Comic book splash panel (full page). {protagonist} walks through massive opened gates,
            wearing {costume}. Wide-eyed expression of wonder and joy. Classic hero entrance pose.

            Background reveals stunning magical courtyard: floating lanterns, students in colorful
            robes, gothic towers reaching clouds, ornate fountain with sparkles. Professor Hoot
            soars overhead with speech bubble: "Welcome to the Grand Academy!"

            Sound effects scattered throughout: "CLANG!" for gates, "WHOOOOSH!" for magical breeze,
            "SPARKLE!" for floating lights. Comic book explosion-style burst behind gates showing
            the magical world opening up.

            Epic comic book art: dramatic perspective, vibrant magical colors, detailed fantasy
            architecture, classic comic book panel composition with multiple action elements.
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
            scene_type="chaos",  # Cinematic: dynamic action shot with dramatic lighting
            artistic_prompt="""
            Dynamic comic book panel. Wooden crate shakes violently in courtyard center, with
            "SHAKE!" "RATTLE!" "CRACK!" sound effects. Smoke and small flames emerge with
            "HISS!" "POOF!" effects.

            {protagonist} walks bravely toward danger, wearing {costume}. Confident expression,
            one hand raised calmly. Speech bubble: "It's okay, little one..."

            Background shows other students running with motion lines and "AAAH!" screams in
            speech bubbles. Professor Flamel shouts "Everyone back!" in bold lettering.

            Comic book action style: dynamic movement lines, bold colors, dramatic lighting
            from flames, multiple action elements happening simultaneously. Classic superhero
            bravery pose for protagonist.
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
            scene_type="bonding",  # Cinematic: intimate close-up with natural lighting
            artistic_prompt="""
            Comic book intimate panel. Wooden crate pieces scattered across stone ground with
            "CRASH!" "BANG!" sound effects. From the debris, a small baby dragon with bright
            red scales and stubby wings emerges, looking scared and lost.

            {protagonist} kneels down gently, wearing {costume}, extending one hand with
            a piece of bread. Speech bubble: "You're not scary at all... just hungry!"
            The child's expression shows pure kindness and compassion.

            The baby dragon has large expressive eyes, smoke rings floating from tiny hiccups with
            "PUFF!" sound effects. Thought bubble above dragon: "Friend?"

            Comic book art style: detailed line work, warm emotional lighting, soft colors for
            bonding scene, detailed character expressions. Classic heartwarming comic book moment
            with emotional connection between characters.

            Include sound effects: "HICCUP!" "PUFF!" for dragon sounds.
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
            scene_type="action",  # Cinematic: dynamic action shot with dramatic upward angle
            artistic_prompt="""
            Dynamic comic book action panel. {protagonist} soars through the air on a wooden
            broomstick, wearing {costume}. Classic superhero flying pose with cape and scarf
            streaming behind. The child's face shows pure exhilaration and joy.

            Speech bubble with large bold letters: "UP!" Power lines and motion streaks show
            upward movement with "WHOOOOSH!" sound effect trailing behind the broomstick.

            Below, a grassy field with other students gets smaller. Sparky the baby dragon
            watches from the ground with thought bubble: "Wait for me!"

            Blue sky with scattered clouds, dramatic perspective from low angle looking up.
            Golden sunlight creates lens flare effects around the flying figure.

            Comic book action style: dynamic speed lines, bold colors, heroic pose, dramatic
            perspective. Classic superhero comic flight scene with motion effects and
            environmental storytelling.

            Include sound effects: "WHOOOOSH!" "ZOOM!" "SOAR!" for flying motion.
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
            scene_type="flight",  # Cinematic: heroic angle with epic sky lighting
            artistic_prompt="""
            Epic comic book splash panel. {protagonist} flies through a dreamlike cloudscape,
            wearing {costume}, one hand reaching out to touch passing clouds. Expression shows
            pure wonder and peace, gentle smile on their face.

            Multiple moons visible in twilight purple-blue sky filled with stars. Three distinct
            moons of different sizes create magical lighting. The child and broomstick silhouetted
            against cosmic backdrop.

            Sparky the baby dragon flies alongside with tiny wings working hard. Speech bubble
            from dragon: "This is amazing!" Motion lines show wing flapping with "FLUTTER!"
            sound effects.

            Cloud formations below look like soft ocean waves. Starlight creates magical sparkle
            effects throughout the scene with "TWINKLE!" annotations.

            Comic book art style: ethereal fantasy colors, dramatic lighting effects, sense of
            infinite possibility and freedom. Epic scope with detailed cosmic background and
            magical atmosphere.

            Include sound effects: "FLUTTER!" "TWINKLE!" "WHOOSH!" for magical flight.
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
            scene_type="mischief",  # Cinematic: dynamic chaos with dramatic lighting
            artistic_prompt="""
            Chaotic comic book action panel. Ancient library in complete chaos with books flying
            everywhere, pages flapping like birds. Multiple "FLUTTER!" "WHOOSH!" "FLAP!" sound
            effects scattered throughout as books soar through the air.

            {protagonist} ducks behind overturned wooden chair, wearing {costume}, laughing at the
            absurd situation. Speech bubble: "Oops! This wasn't in the instruction manual!"

            Midnight the black cat leaps athletically through the air, catching a flying book with
            perfect grace. Action lines show cat's acrobatic movement with "POUNCE!" sound effect.

            Tall wooden bookshelves stretch into shadows above. Papers swirl everywhere like a
            tornado. Warm candlelight creates dramatic shadows and highlights.

            Comic book chaos style: dynamic action lines, multiple motion effects, detailed
            expressions showing mischief and surprise. Classic comic book mischief scene with
            environmental storytelling and character reactions.

            Include sound effects: "FLUTTER!" "WHOOSH!" "POUNCE!" "RUSTLE!" for flying books.
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
            scene_type="friendship",  # Cinematic: intimate portrait with golden lighting
            artistic_prompt="""
            Heartwarming comic book panel. Cozy library window seat with warm golden afternoon
            light streaming through tall windows. {protagonist} sits peacefully wearing {costume},
            with a few papers still stuck in their hair from the book chaos.

            Midnight the black cat is curled contentedly in the child's lap, eyes closed in bliss.
            The child's hand gently pets the cat. Speech bubble: "I think I've found my people."

            Outside the window, Sparky the baby dragon presses his face against the glass with
            big hopeful eyes. Small speech bubble from Sparky: "Can I come in?" Tiny paw prints
            and nose prints visible on the window.

            Warm golden hour lighting creates a cozy atmosphere. Soft focus background with
            scattered books and papers. Sense of found family and belonging.

            Comic book art style: warm emotional tones, detailed character expressions showing
            contentment and love, intimate panel composition. Classic heartwarming family moment
            with emotional depth and connection.

            Include sound effects: "PURR!" from cat, soft "TAP TAP" from dragon at window.
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
            scene_type="peaceful",  # Cinematic: dramatic silhouette with magical moonlight
            artistic_prompt="""
            Epic finale comic book panel. Castle tower balcony at night with ornate stone railing.
            {protagonist} stands gazing out at incredible view, wearing {costume} that seems to
            contain actual moving stars. Profile shows peaceful contentment and quiet wonder.

            Three magical moons of different sizes hang in star-filled sky. Castle grounds twinkle
            with warm lights below. Cosmic backdrop with shooting stars and magical aurora effects.

            Midnight the black cat sits beside them on the railing, also gazing at the view.
            Sparky the small dragon curls contentedly at their feet, finally at peace.

            Speech bubble from child: "I'm ready for tomorrow... I'm ready for everything."
            Thought bubble contains small images of future adventures - flying, magic lessons,
            more friends.

            Text at bottom in classic comic book style: "THE END... of the Beginning."

            Comic book art style: dramatic silhouette against cosmic sky, magical lighting effects,
            silver moonlight rim lighting, warm window glow, sense of infinite possibility and
            new beginnings. Epic conclusion with emotional depth.

            Include atmospheric effects: "SPARKLE!" for starry cape, "TWINKLE!" for magical lights.
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


# COMIC PANEL VERSION - StoryGift-Style Layout
MAGIC_CASTLE_COMIC_THEME = [
    # PAGE 1: The Arrival - Two panels showing gate approach and test
    ComicPageTemplate(
        page_number=1,
        narrative="""The morning mist clung to the cobblestones as {name} finally arrived at the Grand Academy of Arcane Arts. Standing before the massive iron gates, heart pounding with excitement, {name} couldn't believe this was really happening. "Only the worthy may pass," hooted Professor Hoot from his pedestal, peering down through his enormous spectacles. """,
        left_panel=ComicPanel(
            image_prompt="""
            {protagonist} stands before massive ornate iron gates of an ancient magical castle, wearing {costume}. The child looks up with wonder and excitement. A large majestic owl with round spectacles perches on a stone pillar beside the gates. Morning golden lighting with magical atmosphere, floating sparkles and runes glowing on the gates. Professional children's book illustration style.
            """,
            dialogue=[
                DialogueBubble(
                    speaker="PROFESSOR HOOT",
                    text="Only the worthy may pass, young one.",
                    position="left"
                )
            ]
        ),
        right_panel=ComicPanel(
            image_prompt="""
            {protagonist} in determined pose, both hands gripping a wooden wand pointed at massive iron gates, wearing {costume}. Brilliant magical energy bursts from wand tip. The child's face shows pure determination and focus. Gate lock glows with activating magical energy. Professional children's book illustration style.
            """,
            dialogue=[
                DialogueBubble(
                    speaker="{name}",
                    text="ALOHOMORA!",
                    position="right"
                )
            ]
        ),
        costume="purple wizard robe with gold star embroidery"
    ),

    # PAGE 2: Gateway and Courtyard - Two panels showing entrance and wonder
    ComicPageTemplate(
        page_number=2,
        narrative="""With a thunderous CLANG, the ancient gates swung wide open. Beyond them lay a world {name} had only dreamed about - a courtyard filled with floating lanterns, students in colorful robes, and a magnificent castle that seemed to touch the clouds. "Welcome to the Grand Academy," Professor Hoot smiled. "Your adventure begins now!" """,
        left_panel=ComicPanel(
            image_prompt="""
            {protagonist} walks through massive opened gates, wearing {costume}. Wide-eyed expression of wonder and joy. Background reveals stunning magical courtyard: floating lanterns, students in colorful robes, gothic towers reaching clouds, ornate fountain with sparkles. Professional children's book illustration style.
            """,
            dialogue=[
                DialogueBubble(
                    speaker="PROFESSOR HOOT",
                    text="Welcome to the Grand Academy!",
                    position="left"
                )
            ]
        ),
        right_panel=ComicPanel(
            image_prompt="""
            {protagonist} stands in the magical courtyard, mouth agape in wonder, wearing {costume}. Around them, students practice magic, floating objects drift by, and the magnificent castle towers into clouds. The child's face shows pure amazement and joy. Professional children's book illustration style.
            """,
            dialogue=[
                DialogueBubble(
                    speaker="{name}",
                    text="It's more beautiful than I ever imagined!",
                    position="right"
                )
            ]
        ),
        costume="purple velvet cloak flowing behind"
    ),

    # PAGE 3: Beast Taming Chaos - Two panels showing danger and bravery
    ComicPageTemplate(
        page_number=3,
        narrative="""The first class was Beast Taming, and it started with chaos. A wooden crate in the center of the courtyard shook violently, smoke pouring from the cracks. Other students ran screaming, but {name} stepped closer. "Everyone back!" shouted Professor Flamel. But {name} wasn't afraid. Something in that crate needed help, not fear. """,
        left_panel=ComicPanel(
            image_prompt="""
            Wooden crate shakes violently in courtyard center, smoke and small flames emerging from the gaps. Other students run in panic in the background. An elderly professor (Professor Flamel) shouts warnings. Dramatic lighting from flames, sense of danger and chaos. Professional children's book illustration style.
            """,
            dialogue=[
                DialogueBubble(
                    speaker="PROFESSOR FLAMEL",
                    text="Everyone back! It's not safe!",
                    position="left"
                ),
                DialogueBubble(
                    speaker="STUDENT",
                    text="AAAH! It's going to explode!",
                    position="bottom"
                )
            ]
        ),
        right_panel=ComicPanel(
            image_prompt="""
            {protagonist} walks bravely toward the dangerous crate, wearing {costume} with sleeves rolled up. Expression shows brave curiosity rather than fear. They approach with one hand slightly raised in a calming gesture. Dramatic side lighting from the flames. Professional children's book illustration style.
            """,
            dialogue=[
                DialogueBubble(
                    speaker="{name}",
                    text="It's okay, little one... I'm here to help.",
                    position="right"
                )
            ]
        ),
        costume="casual purple wizard robes with rolled-up sleeves"
    ),

    # PAGE 4: Meeting Sparky - Two panels showing emergence and bonding
    ComicPageTemplate(
        page_number=4,
        narrative="""The crate EXPLODED open - but instead of a terrifying monster, out tumbled the smallest, saddest baby dragon {name} had ever seen. Red scales, tiny wings, and the most pitiful hiccup that sent a tiny smoke ring floating into the air. "You're not scary at all," {name} whispered, kneeling down. "You're just hungry and lonely, aren't you?" """,
        left_panel=ComicPanel(
            image_prompt="""
            Wooden crate explodes open with pieces scattered across stone ground. From the debris, a small baby dragon with bright red scales and stubby wings emerges, looking scared and lost. Large expressive eyes, smoke rings from tiny hiccups. Professional children's book illustration style.
            """,
            dialogue=[
                DialogueBubble(
                    speaker="SPARKY",
                    text="*HICCUP* *PUFF*",
                    position="left"
                )
            ]
        ),
        right_panel=ComicPanel(
            image_prompt="""
            {protagonist} kneels down gently, wearing {costume}, extending one hand with a piece of bread toward the baby dragon. The child's expression shows pure kindness and compassion. The baby dragon looks cautiously hopeful, leaning slightly toward the child. Professional children's book illustration style.
            """,
            dialogue=[
                DialogueBubble(
                    speaker="{name}",
                    text="You're not scary at all... just hungry!",
                    position="right"
                ),
                DialogueBubble(
                    speaker="SPARKY",
                    text="Friend?",
                    position="bottom"
                )
            ]
        ),
        costume="purple wizard robes with a bit of soot from the explosion"
    ),

    # PAGE 5: Flight Preparation and Launch - Two panels showing lesson and takeoff
    ComicPageTemplate(
        page_number=5,
        narrative="""After lunch came the class {name} had been waiting for: Flight Training! The broomstick vibrated with magical energy. At first it bucked like a wild horse, but {name} held on tight. "UP!" {name} commanded, and suddenly - WHOOSH! The ground fell away, and the sky opened up like a doorway to freedom. """,
        left_panel=ComicPanel(
            image_prompt="""
            {protagonist} stands on a grassy field with other students, holding a wooden broomstick that vibrates with magical energy, wearing {costume}. The child looks determined and excited. Other students watch nervously in background. Flight instructor gives guidance. Professional children's book illustration style.
            """,
            dialogue=[
                DialogueBubble(
                    speaker="FLIGHT INSTRUCTOR",
                    text="Remember, confidence is key! Trust your broomstick!",
                    position="left"
                ),
                DialogueBubble(
                    speaker="{name}",
                    text="I'm ready! Let's do this!",
                    position="right"
                )
            ]
        ),
        right_panel=ComicPanel(
            image_prompt="""
            {protagonist} soars upward on a rustic wooden broomstick, wearing {costume} with scarf streaming behind. Their face shows pure exhilaration - genuine smile, wind-swept hair, eyes sparkling with joy. Below, a grassy field with other students grows small. Sparky watches from the ground. Professional children's book illustration style.
            """,
            dialogue=[
                DialogueBubble(
                    speaker="{name}",
                    text="UP! YES! I'm flying!",
                    position="right"
                ),
                DialogueBubble(
                    speaker="SPARKY",
                    text="Wait for me!",
                    position="bottom"
                )
            ]
        ),
        costume="brown leather flight jacket, flying goggles, red scarf"
    ),

    # PAGE 6: Above the Clouds - Two panels showing wonder and cosmic beauty
    ComicPageTemplate(
        page_number=6,
        narrative="""Higher and higher {name} flew, until the castle became a toy below and the clouds became a soft, endless ocean around them. Three moons hung in the magical sky, and for one perfect moment, {name} felt like anything was possible. Even Sparky had somehow followed, his tiny wings working overtime to keep up.""",
        left_panel=ComicPanel(
            image_prompt="""
            {protagonist} flies through a dreamlike cloudscape, wearing {costume}, one hand reaching out to touch passing clouds. Expression shows pure wonder and peace. Cloud formations below look like soft ocean waves. Golden light catches everything. Professional children's book illustration style.
            """,
            dialogue=[
                DialogueBubble(
                    speaker="{name}",
                    text="This is the most beautiful thing I've ever seen!",
                    position="right"
                )
            ]
        ),
        right_panel=ComicPanel(
            image_prompt="""
            {protagonist} silhouetted against cosmic backdrop with three moons of different sizes in twilight purple-blue sky filled with stars. Sparky the baby dragon flies alongside with tiny wings working hard. Starlight creates magical sparkle effects throughout the scene. Professional children's book illustration style.
            """,
            dialogue=[
                DialogueBubble(
                    speaker="SPARKY",
                    text="This is amazing! I can see forever!",
                    position="left"
                ),
                DialogueBubble(
                    speaker="{name}",
                    text="Anything is possible up here...",
                    position="right"
                )
            ]
        ),
        costume="leather flight jacket, goggles reflecting the magical sky"
    ),

    # PAGE 7: Library Incident - Two panels showing temptation and chaos
    ComicPageTemplate(
        page_number=7,
        narrative="""The Ancient Library held thousands of magical books - and one very forbidden section. {name} couldn't resist reaching for a glowing red book, despite Midnight the cat's warning meow. The moment {name}'s finger touched the spine, every book in the library came ALIVE!""",
        left_panel=ComicPanel(
            image_prompt="""
            {protagonist} reaches toward a glowing red book on a high shelf in an ancient library, wearing {costume}. Midnight the black cat sits nearby with warning expression, ears back. Tall wooden bookshelves stretch into shadows. Warm candlelight creates dramatic shadows. Professional children's book illustration style.
            """,
            dialogue=[
                DialogueBubble(
                    speaker="MIDNIGHT",
                    text="MEOW! No! Don't touch that!",
                    position="left"
                ),
                DialogueBubble(
                    speaker="{name}",
                    text="Just one little peek...",
                    position="right"
                )
            ]
        ),
        right_panel=ComicPanel(
            image_prompt="""
            Ancient library in complete chaos with books flying everywhere, pages flapping like birds. {protagonist} ducks behind overturned wooden chair, wearing {costume}, laughing at the absurd situation. Papers swirl everywhere like a tornado. Midnight leaps athletically through the air. Professional children's book illustration style.
            """,
            dialogue=[
                DialogueBubble(
                    speaker="{name}",
                    text="Oops! This wasn't in the instruction manual!",
                    position="right"
                ),
                DialogueBubble(
                    speaker="MIDNIGHT",
                    text="I WARNED you!",
                    position="left"
                )
            ]
        ),
        costume="cozy cream knitted sweater with wizard crest"
    ),

    # PAGE 8: Library Resolution - Two panels showing teamwork and friendship
    ComicPageTemplate(
        page_number=8,
        narrative="""After the library chaos was sorted (and {name} promised never to touch the Restricted Section again), Midnight curled up in {name}'s lap while Sparky pressed his nose against the window, wanting to join. "I think I've found my people," {name} smiled, scratching Midnight's ears. "And my cat. And my dragon." """,
        left_panel=ComicPanel(
            image_prompt="""
            {protagonist} and Midnight the black cat work together to catch flying books, both leaping and reaching. The child wears {costume} and shows determination mixed with laughter. Books swirl around them but they're making progress. Teamwork in action. Professional children's book illustration style.
            """,
            dialogue=[
                DialogueBubble(
                    speaker="{name}",
                    text="Come on Midnight! We can fix this together!",
                    position="right"
                ),
                DialogueBubble(
                    speaker="MIDNIGHT",
                    text="I suppose you're not completely hopeless...",
                    position="left"
                )
            ]
        ),
        right_panel=ComicPanel(
            image_prompt="""
            {protagonist} sits peacefully in library window seat, wearing {costume}, bathed in warm golden afternoon light. Midnight is curled contentedly in their lap, eyes closed. Sparky presses his face against the window from outside, looking in hopefully. Sense of found family. Professional children's book illustration style.
            """,
            dialogue=[
                DialogueBubble(
                    speaker="{name}",
                    text="I think I've found my people...",
                    position="right"
                ),
                DialogueBubble(
                    speaker="SPARKY",
                    text="Can I come in? Please?",
                    position="bottom"
                )
            ]
        ),
        costume="cream knitted sweater, slightly disheveled with papers in hair"
    ),

    # PAGE 9: Evening Preparation - Two panels showing preparation and anticipation
    ComicPageTemplate(
        page_number=9,
        narrative="""As evening approached, {name} prepared for the first night at the Academy. Looking out from the dormitory window at the magical grounds below, with Midnight purring beside them and Sparky finally allowed inside, everything felt perfect. Tomorrow would bring new lessons, new adventures, and new magic to master.""",
        left_panel=ComicPanel(
            image_prompt="""
            {protagonist} sits at dormitory window as sunset light floods the room, wearing {costume}. They're writing in a journal or diary, reflecting on the day's events. Magical school supplies scattered around - wands, spell books, crystal orbs. Cozy dormitory setting. Professional children's book illustration style.
            """,
            dialogue=[
                DialogueBubble(
                    speaker="{name}",
                    text="Dear Diary, today was the most amazing day of my life...",
                    position="right"
                )
            ]
        ),
        right_panel=ComicPanel(
            image_prompt="""
            {protagonist} gazes out window at magical academy grounds at twilight, wearing {costume}. Midnight sits on windowsill, Sparky curls contentedly nearby. Outside, the castle grounds twinkle with warm lights, students practice magic in courtyards. Peaceful evening scene. Professional children's book illustration style.
            """,
            dialogue=[
                DialogueBubble(
                    speaker="{name}",
                    text="Tomorrow brings even more magic...",
                    position="right"
                ),
                DialogueBubble(
                    speaker="MIDNIGHT",
                    text="*purr* Sweet dreams, little wizard.",
                    position="left"
                )
            ]
        ),
        costume="comfortable pajamas with star patterns"
    ),

    # PAGE 10: Under the Moons - Two panels showing reflection and future dreams
    ComicPageTemplate(
        page_number=10,
        narrative="""As the three moons rose over the Grand Academy, {name} stood on the Astronomy Tower balcony with Midnight by their side and Sparky curled at their feet. The first day was over, but this was just the beginning. "I'm ready for tomorrow," {name} whispered to the stars. "I'm ready for everything." THE END... of the Beginning. """,
        left_panel=ComicPanel(
            image_prompt="""
            {protagonist} stands at ornate stone balcony railing on Astronomy Tower, wearing {costume}, gazing up at three magical moons in star-filled sky. Profile shows peaceful contentment and quiet wonder. Midnight sits beside them on the railing. Moonlight creates silver rim lighting. Professional children's book illustration style.
            """,
            dialogue=[
                DialogueBubble(
                    speaker="{name}",
                    text="I'm ready for tomorrow... for everything.",
                    position="right"
                )
            ]
        ),
        right_panel=ComicPanel(
            image_prompt="""
            Wide view from the tower balcony showing the entire magical academy spread out below, twinkling with lights. {protagonist} silhouetted against cosmic sky with Midnight and Sparky. The world spreads out below, full of possibility. Epic scope with magical atmosphere. Professional children's book illustration style.
            """,
            dialogue=[
                DialogueBubble(
                    speaker="SPARKY",
                    text="Sweet dreams, {name}. Tomorrow we fly again!",
                    position="left"
                ),
                DialogueBubble(
                    speaker="MIDNIGHT",
                    text="The adventure has only just begun...",
                    position="bottom"
                )
            ]
        ),
        costume="formal royal silk robes with starry cape containing moving stars"
    ),
]