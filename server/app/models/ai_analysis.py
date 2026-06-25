from datetime import datetime
from app import db


class AIAnalysis(db.Model):
    __tablename__ = "ai_analyses"

    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.Integer, db.ForeignKey("institutions.id"), nullable=False, unique=True)
    score = db.Column(db.Integer, default=0)
    priority = db.Column(db.String(20), default="Low")
    reason = db.Column(db.Text, nullable=True)
    next_best_action = db.Column(db.Text, nullable=True)
    outreach_message = db.Column(db.Text, nullable=True)
    follow_up_suggestions = db.Column(db.Text, nullable=True)  # JSON string
    status = db.Column(db.String(30), default="Pending")  # Pending, Completed, Failed
    analyzed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        import json
        suggestions = []
        if self.follow_up_suggestions:
            try:
                suggestions = json.loads(self.follow_up_suggestions)
            except (json.JSONDecodeError, TypeError):
                suggestions = []
        return {
            "id": self.id,
            "institution_id": self.institution_id,
            "score": self.score,
            "priority": self.priority,
            "reason": self.reason,
            "next_best_action": self.next_best_action,
            "outreach_message": self.outreach_message,
            "follow_up_suggestions": suggestions,
            "status": self.status,
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None,
        }

