import joblib
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from config import FAISS_INDEX_PATH, PRODUCTS_META_PATH

# Load FAISS + metadata
df = joblib.load(PRODUCTS_META_PATH)
index = faiss.read_index(FAISS_INDEX_PATH)
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

#  Search products
def search_products(query, k=3, threshold=0.35, category=None, price_range=(0, 1000), offset=0):
    # Encode query
    query_embedding = model.encode([query], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(query_embedding)

    # Search FAISS
    pool_size = k * 20
    distances, indices = index.search(query_embedding, pool_size)

    results, count = [], 0
    for idx, dist in zip(indices[0][offset:], distances[0][offset:]):
        if dist < threshold:
            continue
        product = df.iloc[idx]
        if category and category != "All" and product["category"].lower() != category.lower():
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
    new_emb = model.encode([new_query], convert_to_numpy=True).astype("float32")
    last_emb = model.encode([last_query], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(new_emb)
    faiss.normalize_L2(last_emb)
    sim = cosine_similarity(new_emb, last_emb)[0][0]
    return sim >= FOLLOWUP_THRESHOLD
