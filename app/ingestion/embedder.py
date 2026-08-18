from sentence_transformers import SentenceTransformer
from typing import List


class Embedder:
    """
    Generates vector embeddings for text using
    a Sentence Transformers model.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding for a single piece of text.
        """

        if not text.strip():
            raise ValueError("Cannot generate an embedding for empty text.")

        embedding = self.model.encode(text)

        return embedding.tolist()

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple pieces of text.
        """

        if not texts:
            raise ValueError("No texts provided for embedding generation.")

        embeddings = self.model.encode(texts)

        return embeddings.tolist()