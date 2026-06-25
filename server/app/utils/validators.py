import re

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

INSTITUTION_TYPES = [
    "Private University", "Government University", "Engineering College",
    "Management College", "Degree College", "Training Institute", "Other"
]

PROGRAM_INTERESTS = [
    "Artificial Intelligence", "Machine Learning", "Data Science",
    "Web Development", "Cloud Computing", "Cybersecurity",
    "Placement Training", "Faculty Development Program", "Workshop", "Other"
]

LEAD_SOURCES = [
    "Website", "Referral", "LinkedIn", "Education Conference",
    "Email Campaign", "Existing Partner", "Manual Research", "Other"
]

LEAD_STATUSES = [
    "New Lead", "Contacted", "Meeting Scheduled", "Proposal Sent",
    "Negotiation", "Closed-Won", "Closed-Lost"
]

TASK_TYPES = [
    "Phone Call", "Email Follow-up", "Send Brochure", "Schedule Meeting",
    "Proposal Follow-up", "Negotiation Follow-up", "General Follow-up"
]

PRIORITIES = ["High", "Medium", "Low"]

FOLLOW_UP_STATUSES = ["Pending", "Completed", "Overdue"]

MEETING_MODES = ["Online", "Offline"]

MEETING_STATUSES = ["Scheduled", "Completed", "Cancelled"]


def validate_email(email):
    return EMAIL_REGEX.match(email) is not None


def validate_phone(phone):
    digits = re.sub(r"\D", "", phone)
    return 10 <= len(digits) <= 15


def validate_institution_data(data, institution_id=None):
    errors = {}
    required = [
        "name", "location", "contact_person", "email", "phone",
        "institution_type", "student_strength", "program_interest",
        "lead_source", "lead_status"
    ]
    for field in required:
        if not data.get(field):
            errors[field] = "This field is required"

    if data.get("email") and not validate_email(data["email"]):
        errors["email"] = "Invalid email format"

    if data.get("phone") and not validate_phone(data["phone"]):
        errors["phone"] = "Phone must be 10-15 digits"

    if data.get("student_strength") is not None:
        try:
            strength = int(data["student_strength"])
            if strength <= 0:
                errors["student_strength"] = "Must be a positive number"
        except (ValueError, TypeError):
            errors["student_strength"] = "Must be a positive number"

    if data.get("institution_type") and data["institution_type"] not in INSTITUTION_TYPES:
        errors["institution_type"] = "Invalid institution type"

    if data.get("program_interest") and data["program_interest"] not in PROGRAM_INTERESTS:
        errors["program_interest"] = "Invalid program interest"

    if data.get("lead_source") and data["lead_source"] not in LEAD_SOURCES:
        errors["lead_source"] = "Invalid lead source"

    if data.get("lead_status") and data["lead_status"] not in LEAD_STATUSES:
        errors["lead_status"] = "Invalid lead status"

    return errors


def score_to_priority(score):
    if score >= 80:
        return "High"
    if score >= 50:
        return "Medium"
    return "Low"
