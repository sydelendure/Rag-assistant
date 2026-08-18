from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch


DOCUMENTS_DIR = Path("documents")
DOCUMENTS_DIR.mkdir(exist_ok=True)


styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "DocumentTitle",
    parent=styles["Title"],
    alignment=TA_CENTER,
    spaceAfter=20,
)

heading_style = ParagraphStyle(
    "Heading",
    parent=styles["Heading2"],
    spaceBefore=12,
    spaceAfter=8,
)

body_style = ParagraphStyle(
    "Body",
    parent=styles["BodyText"],
    leading=16,
    spaceAfter=8,
)


policies = {
    "Leave_Policy.pdf": {
        "title": "NexaTech Solutions - Leave Policy",
        "sections": [
            (
                "1. Purpose",
                "This policy defines the leave entitlements and procedures applicable "
                "to employees of NexaTech Solutions."
            ),
            (
                "2. Annual Leave",
                "Full-time employees are entitled to 20 days of annual leave per "
                "calendar year. Annual leave should normally be requested at least "
                "three working days in advance and requires manager approval."
            ),
            (
                "3. Sick Leave",
                "Employees are entitled to 10 days of sick leave per calendar year. "
                "For absences exceeding two consecutive working days, employees may "
                "be required to provide appropriate medical documentation."
            ),
            (
                "4. Casual Leave",
                "Employees may take up to 6 days of casual leave per calendar year "
                "for personal or unforeseen circumstances."
            ),
            (
                "5. Leave Carry Forward",
                "Employees may carry forward a maximum of 5 unused annual leave days "
                "into the following calendar year. Unused casual leave cannot be carried forward."
            ),
            (
                "6. Leave Approval",
                "Employees must submit leave requests through the company's employee "
                "portal. Leave is considered approved only after the reporting manager "
                "has accepted the request."
            ),
            (
                "7. Public Holidays",
                "Public holidays declared by NexaTech Solutions are separate from the "
                "employee's annual leave entitlement."
            ),
        ],
    },

    "Work_From_Home_Policy.pdf": {
        "title": "NexaTech Solutions - Work From Home Policy",
        "sections": [
            (
                "1. Purpose",
                "This policy defines the conditions under which eligible employees "
                "may work remotely."
            ),
            (
                "2. Eligibility",
                "Employees who have completed their probation period may request "
                "regular work-from-home arrangements, subject to role suitability "
                "and manager approval."
            ),
            (
                "3. Remote Working Limit",
                "Eligible employees may work from home for a maximum of 2 working "
                "days per week unless a specific exception has been approved."
            ),
            (
                "4. Manager Approval",
                "Employees must obtain approval from their reporting manager before "
                "working remotely. Approval may depend on project requirements, "
                "team availability, and business needs."
            ),
            (
                "5. Working Hours",
                "Employees working remotely must follow their assigned working hours "
                "and remain available through approved communication channels."
            ),
            (
                "6. Equipment",
                "Employees are responsible for maintaining a suitable work environment "
                "and protecting company equipment and confidential information while "
                "working remotely."
            ),
            (
                "7. Exceptions",
                "Temporary exceptions may be granted for medical, family, travel, "
                "or other exceptional circumstances with appropriate approval."
            ),
        ],
    },

    "Travel_Policy.pdf": {
        "title": "NexaTech Solutions - Travel Policy",
        "sections": [
            (
                "1. Purpose",
                "This policy establishes guidelines for employees travelling for "
                "official company business."
            ),
            (
                "2. Travel Approval",
                "Business travel must be approved by the employee's manager before "
                "tickets or accommodation are booked."
            ),
            (
                "3. Transportation",
                "Employees should select economical and practical transportation. "
                "Domestic flights may be booked when travel by air provides a reasonable "
                "time advantage."
            ),
            (
                "4. Accommodation",
                "Employees may claim reasonable hotel accommodation costs within the "
                "company's approved travel limits."
            ),
            (
                "5. Meals",
                "Employees travelling for business may claim eligible meal expenses "
                "within the applicable daily allowance."
            ),
            (
                "6. Local Transportation",
                "Reasonable taxi, public transportation, or approved ride-service "
                "expenses incurred for business purposes may be reimbursed."
            ),
            (
                "7. Travel Documentation",
                "Employees must retain receipts and supporting documentation for "
                "reimbursable travel expenses."
            ),
        ],
    },

    "Expense_Reimbursement_Policy.pdf": {
        "title": "NexaTech Solutions - Expense Reimbursement Policy",
        "sections": [
            (
                "1. Purpose",
                "This policy defines the expenses that employees may claim for "
                "legitimate business purposes."
            ),
            (
                "2. Eligible Expenses",
                "Eligible expenses may include approved business travel, transportation, "
                "hotel accommodation, meals during business travel, and other expenses "
                "specifically approved by the company."
            ),
            (
                "3. Receipts",
                "Employees must provide valid receipts or equivalent supporting "
                "documentation for reimbursable expenses."
            ),
            (
                "4. Submission Deadline",
                "Expense claims should be submitted within 15 calendar days after "
                "completion of the business activity."
            ),
            (
                "5. Approval",
                "Expense claims must be reviewed and approved by the employee's "
                "reporting manager before reimbursement is processed."
            ),
            (
                "6. Non-Reimbursable Expenses",
                "Personal purchases, entertainment expenses without business justification, "
                "traffic fines, and expenses exceeding approved limits without prior "
                "authorization are generally not reimbursable."
            ),
        ],
    },

    "Attendance_Policy.pdf": {
        "title": "NexaTech Solutions - Attendance Policy",
        "sections": [
            (
                "1. Working Hours",
                "The standard working schedule is Monday through Friday, from 9:00 AM "
                "to 6:00 PM, including a one-hour lunch break."
            ),
            (
                "2. Attendance Requirement",
                "Employees are expected to maintain regular attendance and be available "
                "during their assigned working hours."
            ),
            (
                "3. Late Arrival",
                "Employees who expect to arrive late should inform their reporting "
                "manager as early as reasonably possible."
            ),
            (
                "4. Early Departure",
                "Employees requiring an early departure should obtain manager approval "
                "unless there is an emergency."
            ),
            (
                "5. Absence Reporting",
                "Unexpected absences should be reported to the reporting manager "
                "before the employee's scheduled start time whenever possible."
            ),
            (
                "6. Attendance Exceptions",
                "Approved leave, business travel, and approved work-from-home days "
                "are considered authorized attendance exceptions."
            ),
        ],
    },

    "Employee_Benefits.pdf": {
        "title": "NexaTech Solutions - Employee Benefits",
        "sections": [
            (
                "1. Health Insurance",
                "Eligible full-time employees are provided access to the company's "
                "group health insurance program subject to the terms of the insurance plan."
            ),
            (
                "2. Wellness Benefits",
                "Employees may participate in company-sponsored wellness initiatives "
                "and programs offered during the year."
            ),
            (
                "3. Learning and Development",
                "Employees may request access to approved training courses, technical "
                "certifications, and professional development programs."
            ),
            (
                "4. Internet Allowance",
                "Eligible employees working under approved remote arrangements may "
                "receive an internet allowance subject to company limits."
            ),
            (
                "5. Employee Discounts",
                "Employees may receive discounts through selected company partnerships "
                "and benefit programs."
            ),
            (
                "6. Eligibility",
                "Eligibility for specific benefits may depend on employment status, "
                "tenure, and the terms of the relevant benefit program."
            ),
        ],
    },

    "Code_of_Conduct.pdf": {
        "title": "NexaTech Solutions - Code of Conduct",
        "sections": [
            (
                "1. Professional Behaviour",
                "Employees are expected to treat colleagues, customers, partners, "
                "and other stakeholders with professionalism, respect, and fairness."
            ),
            (
                "2. Confidentiality",
                "Employees must protect confidential company information and must not "
                "share sensitive information with unauthorized individuals."
            ),
            (
                "3. Conflict of Interest",
                "Employees must disclose situations where personal, financial, or "
                "external interests could influence their professional responsibilities."
            ),
            (
                "4. Workplace Harassment",
                "NexaTech Solutions does not tolerate harassment, discrimination, "
                "bullying, intimidation, or other inappropriate workplace behaviour."
            ),
            (
                "5. Company Resources",
                "Company systems, devices, software, and other resources must be used "
                "responsibly and primarily for authorized business purposes."
            ),
            (
                "6. Gifts and Hospitality",
                "Employees must not accept gifts or hospitality that could improperly "
                "influence business decisions or create a conflict of interest."
            ),
            (
                "7. Violations",
                "Violations of this Code of Conduct may result in corrective or "
                "disciplinary action in accordance with company procedures."
            ),
        ],
    },
}


def create_pdf(filename, title, sections):
    file_path = DOCUMENTS_DIR / filename

    document = SimpleDocTemplate(
        str(file_path),
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50,
    )

    content = []

    content.append(Paragraph(title, title_style))
    content.append(
        Paragraph(
            "NexaTech Solutions | Internal Company Policy",
            body_style,
        )
    )
    content.append(Spacer(1, 10))

    for heading, text in sections:
        content.append(Paragraph(heading, heading_style))
        content.append(Paragraph(text, body_style))

    document.build(content)

    print(f"Created: {file_path}")


for filename, policy in policies.items():
    create_pdf(
        filename,
        policy["title"],
        policy["sections"],
    )

print("\nAll policy documents created successfully.")