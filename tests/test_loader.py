from app.ingestion.loader import load_pdf


pdf_path = "documents/Leave_Policy.pdf"

text = load_pdf(pdf_path)

print("\n--- EXTRACTED TEXT ---\n")
print(text)