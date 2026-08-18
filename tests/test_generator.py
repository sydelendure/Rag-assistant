from app.retrieval.retriever import Retriever
from app.generation.generator import Generator
query = "How long do I have to submit an expense claim??"

retriever = Retriever(top_k=3)

results = retriever.retrieve(query)

print("\n--- RETRIEVED CONTEXT ---\n")

for result in results:
    print(f"Document: {result['document']}")
    print(f"Section: {result['section']}")
    print(f"Text: {result['text']}")
    print("-" * 60)


generator = Generator()

answer = generator.generate(
    question=query,
    retrieved_chunks=results,
)

print("\n--- GENERATED ANSWER ---\n")
print(answer)