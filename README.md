# Employee Policy & Knowledge Assistant

A standalone Retrieval-Augmented Generation (RAG) application that allows employees to ask questions about company policies and receive answers based on the organization's internal policy documents.

## 1. Use Case

The application acts as an intelligent Employee Policy & Knowledge Assistant for any organization or enterprise.

It provides employees with a simple way to query internal policies such as:

- Leave Policy
- Work From Home Policy
- Travel Policy
- Expense Reimbursement Policy
- Attendance Policy
- Employee Benefits
- Code of Conduct

Instead of manually searching through multiple documents, employees can ask questions in natural language and receive answers based on the relevant policy information.

---

## 2. RAG Architecture

The application follows the standard RAG pipeline:

```text
                    Policy PDFs
                        |
                        v
                 PDF Text Extraction
                        |
                        v
                     Chunking
                        |
                        v
                    Embeddings
                        |
                        v
                    ChromaDB
                        |
                        |
                  User Question
                        |
                        v
                  Query Embedding
                        |
                        v
                  Similarity Search
                        |
                        v
                Relevant Policy Chunks
                        |
                        v
                    Qwen3:8b
                     Ollama
                        |
                        v
                  Generated Answer
                        |
                        v
                    FastAPI
                        |
                        v
                    REST API

---

## 3. Running the Application

### Start the FastAPI Backend
```bash
PYTHONPATH=. .venv/bin/uvicorn app.api.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Start the Streamlit UI
In a separate terminal:
```bash
.venv/bin/streamlit run ui.py
```
Web Interface: [http://localhost:8501](http://localhost:8501)