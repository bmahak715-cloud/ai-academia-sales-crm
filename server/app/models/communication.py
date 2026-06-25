from datetime import datetime
from app import db


class Communication(db.Model):
    __tablename__ = "communications"

    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.Integer, db.ForeignKey("institutions.id"), nullable=False)
    message_type = db.Column(db.String(50), nullable=False)  # outreach, follow_up
    subject = db.Column(db.String(200), nullable=True)
    body = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default="Draft")  # Draft, Sent
    sent_at = db.Column(db.DateTime, nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "institution_id": self.institution_id,
            "institution_name": self.institution.name if self.institution else None,
            "message_type": self.message_type,
            "subject": self.subject,
            "body": self.body,
            "status": self.status,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "created_by_id": self.created_by_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

