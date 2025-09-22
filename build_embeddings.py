import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import joblib

df = pd.read_csv("products.csv")
model = SentenceTransformer("all-MiniLM-L6-v2")

embeddings = model.encode(df["description"].tolist(), convert_to_numpy=True).astype("float32")

# save embeddings
np.save("embeddings.npy", embeddings)

# save metadata without embeddings
df.drop(columns=["description_embeddings"], errors="ignore", inplace=True)
joblib.dump(df, "products_meta.pkl")
