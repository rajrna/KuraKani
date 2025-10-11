from dotenv import load_dotenv
import os

load_dotenv()

HF_TOKEN = os.getenv("HF_API_KEY")
FAISS_INDEX_PATH = "data/faiss_index.bin"
PRODUCTS_META_PATH = "data/products_meta.pkl"