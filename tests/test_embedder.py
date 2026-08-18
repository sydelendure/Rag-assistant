from app.ingestion.loader import load_pdf
from app.ingestion.chunker import chunk_text
from app.ingestion.embedder import Embedder


pdf_path = "documents/Leave_Policy.pdf"

# 1. Load the PDF
text = load_pdf(pdf_path)

# 2. Create chunks
chunks = chunk_text(
    text,
    document_name="Leave_Policy.pdf"
)

# 3. Extract chunk text
texts = [chunk["text"] for chunk in chunks]

# 4. Create embedding model
embedder = Embedder()

# 5. Generate embeddings
embeddings = embedder.generate_embeddings(texts)

print(f"\nNumber of chunks: {len(chunks)}")
print(f"Number of embeddings: {len(embeddings)}")
print(f"Embedding dimensions: {len(embeddings[0])}")

print("\nFirst embedding:")
print(embeddings[0])