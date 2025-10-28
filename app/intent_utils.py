from render_utils import render_chat_message, render_products
from faiss_utils import search_products
from voice_utils import render_voice
from gpt_utils import generate_gpt_response
import streamlit as st


def handle_greeting(query, state):
    reply = "Hello, how can I help you today?"
    state.history.append({"role": "assistant", "content": reply})
    return reply


def handle_more_results(query, state, k, option, price_range):
    new_products = search_products(
        state.last_query,
        k=k,
        category=option,
        price_range=price_range,
        offset=state.offset
    )
    if new_products:
        state.last_products.extend(new_products)
        state.offset += len(new_products)
        render_products(new_products)

        with st.spinner("Thinking..."):
            answer = generate_gpt_response(state.last_query, new_products, followup=query)
        state.history.append({"role": "assistant", "content": answer})
        return answer
    else:
        reply = "No more similar products."
        state.history.append({"role": "assistant", "content": reply})
        return reply


def handle_product_search(query, state, k, option, price_range):

    state.last_query = query
    state.offset = 0

    products = search_products(query, k=k, category=option, price_range=price_range) or []

    if not products:
        reply = f"No good matches found for: {query}"
        state.history.append({"role": "assistant", "content": reply})
        return reply
    
    # Update session state
    state.last_products = products
    state.offset = len(products)

    with st.chat_message("assistant"):
        render_products(products)

    with st.spinner("Thinking..."):
        answer = generate_gpt_response(query, products)
    state.history.append({"role": "assistant", "content": answer})
    return answer


def handle_followup(query, state):
    if not state.last_query or not state.last_products:
        reply = "Could you please tell me what products you're referring to?"
        state.history.append({"role": "assistant", "content": reply})
        return reply
    with st.spinner("Thinking..."):
        answer = generate_gpt_response(state.last_query, state.last_products, followup=query)
  
    state.history.append({"role": "assistant", "content": answer})
    return answer


def handle_chitchat(query, state):
    answer = "Sorry, I can only help with product-related questions. Please ask me about products."

    state.history.append({"role": "assistant", "content": answer})
    return answer

INTENT_HANDLERS = {
    "greeting": handle_greeting,
    "more_results": handle_more_results,
    "product_search": handle_product_search,
    "followup": handle_followup,
    "chitchat": handle_chitchat,
}