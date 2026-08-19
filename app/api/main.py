from pathlib import Path
import shutil

from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel

from app.retrieval.retriever import Retriever
from app.generation.generator import Generator
from app.ingestion.ingest import ingest_document


app = FastAPI(
    title="Employee Policy Knowledge Assistant",
    description="RAG-based employee policy question answering system.",
    version="1.0.0",
)


# ==================================================
# Request / Response Models
# ==================================================

class QuestionRequest(BaseModel):
    question: str
    document: str | None = None


class Source(BaseModel):
    document: str
    topic: str = ""
    section: str = ""
    page: int = 1


class AnswerResponse(BaseModel):
    answer: str
    sources: list[Source]


# ==================================================
# Initialize RAG Components
# ==================================================

retriever = Retriever(top_k=5)
generator = Generator()


# ==================================================
# Root Endpoint
# ==================================================

@app.get("/")
def root():
    return {
        "message": "Employee Policy Knowledge Assistant API is running."
    }


# ==================================================
# Health Check
# ==================================================

@app.get("/health")
def health_check():

    try:
        document_count = retriever.vector_store.count()
        engine_name = (
            "Pinecone Cloud"
            if "Pinecone" in retriever.vector_store.__class__.__name__
            else "ChromaDB Local"
        )

        llm_engine = (
            f"Groq Cloud ({generator.groq_model})"
            if getattr(generator, "provider", "") == "groq"
            else f"Ollama Local ({generator.ollama_model})"
        )

        return {
            "status": "healthy",
            "service": "Employee Policy Knowledge Assistant",
            "vector_store": "connected",
            "vector_engine": engine_name,
            "llm_engine": llm_engine,
            "documents_indexed": document_count,
        }

    except Exception:

        return {
            "status": "unhealthy",
            "service": "Employee Policy Knowledge Assistant",
            "vector_store": "unavailable",
        }


@app.get("/documents")
def list_documents():
    """List all available policy documents."""
    docs_dir = Path("documents")
    if not docs_dir.exists():
        return {"documents": []}

    supported_extensions = {
        ".pdf", ".csv", ".xlsx", ".xls", ".docx", ".doc", ".txt", ".md",
        ".png", ".jpg", ".jpeg", ".webp", ".tiff", ".bmp"
    }
    files = [
        {"filename": p.name, "size_bytes": p.stat().st_size}
        for p in docs_dir.glob("*.*")
        if p.suffix.lower() in supported_extensions
    ]
    return {"documents": files}


# ==================================================
# Ask Question
# ==================================================

@app.post(
    "/ask",
    response_model=AnswerResponse,
)
def ask_question(request: QuestionRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:

        # ------------------------------------------
        # Retrieve relevant policy chunks
        # ------------------------------------------

        retrieved_chunks = retriever.retrieve(
            question,
            document_filter=request.document,
        )

        # ------------------------------------------
        # Generate answer
        # ------------------------------------------

        answer = generator.generate(
            question=question,
            retrieved_chunks=retrieved_chunks,
        )

        # ------------------------------------------
        # Prepare source information
        # ------------------------------------------

        sources = [
            Source(
                document=chunk.get("document", "Document"),
                topic=chunk.get("topic", ""),
                section=chunk.get("section", "General"),
                page=chunk.get("page", 1),
            )
            for chunk in retrieved_chunks
        ]

        return AnswerResponse(
            answer=answer,
            sources=sources,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"An internal error occurred: {error}",
        )


# ==================================================
# Upload and Index Policy Document
# ==================================================

@app.post("/documents/upload")
def upload_document(
    file: UploadFile = File(...)
):

    # ----------------------------------------------
    # Validate filename
    # ----------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided.",
        )

    # ----------------------------------------------
    # Validate file type
    # ----------------------------------------------

    supported_extensions = {
        ".pdf", ".csv", ".xlsx", ".xls", ".docx", ".doc", ".txt", ".md",
        ".png", ".jpg", ".jpeg", ".webp", ".tiff", ".bmp"
    }
    file_suffix = Path(file.filename).suffix.lower()
    if file_suffix not in supported_extensions:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported format '{file_suffix}'. "
                f"Supported: {', '.join(sorted(supported_extensions))}"
            ),
        )

    # ----------------------------------------------
    # Create documents directory
    # ----------------------------------------------

    documents_directory = Path("documents")

    documents_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Prevent directory traversal
    safe_filename = Path(
        file.filename
    ).name

    file_path = (
        documents_directory / safe_filename
    )

    try:

        # ------------------------------------------
        # 1. Save uploaded file
        # ------------------------------------------

        with file_path.open("wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer,
            )

        # ------------------------------------------
        # 2. Ingest the uploaded file
        # ------------------------------------------

        ingestion_result = ingest_document(
            file_path
        )

        # ------------------------------------------
        # 3. Return successful result
        # ------------------------------------------

        return {
            "message": (
                "Document uploaded and "
                "indexed successfully."
            ),
            "filename": safe_filename,
            "chunks_created": (
                ingestion_result["chunks"]
            ),
        }

    except ValueError as error:

        # Remove invalid/failed upload
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:

        # Remove file if ingestion failed
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to upload and index "
                f"the document: {error}"
            ),
        )

    finally:

        file.file.close()


# ==================================================
# Delete Policy Document
# ==================================================

@app.delete("/documents/{filename}")
def delete_document(filename: str):
    """Delete a document from disk and remove its vectors from vector store."""
    safe_name = Path(filename).name
    file_path = Path("documents") / safe_name

    if file_path.exists():
        file_path.unlink()

    retriever.vector_store.delete_document(safe_name)

    return {
        "message": f"Document '{safe_name}' deleted successfully.",
        "remaining_chunks": retriever.vector_store.count(),
    }


# ==================================================
# HR Support & Ticket Escalation
# ==================================================

class TicketCreateRequest(BaseModel):
    subject: str
    message: str
    category: str = "Policy Clarification"
    urgency: str = "Normal"
    name: str | None = "Employee"
    email: str | None = ""
    is_anonymous: bool = False
    source_question: str | None = None


@app.post("/hr/tickets")
def submit_hr_ticket(ticket: TicketCreateRequest):
    """Create a new HR escalation ticket."""
    from app.services.hr_service import create_ticket

    if not ticket.subject.strip() or not ticket.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Ticket subject and message cannot be empty.",
        )

    record = create_ticket(
        subject=ticket.subject,
        message=ticket.message,
        category=ticket.category,
        urgency=ticket.urgency,
        name=ticket.name,
        email=ticket.email,
        is_anonymous=ticket.is_anonymous,
        source_question=ticket.source_question,
    )
    return record


@app.get("/hr/tickets")
def list_hr_tickets():
    """List all submitted HR escalation tickets."""
    from app.services.hr_service import get_all_tickets

    return get_all_tickets()