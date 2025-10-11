import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

import requests

def generate_gpt_response(query, products, followup=None):
    products = products or []
    # Build product context
    context = "\n".join([
        f"{i+1}. {p['name']} ({p['category']}): {p['description']}"
        for i, p in enumerate(products)
    ])

    # Build prompt dynamically
    if followup:
        prompt = f"""
        The user originally queried: {query}
        Here are the products retrieved: {context}
        Now the user asks follow-up question: {followup}
        Answer the follow-up clearly and concisely.
        Write a concise, polite response in 1-2 sentences.
        Do not include any reasoning or thought process, only the final answer.
        """
    else:
        prompt = f"""
        The user asked: {query}
        Here are the relevant products that are available: {context}
        If no products are listed, politely inform the user that no matches were found.
        Write a clear, helpful, language-matching response based on these products.
        Output only your final answer and do not include the thought process in the final answer.
        Reply with the same language as the user.
        """

    # Send the request to the local Ollama API
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "qwen3:4b",   # Your local model name in Ollama
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        data = response.json()
        return data.get("response", "").strip()
    else:
        return f"Error: {response.status_code} - {response.text}"