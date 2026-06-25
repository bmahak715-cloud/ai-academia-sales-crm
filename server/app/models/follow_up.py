from datetime import datetime
from app import db


class FollowUp(db.Model):
    __tablename__ = "follow_ups"

    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.Integer, db.ForeignKey("institutions.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    task_type = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.Date, nullable=False)
    priority = db.Column(db.String(20), nullable=False, default="Medium")
    assigned_to_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    status = db.Column(db.String(30), nullable=False, default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    def effective_status(self):
        from datetime import date
        if self.status == "Completed":
            return "Completed"
        if self.due_date and self.due_date < date.today():
            return "Overdue"
        return self.status

    def to_dict(self):
        return {
            "id": self.id,
            "institution_id": self.institution_id,
            "institution_name": self.institution.name if self.institution else None,
            "title": self.title,
            "task_type": self.task_type,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "priority": self.priority,
            "assigned_to_id": self.assigned_to_id,
            "assigned_to": self.assigned_user.to_dict() if self.assigned_user else None,
            "status": self.effective_status(),
            "raw_status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

