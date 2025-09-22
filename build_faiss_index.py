import numpy as np
import faiss

embeddings = np.load("embeddings.npy")
faiss.normalize_L2(embeddings)

d = embeddings.shape[1]
index = faiss.IndexFlatIP(d)
index.add(embeddings)

faiss.write_index(index, "faiss_index.bin")
