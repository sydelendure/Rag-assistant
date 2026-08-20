# Imports & Ingestion Submodules #
from pathlib import Path

from app.ingestion.loader import load_document_pages
from app.ingestion.chunker import chunk_document
from app.ingestion.embedder import Embedder
from app.vectorstore import get_vector_store

# Supported Formats & Directory Path #
DOCUMENTS_DIR = Path("documents")
SUPPORTED_EXTENSIONS = {
    ".pdf", ".csv", ".xlsx", ".xls", ".docx", ".doc", ".txt", ".md",
    ".png", ".jpg", ".jpeg", ".webp", ".tiff", ".bmp"
}


# Single Document End-to-End Ingestion Pipeline #
def ingest_document(file_path: Path):
    """
    Process a single document of any supported format:
    (.pdf, .csv, .xlsx, .xls, .docx, .txt, .md, images).

    Pipeline:
    Document → Multi-Page/Sheet/Row Extraction → Chunking → Embeddings → Vector DB
    """

    # Validate File Existence & Format #
    if not file_path.exists():
        raise FileNotFoundError(
            f"Document not found: {file_path}"
        )

    suffix = file_path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported format '{suffix}'. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    print(f"Processing: {file_path.name}")

    # Step 1: Load Document Pages & Structured Rows #
    pages = load_document_pages(str(file_path))
    if not pages:
        raise ValueError(
            f"No text could be extracted from {file_path.name}."
        )

    # Step 2: Create Hierarchical Chunks #
    chunks = chunk_document(
        pages,
        document_name=file_path.name,
    )
    if not chunks:
        raise ValueError(
            f"No chunks were created from {file_path.name}."
        )

    print(
        f"  Created {len(chunks)} chunks across {len(pages)} pages."
    )

    # Step 3: Prepare Enriched Text for Embeddings #
    texts = [
        f"Document: {chunk['document']}\n"
        f"Policy: {chunk.get('topic', chunk['document'])}\n"
        f"Section: {chunk.get('section', 'General')}\n"
        f"Page: {chunk.get('page', 1)}\n"
        f"Content: {chunk['text']}"
        for chunk in chunks
    ]

    # Step 4: Generate Dense Embeddings #
    print("Generating embeddings...")
    embedder = Embedder()
    embeddings = embedder.generate_embeddings(texts)

    # Step 5: Store in Vector Database (Pinecone / ChromaDB) #
    print("Storing data in vector store...")
    vector_store = get_vector_store()
    vector_store.add_documents(chunks, embeddings)

    print(
        f"Successfully indexed "
        f"{file_path.name} "
        f"({len(chunks)} chunks)."
    )

    return {
        "filename": file_path.name,
        "chunks": len(chunks),
    }


# Bulk Directory Ingestion Runner #
def ingest_documents():
    """
    Load all policy documents of all supported formats, create chunks,
    generate embeddings, and store them in the vector database.

    Used for initial/bulk ingestion.
    """
    all_files = [
        f for f in DOCUMENTS_DIR.glob("*.*")
        if f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    if not all_files:
        raise FileNotFoundError(
            f"No supported documents found in the documents directory. "
            f"Supported extensions: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    total_chunks = 0

    # Ingest Every Discovered Document #
    for doc_file in all_files:
        result = ingest_document(doc_file)
        total_chunks += result["chunks"]

    print(
        f"\nSuccessfully stored "
        f"{total_chunks} chunks in the vector database."
    )


# Command-Line Main Execution #
if __name__ == "__main__":
    ingest_documents()