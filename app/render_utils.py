import streamlit as st

# --- render the product cards ---
def render_product_card(p, i):
    with st.container(border=True):
        st.markdown(f"**{i}. {p['name']}** ({p['category']})")
        st.write(f"Price: ${p['price']}")
        st.write(f"Description: {p['description']}")

# --- render the products ---
def render_products(products):
    st.subheader("Search Results")
    for i, p in enumerate(products, start = 1):
        render_product_card(p,i)

# --- render the messages ---
def render_chat_message(role,content):
    # with st.chat_message(role):
    #     st.write(content) 
    if role == "user":
        st.markdown(f'<div class="chat-bubble user">{content}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble assistant">{content}</div>', unsafe_allow_html=True)
