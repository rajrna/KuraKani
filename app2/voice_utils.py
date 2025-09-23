from gtts import gTTS
import tempfile
import streamlit as st

def generate_tts(text):
    tts = gTTS(text,lang = "en")
    with tempfile.NamedTemporaryFile(delete = False, suffix=".mp3") as f:
        tts.save(f.name)
        return f.name

def render_voice(transcript):
    audio_file = generate_tts(transcript)
    st.audio(audio_file, format = "audio/mp3")