import streamlit as st
from streamlit_mic_recorder import mic_recorder
import tempfile
import whisper

from intention_utils import check_greetings, check_more_results
from intent_classifier import classify_intent
from intent_utils import INTENT_HANDLERS
from render_utils import render_chat_message, render_product_card, render_products
from voice_utils import render_voice
from gtts import gTTS


st.markdown(
    """
    <style>
    /* Chat container */
    .chat-bubble {
        padding: 12px 16px;
        border-radius: 12px;
        margin: 6px 0;
        max-width: 85%;
        line-height: 1.5;
    }

    /* User message */
    .chat-bubble.user {
        background-color: #10a37f;
        color: white;
        margin-left: auto;
    }

    /* Assistant message */
    .chat-bubble.assistant {
        background-color: #444654;
        color: white;
        margin-right: auto;
    }
    
    /*To keep input fields at bottom */
    .st-key-input_box {
        position: fixed;
        bottom: 3rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

class ChatState:
    def __init__(self):
        self.history = []
        self.last_query = None
        self.last_products = []
        self.offset = 0
        self.k = 3
        self.option = "All"
        self.price_range = (0, 1000)


def main():
    st.set_page_config(page_title="KuraKani AI", layout="wide")
    st.title("KuraKani AI")

    # Session State
    if "chat_state" not in st.session_state:
        st.session_state.chat_state = ChatState()
    state = st.session_state.chat_state

    # Whisper model
    whisper_model = whisper.load_model("base")

    # Sidebar
    st.sidebar.header("Search Settings")
    state.k = st.sidebar.slider("Number of Results", 1, 10, 3)
    price_range = st.sidebar.slider("Price range", 0, 3000, (0, 1000))
    with st.sidebar:
        state.option = st.selectbox("Choose Category", ("All", "Keyboard", "Mouse", "Smart Phones", "Camera"), index=0)

    # Display chat history
    for message in state.history:
        render_chat_message(message["role"], message["content"])

    with st.container(key= "input_box"):
        col1, col2 = st.columns([8, 1])
        with col1:
        # User input
            query = st.chat_input("How can I help: ")
        # Voice input
        with col2:
            audio = mic_recorder(
            start_prompt="🎙",
            stop_prompt="🛑",
            format="wav",
            key=None
            )

    if audio and "bytes" in audio:
        # Save WAV bytes to a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio["bytes"])
            temp_path = temp_audio.name
        # Transcribe
        result = whisper_model.transcribe(temp_path)
        query_text = result["text"]
        query = str(result.get("text", "")).strip()
        # remove later
        if query_text:
            st.write("🎤 You said:", query_text)
            
    if not query:
        return
    query = query.strip()
    if not query:
        st.error("Please enter a valid message.")
        return

    # ---Save user query---
    state.history.append({"role": "user", "content": query})
    render_chat_message("user", query)

    try:
        intent, rewritten_query = classify_intent(query)
        handler = INTENT_HANDLERS.get(intent)

        if handler:
            if intent == "product_search" or intent == "more_results":
                reply = handler(rewritten_query or query, state, state.k, state.option, state.price_range)
            else:
                reply = handler(rewritten_query or query, state)    
        else:
            reply = "Sorry, I didn't understand that."

        #show bot response
        render_chat_message("assistant", reply)
        render_voice(reply)
        state.history.append({"role": "assistant", "content": reply})
    except Exception as e:
        st.error(f"Error: {e}")

if __name__ == "__main__":
    main()