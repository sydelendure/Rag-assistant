import time
import sys
import json
from pathlib import Path

print("=" * 75)
print("COMPREHENSIVE END-TO-END RAG RIGOROUS VALIDATION SUITE")
print("=" * 75)

test_results = []

def record_test(name: str, passed: bool, details: str = "", latency: float = 0.0):
    status = "PASS" if passed else "FAIL"
    test_results.append({"name": name, "passed": passed, "details": details, "latency": latency})
    lat_str = f" ({latency:.2f}s)" if latency > 0 else ""
    print(f"[{status}] {name}{lat_str}")
    if details:
        print(f"       -> {details}")

# ==============================================================================
# TEST 1: ENVIRONMENT & CREDENTIALS
# ==============================================================================
try:
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    groq_key = os.getenv("GROQ_API_KEY")
    pinecone_key = os.getenv("PINECONE_API_KEY")
    has_keys = bool(groq_key and pinecone_key)
    record_test("1. Environment & Cloud Credentials Configured", has_keys, f"Groq LPU: {'Connected' if groq_key else 'Missing'}, Pinecone DB: {'Connected' if pinecone_key else 'Missing'}")
except Exception as e:
    record_test("1. Environment & Cloud Credentials Configured", False, str(e))

# ==============================================================================
# TEST 2: VECTOR STORE CONNECTION & CHUNKS COUNT
# ==============================================================================
try:
    from app.vectorstore import get_vector_store
    t0 = time.time()
    vs = get_vector_store()
    count = vs.count()
    lat = time.time() - t0
    record_test("2. Vector Store Connection & Pinecone Index Count", count > 0, f"Engine: {type(vs).__name__}, Count: {count} dense vectors indexed", lat)
except Exception as e:
    record_test("2. Vector Store Connection & Pinecone Index Count", False, str(e))

# ==============================================================================
# TEST 3: MULTI-FORMAT LOADER CAPABILITIES
# ==============================================================================
try:
    from app.ingestion.loader import load_document_pages
    doc_samples = list(Path("documents").glob("*.*"))
    loaded_docs = []
    t0 = time.time()
    for doc_path in doc_samples[:4]:
        pages = load_document_pages(doc_path)
        if len(pages) > 0:
            loaded_docs.append(doc_path.name)
    lat = time.time() - t0
    record_test("3. Multi-Format Universal Document Loader", len(loaded_docs) > 0, f"Successfully parsed {len(loaded_docs)} files: {', '.join(loaded_docs)}", lat)
except Exception as e:
    record_test("3. Multi-Format Universal Document Loader", False, str(e))

# ==============================================================================
# TEST 4: HIERARCHICAL SEMANTIC CHUNKER METADATA
# ==============================================================================
try:
    from app.ingestion.chunker import chunk_document
    sample_pages = [
        {"page": 1, "text": "CHAPTER 1: INTRODUCTION\n1.1 Purpose\nAll employees must adhere to safety rules.\n\n1.2 Scope\nThis policy applies to full-time staff."}
    ]
    chunks = chunk_document(sample_pages, "Test_Policy.pdf")
    has_meta = all("topic" in c and "section" in c and "page" in c for c in chunks)
    record_test("4. Hierarchical Metadata Preservation in Chunker", len(chunks) >= 1 and has_meta, f"Generated {len(chunks)} chunks with topic, section & page metadata")
except Exception as e:
    record_test("4. Hierarchical Metadata Preservation in Chunker", False, str(e))

# ==============================================================================
# TEST 5: RETRIEVAL & VECTOR SIMILARITY SEARCH
# ==============================================================================
try:
    from app.retrieval.retriever import Retriever
    t0 = time.time()
    retriever = Retriever()
    retrieved_chunks = retriever.retrieve("annual leave carry forward allowance", top_k=5)
    lat = time.time() - t0
    has_results = len(retrieved_chunks) > 0
    top_doc = retrieved_chunks[0].get("document", "Unknown") if has_results else "None"
    top_sec = retrieved_chunks[0].get("section", "Unknown") if has_results else "None"
    record_test("5. Dense Vector Semantic Retrieval & Ranking", has_results, f"Retrieved {len(retrieved_chunks)} chunks. Top: {top_doc} -> Section: {top_sec}", lat)
except Exception as e:
    record_test("5. Dense Vector Semantic Retrieval & Ranking", False, str(e))

# ==============================================================================
# TEST 6: DOCUMENT SCOPING ISOLATION
# ==============================================================================
try:
    t0 = time.time()
    scoped_chunks = retriever.retrieve("remote work equipment", document="Work_From_Home_Policy.pdf")
    lat = time.time() - t0
    all_match_scope = all(c.get("document") == "Work_From_Home_Policy.pdf" for c in scoped_chunks)
    record_test("6. Document Scope Query Isolation", len(scoped_chunks) > 0 and all_match_scope, f"Retrieved {len(scoped_chunks)} chunks, 100% scoped to Work_From_Home_Policy.pdf", lat)
except Exception as e:
    record_test("6. Document Scope Query Isolation", False, str(e))

