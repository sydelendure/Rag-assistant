from app.retrieval.retriever import Retriever


retriever = Retriever(top_k=3)

query = "How many annual leave days do employees get?"

print(f"\nQUERY: {query}")

results = retriever.retrieve(query)

print("\n--- RETRIEVAL RESULTS ---\n")

if not results:
    print("No results passed the similarity threshold.")

for index, result in enumerate(results, start=1):
    print(f"RESULT {index}")
    print(f"Document: {result['document']}")
    print(f"Section: {result['section']}")
    print(f"Text: {result['text']}")
    print(f"Distance: {result['distance']}")
    print("-" * 60)