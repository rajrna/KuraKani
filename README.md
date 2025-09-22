## Xten-Kurakani

AI driven chatbot.

## About

KuraKani AI is an AI and rule based hybrid chatbot prototype. It is built with Streamlit and Python. It allows users to search for products using natural language queries to find relevant items from product catalog.

## Features

- Natural language product search
- FAISS vector similarity search
- Category and price range filters
- Follow-up handling

## Installation

1. Create virutal environment(Optional):

```bash
python -m venv venv
venv\Scripts\activate
```

2. Install all required packages

```bash
pip install requirements.txt
```

3. Prepare product dataset and FAISS index

- Prepare a csv file "products.csv" with following headers:
  id,name,category,price,description

- Run following scripts in sequence:

```bash
python create_embeddings.py script
python build_embeddings.pty
python build_faiss_index.py
```

# Usage

1. Run the Streamlit app:

```bash
streamlit run app.py
```

2. Use the sidebar to set:

- Number of results (k)

- Price range

- Category

3. Type query in the chat input.

# How it Works

1. Query Embeddings

- User queries are converted to embeddings using Sentence-BERT.

- FAISS performs vector similarity search to find matching products.

2. Filtering & Offset

- Results are filtered by category and price range.

3. GPT Integration

- Generates contextual responses based on products and follow-up queries.

4. Session State

- Streamlit st.session_state stores chat history, last query, last products, and offset.
