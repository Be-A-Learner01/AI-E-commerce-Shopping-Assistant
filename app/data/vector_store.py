from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from .products_loader import load_products_docs,products
import os
from langsmith import traceable



embeddings = HuggingFaceEmbeddings(model_name = "BAAI/bge-m3")


@traceable(name="saved")
def saved_to_store(products):
    os.makedirs(r"data\product_store", exist_ok=True)
    docs = load_products_docs(products)
    vector_store = Chroma(
        collection_name="products_db",
        embedding_function=embeddings,
        persist_directory=r"data\product_store"
    )
    vector_store.add_documents(
        docs,
        ids=[str(doc.metadata["id"]) for doc in docs]
    )
    return vector_store

if not os.path.exists(r"data\product_store"):
    vector_store = saved_to_store(products)
else:
    vector_store = Chroma(
        collection_name="products_db",
        embedding_function=embeddings,
        persist_directory=r"data\product_store"
    )







