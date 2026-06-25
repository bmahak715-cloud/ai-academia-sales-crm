from datetime import datetime
from flask import Blueprint, request, jsonify
from sqlalchemy import or_
from app import db
from app.models.meeting import Meeting
from app.models.institution import Institution
from app.utils.auth import login_required, get_current_user_id
from app.services.activity_service import log_activity
from app.services.notification_service import create_notification, notify_assigned_user

meetings_bp = Blueprint("meetings", __name__)


@meetings_bp.route("", methods=["GET"])
@login_required
def list_meetings():
    params = request.args
    query = Meeting.query

    search = params.get("search", "").strip()
    if search:
        query = query.join(Institution).filter(or_(
            Institution.name.ilike(f"%{search}%"),
            Meeting.contact_person.ilike(f"%{search}%"),
        ))

    if params.get("status"):
        query = query.filter(Meeting.status == params["status"])

    if params.get("institution_id"):
        query = query.filter(Meeting.institution_id == int(params["institution_id"]))

    if params.get("date"):
        try:
            d = datetime.strptime(params["date"], "%Y-%m-%d").date()
            query = query.filter(Meeting.meeting_date == d)
        except ValueError:
            pass

    meetings = query.order_by(Meeting.meeting_date.desc()).all()
    return jsonify({"meetings": [m.to_dict() for m in meetings]})


@meetings_bp.route("", methods=["POST"])
@login_required
def create_meeting():
    data = request.get_json() or {}
    required = ["institution_id", "contact_person", "meeting_date", "meeting_time", "mode"]
    errors = {f: "Required" for f in required if not data.get(f)}
    if errors:
        return jsonify({"error": "Validation failed", "errors": errors}), 400

    institution = Institution.query.get(data["institution_id"])
    if not institution:
        return jsonify({"error": "Institution not found"}), 404

    try:
        mdate = datetime.strptime(data["meeting_date"], "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid meeting_date"}), 400

    meeting = Meeting(
        institution_id=data["institution_id"],
        contact_person=data["contact_person"],
        meeting_date=mdate,
        meeting_time=data["meeting_time"],
        mode=data["mode"],
        location_or_link=data.get("location_or_link", ""),
        agenda=data.get("agenda", ""),
        status="Scheduled",
        assigned_to_id=data.get("assigned_to_id") or institution.assigned_to_id,
    )
    db.session.add(meeting)
    db.session.commit()

    log_activity(
        institution.id, "Meeting scheduled",
        f"Meeting scheduled on {mdate.isoformat()} at {meeting.meeting_time}.",
        get_current_user_id()
    )
    notify_assigned_user(
        institution, "Meeting scheduled",
        f"Meeting scheduled with {institution.name} on {mdate.isoformat()}"
    )

    update_status = data.get("update_lead_status", False)
    if update_status:
        institution.lead_status = "Meeting Scheduled"
        db.session.commit()
        log_activity(
            institution.id, "Lead status changed",
            "Status updated to Meeting Scheduled after scheduling meeting.",
            get_current_user_id()
        )

    return jsonify({
        "meeting": meeting.to_dict(),
        "ask_status_update": not update_status,
    }), 201


@meetings_bp.route("/<int:id>", methods=["PUT"])
@login_required
def update_meeting(id):
    meeting = Meeting.query.get_or_404(id)
    data = request.get_json() or {}

    for field in ["contact_person", "meeting_time", "mode", "location_or_link",
                  "agenda", "meeting_notes", "status"]:
        if data.get(field):
            setattr(meeting, field, data[field])

    if data.get("meeting_date"):
        try:
            meeting.meeting_date = datetime.strptime(data["meeting_date"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid meeting_date"}), 400

    if data.get("assigned_to_id"):
        meeting.assigned_to_id = data["assigned_to_id"]

    db.session.commit()
    return jsonify({"meeting": meeting.to_dict()})


@meetings_bp.route("/<int:id>", methods=["DELETE"])
@login_required
def delete_meeting(id):
    meeting = Meeting.query.get_or_404(id)
    meeting.status = "Cancelled"
    db.session.commit()
    return jsonify({"message": "Meeting cancelled", "meeting": meeting.to_dict()})


@meetings_bp.route("/<int:id>/complete", methods=["PATCH"])
@login_required
def complete_meeting(id):
    meeting = Meeting.query.get_or_404(id)
    data = request.get_json() or {}

    meeting.status = "Completed"
    meeting.meeting_notes = data.get("meeting_notes", meeting.meeting_notes)
    meeting.requirements = data.get("requirements", "")
    meeting.budget_discussion = data.get("budget_discussion", "")
    meeting.expected_dates = data.get("expected_dates", "")
    meeting.next_step = data.get("next_step", "")

    db.session.commit()

    log_activity(
        meeting.institution_id, "Meeting completed",
        f"Meeting with {meeting.institution.name} completed.",
        get_current_user_id()
    )
    return jsonify({"meeting": meeting.to_dict()})
