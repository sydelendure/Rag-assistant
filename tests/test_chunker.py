from app.ingestion.loader import load_pdf
from app.ingestion.chunker import chunk_text


pdf_path = "documents/Leave_Policy.pdf"

text = load_pdf(pdf_path)

chunks = chunk_text(
    text,
    document_name="Leave_Policy.pdf"
)

print(f"\nTotal chunks: {len(chunks)}\n")

for index, chunk in enumerate(chunks, start=1):
    print("=" * 60)
    print(f"CHUNK {index}")
    print(f"Document: {chunk['document']}")
    print(f"Section: {chunk['section']}")
    print(f"Text: {chunk['text']}")
    print()