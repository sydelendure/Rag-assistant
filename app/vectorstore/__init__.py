# Imports & Configuration #
import os
from dotenv import load_dotenv

load_dotenv()

from app.vectorstore.chroma import ChromaVectorStore


# Vector Database Factory (Pinecone Cloud / ChromaDB Local) #
def get_vector_store():
    """
    Factory function to return the configured vector store:
    - PineconeVectorStore (if VECTOR_STORE_TYPE=pinecone or PINECONE_API_KEY is configured)
    - ChromaVectorStore (default local vector database)
    """
    store_type = os.getenv("VECTOR_STORE_TYPE", "").lower()
    pinecone_key = os.getenv("PINECONE_API_KEY", "")

    # Check Pinecone Configuration #
    if store_type == "pinecone" or (pinecone_key and store_type != "chroma"):
        try:
            from app.vectorstore.pinecone_store import PineconeVectorStore

            return PineconeVectorStore()
        except Exception as e:
            print(f"Warning: Failed to initialize Pinecone ({e}). Falling back to ChromaDB.")
            return ChromaVectorStore()

    # Fallback to Local ChromaDB #
    return ChromaVectorStore()
