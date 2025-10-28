# from gtts import gTTS
# import tempfile
# import streamlit as st

# def generate_tts(text):
#     tts = gTTS(text,lang = "en")
#     with tempfile.NamedTemporaryFile(delete = False, suffix=".mp3") as f:
#         tts.save(f.name)
#         return f.name

# def render_voice(transcript):
#     audio_file = generate_tts(transcript)
#     st.audio(audio_file, format = "audio/mp3")
import tempfile
import streamlit as st
import asyncio
import edge_tts
from langdetect import detect

# Map detected languages to Edge TTS voices
VOICE_MAP = {
    "en": "en-US-JennyNeural",      # English
    "de": "de-DE-KatjaNeural",      # German
    "fr": "fr-FR-DeniseNeural",     # French
    "es": "es-ES-ElviraNeural",     # Spanish
    "it": "it-IT-ElsaNeural",       # Italian
    "hi": "hi-IN-SwaraNeural",      # Hindi
    "ja": "ja-JP-NanamiNeural",     # Japanese
    "ko": "ko-KR-SunHiNeural",      # Korean
    "zh-cn": "zh-CN-XiaoxiaoNeural",# Simplified Chinese
    "ne": "ne-NP-HemkalaNeural",      # Nepali 
}

async def generate_edge_tts(text):
    # Detect language
    try:
        lang = detect(text)
    except Exception:
        lang = "en"

    voice = VOICE_MAP.get(lang, "en-US-JennyNeural")

    # Create temporary MP3 file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        output_path = tmp.name

    # Generate TTS
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)
    return output_path

def render_voice(text):
  
    try:
        audio_file = asyncio.run(generate_edge_tts(text))
        st.audio(audio_file, format="audio/mp3")
    except Exception as e:
        st.warning(f"⚠️ Voice generation failed: {e}")
