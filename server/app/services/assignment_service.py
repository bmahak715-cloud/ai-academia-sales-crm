from app import db
from app.models.user import User
from app.models.institution import Institution


def get_active_sales_reps():
    return User.query.filter(
        User.is_active == True,
        User.role.in_(["Sales Executive", "Sales Manager"])
    ).all()


def assign_least_leads():
    reps = get_active_sales_reps()
    if not reps:
        admin = User.query.filter_by(role="Admin").first()
        return admin

    best_rep = None
    min_count = float("inf")
    active_statuses = ["New Lead", "Contacted", "Meeting Scheduled",
                       "Proposal Sent", "Negotiation"]

    for rep in reps:
        count = Institution.query.filter(
            Institution.assigned_to_id == rep.id,
            Institution.lead_status.in_(active_statuses)
        ).count()
        if count < min_count:
            min_count = count
            best_rep = rep

    return best_rep


def assign_institution(institution, user_id=None):
    if user_id:
        user = User.query.get(user_id)
        if user and user.is_active:
            institution.assigned_to_id = user.id
            return user
    rep = assign_least_leads()
    if rep:
        institution.assigned_to_id = rep.id
    return rep
