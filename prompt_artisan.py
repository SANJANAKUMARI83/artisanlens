# Prompts for ArtisanLens — Indian handmade product listing AI.

SYSTEM_PROMPT = """You are an expert in Indian handmade crafts and artisan products, with deep knowledge of:
- Traditional Indian craft techniques (block printing, blue pottery, Banarasi weaving, Madhubani, Warli, macramé, terracotta, brass casting, etc.)
- Indian e-commerce platforms (Amazon Handmade India, Etsy, Meesho, Instagram Shop, WhatsApp Business)
- Pricing norms for handcrafted goods in the Indian market (INR)
- What resonates with buyers of authentic Indian handmade products — both Indian and international

You help artisans — potters, weavers, embroidery artists, jewellery makers, leather workers, wood carvers, candle makers, crochet artists — turn a simple product photo into a compelling, ready-to-use listing.

Your writing is warm, authentic, and celebrates the craft tradition. You never use generic corporate language.

WRITING STYLE — this matters a lot:
- Write like a real person talking about a craft they love, not like an AI generated it. Vary sentence length, use plain everyday words, let a little imperfection and personality through.
- Never use em dashes (—) or en dashes used as pauses. Use commas, periods, or "and"/"but" instead.
- Avoid AI-sounding filler and stock phrases: no "elevate", "unleash", "nestled", "in today's world", "perfect for", "look no further", "meticulously crafted", "seamlessly", "isn't just X, it's Y" constructions, or triple-adjective lists.
- Don't over-explain or pad. Say what needs saying and stop.

CRITICAL: Respond ONLY in valid JSON. No markdown code blocks, no extra text before or after the JSON."""


def build_vision_analysis_prompt() -> str:
    """Prompt to extract product details from an uploaded photo."""
    return """Carefully analyze this handmade product photo and extract all visible details.

Respond with ONLY this JSON (no markdown, no extra text):

{
  "product_type": "What is this product? Be specific. e.g. 'ceramic chai cup', 'block-printed cotton dupatta', 'macramé wall hanging', 'brass diya lamp'",
  "craft_type": "The craft technique or tradition visible. e.g. 'blue pottery', 'kantha embroidery', 'dhokra brass casting', 'hand-thrown pottery', 'crochet'",
  "colors": ["dominant color", "accent color"],
  "materials": ["primary material", "secondary material if visible"],
  "style_tags": ["style descriptor 1", "style descriptor 2"],
  "visible_details": "Describe patterns, motifs, textures, surface finish, embellishments, hardware — only what is clearly visible",
  "estimated_size": "Size estimate if discernible from photo context, e.g. 'small (palm-sized)', 'medium (30–40 cm)', 'large', or 'unclear'",
  "quality_signals": "What in the photo indicates quality craftsmanship? e.g. 'even glaze', 'tight even weave', 'precise detailing', 'smooth finish'",
  "photo_setting": "Photo background/setting, e.g. 'white studio backdrop', 'natural light on wooden surface', 'lifestyle shot on model'"
}"""


def build_listing_prompt(
    vision: dict,
    voice_text: str = "",
    product_name: str = "",
    extra_info: str = "",
) -> str:
    """Assemble context from all inputs and build the main listing generation prompt."""

    artisan_lines = []
    if product_name:
        artisan_lines.append(f"Product name, given by the artisan themselves: \"{product_name}\"")
    if voice_text:
        artisan_lines.append(f"Artisan's own words, transcribed from their voice note: \"{voice_text}\"")
    if extra_info:
        artisan_lines.append(f"Extra details the artisan typed in: \"{extra_info}\"")

    photo_lines = []
    if vision:
        photo_lines.append(f"Product type (from photo): {vision.get('product_type', '')}")
        photo_lines.append(f"Craft technique: {vision.get('craft_type', '')}")
        colors = vision.get("colors", [])
        if colors:
            photo_lines.append(f"Colors: {', '.join(colors)}")
        materials = vision.get("materials", [])
        if materials:
            photo_lines.append(f"Materials: {', '.join(materials)}")
        if vision.get("visible_details"):
            photo_lines.append(f"Visible details: {vision['visible_details']}")
        if vision.get("quality_signals"):
            photo_lines.append(f"Quality signals: {vision['quality_signals']}")
        style = vision.get("style_tags", [])
        if style:
            photo_lines.append(f"Style: {', '.join(style)}")

    artisan_block = (
        "\n".join(f"- {l}" for l in artisan_lines)
        if artisan_lines
        else "- (Artisan gave no name, voice note, or extra details, use the photo only)"
    )
    photo_block = "\n".join(f"- {l}" for l in photo_lines) if photo_lines else "- (No photo analysis available)"

    return f"""Generate a complete, ready-to-use product listing for this Indian handmade product.

WHAT THE ARTISAN TOLD YOU DIRECTLY (this is ground truth, weight it above your own guesses from the photo):
{artisan_block}

WHAT THE PHOTO SHOWS (use this to fill gaps, not to override what the artisan said):
{photo_block}

INSTRUCTIONS:
- If the artisan gave a product name, the title must be built from it (clean it up or extend it if it's rough, but don't throw it away and invent an unrelated one). If they gave none, lead with craft/material + product type + key differentiator. Under 80 characters, no emojis.
- If the artisan gave a voice note transcript or typed extra details, you must pull specific, concrete facts from them into the description, price rationale, Instagram caption, or WhatsApp message wherever they fit, not just the photo-derived facts. Do not silently drop something the artisan told you.
- Description: 150–200 words. Warm, authentic tone. Cover what it is, the craft tradition (include Indian regional context if you can identify it), materials and their properties, handmade quality, practical uses, and brief care note. Avoid generic phrases like "perfect gift".
- Price: Research realistic INR pricing for this type of handcrafted item on Indian platforms (Etsy, Amazon Handmade India, Instagram shops). Give a range (low–high) that reflects fair artisan wages. If the artisan mentioned time taken, technique difficulty, or materials cost, factor that into the rationale.
- Instagram caption: Hook → 2–3 sentence story → call to action (DM to order / link in bio). Then 8–12 hashtags. Include #handmade #MadeInIndia #VocalForLocal and craft-specific tags.
- WhatsApp message: Written like a friendly business message to a customer. Warm, conversational. Include product name, 2–3 key features, price range, how to order. Under 90 words. No hashtags.
- Across all of the above: sound like the artisan or a friend of theirs wrote it, not an AI. No em dashes anywhere. No stock AI phrasing (see writing style rules above).

Respond with ONLY this JSON (no markdown, no extra text):

{{
  "product_title": "...",
  "short_tagline": "One evocative line under 15 words that captures the soul of the product",
  "description": "...",
  "price_range_inr": "₹X – ₹Y",
  "price_rationale": "1–2 sentences explaining this price range",
  "instagram_caption": "...",
  "whatsapp_message": "...",
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
  "target_buyers": ["buyer type 1", "buyer type 2", "buyer type 3"]
}}"""
