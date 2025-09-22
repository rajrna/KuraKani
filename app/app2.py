import streamlit as st
from faiss_utils import search_products, is_followup
from gpt_utils import generate_gpt_response
from intention_utils import check_greetings, check_more_results
from render_utils import render_chat_message, render_product_card, render_products
from streamlit_mic_recorder import mic_recorder
from voice_utils import generate_tts
import tempfile
import whisper
from gtts import gTTS
import tempfile
import os


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
    </style>
    """,
    unsafe_allow_html=True,
)


def main():
    st.set_page_config(page_title="KuraKani AI", layout="wide")
    st.title("KuraKani AI")

    # --- Session State ---
    if "history" not in st.session_state:
        st.session_state.history = []
    if "last_query" not in st.session_state:
        st.session_state.last_query = None
    if "last_products" not in st.session_state:
        st.session_state.last_products = []
    if "offset" not in st.session_state:
        st.session_state.offset = 0

    whisper_model = whisper.load_model("base")

    # --- Sidebar ---
    st.sidebar.header("Search Settings")
    k = st.sidebar.slider("Number of Results", 1, 10, 3)
    price_range = st.sidebar.slider("Price range", 0, 3000, (0, 1000))
    with st.sidebar:
        option = st.selectbox("Choose Category", ("All", "Keyboard", "Mouse", "Smart Phones", "Camera"), index=0)

    # --- Display chat history ---
    for message in st.session_state.history:
        render_chat_message(message["role"], message["content"])

    
    col1, col2 = st.columns([8, 1])

    with col1:
        # --- User input ---
        query = st.chat_input("How can I help: ")

    # --------------------------------------------------------------
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
        
        if query_text:
            st.write("🎤 You said:", query_text)
            

    # -----------------------------------------------
    if not query:
        return
    query = query.strip()
    if not query:
        st.error("Please enter a valid message.")
        return

    # ---Save user query---
    st.session_state.history.append({"role": "user", "content": query})
    render_chat_message("user", query)

    try:
        # --- Show more results ---
        if check_more_results(query) and st.session_state.last_query:
            new_products = search_products(
                st.session_state.last_query,
                k=k,
                category=option,
                price_range=price_range,
                offset=st.session_state.offset
            )
            if new_products:
                st.session_state.last_products.extend(new_products)
                st.session_state.offset += len(new_products)
                bot_reply = f"Here are more products related to: {st.session_state.last_query}."
                render_products(new_products)

                with st.spinner("Thinking..."):
                    answer = generate_gpt_response(
                        st.session_state.last_query,
                        new_products,
                        followup=query
                    )
                render_chat_message("assistant", answer)
                st.session_state.history.append({"role": "assistant", "content": answer})
            else:
                bot_reply = "No more similar products."
                render_chat_message("assistant", bot_reply)
                st.session_state.history.append({"role": "assistant", "content": bot_reply})
            return

        # --- Greeting detection ---
        intent, processed_query = check_greetings(query)
        if intent == "greeting":
            bot_reply = "Hello, how can I help you today?"
            render_chat_message("assistant", bot_reply)
            audio_file = generate_tts(bot_reply)
            st.audio(audio_file, format = "audio/mp3")
            st.session_state.history.append({"role": "assistant", "content": bot_reply})
            return

        # --- Follow-up vs new search ---
        if intent == "query" and st.session_state.last_query and st.session_state.last_products:
            if is_followup(processed_query, st.session_state.last_query):
                # Related → GPT follow-up
                with st.spinner("Thinking..."):
                    answer = generate_gpt_response(
                        st.session_state.last_query,
                        st.session_state.last_products,
                        followup=query
                    )
                render_chat_message("assistant", answer)
                st.session_state.history.append({"role": "assistant", "content": answer})
                return
            else:
                # New search → reset state
                st.session_state.last_query = None
                st.session_state.last_products = []
                st.session_state.offset = 0

        # --- New product search ---
        products = search_products(processed_query, k=k, category=option, price_range=price_range)

        if not products:
            message = f"No good matches found for: {processed_query}"
            render_chat_message("assistant", message)
            st.session_state.history.append({"role": "assistant", "content": message})
        else:
            # Update state for new search
            st.session_state.last_query = processed_query
            st.session_state.last_products = products
            st.session_state.offset = len(products)

            with st.chat_message("assistant"):
                render_products(products)

            with st.spinner("Thinking..."):
                answer = generate_gpt_response(processed_query, products)
            render_chat_message("assistant", answer)

            # audio part
            audio_file = generate_tts(answer)
            st.audio(audio_file, format = "audio/mp3")
            st.session_state.history.append({"role": "assistant", "content": answer})

    except Exception as e:
        st.error(f"Some error occurred: {e}")

if __name__ == "__main__":
    main()