import json
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os

# --- load environment variables ---
load_dotenv()
hf_token = os.getenv("HF_API_KEY")

# --- setup Hugging Face Inference API client ---
client = InferenceClient(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    token=hf_token
)

def rule_classify_intent(query):
    query = query.lower().strip()
    if any(word in query for word in ["hi", "hello", "hey"]):
        return "greeting", None
    if "more" in query and "results" in query:
        return "more_results", None
    return None, None

def llm_classify_intent(query):
    prompt = f"""
    You are an intent detection and query rewriting engine for an e-commerce assistant.
    Always respond in JSON with fields:
    - intent: one of [product_search, chitchat]
    - search_query: if intent is product_search, rewrite the query into a concise,
      keyword-friendly form for FAISS/product search. Otherwise, set to null.
    """

    user_prompt = f"User query: {query}"

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_prompt}
    ]
    response = client.chat_completion(messages,
        model="client",
        temperature=0
    )

    try:
        parsed = json.loads(response.choices[0].message["content"])
        intent = parsed.get("intent", "chitchat")
        search_query = parsed.get("search_query", None)
        return intent, search_query
    except Exception:
        return "chitchat", None

def classify_intent(query):
    intent, search_query = rule_classify_intent(query)
    if intent:
        return intent, search_query
    return llm_classify_intent(query)