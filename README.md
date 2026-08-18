# 🏢 Employee Policy & Knowledge Assistant (RAG)

A high-performance **Retrieval-Augmented Generation (RAG)** system powered by **Groq LPU Cloud Inference**, **Pinecone Cloud Vector Database**, and **Multi-Format Ingestion (PDF, CSV, Excel, Word, Text, and OCR Images)**.

Employees can ask natural language questions regarding corporate guidelines, benefits, and compliance rules, receiving instantaneous, grounded answers with exact document and page citations.

---

## 🏗️ System Architecture & Data Flow

```mermaid
flowchart TD
    subgraph INGESTION["📥 1. Ingestion Pipeline"]
        A["📄 Policy Files<br/>(PDF, CSV, XLSX, DOCX, TXT, Images)"] --> B{"Universal Loader"}
        B -->|PDFs / Text / Word| C["PyMuPDF & python-docx"]
        B -->|Tables / Spreadsheets| D["Pandas & OpenPyXL"]
        B -->|Images / Infographics| E["Vision OCR Engine"]
        
        C & D & E --> F["Smart Structural Chunker<br/>(Topic, Section & Page Tracking)"]
        F --> G["Sentence Transformer<br/>(all-MiniLM-L6-v2)"]
        G --> H[("🌲 Pinecone Cloud / ChromaDB<br/>Vector Store (384-dim)")]
    end

    subgraph QUERY["⚡ 2. Query & Generation Pipeline"]
        U["👤 Employee / User"] -->|Selects Scope & Asks Query| UI["🖥️ Streamlit Web UI<br/>(Port 8501)"]
        UI -->|HTTP POST /ask| API["🚀 FastAPI Gateway<br/>(Port 8000)"]
        
        API --> Q_EMB["Query Embedder"]
        Q_EMB --> V_SEARCH["Dense Vector Search<br/>+ Document Filtering"]
        H -.->|Retrieves Top Chunks| V_SEARCH
        
        V_SEARCH --> CTX["Enriched Policy Context<br/>+ Citations Metadata"]
        CTX --> LLM{"LLM Inference Engine"}
        
        LLM -->|Primary Engine| GROQ["⚡ Groq Cloud LPU<br/>(groq/compound-mini ~0.8s)"]
        LLM -.->|Local Fallback| OLLAMA["🦙 Ollama Local<br/>(qwen3:8b)"]
        
        GROQ & OLLAMA --> GEN_ANS["Accurate Grounded Answer<br/>+ Document/Page Sources"]
        GEN_ANS --> API
        API --> UI
        UI -->|Renders Answer & Badges| U
    end

    style INGESTION fill:#f8fafc,stroke:#cbd5e1,stroke-width:2px
    style QUERY fill:#f0fdf4,stroke:#86efac,stroke-width:2px
    style GROQ fill:#fef08a,stroke:#eab308,stroke-width:2px
    style H fill:#dbeafe,stroke:#3b82f6,stroke-width:2px
```

---

## ✨ Key Features

* **⚡ Ultra-Fast Inference:** Powered by **Groq LPU** (`groq/compound-mini`), achieving sub-second (~0.8s – 1.4s) answer generation.
* **🌲 Scalable Cloud Vectors:** Serverless **Pinecone Cloud Vector Database** with cosine similarity indexing and metadata filtering.
* **📂 Universal Multi-Format Support:**
  * 📄 **PDFs:** Page-by-page text extraction with header tracking.
  * 📊 **Spreadsheets:** Row-and-column semantic mapping for `.csv`, `.xlsx`, and `.xls`.
  * 📝 **Documents:** `.docx`, `.doc`, `.txt`, `.md` structured parsing.
  * 📸 **Image OCR:** Scanned policies, infographics, and posters (`.png`, `.jpg`, `.jpeg`, `.webp`, `.tiff`, `.bmp`).
* **🎯 Knowledge Base Scoping:** Search across all documents simultaneously or isolate queries to a specific policy.
* **🔍 Dynamic Suggested Questions:** Instant question prompts that automatically adapt based on the selected document scope.
* **🛡️ Zero Hallucinations:** Strict grounding rules prevent fabricated answers when questions fall outside company policies.
* **🎨 Modern Streamlit UI:** Premium interface with citation pills, scope switcher, dynamic badges, and document deletion management.

---

## 🚀 Getting Started

### 1. Clone & Install Dependencies
```bash
# Clone the repository
git clone https://github.com/sydelendure/Rag-assistant.git
cd Rag-assistant

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy the template configuration and add your API keys:
```bash
cp .env.example .env
```

Edit `.env`:
```env
# Vector Store Engine
VECTOR_STORE_TYPE=pinecone

# Pinecone Credentials (https://app.pinecone.io)
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=employee-policy-rag

# Groq Cloud Credentials (https://console.groq.com/keys)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=groq/compound-mini
```

---

## 🏃 Running the Application

### Option A: One-Click Start (Recommended)
Run both the **FastAPI Backend** and **Streamlit UI** simultaneously:
```bash
./start.sh
```

### Option B: Manual Start in Separate Terminals

**Terminal 1 — FastAPI Backend:**
```bash
source .venv/bin/activate
PYTHONPATH=. uvicorn app.api.main:app --host 127.0.0.1 --port 8000 --reload
```
* Interactive API Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

**Terminal 2 — Streamlit Frontend:**
```bash
source .venv/bin/activate
streamlit run ui.py
```
* Web Application: [http://localhost:8501](http://localhost:8501)

---

## 🧪 Testing & Verification

Run the automated test suite covering 6 policy domains, negative out-of-scope queries, and document scope isolation:
```bash
.venv/bin/python test_rag_rigorous.py
```

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service health, vector store status, LLM engine & chunk count |
| `POST` | `/ask` | Ask natural language questions with optional document scoping |
| `GET` | `/documents` | List all indexed policy documents with metadata |
| `POST` | `/documents/upload` | Upload & index any supported file (`.pdf`, `.csv`, `.xlsx`, `.docx`, `.png`, etc.) |
| `DELETE` | `/documents/{filename}` | Delete a document and purge its vectors from the database |