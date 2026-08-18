from app.ingestion.loader import load_pdf
from app.ingestion.chunker import chunk_text
from app.ingestion.embedder import Embedder
from app.vectorstore.chroma import ChromaVectorStore


# --------------------------------------------------
# 1. Load the policy document
# --------------------------------------------------

pdf_path = "documents/Leave_Policy.pdf"

text = load_pdf(pdf_path)


# --------------------------------------------------
# 2. Create chunks
# --------------------------------------------------

chunks = chunk_text(
    text,
    document_name="Leave_Policy.pdf",
)

texts = [
    f"{chunk['section']}\n{chunk['text']}"
    for chunk in chunks
]
# --------------------------------------------------
# 3. Generate embeddings
# --------------------------------------------------



embedder = Embedder()

embeddings = embedder.generate_embeddings(texts)


# --------------------------------------------------
# 4. Create ChromaDB vector store
# --------------------------------------------------

vector_store = ChromaVectorStore()


# --------------------------------------------------
# 5. Store chunks + embeddings + metadata
# --------------------------------------------------

vector_store.add_documents(
    chunks,
    embeddings,
)


print(f"\nStored {len(chunks)} chunks in ChromaDB.")


# --------------------------------------------------
# 6. Test semantic search
# --------------------------------------------------

query = "How many annual leave days do employees get?"

query_embedding = embedder.generate_embedding(query)

results = vector_store.search(
    query_embedding,
    top_k=3,
)


# --------------------------------------------------
# 7. Display results
# --------------------------------------------------

print("\n--- SEARCH RESULTS ---\n")

for index, document in enumerate(
    results["documents"][0],
    start=1,
):
    metadata = results["metadatas"][0][index - 1]

    print(f"RESULT {index}")
    print(f"Document: {metadata['document']}")
    print(f"Section: {metadata['section']}")
    print(f"Text: {document}")
    print("-" * 60)