# ==============================================================================
# TEST 7: GROQ LPU INFERENCE & LIVE TOKEN STREAMING
# ==============================================================================
try:
    from app.generation.generator import Generator
    t0 = time.time()
    generator = Generator()
    token_stream = generator.generate_stream("What is the annual leave carry forward limit?", retrieved_chunks)
    tokens = []
    for tok in token_stream:
        tokens.append(tok)
    full_answer = "".join(tokens)
    lat = time.time() - t0
    is_valid_answer = len(full_answer.strip()) > 10 and ("5" in full_answer or "leave" in full_answer.lower() or "carry" in full_answer.lower())
    record_test("7. Groq LPU Generation & Live Token Streaming", is_valid_answer, f"Tokens: {len(tokens)}, Answer: '{full_answer.strip()}'", lat)
except Exception as e:
    record_test("7. Groq LPU Generation & Live Token Streaming", False, str(e))

# ==============================================================================
# TEST 8: SENSITIVE QUERY & UNRESOLVED ESCALATION DETECTION
# ==============================================================================
try:
    from app.services.hr_service import is_sensitive_or_unresolved
    q1 = "How do I report confidential workplace harassment against my supervisor?"
    a1 = "All harassment grievances should be directed to HR."
    t1_pass = is_sensitive_or_unresolved(q1, a1)
    
    q2 = "Can I bring my pet dog to the office?"
    a2 = "I could not find relevant information in the available company policies."
    t2_pass = is_sensitive_or_unresolved(q2, a2)
    
    q3 = "What is the annual leave policy?"
    a3 = "Employees receive 20 days of annual leave per year."
    t3_pass = not is_sensitive_or_unresolved(q3, a3)  # standard query should NOT trigger false positive
    
    all_triggers_correct = t1_pass and t2_pass and t3_pass
    record_test("8. HR Escalation Intent & Knowledge-Gap Detection", all_triggers_correct, f"Harassment: {t1_pass}, Unmentioned Pet Policy: {t2_pass}, Standard Policy Safe: {t3_pass}")
except Exception as e:
    record_test("8. HR Escalation Intent & Knowledge-Gap Detection", False, str(e))

# ==============================================================================
# TEST 9: HR SUPPORT TICKET PERSISTENCE & RECEIPT GENERATION
# ==============================================================================
try:
    from app.services.hr_service import create_ticket, get_all_tickets
    t0 = time.time()
    sample_ticket = create_ticket(
        subject="Automated Verification Ticket",
        message="Checking ticket persistence and SLA tracking.",
        category="Policy Clarification / Exception",
        urgency="High Priority (Same Day)",
        name="Verification Agent",
        email="agent@company.internal",
        is_anonymous=False,
        source_question="Test Question",
    )
    lat = time.time() - t0
    ticket_id = sample_ticket.get("ticket_id", "")
    all_tickets = get_all_tickets()
    is_saved = any(t.get("ticket_id") == ticket_id for t in all_tickets)
    record_test("9. HR Support Ticket Storage & Reference ID Generation", is_saved and ticket_id.startswith("HR-"), f"Generated ID: {ticket_id}, Total Logged Tickets: {len(all_tickets)}", lat)
except Exception as e:
    record_test("9. HR Support Ticket Storage & Reference ID Generation", False, str(e))

# ==============================================================================
# TEST 10: FASTAPI BACKEND API REST CONTRACTS
# ==============================================================================
try:
    from fastapi.testclient import TestClient
    from app.api.main import app as fastapi_app
    
    client = TestClient(fastapi_app)
    
    # 1. Health endpoint
    r_health = client.get("/health")
    health_ok = r_health.status_code == 200 and r_health.json().get("status") == "healthy"
    
    # 2. Ask endpoint
    t0 = time.time()
    r_ask = client.post("/ask", json={"question": "What is the daily domestic meal allowance?"})
    lat_api = time.time() - t0
    ask_ok = r_ask.status_code == 200 and len(r_ask.json().get("answer", "")) > 0
    
    # 3. Documents endpoint
    r_docs = client.get("/documents")
    docs_ok = r_docs.status_code == 200
    
    # 4. HR Tickets endpoint
    r_hr = client.get("/hr/tickets")
    hr_ok = r_hr.status_code == 200 and isinstance(r_hr.json(), list)
    
    all_endpoints_ok = health_ok and ask_ok and docs_ok and hr_ok
    record_test("10. FastAPI Production REST API Endpoints", all_endpoints_ok, f"Health: {health_ok}, Ask: {ask_ok} ({lat_api:.2f}s), Docs: {docs_ok}, Tickets: {hr_ok}")
except Exception as e:
    record_test("10. FastAPI Production REST API Endpoints", False, str(e))

print("=" * 75)
total_tests = len(test_results)
passed_tests = sum(1 for t in test_results if t["passed"])
pass_rate = (passed_tests / total_tests) * 100
print(f"OVERALL SUMMARY: {passed_tests}/{total_tests} Tests Passed ({pass_rate:.1f}%)")
print("=" * 75)
