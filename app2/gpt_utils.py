import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load environment variables
load_dotenv()
hf_token = os.getenv("HF_API_KEY")

# Setup Hugging Face Inference API client
client = InferenceClient(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    token=hf_token
)

def generate_gpt_response(query, products, followup=None):
    context = "\n".join([
        f"{i+1}. {p['name']} ({p['category']}): {p['description']}"
        for i, p in enumerate(products)
    ])

    if followup:
        prompt = f"""
        The user originally queried: {query}
        Here are the products retrieved: {context}
        Now the user asks follow-up question: {followup}
        Answer the follow-up clearly.
        """
    else:
        prompt = f"""
        The user asked: {query}
        Here are the relevant products that are available: {context}
        Write a clear, helpful response based on these products.
        """

    messages = [{"role": "user", "content": prompt}]
    response = client.chat_completion(messages)
    return response.choices[0].message.content
