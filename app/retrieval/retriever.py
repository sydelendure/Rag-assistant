from app.ingestion.embedder import Embedder
from app.vectorstore import get_vector_store


class Retriever:
    """
    Retrieves the most relevant policy chunks
    for a user's question.
    """

    def __init__(self, top_k: int = 5, distance_threshold: float = 1.1):
        self.top_k = top_k
        self.distance_threshold = distance_threshold
        self.embedder = Embedder()
        self.vector_store = get_vector_store()

    def retrieve(
        self,
        query: str,
        distance_threshold: float = None,
        document_filter: str = None,
    ):
        """
        Retrieve relevant policy chunks for a user query.
        Optionally filter search strictly to a specific document.
        """

        if not query.strip():
            raise ValueError("Query cannot be empty.")

        threshold = (
            distance_threshold
            if distance_threshold is not None
            else self.distance_threshold
        )

        # Convert the question into an embedding
        query_embedding = self.embedder.generate_embedding(
            query
        )

        where_clause = {"document": document_filter} if document_filter else None

        # Search ChromaDB and filter weak matches
        results = self.vector_store.search(
            query_embedding,
            top_k=self.top_k,
            distance_threshold=threshold,
            where=where_clause,
        )

        retrieved_chunks = []

        documents = results.get(
            "documents",
            [[]],
        )[0]

        metadatas = results.get(
            "metadatas",
            [[]],
        )[0]

        distances = results.get(
            "distances",
            [[]],
        )[0]

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):
            meta = metadata if isinstance(metadata, dict) else {}
            retrieved_chunks.append(
                {
                    "text": document,
                    "document": meta.get("document", "Unknown"),
                    "topic": meta.get("topic", "General"),
                    "section": meta.get("section", "General"),
                    "page": meta.get("page", 1),
                    "distance": distance,
                }
            )

        return retrieved_chunks