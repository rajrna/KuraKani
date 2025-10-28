import joblib
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from config import FAISS_INDEX_PATH, PRODUCTS_META_PATH

# Load FAISS + metadata
df = joblib.load(PRODUCTS_META_PATH)
index = faiss.read_index(FAISS_INDEX_PATH)
# model = SentenceTransformer("all-MiniLM-L6-v2")
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

def search_products(query, k=3, threshold=0.35, category=None, price_range=(0, 1000), offset=0, debug=False):
    """
    Hybrid search: FAISS semantic similarity + token overlap boosting
    """
    query_lower = query.lower().strip()
    query_tokens = set(query_lower.split())

    # Encode and normalize query
    query_embedding = model.encode([query], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(query_embedding)

    # Search FAISS
    pool_size = k * 20
    distances, indices = index.search(query_embedding, pool_size)

    results, count = [], 0

    for idx, dist in zip(indices[0][offset:], distances[0][offset:]):
        product = df.iloc[idx]

        # Filter category and price
        if category and category != "All" and product["category"].lower() != category.lower():
            continue
        if not (price_range[0] <= product["price"] <= price_range[1]):
            continue

        # Token overlap boost
        product_tokens = set(product["name"].lower().split())
        overlap = query_tokens & product_tokens
        token_boost = len(overlap) / len(query_tokens)  # fraction of words matching
        final_score = dist + 0.3 * token_boost  # 0.3 = boost factor, tune if needed

        if final_score < threshold:
            continue

        results.append((product, final_score))
        count += 1
        if count >= k:
            break

    # Debug print
    if debug:
        print("\n=== DEBUG SEARCH SCORES ===")
        for prod, score in results:
            print(f"{prod['name']} - score: {score:.4f}")

    # Return only products
    return [p for p, _ in results]



def print_search_results():
    results = search_products(
        "Anne Pro 2",
        k=3,
        category="All",
        price_range=(0, 1000),
        debug=True  # <-- prints scores
    )
    print("\n=== FINAL RESULTS ===")
    for i, product in enumerate(results):
        print(f"{i+1}. {product['name']} ({product['category']}): ${product['price']}\n   {product['description']}\n")
   
def main():
    print_search_results()

if __name__ == "__main__":
    main()    