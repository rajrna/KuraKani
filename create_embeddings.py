import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

# Read the csv file
df = pd.read_csv("new_products.csv")

# Generate embeddings for description
embeddings = model.encode(df["description"].tolist(), show_progress_bar = True)

# Convert to numpy array
embeddings = np.array(embeddings)

# Save the embeddings in df
df["description_embeddings"] = embeddings.tolist()

# Save into csv file
df.to_csv("products.csv", index=False)

