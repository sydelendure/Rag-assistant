# Imports & Module Dependencies #
from app.ingestion.embedder import Embedder
from app.vectorstore import get_vector_store


# Semantic Dense Vector Retriever #
class Retriever:
    """
    Retrieves the most relevant policy chunks
    for a user's question.
    """

    # Initialization (Default Top-K = 5, Distance Threshold = 1.1) #
    def __init__(self, top_k: int = 5, distance_threshold: float = 1.1):
        self.top_k = top_k
        self.distance_threshold = distance_threshold
        self.embedder = Embedder()
        self.vector_store = get_vector_store()

    # Query Retrieval & Optional Scoped Search #
    def retrieve(
        self,
        query: str,
        top_k: int = None,
        distance_threshold: float = None,
        document_filter: str = None,
        document: str = None,
    ):
        """
        Retrieve relevant policy chunks for a user query.
        Optionally filter search strictly to a specific document.
        """
        doc_scope = document_filter or document

        # Validate Query #
        if not query.strip():
            raise ValueError("Query cannot be empty.")

        threshold = (
            distance_threshold
            if distance_threshold is not None
            else self.distance_threshold
        )
        k = top_k if top_k is not None else self.top_k

        # Step 1: Convert User Query into Dense Vector (1 x 384) #
        query_embedding = self.embedder.generate_embedding(
            query
        )

        # Step 2: Build Scoped Filter Metadata Clause #
        where_clause = {"document": doc_scope} if doc_scope else None

        # Step 3: Query Pinecone / ChromaDB Vector Store #
        results = self.vector_store.search(
            query_embedding,
            top_k=k,
            distance_threshold=threshold,
            where=where_clause,
        )

        retrieved_chunks = []

        # Step 4: Parse Results & Metadata #
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        # Step 5: Format Structured Chunks with Citations #
        for document_text, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):
            meta = metadata if isinstance(metadata, dict) else {}
            retrieved_chunks.append(
                {
                    "text": document_text,
                    "document": meta.get("document", "Unknown"),
                    "topic": meta.get("topic", "General"),
                    "section": meta.get("section", "General"),
                    "page": meta.get("page", 1),
                    "distance": distance,
                }
            )

        return retrieved_chunks