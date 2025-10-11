import streamlit as st

# Render the product cards
def render_product_card(p, i):
    with st.container(border=True):
        st.markdown(f"**{i}. {p['name']}** ({p['category']})")
        st.write(f"Price: $ {p['price']}")
        st.write(f"Description: {p['description']}")

# Render the products
def render_products(products):
    st.subheader("Search Results")
    for i, p in enumerate(products, 1):
        render_product_card(p, i)

# Render the messages
def render_chat_message(role, content):
    css_class = "user" if role == "user" else "assistant"
    st.markdown(f'<div class="chat-bubble {css_class}">{content}</div>', unsafe_allow_html=True)
