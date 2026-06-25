from datetime import datetime, date
from flask import Blueprint, request, jsonify
from sqlalchemy import or_
from app import db
from app.models.follow_up import FollowUp
from app.models.institution import Institution
from app.models.user import User
from app.utils.auth import login_required, get_current_user_id
from app.services.activity_service import log_activity
from app.services.notification_service import create_notification

follow_ups_bp = Blueprint("follow_ups", __name__)


@follow_ups_bp.route("", methods=["GET"])
@login_required
def list_follow_ups():
    params = request.args
    query = FollowUp.query

    search = params.get("search", "").strip()
    if search:
        query = query.join(Institution).filter(or_(
            FollowUp.title.ilike(f"%{search}%"),
            Institution.name.ilike(f"%{search}%"),
        ))

    if params.get("status"):
        status_filter = params["status"]
        if status_filter == "Overdue":
            query = query.filter(
                FollowUp.status != "Completed",
                FollowUp.due_date < date.today()
            )
        elif status_filter == "Due Today":
            query = query.filter(
                FollowUp.status != "Completed",
                FollowUp.due_date == date.today()
            )
        elif status_filter == "Upcoming":
            query = query.filter(
                FollowUp.status != "Completed",
                FollowUp.due_date > date.today()
            )
        else:
            query = query.filter(FollowUp.status == status_filter)

    if params.get("priority"):
        query = query.filter(FollowUp.priority == params["priority"])

    if params.get("assigned_to_id"):
        query = query.filter(FollowUp.assigned_to_id == int(params["assigned_to_id"]))

    if params.get("view") == "due_today":
        query = query.filter(
            FollowUp.status != "Completed",
            FollowUp.due_date == date.today()
        )
    elif params.get("view") == "overdue":
        query = query.filter(
            FollowUp.status != "Completed",
            FollowUp.due_date < date.today()
        )
    elif params.get("view") == "upcoming":
        query = query.filter(
            FollowUp.status != "Completed",
            FollowUp.due_date > date.today()
        )
    elif params.get("view") == "completed":
        query = query.filter(FollowUp.status == "Completed")

    follow_ups = query.order_by(FollowUp.due_date).all()
    return jsonify({"follow_ups": [f.to_dict() for f in follow_ups]})


@follow_ups_bp.route("", methods=["POST"])
@login_required
def create_follow_up():
    data = request.get_json() or {}
    required = ["institution_id", "title", "task_type", "due_date", "priority"]
    errors = {f: "Required" for f in required if not data.get(f)}
    if errors:
        return jsonify({"error": "Validation failed", "errors": errors}), 400

    institution = Institution.query.get(data["institution_id"])
    if not institution:
        return jsonify({"error": "Institution not found"}), 404

    try:
        due = datetime.strptime(data["due_date"], "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid due_date format. Use YYYY-MM-DD"}), 400

    fu = FollowUp(
        institution_id=data["institution_id"],
        title=data["title"],
        task_type=data["task_type"],
        description=data.get("description", ""),
        due_date=due,
        priority=data["priority"],
        assigned_to_id=data.get("assigned_to_id") or institution.assigned_to_id,
        status="Pending",
    )
    db.session.add(fu)
    db.session.commit()

    log_activity(
        institution.id, "Follow-up created",
        f"Task '{fu.title}' created, due {due.isoformat()}.",
        get_current_user_id()
    )
    return jsonify({"follow_up": fu.to_dict()}), 201


@follow_ups_bp.route("/<int:id>", methods=["PUT"])
@login_required
def update_follow_up(id):
    fu = FollowUp.query.get_or_404(id)
    data = request.get_json() or {}

    if data.get("title"):
        fu.title = data["title"]
    if data.get("task_type"):
        fu.task_type = data["task_type"]
    if data.get("description"):
        fu.description = data["description"]
    if data.get("due_date"):
        try:
            fu.due_date = datetime.strptime(data["due_date"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid due_date"}), 400
    if data.get("priority"):
        fu.priority = data["priority"]
    if data.get("assigned_to_id"):
        fu.assigned_to_id = data["assigned_to_id"]
    if data.get("status"):
        fu.status = data["status"]

    db.session.commit()
    return jsonify({"follow_up": fu.to_dict()})


@follow_ups_bp.route("/<int:id>", methods=["DELETE"])
@login_required
def delete_follow_up(id):
    fu = FollowUp.query.get_or_404(id)
    db.session.delete(fu)
    db.session.commit()
    return jsonify({"message": "Follow-up deleted"})


@follow_ups_bp.route("/<int:id>/complete", methods=["PATCH"])
@login_required
def complete_follow_up(id):
    fu = FollowUp.query.get_or_404(id)
    fu.status = "Completed"
    fu.completed_at = datetime.utcnow()
    db.session.commit()

    log_activity(
        fu.institution_id, "Follow-up completed",
        f"Task '{fu.title}' completed.",
        get_current_user_id()
    )
    create_notification(
        fu.assigned_to_id or get_current_user_id(),
        "Task completed",
        f"Follow-up '{fu.title}' marked complete.",
        fu.institution_id
    )
    return jsonify({"follow_up": fu.to_dict()})
