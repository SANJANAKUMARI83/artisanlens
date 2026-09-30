"""
ArtisanLens - AI Listing Generator for Indian Handmade Products
Upload a product photo plus an optional voice note, and get a ready-to-post
listing in seconds: title, description, INR price, Instagram caption, WhatsApp message.
"""
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── Page config (must be first Streamlit call) ─────────────────────────────────
st.set_page_config(
    page_title="ArtisanLens - AI Listing Generator",
    page_icon="🪔",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"], .stApp, .stMarkdown, p, span, div, label {
        font-family: 'Inter', -apple-system, sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at 15% 0%, #FFF9F3 0%, #FDF3E7 45%, #FAEBDA 100%);
    }

    /* Push content below Streamlit's own top toolbar so the badge/header never gets clipped */
    header[data-testid="stHeader"] { background: transparent !important; }
    .block-container { padding-top: 4.2rem !important; padding-bottom: 3rem; }

    /* Force readable dark text everywhere in the main content area, regardless of the
       app's base theme, so placeholders/labels/hints never end up white-on-white. */
    [data-testid="stAppViewContainer"] section.main,
    [data-testid="stAppViewContainer"] section.main p,
    [data-testid="stAppViewContainer"] section.main span,
    [data-testid="stAppViewContainer"] section.main label,
    [data-testid="stAppViewContainer"] section.main li,
    [data-testid="stAppViewContainer"] section.main div {
        color: #2C1810;
    }
    [data-testid="stAppViewContainer"] section.main .stTextInput input,
    [data-testid="stAppViewContainer"] section.main .stTextArea textarea {
        color: #2C1810 !important;
    }
    [data-testid="stAppViewContainer"] section.main ::placeholder {
        color: #A08D7C !important; opacity: 1 !important;
    }
    [data-testid="stAppViewContainer"] section.main [data-testid="stFileUploaderDropzoneInstructions"] * {
        color: #6B4C3B !important;
    }
    [data-testid="stAppViewContainer"] section.main [data-testid="stFileUploaderDropzoneInstructions"] small {
        color: #A08D7C !important;
    }
    [data-testid="stAppViewContainer"] section.main [data-testid="stBaseButton-secondary"] {
        color: #2C1810 !important;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2C1810 0%, #3D2317 100%);
    }
    section[data-testid="stSidebar"] * { color: #F3E4D4 !important; }
    section[data-testid="stSidebar"] h2 { font-family: 'Playfair Display', serif; font-weight: 700; }
    section[data-testid="stSidebar"] input {
        background: #FFF9F3 !important; color: #2C1810 !important; border-radius: 10px !important;
        border: 1px solid rgba(232,98,42,.35) !important;
    }
    section[data-testid="stSidebar"] hr { border-color: rgba(243,228,212,.15) !important; margin: 1.2rem 0; }
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color: #C9AC93 !important; }

    /* ── Hero header ── */
    .hero-badge {
        display: inline-block; background: rgba(232,98,42,.12); color: #C6491A !important; font-weight: 600;
        font-size: .72rem; letter-spacing: .09em; text-transform: uppercase; padding: .4rem 1rem;
        border-radius: 999px; margin-bottom: .8rem; border: 1px solid rgba(232,98,42,.25);
    }
    .main-header {
        font-family: 'Playfair Display', serif; font-size: 2.9rem; font-weight: 800;
        background: linear-gradient(100deg, #E8622A 0%, #C6491A 60%, #A63D18 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
        margin-bottom: .2rem; line-height: 1.12; letter-spacing: -.01em;
    }
    .sub-header {
        font-size: 1.08rem; color: #6B4C3B; margin-top: .3rem; margin-bottom: 2rem;
        max-width: 600px; line-height: 1.6; font-weight: 400;
    }

    /* ── Step headers ── */
    .step-row { display: flex; align-items: center; gap: .7rem; margin: 2rem 0 .9rem 0; }
    .step-num {
        display: flex; align-items: center; justify-content: center; width: 30px; height: 30px;
        border-radius: 50%; background: linear-gradient(135deg, #E8622A, #C6491A); color: white !important;
        font-weight: 700; font-size: .9rem; flex-shrink: 0; box-shadow: 0 3px 8px rgba(232,98,42,.35);
    }
    .step-label { font-size: 1.18rem; font-weight: 700; color: #2C1810; margin: 0; font-family: 'Playfair Display', serif; }
    .step-hint { font-size: .85rem; color: #A08D7C; margin: -.4rem 0 1rem 2.4rem; }

    /* ── Cards (bordered containers) ── */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 18px !important;
        box-shadow: 0 4px 20px rgba(44,24,16,.06);
        background: #FFFFFF;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] > div { border-radius: 18px !important; }

    .output-label { font-weight: 700; color: #2C1810; font-size: 1.05rem; margin-bottom: .15rem; }
    .copy-hint { font-size: .8rem; color: #A08D7C; margin-top: -.05rem; margin-bottom: .7rem; }

    /* ── Required / optional field badges ── */
    .field-badge-required {
        background: #E8622A; color: #FFFFFF !important; font-size: .66rem; font-weight: 700;
        letter-spacing: .05em; text-transform: uppercase; padding: .15rem .55rem;
        border-radius: 999px; margin-left: .6rem; vertical-align: middle; display: inline-block;
    }
    .field-badge-optional {
        background: transparent; color: #A08D7C !important; font-size: .66rem; font-weight: 700;
        letter-spacing: .05em; text-transform: uppercase; padding: .13rem .55rem;
        border: 1px solid rgba(160,141,124,.4); border-radius: 999px; margin-left: .6rem;
        vertical-align: middle; display: inline-block;
    }
    .field-label {
        font-weight: 600; color: #2C1810; font-size: .95rem; margin-bottom: .35rem;
    }

    .price-badge {
        background: linear-gradient(90deg, #E8622A, #F08A50); color: white !important; padding: .5rem 1.2rem;
        border-radius: 999px; font-weight: 700; font-size: 1.2rem; display: inline-block;
        box-shadow: 0 6px 16px rgba(232,98,42,.3); letter-spacing: .01em;
    }
    .tagline { font-style: italic; color: #8A6A55; font-size: 1.1rem; margin: .4rem 0 1.1rem 0; font-family: 'Playfair Display', serif; }
    .product-title { font-family: 'Playfair Display', serif; font-weight: 700; color: #2C1810; font-size: 1.7rem; margin-bottom: .2rem; }

    /* ── Buttons ── */
    .stButton>button {
        border-radius: 12px !important; font-weight: 700 !important; letter-spacing: .01em;
        padding: .65rem 1rem !important; transition: transform .15s ease, box-shadow .15s ease;
    }
    .stButton>button[kind="primary"] {
        background: linear-gradient(100deg, #E8622A, #D6501C) !important; border: none !important;
        box-shadow: 0 8px 20px rgba(232,98,42,.35) !important;
    }
    .stButton>button[kind="primary"] * { color: white !important; }
    .stButton>button[kind="primary"]:hover { transform: translateY(-2px); box-shadow: 0 10px 24px rgba(232,98,42,.42) !important; }
    .stButton>button[kind="secondary"] {
        background: #FFF9F3 !important; border: 1.5px solid rgba(232,98,42,.3) !important; color: #C6491A !important;
    }
    .stButton>button:hover { transform: translateY(-1px); }

    /* ── File uploader ── */
    [data-testid="stFileUploaderDropzone"] {
        border-radius: 14px !important; border: 1.5px dashed rgba(232,98,42,.4) !important;
        background: rgba(232,98,42,.03) !important;
    }

    /* ── Inputs ── */
    .stTextArea textarea, .stTextInput input {
        border-radius: 10px !important; border: 1px solid rgba(44,24,16,.12) !important;
        background: #FFFFFF !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: rgba(232,98,42,.5) !important; box-shadow: 0 0 0 1px rgba(232,98,42,.2) !important;
    }

    /* ── Divider ── */
    hr {
        border: none; height: 1px;
        background: linear-gradient(90deg, transparent, rgba(232,98,42,.35), transparent);
        margin: 1.8rem 0;
    }

    /* ── Expander ── */
    [data-testid="stExpander"] {
        border-radius: 14px !important; border: 1px solid rgba(44,24,16,.08) !important; overflow: hidden;
        background: #FFFFFF;
    }

    /* ── Alerts ── */
    [data-testid="stAlert"] { border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)


# ── Session state ──────────────────────────────────────────────────────────────
def _init():
    defaults = {
        "vision_result":   None,
        "listing_result":  None,
        "voice_transcript": "",
        "last_photo_name": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🪔 ArtisanLens")
    st.markdown("AI listing generator for Indian handmade artisans.")
    st.divider()

    # API key — prefer Streamlit secrets, then env var, then user input
    # Built-in key (Streamlit secrets or env var) is used behind the scenes and
    # never shown or pre-filled in the input, so it can't leak through the
    # password field's reveal icon on the public demo. Visitors can still
    # paste their own key to use instead.
    secret_key = st.secrets.get("GOOGLE_API_KEY", "") if hasattr(st, "secrets") else ""
    env_key    = os.getenv("GOOGLE_API_KEY", "")
    built_in_key = secret_key or env_key

    user_key = st.text_input(
        "Google Gemini API Key",
        value="",
        type="password",
        placeholder="Using the built-in demo key" if built_in_key else "Paste your free key here",
        help="Free key from aistudio.google.com. No credit card needed. Leave blank to use the demo's key.",
    )
    api_key = user_key or built_in_key
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key

    st.divider()
    st.markdown("**How it works:**")
    st.markdown(
        "1. Upload a product photo\n"
        "2. Add a voice note or type details *(optional)*\n"
        "3. Click **Generate** → copy your listing"
    )
    st.divider()
    st.caption("Built for the AI for Handmade Challenge 🏆\nPowered by Google Gemini")


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown('<span class="hero-badge">✦ Made for Indian Artisans</span>', unsafe_allow_html=True)
st.markdown('<p class="main-header">🪔 ArtisanLens</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Upload a photo of your handmade product and get a ready-to-post listing: '
    'title, description, price, Instagram caption, and WhatsApp message.</p>',
    unsafe_allow_html=True,
)


# ── Step 1: Photo ──────────────────────────────────────────────────────────────
st.markdown(
    '<div class="step-row"><span class="step-num">1</span>'
    '<p class="step-label">Upload your product photo'
    '<span class="field-badge-required">Required</span></p></div>',
    unsafe_allow_html=True,
)

photo = st.file_uploader(
    "Upload a clear photo of your product",
    type=["jpg", "jpeg", "png", "webp"],
    label_visibility="collapsed",
)

if photo:
    # Reset results if a new photo is uploaded
    if photo.name != st.session_state.last_photo_name:
        st.session_state.vision_result  = None
        st.session_state.listing_result = None
        st.session_state.last_photo_name = photo.name

    col_img, col_tip = st.columns([1, 1])
    with col_img:
        st.image(photo, use_container_width=True)
    with col_tip:
        st.markdown("**Tips for a great photo:**")
        st.markdown(
            "- Natural or bright white light\n"
            "- Clean, simple background\n"
            "- Show the full product\n"
            "- Include detail shots if possible"
        )

st.markdown("---")

# ── Step 2: Extra info (optional) ──────────────────────────────────────────────
st.markdown(
    '<div class="step-row"><span class="step-num">2</span>'
    '<p class="step-label">Tell us more</p></div>'
    '<p class="step-hint">Optional, but it makes a real difference to the result</p>',
    unsafe_allow_html=True,
)

col_a, col_b = st.columns([1, 1])
with col_a:
    st.markdown(
        '<p class="field-label">Product name<span class="field-badge-optional">Optional</span></p>',
        unsafe_allow_html=True,
    )
    product_name = st.text_input(
        "Product name",
        placeholder="e.g. Handwoven Ikat Stole",
        label_visibility="collapsed",
    )
with col_b:
    st.markdown(
        '<p class="field-label">Voice note (Hindi or English, any format)'
        '<span class="field-badge-optional">Optional</span></p>',
        unsafe_allow_html=True,
    )
    voice_file = st.file_uploader(
        "Voice note (Hindi or English, any format)",
        type=["mp3", "wav", "m4a", "ogg", "webm"],
        key="voice_uploader",
        label_visibility="collapsed",
    )

st.markdown(
    '<p class="field-label">Any other details about your product'
    '<span class="field-badge-optional">Optional</span></p>',
    unsafe_allow_html=True,
)
extra_info = st.text_area(
    "Any other details about your product",
    placeholder=(
        "e.g. Made with natural indigo dye, takes 3 days to hand-weave, "
        "inspired by traditional Pochampally patterns, suitable for weddings and festivals"
    ),
    height=90,
    label_visibility="collapsed",
)

st.markdown("---")

# ── Step 3: Generate ───────────────────────────────────────────────────────────
st.markdown(
    '<div class="step-row"><span class="step-num">3</span>'
    '<p class="step-label">Generate your listing</p></div>',
    unsafe_allow_html=True,
)

ready = bool(photo and api_key)
if not photo:
    st.info("Upload a product photo above to get started.")
elif not api_key:
    st.warning("Enter your Google Gemini API key in the sidebar. Get one free at aistudio.google.com")

if st.button("🚀 Generate Listing", type="primary", disabled=not ready, use_container_width=True):
    image_bytes = photo.read()

    # ── Vision analysis ──
    with st.spinner("🔍 Analysing your product photo..."):
        try:
            from llm import call_llm_vision_json
            from prompt_artisan import SYSTEM_PROMPT, build_vision_analysis_prompt

            vision = call_llm_vision_json(
                build_vision_analysis_prompt(),
                image_bytes,
                SYSTEM_PROMPT,
            )
            st.session_state.vision_result = vision
        except Exception as e:
            st.error(f"Photo analysis failed: {e}")
            st.stop()

    # ── Voice transcription (if provided) ──
    voice_text = ""
    if voice_file:
        with st.spinner("🎙️ Transcribing your voice note..."):
            try:
                from llm import transcribe_audio
                audio_bytes = voice_file.read()
                voice_text  = transcribe_audio(audio_bytes, voice_file.name)
                st.session_state.voice_transcript = voice_text
            except Exception as e:
                st.warning(f"Voice transcription skipped (continuing without it): {e}")

    # ── Listing generation ──
    with st.spinner("✍️ Writing your listing..."):
        try:
            from llm import call_llm_json
            from prompt_artisan import build_listing_prompt

            listing = call_llm_json(
                build_listing_prompt(
                    vision=st.session_state.vision_result or {},
                    voice_text=voice_text,
                    product_name=product_name,
                    extra_info=extra_info,
                ),
                SYSTEM_PROMPT,
            )
            st.session_state.listing_result = listing
        except Exception as e:
            st.error(f"Listing generation failed: {e}")
            st.stop()

    st.rerun()


# ── Results ────────────────────────────────────────────────────────────────────
if st.session_state.listing_result:
    listing = st.session_state.listing_result
    st.success("✅ Your listing is ready. Click inside any box to select all, then copy.")
    st.markdown("---")

    # ── Title + tagline + price ──
    title   = listing.get("product_title", "")
    tagline = listing.get("short_tagline", "")
    price   = listing.get("price_range_inr", "")
    rationale = listing.get("price_rationale", "")

    with st.container(border=True):
        st.markdown(f'<p class="product-title">{title}</p>', unsafe_allow_html=True)
        if tagline:
            st.markdown(f'<p class="tagline">"{tagline}"</p>', unsafe_allow_html=True)
        if price:
            st.markdown(f'<span class="price-badge">{price}</span>', unsafe_allow_html=True)
            if rationale:
                st.caption(rationale)

    # ── Description ──
    with st.container(border=True):
        st.markdown('<p class="output-label">📝 Product Description</p>', unsafe_allow_html=True)
        st.markdown('<p class="copy-hint">Copy and paste to your marketplace listing, website, or bio</p>', unsafe_allow_html=True)
        st.text_area(
            "description",
            value=listing.get("description", ""),
            height=200,
            label_visibility="collapsed",
            key="out_desc",
        )

    # ── Instagram ──
    with st.container(border=True):
        st.markdown('<p class="output-label">📸 Instagram Caption</p>', unsafe_allow_html=True)
        st.markdown('<p class="copy-hint">Ready to post, includes hashtags</p>', unsafe_allow_html=True)
        st.text_area(
            "instagram",
            value=listing.get("instagram_caption", ""),
            height=180,
            label_visibility="collapsed",
            key="out_insta",
        )

    # ── WhatsApp ──
    with st.container(border=True):
        st.markdown('<p class="output-label">💬 WhatsApp Message</p>', unsafe_allow_html=True)
        st.markdown('<p class="copy-hint">Paste into WhatsApp Business catalogue or send directly to customers</p>', unsafe_allow_html=True)
        st.text_area(
            "whatsapp",
            value=listing.get("whatsapp_message", ""),
            height=130,
            label_visibility="collapsed",
            key="out_wa",
        )

    # ── Keywords + target buyers ──
    with st.container(border=True):
        col_k, col_t = st.columns(2)
        with col_k:
            keywords = listing.get("keywords", [])
            if keywords:
                st.markdown('<p class="output-label">🔍 Search Keywords</p>', unsafe_allow_html=True)
                st.write("  ·  ".join(keywords))

        with col_t:
            buyers = listing.get("target_buyers", [])
            if buyers:
                st.markdown('<p class="output-label">👥 Target Buyers</p>', unsafe_allow_html=True)
                for b in buyers:
                    st.write(f"• {b}")

    # ── Collapsed: voice transcript + vision details ──
    if st.session_state.voice_transcript:
        with st.expander("🎙️ Voice note transcript"):
            st.write(st.session_state.voice_transcript)

    if st.session_state.vision_result:
        with st.expander("🔬 AI photo analysis"):
            v = st.session_state.vision_result
            cols = st.columns(2)
            with cols[0]:
                st.write(f"**Product type:** {v.get('product_type', 'not detected')}")
                st.write(f"**Craft:** {v.get('craft_type', 'not detected')}")
                st.write(f"**Colors:** {', '.join(v.get('colors', []))}")
                st.write(f"**Materials:** {', '.join(v.get('materials', []))}")
            with cols[1]:
                st.write(f"**Size:** {v.get('estimated_size', 'not detected')}")
                st.write(f"**Style:** {', '.join(v.get('style_tags', []))}")
                st.write(f"**Quality signals:** {v.get('quality_signals', 'not detected')}")
            st.write(f"**Details:** {v.get('visible_details', 'not detected')}")

    st.markdown("---")
    if st.button("🔄 Generate for another product", use_container_width=True):
        st.session_state.listing_result  = None
        st.session_state.vision_result   = None
        st.session_state.voice_transcript = ""
        st.session_state.last_photo_name  = ""
        st.rerun()
