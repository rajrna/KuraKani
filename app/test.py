from faiss_utils import search_products

option = "Keyboard"
products = search_products("keyboards", k=3, threshold=0.45, category=option, price_range=(0,1000), offset=0)
print(products)