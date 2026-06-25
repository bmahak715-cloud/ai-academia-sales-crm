from datetime import datetime
from app import db


class Meeting(db.Model):
    __tablename__ = "meetings"

    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.Integer, db.ForeignKey("institutions.id"), nullable=False)
    contact_person = db.Column(db.String(120), nullable=False)
    meeting_date = db.Column(db.Date, nullable=False)
    meeting_time = db.Column(db.String(20), nullable=False)
    mode = db.Column(db.String(20), nullable=False)
    location_or_link = db.Column(db.String(300), nullable=True)
    agenda = db.Column(db.Text, nullable=True)
    meeting_notes = db.Column(db.Text, nullable=True)
    requirements = db.Column(db.Text, nullable=True)
    budget_discussion = db.Column(db.Text, nullable=True)
    expected_dates = db.Column(db.Text, nullable=True)
    next_step = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), nullable=False, default="Scheduled")
    assigned_to_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "institution_id": self.institution_id,
            "institution_name": self.institution.name if self.institution else None,
            "contact_person": self.contact_person,
            "meeting_date": self.meeting_date.isoformat() if self.meeting_date else None,
            "meeting_time": self.meeting_time,
            "mode": self.mode,
            "location_or_link": self.location_or_link,
            "agenda": self.agenda,
            "meeting_notes": self.meeting_notes,
            "requirements": self.requirements,
            "budget_discussion": self.budget_discussion,
            "expected_dates": self.expected_dates,
            "next_step": self.next_step,
            "status": self.status,
            "assigned_to_id": self.assigned_to_id,
            "assigned_to": self.assigned_user.to_dict() if self.assigned_user else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

