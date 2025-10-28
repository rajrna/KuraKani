import json
import requests

# def rule_classify_intent(query):
#     query = query.lower().strip()
#     if any(word in query for word in ["hi", "hello", "hey"]):
#         return "greeting", None
#     if "more" in query and "results" in query:
#         return "more_results", None
#     return None, None

def llm_classify_intent(query, context=None):
    
    system_prompt = """
    You are an intent detection and query rewriting engine for an e-commerce assistant.
    Always respond in valid JSON with these fields:
    {
      "intent": one of ["product_search","greeting", "chitchat", "followup", "more_results", "refine_search"],
      "search_query": string or null
    }
    Guidelines:
    - If the user says hello or greets → intent = "greeting"
    - If the user asks to see additional products (e.g. "show me more", "next page") → intent = "more_results"
    - If the user wants to narrow or adjust the search ("show only gaming ones", "under $50") → intent = "refine_search"
    - If the user continues a previous topic without introducing a new search → intent = "followup"
    - If the user asks for additional details about a previously shown product → intent = "followup"
    - If the user asks for more specific product among previously shown ones → intent = "followup"
    - If it's small talk or unrelated → "chitchat"
    - If it's a new product query → "product_search"
    - If the query is about finding, comparing, or describing products → intent = "product_search"
    - For "product_search", rewrite the query into concise keywords suitable for a search engine in the same language as original query.
    """

    if context:
        full_prompt = f"{system_prompt}\n\nPrevious user query: {context}\nCurrent user query:{query}"
    else:
        full_prompt = f"{system_prompt}\n\nUser query: {query}"    

    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "qwen3:4b",  
        "prompt": full_prompt,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"[Error] Ollama returned {response.status_code}: {response.text}")
            return "chitchat", None

        data = response.json()
        text = data.get("response", "").strip()

        # Extract JSON safely even if model outputs extra text
        json_start = text.find("{")
        json_end = text.rfind("}") + 1
        if json_start == -1 or json_end == 0:
            return "chitchat", None

        json_part = text[json_start:json_end]
        parsed = json.loads(json_part)

        intent = parsed.get("intent", "chitchat")
        search_query = parsed.get("search_query", None)
        return intent, search_query

    except Exception as e:
        print(f"[Exception in llm_classify_intent] {e}")
        return "chitchat", None


# def classify_intent(query, context=None):
#     intent, search_query = llm_classify_intent(query, context= context)
#     if intent:
#         return intent, search_query
#     return llm_classify_intent(query)
def classify_intent(query, context=None):
    intent, search_query = llm_classify_intent(query, context=context)
    if not intent:
        intent, search_query = llm_classify_intent(query, context=context)

    return intent, search_query
