from dotenv import load_dotenv
import os
from huggingface_hub import InferenceClient
from sentence_transformers import SentenceTransformer

# --- load environment variables ---
load_dotenv()
hf_token = os.getenv("HF_API_KEY")

# --- setup Hugging Face Inference API client ---
client = InferenceClient(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    token=hf_token
)

def generate_gpt_response(query,products,followup= None):
    context = "\n".join([
        f"{i+1}. {p['name']} ({p['category']}): {p['description']}"
        for i, p in enumerate(products)
    ])

    if followup:
        prompt = f"""
        The user originally asked : {query}

        Here are the products retrieved : {context}

        Now the user asks followup question: {followup}

        Answer the followup question.
        """
        messages = [{"role": "user", "content": prompt}]

        response = client.chat_completion(messages)
    
        return response.choices[0].message.content
    
    else:         
        prompt = f"""
        The user asked: {query}

        Here are some of the relevant products:
        {context}

        Write a helpful response to the user's query based on the products listed above.
        """

        messages = [{"role": "user", "content": prompt}]

        response = client.chat_completion(messages)
    
        return response.choices[0].message.content

