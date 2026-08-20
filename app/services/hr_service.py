# Imports & Dependencies #
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Persistent Ticket Storage Path #
TICKETS_FILE = Path("data/hr_tickets.json")


# Storage Directory & JSON File Initializer #
def _ensure_storage():
    """Ensure data directory and tickets storage file exist."""
    TICKETS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not TICKETS_FILE.exists():
        TICKETS_FILE.write_text("[]", encoding="utf-8")


# Create & Persist HR Support Ticket #
def create_ticket(
    subject: str,
    message: str,
    category: str = "Policy Clarification",
    urgency: str = "Normal",
    name: Optional[str] = "Anonymous Employee",
    email: Optional[str] = "anonymous@company.internal",
    is_anonymous: bool = False,
    source_question: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create and store a new HR support ticket.
    """
    _ensure_storage()

    # Generate Unique Ticket Reference ID (e.g. HR-2026-7492) #
    random_suffix = str(uuid.uuid4().hex[:4]).upper()
    current_year = datetime.now().year
    ticket_id = f"HR-{current_year}-{random_suffix}"

    # Structured Ticket Record #
    ticket_record = {
        "ticket_id": ticket_id,
        "created_at": datetime.now().isoformat(),
        "status": "Open",
        "category": category,
        "urgency": urgency,
        "is_anonymous": is_anonymous,
        "employee_name": "Anonymous" if is_anonymous else (name or "Employee"),
        "employee_email": "confidential@company.internal" if is_anonymous else (email or ""),
        "subject": subject.strip(),
        "message": message.strip(),
        "source_question": source_question,
        "assigned_to": "HR Operations Team",
    }

    # Save to JSON Storage #
    try:
        content = TICKETS_FILE.read_text(encoding="utf-8")
        tickets: List[Dict[str, Any]] = json.loads(content) if content else []
    except Exception:
        tickets = []

    tickets.insert(0, ticket_record)
    TICKETS_FILE.write_text(json.dumps(tickets, indent=2), encoding="utf-8")

    return ticket_record


# Retrieve All Stored HR Tickets #
def get_all_tickets() -> List[Dict[str, Any]]:
    """Retrieve all stored HR tickets."""
    _ensure_storage()
    try:
        content = TICKETS_FILE.read_text(encoding="utf-8")
        return json.loads(content) if content else []
    except Exception:
        return []


# Sensitive Keyword & Unresolved Answer Escalation Detector #
def is_sensitive_or_unresolved(question: str, answer: str) -> bool:
    """
    Determine if a user question or generated answer requires HR escalation.
    """
    q_lower = question.lower()
    a_lower = answer.lower()

    # Rule 1: Unresolved or Missing Policy Signals in Answer #
    unresolved_signals = [
        "could not find",
        "cannot find",
        "not mentioned",
        "not contain",
        "do not contain",
        "does not contain",
        "no information",
        "does not specify",
        "do not specify",
        "no policy",
        "no guidance",
        "no rules",
        "not covered",
        "not stated",
        "not found",
        "unclear in the provided",
        "not addressed",
        "not available in the",
    ]
    for signal in unresolved_signals:
        if signal in a_lower:
            return True

    # Rule 2: Workplace Grievance & Sensitive Query Keywords #
    sensitive_keywords = [
        "harass",
        "discrimina",
        "retaliat",
        "complain",
        "grievance",
        "dispute",
        "whistleblow",
        "emergency",
        "mental health",
        "salary error",
        "payroll mistake",
        "pay discrepancy",
        "medical exception",
        "leave exception",
        "posh",
        "favouritism",
        "unfair",
        "maternity exception",
        "paternity exception",
        "contract breach",
        "severance",
        "unpaid bonus",
        "probation extension",
        "resignation dispute",
        "pet",
        "dog",
        "animal",
        "reimbursement rejected",
    ]
    for kw in sensitive_keywords:
        if kw in q_lower:
            return True

    return False
