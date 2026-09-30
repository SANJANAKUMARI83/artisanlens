# 🪔 ArtisanLens

**AI listing generator for Indian handmade artisans.** Upload a product photo, add an optional voice note, and get a ready-to-post listing in seconds: title, description, INR price range, Instagram caption, and WhatsApp message.

Built for the **AI for Handmade Challenge** (Hand for Handmade Foundation), Track 2: AI Solution Provider.

🔗 **Live demo:** [artisanlens-9mvjbfjbdedcjfnxxnujh8.streamlit.app](https://artisanlens-9mvjbfjbdedcjfnxxnujh8.streamlit.app/)

---

## The problem

Most Indian artisans sell beautiful, genuinely handmade products, but writing a good listing (a title that sells, a description that tells the craft's story, a fair price, a caption for Instagram, a message for WhatsApp) takes time and a skill most artisans were never trained in. That gap costs them sales every single day. ArtisanLens closes it: point a phone camera at the product, say a few words about it if you like, and get a complete listing back in under a minute.

## How it works

1. **Upload a product photo.** The AI looks at it and identifies the craft technique, materials, colors, and quality signals.
2. **Tell it more (optional).** Type a product name, record a voice note in Hindi or English, or type extra details like how long it took to make or what inspired the design. This context gets woven directly into the output, not just the photo.
3. **Generate.** In one click, get:
   - A product title and short tagline
   - A 150 to 200 word description with craft and regional context
   - A fair INR price range with a short rationale
   - A ready-to-post Instagram caption with hashtags
   - A friendly WhatsApp message for customers
   - Search keywords and a target buyer profile

Every output is editable and copy-paste ready, styled to read like a person wrote it, not a chatbot.

## Why this matters for artisans

- **No English required to start.** Voice notes work in Hindi or Hinglish.
- **No cost to the artisan.** Runs entirely on Google Gemini's free tier, no OpenAI key, no credit card.
- **No design or marketing skill needed.** One photo and one click gets a complete, multi-platform listing.
- **Built around how artisans actually sell** in India today: Instagram and WhatsApp, not just a storefront.

## Tech stack

- **Frontend:** [Streamlit](https://streamlit.io/), a single-page Python app, no separate backend needed
- **AI:** [Google Gemini](https://ai.google.dev/) (free tier via Google AI Studio), handles vision, audio transcription, and text generation natively in one API, no separate Whisper or OCR step
- **Hosting:** Streamlit Community Cloud (free)
- **Image handling:** Pillow, compressed client-side before upload to stay within API limits

The app calls the Gemini REST API directly (no SDK dependency) and automatically discovers and falls back across available Gemini models, so it keeps working even as Google renames or rate-limits specific model versions.

## Running it locally

```bash
git clone https://github.com/SANJANAKUMARI83/artisanlens.git
cd artisanlens
pip install -r requirements.txt
```

Get a free Gemini API key at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) (no credit card required), then either:

- paste it into the sidebar field when the app is running, or
- copy `.env.example` to `.env` and fill in `GOOGLE_API_KEY`

Then run:

```bash
streamlit run app.py
```

## Project structure

```
app.py               # Streamlit UI and app flow
llm.py                # Gemini API wrapper (vision, audio transcription, text generation)
prompt_artisan.py     # Prompts tuned for Indian handmade crafts and marketplaces
requirements.txt      # Python dependencies
.streamlit/config.toml # App theme
```

## Submission

Built by [Sanjana Kumari](https://www.linkedin.com/in/sanjana-kumari-69850a230) for the AI for Handmade Challenge, Track 2 (AI Solution Provider).
