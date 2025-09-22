import streamlit as st
from faiss_utils import search_products
from gpt_utils import generate_gpt_response
from intention_utils import check_greetings, check_more_results
from render_utils import render_chat_message, render_product_card, render_products
from streamlit_mic_recorder import mic_recorder

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
    st.set_page_config(page_title="KuraKani AI", layout = "wide")
    st.title("KuraKani AI")

    # Initialize session state
    if "history" not in st.session_state:
        st.session_state.history = []
    if "last_query" not in st.session_state:
        st.session_state.last_query = None
    if "last_products" not in st.session_state:
        st.session_state.last_products = []
    if "offset" not in st.session_state:
        st.session_state.offset = 0

    # sidebar 
    st.sidebar.header("Search Settings")
    k = st.sidebar.slider("Number of Results", 1, 10, 3)
    price_range = st.sidebar.slider("Price range",0, 3000, (0,1000) )
    with st.sidebar:
        option = st.selectbox("Choose Category",("All","Keyboard","Mouse","Smart Phones","Camera"),index=0)

    # if st.session_state.last_products:
    #     render_products(st.session_state.last_products)

    audio = mic_recorder(
    start_prompt="🎙",
    stop_prompt="🎙",
    just_once=False,
    use_container_width=False,
    format="webm",
    callback=None,
    args=(),
    kwargs={},
    key=None
    )

    # Display past messages
    for message in st.session_state.history:
        render_chat_message(message["role"], message["content"])

    # user query:
    query = st.chat_input("How can I help: ")
    if query:
        query = query.strip()
        if not query:
            st.error("Please enter a valid message.")
        else:
            #save the query 
            st.session_state.history.append({"role": "user", "content": query})
            render_chat_message("user", query)

            try:
                # check if user wants more results
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
                        st.session_state.history.append({"role":"assistant","content":answer}) 
                    else:
                        bot_reply = "No more similar products."
                        render_chat_message("assistant",bot_reply)
                        st.session_state.history.append({"role":"assistant","content":bot_reply})
                    return    

                # check for greetings
                intent, processed_query = check_greetings(query)
                if intent == "greeting":
                    bot_reply = "Hello, how can I help you today? "
                    render_chat_message("assistant", bot_reply)
                    st.session_state.history.append({"role": "assistant", "content": bot_reply})
                    return
                
                elif intent == "query":
                    # For followup
                    if st.session_state.last_query and st.session_state.last_products:
                        try:
                            answer = generate_gpt_response(
                                st.session_state.last_query,
                                st.session_state.last_products,
                                followup=query
                            )
                            render_chat_message("assistant",answer)
                            st.session_state.history.append({"role": "assistant", "content": answer}) 
                        except Exception as e:
                            st.error("GPT error occured")

                    #First query 
                    else:
                        products = search_products(processed_query, k=k, category= option, price_range= price_range)

                        # check if products are found
                        if not products:
                            message = f"No good matches found for: {processed_query}"
                            render_chat_message("assistant", message)
                            st.session_state.history.append({"role": "assistant", "content": message})
                        else:
                            st.session_state.last_query = processed_query
                            st.session_state.last_products = products

                            # GPT response
                            if products:
                                with st.chat_message("assistant"):
                                    # st.subheader("Search Results: ")
                                    render_products(products)

                                with st.spinner("Thinking"):
                                    # st.subheader("Answer: ")
                                    answer = generate_gpt_response(processed_query, products)
                                    render_chat_message("assistant", answer)
                         
                                st.session_state.history.append({"role": "assistant", "content": answer})                 
            except Exception as e:
                st.error(f"Some error occured:{e} ")

if __name__ == "__main__":
    main()