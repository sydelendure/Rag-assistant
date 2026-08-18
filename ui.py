import os
from pathlib import Path
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
DOCUMENTS_DIR = Path("documents")

# ==================================================
# Page Configuration
# ==================================================
st.set_page_config(
    page_title="Employee Policy Assistant",
    page_icon=":material/corporate_fare:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================================================
# Custom CSS (Anthropic-Inspired Editorial & Warm Light Theme)
# ==================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,500;0,8..60,600;0,8..60,700;1,8..60,400&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Global Base */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #262422;
        background-color: #FAF8F5;
    }

    /* Top Navigation / App Banner */
    .top-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.75rem 0 1.25rem 0;
        border-bottom: 1px solid #E8E2D8;
        margin-bottom: 1.5rem;
    }
    .org-brand {
        display: flex;
        flex-direction: column;
    }
    .org-title {
        font-family: 'Source Serif 4', 'Newsreader', Georgia, serif;
        font-size: 1.55rem;
        font-weight: 600;
        letter-spacing: -0.02em;
        color: #1F1D1A;
        margin: 0;
    }
    .org-subtitle {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.8125rem;
        color: #736C64;
        font-weight: 500;
        margin-top: 0.2rem;
        letter-spacing: 0.01em;
    }

    /* Status Indicators */
    .status-container {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.35rem 0.75rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }
    .status-online {
        background-color: #F1F8F3;
        color: #1E6B37;
        border: 1px solid #CFE7D6;
    }
    .status-offline {
        background-color: #FDF2F0;
        color: #A32D19;
        border: 1px solid #F8D0C9;
    }
    .indicator-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        display: inline-block;
    }
    .dot-green { background-color: #2EA857; }
    .dot-red { background-color: #D63923; }

    /* Anthropic Warm Editorial Hero Panel */
    .hero-panel {
        background: #F4EFEA;
        border: 1px solid #E5DFD6;
        border-radius: 10px;
        padding: 1.5rem 1.75rem;
        margin-bottom: 1.5rem;
    }
    .hero-headline {
        font-family: 'Source Serif 4', 'Newsreader', Georgia, serif;
        font-size: 1.35rem;
        font-weight: 600;
        color: #1F1D1A;
        letter-spacing: -0.015em;
        margin-bottom: 0.4rem;
    }
    .hero-copy {
        font-size: 0.9rem;
        color: #524E48;
        line-height: 1.6;
    }

    /* Policy Category Tags */
    .tag-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin-top: 0.95rem;
    }
    .category-tag {
        font-size: 0.75rem;
        font-weight: 500;
        background: #FAF8F5;
        border: 1px solid #DCD5C9;
        color: #4A4640;
        padding: 0.25rem 0.6rem;
        border-radius: 5px;
    }

    /* Section Subheadings */
    h1, h2, h3, h4, h5, h6, .stSubheader {
        font-family: 'Source Serif 4', 'Newsreader', Georgia, serif !important;
        color: #1F1D1A !important;
        font-weight: 600 !important;
        letter-spacing: -0.015em !important;
    }

    /* Source Citation Footnotes */
    .citations-card {
        margin-top: 0.85rem;
        padding: 0.75rem 1rem;
        background: #FFFFFF;
        border: 1px solid #E8E2D8;
        border-left: 3px solid #CC6B49;
        border-radius: 6px;
    }
    .citations-header {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #736C64;
        margin-bottom: 0.45rem;
    }
    .citation-item {
        display: inline-flex;
        align-items: center;
        font-size: 0.8125rem;
        color: #262422;
        background: #FAF8F5;
        border: 1px solid #E5DFD6;
        padding: 0.25rem 0.6rem;
        border-radius: 4px;
        margin: 0.15rem 0.35rem 0.15rem 0;
        font-family: 'JetBrains Mono', monospace;
    }
    .citation-doc {
        font-weight: 600;
        color: #B25232;
    }
    .citation-section {
        color: #5C564E;
        margin-left: 0.35rem;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #F4EFEA !important;
        border-right: 1px solid #E5DFD6;
    }
    .sidebar-doc-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.45rem 0.65rem;
        background: #FFFFFF;
        border: 1px solid #E5DFD6;
        border-radius: 5px;
        margin-bottom: 0.35rem;
        font-size: 0.8rem;
    }
    .doc-type-badge {
        font-size: 0.65rem;
        font-family: 'JetBrains Mono', monospace;
        background: #F0EAE1;
        color: #5C564E;
        padding: 0.15rem 0.35rem;
        border-radius: 3px;
        font-weight: 600;
    }
    .stat-box {
        background: #FFFFFF;
        border: 1px solid #E5DFD6;
        border-radius: 6px;
        padding: 0.75rem;
        margin-bottom: 0.75rem;
    }
    .stat-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        font-weight: 600;
        color: #736C64;
        letter-spacing: 0.05em;
    }
    .stat-value {
        font-family: 'Source Serif 4', serif;
        font-size: 1.25rem;
        font-weight: 600;
        color: #1F1D1A;
        margin-top: 0.15rem;
    }

    /* Chat Messages Styling */
    .stChatMessage {
        background-color: #FFFFFF !important;
        border: 1px solid #E8E2D8 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        margin-bottom: 0.75rem !important;
    }

    /* Buttons */
    div.stButton > button {
        background-color: #FFFFFF;
        border: 1px solid #DCD5C9;
        color: #262422;
        border-radius: 6px;
        font-weight: 500;
        font-size: 0.875rem;
        transition: all 0.15s ease-in-out;
    }
    div.stButton > button:hover {
        background-color: #F7F3EE;
        border-color: #CC6B49;
        color: #B25232;
    }
    div.stButton > button[kind="primary"] {
        background-color: #CC6B49;
        border: 1px solid #B25232;
        color: #FFFFFF;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #B85837;
        border-color: #9E4628;
        color: #FFFFFF;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==================================================
# API Health Check
# ==================================================
def check_api_health():
    try:
        response = requests.get(f"{API_URL}/health", timeout=3.0)
        if response.status_code == 200:
            return True, response.json()
        return False, {}
    except Exception:
        return False, {}

is_online, health_data = check_api_health()
indexed_chunks = health_data.get("documents_indexed", 0)

# ==================================================
# Sidebar Navigation & Management Portal
# ==================================================
with st.sidebar:
    st.markdown("### Policy Hub & Operations")
    st.caption("Internal Governance & Policy Directory")

    # Diagnostics Box
    st.markdown("---")
    st.markdown("**System Diagnostics**")
    
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.markdown(
            f"""
            <div class="stat-box">
                <div class="stat-label">Vector Store</div>
                <div class="stat-value">{indexed_chunks}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_stat2:
        status_text = "Active" if is_online else "Offline"
        st.markdown(
            f"""
            <div class="stat-box">
                <div class="stat-label">API Status</div>
                <div class="stat-value" style="font-size: 1rem; color: {'#1E6B37' if is_online else '#A32D19'};">{status_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    llm_engine_name = health_data.get("llm_engine", "Local LLM")
    vector_engine_label = health_data.get("vector_engine", "ChromaDB Local")
    st.caption(f"**LLM:** {llm_engine_name}")
    st.caption(f"**DB:** {vector_engine_label}")

    if not is_online:
        st.warning(
            "FastAPI backend is offline. Run `uvicorn app.api.main:app --port 8000` to connect.",
            icon=":material/warning:",
        )

    # Repository Listing
    st.markdown("---")
    st.markdown("**Indexed Policy Documents**")
    
    SUPPORTED_EXTS = {
        ".pdf", ".csv", ".xlsx", ".xls", ".docx", ".doc", ".txt", ".md",
        ".png", ".jpg", ".jpeg", ".webp", ".tiff", ".bmp"
    }
    if DOCUMENTS_DIR.exists():
        doc_files = sorted([f for f in DOCUMENTS_DIR.glob("*.*") if f.suffix.lower() in SUPPORTED_EXTS])
        if doc_files:
            for doc_file in doc_files:
                doc_title = doc_file.stem.replace("_", " ")
                doc_ext = doc_file.suffix.upper().replace(".", "")
                c_doc, c_del = st.columns([4, 1])
                with c_doc:
                    st.markdown(
                        f"""
                        <div class="sidebar-doc-row">
                            <span style="color: #38342E; font-weight: 500; font-size: 0.85rem;">{doc_title}</span>
                            <span class="doc-type-badge">{doc_ext}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with c_del:
                    if st.button("✕", key=f"del_{doc_file.name}", help=f"Delete {doc_file.name} from vector store"):
                        try:
                            requests.delete(f"{API_URL}/documents/{doc_file.name}", timeout=10)
                            st.session_state.upload_status = {"type": "success", "msg": f"Deleted '{doc_file.name}'."}
                            st.rerun()
                        except Exception as ex:
                            st.session_state.upload_status = {"type": "error", "msg": f"Delete failed: {ex}"}
                            st.rerun()
        else:
            st.info("No documents currently indexed.")
    else:
        st.info("Documents repository directory not initialized.")

    # Upload & Ingest New Policies
    st.markdown("---")
    
    # Check if there was an upload status message
    has_upload_status = "upload_status" in st.session_state and st.session_state.upload_status is not None
    
    with st.expander("Ingest New Document", expanded=has_upload_status, icon=":material/upload_file:"):
        if has_upload_status:
            status_info = st.session_state.pop("upload_status")
            if status_info["type"] == "success":
                st.success(status_info["msg"], icon=":material/check_circle:")
            else:
                st.error(status_info["msg"], icon=":material/error:")

        uploaded_doc = st.file_uploader(
            "Select Document File",
            type=["pdf", "csv", "xlsx", "xls", "docx", "doc", "txt", "md", "png", "jpg", "jpeg", "webp", "tiff", "bmp"],
            help="Upload an authorized PDF, CSV, Excel, Word, Text file, or Scanned Image/Infographic to parse, embed, and index into the vector database.",
        )
        if uploaded_doc is not None:
            if st.button("Process & Index", type="primary", icon=":material/sync:"):
                if not is_online:
                    st.error("Operation failed: FastAPI backend is unreachable.")
                else:
                    with st.spinner(f"Ingesting '{uploaded_doc.name}'..."):
                        try:
                            res = requests.post(
                                f"{API_URL}/documents/upload",
                                files={
                                    "file": (
                                        uploaded_doc.name,
                                        uploaded_doc.getvalue(),
                                        uploaded_doc.type or "application/octet-stream",
                                    )
                                },
                                timeout=120,
                            )
                            if res.status_code == 200:
                                res_json = res.json()
                                success_msg = f"Indexed '{res_json['filename']}' ({res_json['chunks_created']} chunks added)."
                                st.session_state.upload_status = {"type": "success", "msg": success_msg}
                                st.toast(success_msg)
                                st.rerun()
                            else:
                                err_detail = res.json().get("detail", res.text)
                                st.session_state.upload_status = {"type": "error", "msg": f"Ingestion rejected: {err_detail}"}
                                st.rerun()
                        except Exception as e:
                            st.session_state.upload_status = {"type": "error", "msg": f"Ingestion failed: {e}"}
                            st.rerun()

    # Conversation Actions
    st.markdown("---")
    if st.button("Reset Conversation", icon=":material/restart_alt:"):
        st.session_state.messages = []
        st.rerun()


# ==================================================
# Main App Header
# ==================================================
vector_engine_name = health_data.get("vector_engine", "CHROMA VECTOR DB").upper()
if is_online:
    status_indicator_html = f'<div class="status-container status-online"><span class="indicator-dot dot-green"></span><span>CONNECTED | {vector_engine_name} ({indexed_chunks} CHUNKS)</span></div>'
else:
    status_indicator_html = '<div class="status-container status-offline"><span class="indicator-dot dot-red"></span><span>DISCONNECTED | BACKEND UNREACHABLE</span></div>'

st.markdown(
    f'<div class="top-nav"><div class="org-brand"><h1 class="org-title">Employee Policy Assistant</h1><div class="org-subtitle">Enterprise Retrieval-Augmented Generation (RAG) System</div></div><div>{status_indicator_html}</div></div>',
    unsafe_allow_html=True,
)

# Document Scope Selector
available_docs = ["All Documents"]
if DOCUMENTS_DIR.exists():
    available_docs += sorted([p.name for p in DOCUMENTS_DIR.glob("*.*") if p.suffix.lower() in SUPPORTED_EXTS])

selected_scope = st.selectbox(
    "Knowledge Base Scope",
    options=available_docs,
    index=0,
    help="Target your query strictly to a specific document or search across the entire knowledge base.",
)

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Comprehensive Document-Specific Suggestions Mapping
DOCUMENT_SUGGESTIONS = {
    "All Documents": [
        "What is the annual leave entitlement and carry-forward limit?",
        "What are the eligibility requirements for working from home?",
        "What is the deadline and documentation required for expense claims?",
        "What are employee responsibilities for workplace health and safety?",
        "What is the company policy against harassment and discrimination?",
        "What health insurance and professional development benefits are provided?",
    ],
    "Company_Policy_Handbook.pdf": [
        "What are the workplace safety rules and hazard reporting procedures?",
        "What is the policy against harassment, discrimination, and retaliation?",
        "What are the annual and sick leave entitlements in the handbook?",
        "What are the disciplinary procedures for policy violations?",
        "What home workspace and security standards are required for remote work?",
        "What is the policy on company asset protection and confidential data?",
    ],
    "Leave_Policy.pdf": [
        "What is the annual leave entitlement and monthly accrual rate?",
        "How many unused annual leave days can be carried forward to the next year?",
        "What is the sick leave allowance and when is medical documentation required?",
        "What are the notice periods and approval processes for planned leave?",
        "How are public holidays treated when falling during annual leave?",
        "What are the rules regarding unpaid leave and casual leave?",
    ],
    "Work_From_Home_Policy.pdf": [
        "What are the eligibility criteria and weekly limits for working from home?",
        "What core working hours must remote employees maintain?",
        "What internet connectivity and data security requirements apply to WFH?",
        "Under what circumstances can work-from-home approval be revoked?",
    ],
    "Travel_Policy.pdf": [
        "What is the approval process for domestic and international business travel?",
        "What are the daily allowances for meals, lodging, and local transit?",
        "What travel expenses are strictly non-reimbursable?",
        "What is the timeline for submitting travel expense reports after a trip?",
    ],
    "Expense_Reimbursement_Policy.pdf": [
        "What is the 15-day deadline for submitting reimbursement claims?",
        "What original receipts or tax invoices are required for claim approval?",
        "What spending limits require advance manager approval?",
        "How are reimbursement claims verified and paid out in payroll cycles?",
    ],
    "Attendance_Policy.pdf": [
        "What are the standard working hours and grace period for daily check-in?",
        "What is the procedure for notifying managers about tardiness or emergencies?",
        "How are unexcused absences and repeated lateness handled disciplinary-wise?",
        "What are the rules regarding shift handovers and overtime approval?",
    ],
    "Employee_Benefits.pdf": [
        "What medical, hospitalization, and dental insurance coverage is provided?",
        "What annual allowance is available for professional certifications and courses?",
        "What wellness, mental health, and employee assistance programs exist?",
        "When do new hires become eligible to enroll in corporate benefit plans?",
    ],
    "Code_of_Conduct.pdf": [
        "What is the company policy regarding conflict of interest and external gigs?",
        "What are the rules on accepting gifts, entertainment, or hospitality from vendors?",
        "How can an employee report unethical behavior or misconduct confidentially?",
        "What are the standards for treating colleagues with mutual respect and dignity?",
    ],
}

def get_suggestions_for_scope(scope: str) -> list[str]:
    if scope in DOCUMENT_SUGGESTIONS:
        return DOCUMENT_SUGGESTIONS[scope]
    clean_name = scope.replace(".pdf", "").replace("_", " ")
    return [
        f"What are the key rules and guidelines in {clean_name}?",
        f"What are employee responsibilities outlined in {clean_name}?",
        f"What approval processes are required under {clean_name}?",
        f"What are the policy violations and penalties mentioned in {clean_name}?",
    ]

active_suggestions = get_suggestions_for_scope(selected_scope)
half = (len(active_suggestions) + 1) // 2
quick_prompts_a = active_suggestions[:half]
quick_prompts_b = active_suggestions[half:]

# Welcome Hero & Suggested Topics (When Thread is Empty)
if len(st.session_state.messages) == 0:
    scope_display_title = selected_scope.replace(".pdf", "").replace("_", " ")
    st.markdown(
        f"""
        <div class="hero-panel">
            <div class="hero-headline">Internal Policy Inquiry Portal</div>
            <div class="hero-copy">
                Query internal regulations, compliance guidelines, employee benefits, remote work provisions, and administrative processes. All responses are synthesized strictly from validated corporate documentation with full citation tracking.
            </div>
            <div class="tag-grid">
                <span class="category-tag">Annual & Sick Leave</span>
                <span class="category-tag">Remote Work Eligibility</span>
                <span class="category-tag">Travel & Daily Allowance</span>
                <span class="category-tag">Expense Claims & Receipts</span>
                <span class="category-tag">Group Health Insurance</span>
                <span class="category-tag">Code of Conduct</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("##### Suggested Queries")
    col_a, col_b = st.columns(2)

    for p in quick_prompts_a:
        if col_a.button(p, key=f"welcome_q_{p}", icon=":material/arrow_forward:"):
            st.session_state.pending_prompt = p
            st.rerun()

    for p in quick_prompts_b:
        if col_b.button(p, key=f"welcome_q_{p}", icon=":material/arrow_forward:"):
            st.session_state.pending_prompt = p
            st.rerun()

# Conversation Stream
for message in st.session_state.messages:
    role_icon = ":material/person:" if message["role"] == "user" else ":material/smart_toy:"
    with st.chat_message(message["role"], avatar=role_icon):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("sources"):
            with st.expander(f"Source References ({len(message['sources'])} documents matched)", expanded=False):
                for s in message["sources"]:
                    doc_name = s.get("document", "Document")
                    page_num = s.get("page")
                    topic = s.get("topic", "")
                    sec = s.get("section", "General")
                    page_str = f" | Page {page_num}" if page_num else ""
                    topic_str = f" | {topic}" if topic and topic != doc_name else ""
                    st.markdown(f"- **`{doc_name}`**{page_str} - Section: **{sec}**{topic_str}")

# If conversation is in progress, keep suggested queries accessible in an expander
if len(st.session_state.messages) > 0:
    with st.expander("Suggested Questions", expanded=False):
        col_s1, col_s2 = st.columns(2)
        for p in quick_prompts_a:
            if col_s1.button(p, key=f"chat_q_{p}", icon=":material/arrow_forward:"):
                st.session_state.pending_prompt = p
                st.rerun()
        for p in quick_prompts_b:
            if col_s2.button(p, key=f"chat_q_{p}", icon=":material/arrow_forward:"):
                st.session_state.pending_prompt = p
                st.rerun()

# Input Handling
user_input = st.chat_input("Enter your policy inquiry (e.g., leave carry-forward, travel allowance, expense filing)...")

query_to_run = None
if st.session_state.get("pending_prompt"):
    query_to_run = st.session_state.pop("pending_prompt")
elif user_input:
    query_to_run = user_input

if query_to_run:
    st.session_state.messages.append({"role": "user", "content": query_to_run})
    with st.chat_message("user", avatar=":material/person:"):
        st.markdown(query_to_run)

    with st.chat_message("assistant", avatar=":material/smart_toy:"):
        with st.spinner("Analyzing company policies and synthesizing answer..."):
            if not is_online:
                err_text = "Service Unavailable: The backend API is unreachable. Please verify that the FastAPI service is active on port 8000."
                st.markdown(err_text)
                st.session_state.messages.append(
                    {"role": "assistant", "content": err_text, "sources": []}
                )
            else:
                try:
                    payload = {"question": query_to_run}
                    if selected_scope != "All Documents":
                        payload["document"] = selected_scope

                    res = requests.post(
                        f"{API_URL}/ask",
                        json=payload,
                        timeout=90,
                    )
                    if res.status_code == 200:
                        data = res.json()
                        answer_text = data.get("answer", "No answer generated.")
                        sources_list = data.get("sources", [])
                        
                        st.markdown(answer_text)
                        if sources_list:
                            with st.expander(f"Source References ({len(sources_list)} documents matched)", expanded=False):
                                for s in sources_list:
                                    doc_name = s.get("document", "Document")
                                    page_num = s.get("page")
                                    topic = s.get("topic", "")
                                    sec = s.get("section", "General")
                                    page_str = f" | Page {page_num}" if page_num else ""
                                    topic_str = f" | {topic}" if topic and topic != doc_name else ""
                                    st.markdown(f"- **`{doc_name}`**{page_str} - Section: **{sec}**{topic_str}")

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": answer_text,
                                "sources": sources_list,
                            }
                        )
                    else:
                        err_msg = res.json().get("detail", res.text)
                        err_out = f"Request Failed ({res.status_code}): {err_msg}"
                        st.markdown(err_out)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": err_out, "sources": []}
                        )
                except requests.exceptions.Timeout:
                    timeout_out = "Timeout: The response generation exceeded the time threshold. Please try again."
                    st.markdown(timeout_out)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": timeout_out, "sources": []}
                    )
                except Exception as ex:
                    conn_out = f"Connection Error: {ex}"
                    st.markdown(conn_out)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": conn_out, "sources": []}
                    )