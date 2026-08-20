# Imports & Pinecone SDK #
import os
import hashlib
from typing import List, Dict, Any
from pinecone import Pinecone, ServerlessSpec


# Pinecone Cloud Vector Store Integration #
class PineconeVectorStore:
    """
    Pinecone cloud vector database integration for employee policy RAG.
    Compatible with the same API contract as ChromaVectorStore.
    """

    # Initialization & Index Connection #
    def __init__(
        self,
        api_key: str = None,
        index_name: str = None,
        dimension: int = 384,
        metric: str = "cosine",
    ):
        self.api_key = api_key or os.getenv("PINECONE_API_KEY", "")
        self.index_name = index_name or os.getenv(
            "PINECONE_INDEX_NAME", "employee-policy-rag"
        )
        self.dimension = dimension
        self.metric = metric

        if not self.api_key:
            raise ValueError(
                "PINECONE_API_KEY environment variable is not set. "
                "Please add PINECONE_API_KEY to your environment or .env file."
            )

        self.pc = Pinecone(api_key=self.api_key)

        # Check Index Existence or Create AWS Serverless Index #
        existing_indexes = [idx.name for idx in self.pc.list_indexes()]
        if self.index_name not in existing_indexes:
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric=self.metric,
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )

        self.index = self.pc.Index(self.index_name)

    # Vector Count Checker #
    def count(self) -> int:
        """Return the number of vectors stored in the index."""
        try:
            stats = self.index.describe_index_stats()
            return stats.total_vector_count or 0
        except Exception:
            return 0

    # Batch Add Chunks & Embeddings (Deduplication via SHA-256) #
    def add_documents(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]],
    ):
        """
        Upsert chunk vectors and metadata into Pinecone.
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings.")

        vectors = []
        for chunk, embedding in zip(chunks, embeddings):
            document_name = chunk.get("document", "Unknown")
            section = chunk.get("section", "General")
            topic = chunk.get("topic", document_name)
            page = chunk.get("page", 1)
            text = chunk.get("text", "")

            unique_string = f"{document_name}_{topic}_{section}_{page}_{text}"
            chunk_id = hashlib.sha256(unique_string.encode("utf-8")).hexdigest()

            vectors.append(
                {
                    "id": chunk_id,
                    "values": embedding,
                    "metadata": {
                        "document": document_name,
                        "section": section,
                        "topic": topic,
                        "page": int(page),
                        "text": text,
                    },
                }
            )

        # Pinecone Upsert in Batches of 100 #
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i : i + batch_size]
            self.index.upsert(vectors=batch)

    # Top-K Nearest Neighbors Cosine Search #
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        distance_threshold: float = 1.1,
        where: Dict[str, Any] = None,
    ) -> Dict[str, List[Any]]:
        """
        Query Pinecone for top-k similar vectors.
        """
        if not query_embedding:
            raise ValueError("Query embedding cannot be empty.")

        query_args = {
            "vector": query_embedding,
            "top_k": top_k,
            "include_metadata": True,
        }

        if where:
            query_args["filter"] = where

        results = self.index.query(**query_args)

        filtered_documents = []
        filtered_metadatas = []
        filtered_distances = []

        for match in results.matches:
            # Convert Similarity (1.0 = identical) to Distance (0.0 = identical) #
            similarity = match.score
            distance = 1.0 - similarity if similarity is not None else 0.0

            if distance <= distance_threshold:
                metadata = match.metadata or {}
                text = metadata.get("text", "")
                filtered_documents.append(text)
                filtered_metadatas.append(metadata)
                filtered_distances.append(distance)

        return {
            "documents": [filtered_documents],
            "metadatas": [filtered_metadatas],
            "distances": [filtered_distances],
        }

    # Delete Document by Name Filter #
    def delete_document(self, document_name: str):
        """Delete all vectors belonging to a specific document."""
        self.index.delete(filter={"document": {"$eq": document_name}})

    delete_by_document = delete_document

    # Purge All Vectors in Index #
    def delete_all(self):
        """Delete all vectors in the index."""
        self.index.delete(delete_all=True)
