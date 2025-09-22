import joblib
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from config import FAISS_INDEX_PATH, PRODUCTS_META_PATH
from sklearn.metrics.pairwise import cosine_similarity

# --- load data ---
df = joblib.load(PRODUCTS_META_PATH)
index = faiss.read_index(FAISS_INDEX_PATH)
model = SentenceTransformer("all-MiniLM-L6-v2")


# --- search products ---
def search_products(query, k=3, threshold=0.35, category=None, price_range=(0,1000), offset=0):
    # --- Encode query ---
    query_embedding = model.encode([query], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(query_embedding)

    # --- search in FAISS ---
    pool_size = k * 20   # fetch more to allow filtering + offset
    distances, indices = index.search(query_embedding, pool_size)

    results = []
    count = 0

    for idx, distance in zip(indices[0][offset:], distances[0][offset:]):
        if distance < threshold:
            continue

        product = df.iloc[idx]

        if category and category != "All":
            if product["category"].lower() != category.lower():
                continue

        if not (price_range[0] <= product["price"] <= price_range[1]):
            continue

        results.append(product)
        count += 1

        if count >= k:
            break

    return results


FOLLOWUP_THRESHOLD = 0.7 

def is_followup(new_query, last_query):
    if not last_query:
        return False
    # --- Get embeddings ---
    new_emb = model.encode([new_query], convert_to_numpy=True).astype("float32")
    last_emb = model.encode([last_query], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(new_emb)
    faiss.normalize_L2(last_emb)
    sim = cosine_similarity(new_emb, last_emb)[0][0]
    return sim >= FOLLOWUP_THRESHOLD