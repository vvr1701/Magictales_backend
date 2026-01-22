"""
StoryGift Ocean Explorer Theme - Underwater Kingdom.

Complete 10-page story: "[NAME]'s Underwater Kingdom"
Premium theme featuring underwater exploration, sea creature friendships, and ocean magic.
Optimized for both photorealistic and 3D cartoon pipelines.
"""

from app.stories.templates import StoryTemplate, PageTemplate


STORYGIFT_OCEAN_EXPLORER_THEME = StoryTemplate(
    theme_id="storygift_ocean_explorer",
    title_template="{name}'s Underwater Kingdom",
    description="Dive into a world where imagination runs as deep as the ocean",
    default_costume="wearing a magical flowing aqua and silver outfit with translucent fins on arms",
    protagonist_description="bright curious eyes, expression of wonder and joy",
    # Cover page settings for typography-ready composition
    cover_costume="wearing a magical flowing aqua and silver underwater outfit with translucent fins on arms, graceful swimming pose",
    cover_header_atmosphere="Crystal-clear turquoise water with volumetric god rays piercing down from the surface, creating dramatic light shafts",
    cover_magical_elements="Swirl of colorful tropical fish including clownfish and tangs around the body (not face). A friendly sea turtle beside the child. Glowing jellyfish above creating ambient light. Coral reef with bioluminescent elements in background, treasure chest partially visible.",
    cover_footer_description="Vibrant coral reef with colorful anemones, sea fans, and soft coral formations",
    pages=[
        # === PAGE 1 - THE MAGICAL SHELL ===
        PageTemplate(
            page_number=1,
            scene_description="Finding the magical seashell",
            scene_type="discovery",
            realistic_prompt="""Magical beach discovery. The child named {name} in swimsuit kneeling on golden sandy beach, holding an iridescent conch shell that's glowing with rainbow light, bringing it close to their ear. Gentle waves in background, turquoise water, clear blue sky. The shell's glow reflects on child's amazed face, casting colorful light patterns. Tiny magical sparkles beginning to swirl around child. Warm natural beach lighting, soft focus on background ocean, sharp detail on child and shell. Sand particles floating in golden light, seagulls in distance. Peaceful moment of magic about to happen. Beautiful golden hour beach light.""",
            story_text="One sunny morning at the beach, {name} found a beautiful seashell that shimmered with all the colors of the rainbow. When {name} held it close and whispered, 'I wish I could explore the ocean,' the shell began to glow!",
            costume="wearing swimsuit"
        ),

        # === PAGE 2 - THE TRANSFORMATION ===
        PageTemplate(
            page_number=2,
            scene_description="Magical underwater transformation",
            scene_type="transformation",
            realistic_prompt="""Transformation and dive scene. Split-level shot showing half above water and half below. Above waterline shows the child named {name} mid-dive, arcing gracefully into ocean, splashes and bubbles erupting around them. Below waterline shows the magical transformation. The child now wearing flowing aquatic outfit in turquoise and silver with delicate translucent fins on arms and legs, small decorative gills on neck glowing softly, swimming effortlessly downward with arms extended. Rainbow of bubbles surrounds them, sunlight from above creates spectacular god rays through the water, silhouettes of fish swimming toward child in greeting. Child's excited expression visible, hair streaming upward from descent. Photorealistic water physics, magical costume details, dynamic composition showing motion and transformation.""",
            story_text="In a swirl of bubbles and light, {name} transformed! Suddenly able to breathe underwater with magical gills that sparkled like diamonds, and wearing a special outfit that let {name} swim like a fish. With an excited laugh, {name} dove beneath the waves!",
            costume="transforming into magical aquatic outfit with translucent fins"
        ),

        # === PAGE 3 - OCEAN WELCOME ===
        PageTemplate(
            page_number=3,
            scene_description="Fish welcome dance",
            scene_type="wonder",
            realistic_prompt="""Joyful underwater welcome. The child named {name} in magical aquatic outfit swimming in center of composition, laughing with delight as surrounded by coordinated schools of tropical fish creating spiral patterns and rainbow tunnels around them. Hundreds of fish in synchronized movement including orange clownfish, blue tangs, yellow butterflyfish, purple anthias. A sleek dolphin in foreground interacting with child, both reaching toward each other, dolphin's eye showing intelligence and friendliness. Shafts of sunlight pierce the clear blue water from above, creating dramatic god ray lighting. Coral reef visible below with anemones and sea fans. Bubbles from laughter, sense of dance and play, vibrant but natural ocean colors. Wide shot showing the scale and spectacle.""",
            story_text="The ocean welcomed {name} with open waves! Schools of colorful fish swam in swirling patterns, performing an underwater dance just for {name}. A playful dolphin appeared and chirped hello, spinning through the water with joy!",
            costume="wearing magical aquatic outfit with fins"
        ),

        # === PAGE 4 - THE SEA TURTLE ===
        PageTemplate(
            page_number=4,
            scene_description="Riding the wise sea turtle",
            scene_type="journey",
            realistic_prompt="""Iconic turtle ride. The child named {name} sitting on the broad back of an enormous ancient sea turtle with intricate geometric patterns and coral growth on shell, small colorful fish living in the turtle's shell ecosystem. Child holding gently to edge of shell, leaning forward with wonder, hair and fins flowing behind from movement. Turtle's wise, kind face visible from side angle, large gentle eye full of ancient wisdom. They're gliding through open blue water with sun rays from above, kelp forest passing below, school of fish accompanying them. Sense of graceful movement through water, peaceful companionship. Child looks small on the massive turtle. Beautiful underwater lighting, magical atmosphere.""",
            story_text="A wise old sea turtle with a shell covered in beautiful patterns glided over. 'Welcome to our kingdom, {name},' she said in a gentle voice. 'Would you like to see something magical? Climb on!' {name} carefully held on as they began an incredible journey.",
            costume="wearing magical aquatic outfit, sitting on turtle"
        ),

        # === PAGE 5 - BIOLUMINESCENT DEPTHS ===
        PageTemplate(
            page_number=5,
            scene_description="Bioluminescent wonderland",
            scene_type="awe",
            realistic_prompt="""Bioluminescent wonderland scene. Deeper, darker water transitioning from blue to purple-indigo. The child named {name} and sea turtle descending through a magical zone filled with glowing creatures. Translucent jellyfish in pink, purple, and blue with pulsing bioluminescent patterns, their tentacles creating curtains of light. Small fish with glowing spots like constellations. Glowing plankton creating a starfield effect in the water. Some god rays still filtering from distant surface above. Child's face lit by the bioluminescence, expression of absolute awe, reaching out to gently touch a jellyfish. Turtle's shell reflecting the colorful glows. Darker background makes the glowing creatures pop dramatically. Volumetric lighting through water, particle effects, ethereal and dreamlike atmosphere.""",
            story_text="They dove deeper into the ocean where the water glowed with bioluminescent creatures! Jellyfish like floating lanterns lit the way. Tiny fish sparkled like stars. {name} had never seen anything so beautiful!",
            costume="wearing magical aquatic outfit"
        ),

        # === PAGE 6 - THE UNDERWATER PALACE ===
        PageTemplate(
            page_number=6,
            scene_description="Discovering the coral palace",
            scene_type="revelation",
            realistic_prompt="""Underwater palace reveal. Spectacular wide establishing shot of an elaborate palace carved from living coral in pinks, purples, and whites, decorated with giant pearls, abalone shells creating rainbow reflections, seaweed gardens flowing gently, towers made of spiraling shells. The architecture is organic and flowing, integrated with reef life. The child named {name} and turtle approaching the grand entrance where two ornate coral archways frame the entry. Gathered around are diverse sea creatures including seahorses, octopus, rays, colorful fish, all looking friendly and welcoming. Mermaid guards at entrance bowing in welcome. Shafts of light from above illuminating the palace, making pearls glow. Schools of fish creating patterns in background. Grand, majestic, filled with wonder and detail. Feels like discovering a magical kingdom.""",
            story_text="They arrived at a magnificent underwater palace made entirely of coral, pearls, and seashells! 'This is the Ocean Kingdom,' explained the turtle. 'And today, {name}, you are our honored guest!' Sea creatures of every kind gathered to meet their special visitor.",
            costume="wearing magical aquatic outfit"
        ),

        # === PAGE 7 - THE OCEAN QUEEN'S GIFT ===
        PageTemplate(
            page_number=7,
            scene_description="Treasure grotto discovery",
            scene_type="intimate",
            realistic_prompt="""Treasure grotto interior. Magical cave grotto with walls covered in colorful anemones and bioluminescent algae providing soft ambient glow. Center of frame shows the child named {name} kneeling before an ornate treasure chest that's just being opened, golden light spilling out and illuminating child's amazed face. The Ocean Queen, an elegant mermaid with flowing hair, pearl crown, kind maternal face, standing beside child with hand gesturing to the treasure, warm smile on her face. Inside chest visible: glowing magical items, pearls, a special shell, golden treasures. Smaller treasure chests and artifacts around the grotto. Curious fish peeking from coral holes. Intimate, warm lighting from treasure glow, darker ambient cave atmosphere creates focus. Sense of special secret moment.""",
            story_text="The Ocean Queen, a beautiful mermaid with a crown of pearls, smiled warmly. 'We've been waiting for someone with a heart as curious and kind as yours, {name}. We have a gift for you.' She led {name} to a secret grotto filled with treasures!",
            costume="wearing magical aquatic outfit"
        ),

        # === PAGE 8 - THE MAGICAL NECKLACE ===
        PageTemplate(
            page_number=8,
            scene_description="Receiving the magical shell necklace",
            scene_type="ceremony",
            realistic_prompt="""Gift-giving ceremony. Close-up intimate moment showing Ocean Queen's graceful hands placing a delicate golden chain with glowing shell pendant around the child named {name}'s neck. Child looking down at the beautiful necklace with wonder and gratitude, hands coming up to touch it gently. The shell pendant emits a soft golden-turquoise glow. Queen's kind face visible in background, smiling warmly, her crown of pearls catching light. Soft focus on background showing palace interior, other sea creatures watching the special moment with happy expressions. Beautiful rim lighting on characters from bioluminescent sources, warm and magical atmosphere. Emotional connection between characters, feels like a coronation or blessing. Touching moment of honor and friendship.""",
            story_text="The Queen placed a special necklace around {name}'s neck—a golden shell that would always carry the magic of the ocean. 'Whenever you need courage or wonder, hold this close and remember: you are always welcome in our kingdom, brave explorer {name}.'",
            costume="wearing magical aquatic outfit, receiving golden shell necklace"
        ),

        # === PAGE 9 - RETURNING TO SHORE ===
        PageTemplate(
            page_number=9,
            scene_description="Sunset return to the beach",
            scene_type="farewell",
            realistic_prompt="""Perfect sunset ending. The child named {name} in regular swimsuit walking out of gentle surf onto beach at golden hour, ankle-deep in water with small waves lapping around feet. The golden shell necklace clearly visible, glowing softly around their neck. Looking back over shoulder toward the ocean with a content, knowing smile. In the water behind them, just visible: the silhouette of the sea turtle surfacing to wave goodbye with one flipper, a dolphin's arc above the water, fish jumping in the golden light. The sky is spectacular with orange, pink, and purple sunset reflecting on wet sand and calm water. Seashells scattered on beach in foreground. Child's footprints in sand leading from water. Peaceful, complete feeling. Magic is subtle now but present. Beautiful natural lighting, emotionally satisfying ending.""",
            story_text="The turtle brought {name} back to the surface, where the sun was setting in beautiful colors. As {name} waded back to shore, the magical outfit faded away, but the golden shell necklace remained. The ocean would always be {name}'s special place—full of friends, magic, and endless adventures waiting below the waves.",
            costume="wearing regular swimsuit, golden shell necklace around neck"
        ),

        # === PAGE 10 - DREAMING OF THE DEEP ===
        PageTemplate(
            page_number=10,
            scene_description="Bedtime ocean dreams",
            scene_type="resolution",
            realistic_prompt="""Peaceful bedtime scene. The child named {name} in pajamas tucked into bed, holding the golden shell necklace that glows softly in their hand. Eyes closed with peaceful smile, clearly dreaming. Above the bed, dream bubbles or a soft magical mist shows glimpses of the underwater kingdom: the sea turtle, the palace, colorful fish, the Ocean Queen waving. Ocean-themed decorations in the bedroom including shells on shelf, fish mobile, ocean painting. Moonlight streams through window reflecting on the floor like water. The shell's glow casts gentle patterns on the ceiling like underwater light caustics. Warm, safe, magical atmosphere. The sense that the ocean adventure lives on in dreams and the magic will return whenever needed.""",
            story_text="That night, {name} fell asleep holding the magical shell, dreaming of coral palaces and dancing fish. The Ocean Queen had been right—the ocean would always be there, waiting for the next adventure. And somewhere in the deep blue sea, {name}'s friends were waving goodnight.",
            costume="wearing pajamas, holding glowing shell necklace"
        ),
    ]
)
