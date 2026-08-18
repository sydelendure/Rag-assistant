import hashlib

import chromadb


class ChromaVectorStore:
    """
    Handles storage and retrieval of document chunks
    using ChromaDB.
    """

    def __init__(
        self,
        persist_directory: str = "chroma_db",
        collection_name: str = "employee_policies",
    ):
        self.client = chromadb.PersistentClient(
            path=persist_directory
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

    # --------------------------------------------------
    # Add Documents
    # --------------------------------------------------

    def add_documents(
        self,
        chunks,
        embeddings,
    ):
        """
        Store chunks, embeddings, and metadata in ChromaDB.

        Each chunk receives a unique ID based on its
        document name, section, and text.
        """

        if not chunks:
            raise ValueError(
                "No chunks provided."
            )

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks and embeddings must match."
            )

        ids = []

        documents = []

        metadatas = []

        for chunk in chunks:
            document_name = chunk["document"]
            section = chunk.get("section", "General")
            topic = chunk.get("topic", document_name)
            page = int(chunk.get("page", 1))
            text = chunk["text"]

            # Create a stable unique ID
            unique_string = (
                f"{document_name}|"
                f"{topic}|"
                f"{section}|"
                f"page_{page}|"
                f"{text}"
            )

            chunk_id = hashlib.sha256(
                unique_string.encode("utf-8")
            ).hexdigest()

            ids.append(chunk_id)
            documents.append(text)
            metadatas.append(
                {
                    "document": document_name,
                    "section": section,
                    "topic": topic,
                    "page": page,
                }
            )

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    # --------------------------------------------------
    # Search
    # --------------------------------------------------

    def search(
        self,
        query_embedding,
        top_k: int = 5,
        distance_threshold: float = 1.1,
        where: dict = None,
    ):
        """
        Search ChromaDB for semantically similar chunks.

        Results whose distance is greater than the
        threshold are filtered out.
        """

        if not query_embedding:
            raise ValueError(
                "Query embedding cannot be empty."
            )

        query_args = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
            "include": [
                "documents",
                "metadatas",
                "distances",
            ],
        }

        if where:
            query_args["where"] = where

        results = self.collection.query(**query_args)

        filtered_documents = []
        filtered_metadatas = []
        filtered_distances = []

        documents = results["documents"][0] if results.get("documents") else []
        metadatas = results["metadatas"][0] if results.get("metadatas") else []
        distances = results["distances"][0] if results.get("distances") else []

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):

            if distance <= distance_threshold:

                filtered_documents.append(
                    document
                )

                filtered_metadatas.append(
                    metadata
                )

                filtered_distances.append(
                    distance
                )

        return {
            "documents": [
                filtered_documents
            ],
            "metadatas": [
                filtered_metadatas
            ],
            "distances": [
                filtered_distances
            ],
        }

    def count(self) -> int:
        """Return the number of vectors stored in the collection."""
        try:
            return self.collection.count()
        except Exception:
            return 0

    # --------------------------------------------------
    # Delete Documents
    # --------------------------------------------------

    def delete_document(self, document_name: str):
        """Delete all chunks belonging to a specific document."""
        self.collection.delete(where={"document": document_name})

    def delete_all(self):
        """Delete all indexed chunks in the vector collection."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )