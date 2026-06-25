from datetime import datetime
from app import db


class Institution(db.Model):
    __tablename__ = "institutions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    location = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    institution_type = db.Column(db.String(80), nullable=False)
    student_strength = db.Column(db.Integer, nullable=False)
    program_interest = db.Column(db.String(120), nullable=False)
    lead_source = db.Column(db.String(80), nullable=False)
    lead_status = db.Column(db.String(50), nullable=False, default="New Lead")
    assigned_to_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    previous_partnership = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    ai_analysis = db.relationship(
        "AIAnalysis", backref="institution", uselist=False, cascade="all, delete-orphan"
    )
    follow_ups = db.relationship(
        "FollowUp", backref="institution", lazy="dynamic", cascade="all, delete-orphan"
    )
    meetings = db.relationship(
        "Meeting", backref="institution", lazy="dynamic", cascade="all, delete-orphan"
    )
    communications = db.relationship(
        "Communication", backref="institution", lazy="dynamic", cascade="all, delete-orphan"
    )
    activities = db.relationship(
        "Activity", backref="institution", lazy="dynamic", cascade="all, delete-orphan"
    )

    def to_dict(self, include_ai=True, include_relations=False):
        data = {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "contact_person": self.contact_person,
            "email": self.email,
            "phone": self.phone,
            "institution_type": self.institution_type,
            "student_strength": self.student_strength,
            "program_interest": self.program_interest,
            "lead_source": self.lead_source,
            "lead_status": self.lead_status,
            "assigned_to_id": self.assigned_to_id,
            "assigned_to": self.assigned_user.to_dict() if self.assigned_user else None,
            "previous_partnership": self.previous_partnership,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_ai and self.ai_analysis:
            data["ai_analysis"] = self.ai_analysis.to_dict()
        if include_relations:
            data["follow_ups"] = [f.to_dict() for f in self.follow_ups]
            data["meetings"] = [m.to_dict() for m in self.meetings]
            data["communications"] = [c.to_dict() for c in self.communications]
            data["activities"] = [a.to_dict() for a in self.activities.order_by(
                db.desc("created_at")
            ).limit(20)]
        return data

