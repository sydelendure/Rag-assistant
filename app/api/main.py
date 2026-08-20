# Imports & FastAPI Framework #
from pathlib import Path
import shutil

from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel

from app.retrieval.retriever import Retriever
from app.generation.generator import Generator
from app.ingestion.ingest import ingest_document

# FastAPI Application Instance #
app = FastAPI(
    title="Employee Policy Knowledge Assistant",
    description="RAG-based employee policy question answering system.",
    version="1.0.0",
)


# Pydantic Request & Response Data Models #
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


# Global RAG Engine Components (Retriever & Generator) #
retriever = Retriever(top_k=5)
generator = Generator()


# Root API Endpoint #
@app.get("/")
def root():
    return {
        "message": "Employee Policy Knowledge Assistant API is running."
    }


# Health Check & Diagnostic Status Endpoint #
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


# List All Available Policy Documents Endpoint #
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


# Ask Question & Synthesize Answer Endpoint #
@app.post(
    "/ask",
    response_model=AnswerResponse,
)
def ask_question(request: QuestionRequest):

    # Validate Input Query #
    question = request.question.strip()
    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:
        # Step 1: Retrieve Relevant Policy Chunks #
        retrieved_chunks = retriever.retrieve(
            question,
            document_filter=request.document,
        )

        # Step 2: Synthesize Answer via LLM #
        answer = generator.generate(
            question=question,
            retrieved_chunks=retrieved_chunks,
        )

        # Step 3: Format Citation Sources #
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


# Upload & Ingest New Policy Document Endpoint #
@app.post("/documents/upload")
def upload_document(
    file: UploadFile = File(...)
):

    # Validate File Name #
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided.",
        )

    # Validate File Format Extension #
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

    # Create Documents Directory & Safe Path #
    documents_directory = Path("documents")
    documents_directory.mkdir(
        parents=True,
        exist_ok=True,
    )
    safe_filename = Path(file.filename).name
    file_path = documents_directory / safe_filename

    try:
        # Step 1: Save Uploaded File to Disk #
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Step 2: Ingest & Index into Vector Database #
        ingestion_result = ingest_document(file_path)

        # Step 3: Return Ingestion Confirmation #
        return {
            "message": "Document uploaded and indexed successfully.",
            "filename": safe_filename,
            "chunks_created": ingestion_result["chunks"],
        }

    except ValueError as error:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload and index the document: {error}",
        )

    finally:
        file.file.close()


# Delete Document & Purge Vectors Endpoint #
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


# HR Ticket Escalation Pydantic Model #
class TicketCreateRequest(BaseModel):
    subject: str
    message: str
    category: str = "Policy Clarification"
    urgency: str = "Normal"
    name: str | None = "Employee"
    email: str | None = ""
    is_anonymous: bool = False
    source_question: str | None = None


# Create HR Support Ticket Endpoint #
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


# List All Submitted HR Tickets Endpoint #
@app.get("/hr/tickets")
def list_hr_tickets():
    """List all submitted HR escalation tickets."""
    from app.services.hr_service import get_all_tickets

    return get_all_tickets()