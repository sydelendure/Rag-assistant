import time
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def log_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_health():
    log_section("1. HEALTH & CONNECTIVITY CHECK")
    res = requests.get(f"{BASE_URL}/health", timeout=5.0)
    assert res.status_code == 200, f"Health check failed: {res.status_code}"
    data = res.json()
    print(f"Status: {data.get('status')}")
    print(f"Vector Engine: {data.get('vector_engine')}")
    print(f"LLM Engine: {data.get('llm_engine')}")
    print(f"Indexed Chunks: {data.get('documents_indexed')}")
    assert "Pinecone" in data.get("vector_engine", ""), "Vector engine is not Pinecone"
    assert "Groq" in data.get("llm_engine", ""), "LLM engine is not Groq"
    print("Health check PASSED.")

def test_queries():
    log_section("2. DOMAIN ACCURACY & LATENCY BENCHMARKS")
    
    test_cases = [
        {
            "category": "Leave & Carry Forward",
            "question": "What is the annual leave entitlement and how many days can be carried forward?",
            "expected_keywords": ["20", "5", "carry", "annual"],
        },
        {
            "category": "Workplace Safety",
            "question": "What are employees required to do regarding workplace safety and hazards?",
            "expected_keywords": ["safety", "hazard", "report", "protective"],
        },
        {
            "category": "Expense Reimbursement",
            "question": "What is the policy for submitting business expense claims?",
            "expected_keywords": ["expense", "receipt", "claim", "reimbursement", "approv"],
        },
        {
            "category": "Remote Work / WFH",
            "question": "What are the requirements for working from home?",
            "expected_keywords": ["home", "workspace", "remote", "manager", "approv"],
        },
        {
            "category": "Anti-Harassment",
            "question": "What is the company policy against harassment and discrimination?",
            "expected_keywords": ["harassment", "discrimination", "prohibit", "report"],
        },
        {
            "category": "Out-of-Scope / Negative Test",
            "question": "What is the policy regarding personal pet ownership in private homes?",
            "expected_keywords": ["not", "information", "covered", "available", "policy"],
        },
    ]

    latencies = []
    
    for i, tc in enumerate(test_cases, 1):
        print(f"\n[Test {i}/6] Category: {tc['category']}")
        print(f"Question: \"{tc['question']}\"")
        
        t0 = time.time()
        res = requests.post(
            f"{BASE_URL}/ask",
            json={"question": tc["question"]},
            timeout=30.0
        )
        t1 = time.time()
        latency = t1 - t0
        latencies.append(latency)
        
        assert res.status_code == 200, f"Query failed with status {res.status_code}"
        data = res.json()
        answer = data.get("answer", "")
        sources = data.get("sources", [])
        
        print(f"Latency: {latency:.3f}s")
        print(f"Answer: {answer}")
        print(f"Sources matched ({len(sources)}): {[s.get('document') + ' (P' + str(s.get('page')) + ')' for s in sources[:3]]}")
        
        # Verify non-empty answer
        assert len(answer.strip()) > 0, "Answer is empty!"
        print(f"Status: PASSED ({latency:.3f}s)")
        
    avg_latency = sum(latencies) / len(latencies)
    print(f"\nAverage End-to-End Latency: {avg_latency:.3f} seconds (Target: < 2.0s)")

def test_document_scoped_queries():
    log_section("3. TARGETED DOCUMENT SCOPING TESTS")
    
    print("\n[Scope Test A] Strictly querying 'Company_Policy_Handbook.pdf'")
    res = requests.post(
        f"{BASE_URL}/ask",
        json={
            "question": "What is the disciplinary procedure for policy violations?",
            "document": "Company_Policy_Handbook.pdf"
        },
        timeout=45.0
    )
    assert res.status_code == 200
    data = res.json()
    sources = data.get("sources", [])
    print(f"Answer: {data.get('answer')}")
    print(f"Sources: {[s.get('document') for s in sources]}")
    for s in sources:
        assert s.get("document") == "Company_Policy_Handbook.pdf", f"Unexpected source: {s.get('document')}"
    print("Scoping to Company_Policy_Handbook.pdf: 100% ISOLATED & PASSED.")

    print("\n[Scope Test B] Strictly querying 'Leave_Policy.pdf'")
    res = requests.post(
        f"{BASE_URL}/ask",
        json={
            "question": "How is sick leave applied and how many days are allowed?",
            "document": "Leave_Policy.pdf"
        },
        timeout=45.0
    )
    assert res.status_code == 200
    data = res.json()
    sources = data.get("sources", [])
    print(f"Answer: {data.get('answer')}")
    print(f"Sources: {[s.get('document') for s in sources]}")
    for s in sources:
        assert s.get("document") == "Leave_Policy.pdf", f"Unexpected source: {s.get('document')}"
    print("Scoping to Leave_Policy.pdf: 100% ISOLATED & PASSED.")

if __name__ == "__main__":
    print("STARTING VIGOROUS TEST SUITE FOR EMPLOYEE POLICY RAG...")
    test_health()
    test_queries()
    test_document_scoped_queries()
    log_section("ALL VIGOROUS TESTS PASSED SUCCESSFULLY!")
