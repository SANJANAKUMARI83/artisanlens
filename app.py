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
    .main-header { font-size: 2.4rem; font-weight: 800; color: #E8622A; margin-bottom: 0; }
    .sub-header  { font-size: 1.05rem; color: #6B4C3B; margin-top: 0; margin-bottom: 1.5rem; }
    .step-label  { font-size: 1.1rem; font-weight: 700; color: #2C1810; margin-bottom: 0.3rem; }
    .output-box  { background: #FFF8F2; border-left: 4px solid #E8622A; padding: 1rem 1.2rem;
                   border-radius: 6px; margin-bottom: 1rem; white-space: pre-wrap; font-size: 0.95rem; }
    .price-badge { background: #E8622A; color: white; padding: 0.35rem 0.9rem;
                   border-radius: 20px; font-weight: 700; font-size: 1.1rem; display: inline-block; }
    .tagline     { font-style: italic; color: #6B4C3B; font-size: 1.05rem; margin: 0.2rem 0 1rem 0; }
    .copy-hint   { font-size: 0.78rem; color: #999; margin-top: -0.5rem; margin-bottom: 0.8rem; }
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
    secret_key  = st.secrets.get("GOOGLE_API_KEY", "") if hasattr(st, "secrets") else ""
    env_key     = os.getenv("GOOGLE_API_KEY", "")
    default_key = secret_key or env_key

    api_key = st.text_input(
        "Google Gemini API Key",
        value=default_key,
        type="password",
        help="Free key from aistudio.google.com. No credit card needed.",
    )
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
    st.caption("Built for the AI for Handmade Challenge 🏆\nPowered by Gemini 1.5 Flash")


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown('<p class="main-header">🪔 ArtisanLens</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Upload a photo of your handmade product and get a ready-to-post listing: '
    'title, description, price, Instagram caption, and WhatsApp message.</p>',
    unsafe_allow_html=True,
)


# ── Step 1: Photo ──────────────────────────────────────────────────────────────
st.markdown('<p class="step-label">📷 Step 1: Upload your product photo</p>', unsafe_allow_html=True)

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
st.markdown('<p class="step-label">🎙️ Step 2: Tell us more *(optional but helpful)*</p>', unsafe_allow_html=True)

col_a, col_b = st.columns([1, 1])
with col_a:
    product_name = st.text_input(
        "Product name",
        placeholder="e.g. Handwoven Ikat Stole",
    )
with col_b:
    voice_file = st.file_uploader(
        "Voice note (Hindi or English, any format)",
        type=["mp3", "wav", "m4a", "ogg", "webm"],
        key="voice_uploader",
    )

extra_info = st.text_area(
    "Any other details about your product",
    placeholder=(
        "e.g. Made with natural indigo dye, takes 3 days to hand-weave, "
        "inspired by traditional Pochampally patterns, suitable for weddings and festivals"
    ),
    height=90,
)

st.markdown("---")

# ── Step 3: Generate ───────────────────────────────────────────────────────────
st.markdown('<p class="step-label">✨ Step 3: Generate your listing</p>', unsafe_allow_html=True)

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

    st.markdown(f"### {title}")
    if tagline:
        st.markdown(f'<p class="tagline">"{tagline}"</p>', unsafe_allow_html=True)
    if price:
        st.markdown(f'<span class="price-badge">{price}</span>', unsafe_allow_html=True)
        if rationale:
            st.caption(rationale)

    st.markdown("---")

    # ── Description ──
    st.markdown("**📝 Product Description**")
    st.markdown('<p class="copy-hint">Copy and paste to your marketplace listing, website, or bio</p>', unsafe_allow_html=True)
    st.text_area(
        "description",
        value=listing.get("description", ""),
        height=200,
        label_visibility="collapsed",
        key="out_desc",
    )

    # ── Instagram ──
    st.markdown("**📸 Instagram Caption**")
    st.markdown('<p class="copy-hint">Ready to post, includes hashtags</p>', unsafe_allow_html=True)
    st.text_area(
        "instagram",
        value=listing.get("instagram_caption", ""),
        height=180,
        label_visibility="collapsed",
        key="out_insta",
    )

    # ── WhatsApp ──
    st.markdown("**💬 WhatsApp Message**")
    st.markdown('<p class="copy-hint">Paste into WhatsApp Business catalogue or send directly to customers</p>', unsafe_allow_html=True)
    st.text_area(
        "whatsapp",
        value=listing.get("whatsapp_message", ""),
        height=130,
        label_visibility="collapsed",
        key="out_wa",
    )

    # ── Keywords + target buyers ──
    col_k, col_t = st.columns(2)
    with col_k:
        keywords = listing.get("keywords", [])
        if keywords:
            st.markdown("**🔍 Search Keywords**")
            st.write("  ·  ".join(keywords))

    with col_t:
        buyers = listing.get("target_buyers", [])
        if buyers:
            st.markdown("**👥 Target Buyers**")
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
