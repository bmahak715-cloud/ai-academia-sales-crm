from datetime import datetime, date, timedelta
from flask import Blueprint, request, jsonify
from sqlalchemy import or_, desc, asc
from app import db
from app.models.institution import Institution
from app.models.ai_analysis import AIAnalysis
from app.models.follow_up import FollowUp
from app.models.user import User
from app.utils.auth import login_required, get_current_user_id
from app.utils.validators import validate_institution_data
from app.services.ai_service import analyze_lead, save_analysis, regenerate_outreach
from app.services.assignment_service import assign_institution
from app.services.activity_service import log_activity
from app.services.notification_service import create_notification, notify_assigned_user

institutions_bp = Blueprint("institutions", __name__)


def _apply_filters(query, params):
    search = params.get("search", "").strip()
    if search:
        query = query.filter(or_(
            Institution.name.ilike(f"%{search}%"),
            Institution.contact_person.ilike(f"%{search}%"),
            Institution.email.ilike(f"%{search}%"),
        ))

    if params.get("status"):
        query = query.filter(Institution.lead_status == params["status"])

    if params.get("institution_type"):
        query = query.filter(Institution.institution_type == params["institution_type"])

    if params.get("lead_source"):
        query = query.filter(Institution.lead_source == params["lead_source"])

    if params.get("program_interest"):
        query = query.filter(Institution.program_interest == params["program_interest"])

    if params.get("assigned_to_id"):
        query = query.filter(Institution.assigned_to_id == int(params["assigned_to_id"]))

    if params.get("ai_priority"):
        query = query.join(AIAnalysis).filter(AIAnalysis.priority == params["ai_priority"])

    sort = params.get("sort", "newest")
    if sort == "newest":
        query = query.order_by(desc(Institution.created_at))
    elif sort == "name":
        query = query.order_by(asc(Institution.name))
    elif sort == "ai_score":
        query = query.join(AIAnalysis, isouter=True).order_by(desc(AIAnalysis.score))
    elif sort == "follow_up_date":
        query = query.order_by(desc(Institution.updated_at))

    return query


@institutions_bp.route("", methods=["GET"])
@login_required
def list_institutions():
    params = request.args
    query = Institution.query
    query = _apply_filters(query, params)
    institutions = query.all()
    return jsonify({"institutions": [i.to_dict() for i in institutions]})


@institutions_bp.route("/<int:id>", methods=["GET"])
@login_required
def get_institution(id):
    institution = Institution.query.get_or_404(id)
    return jsonify({"institution": institution.to_dict(include_relations=True)})


@institutions_bp.route("", methods=["POST"])
@login_required
def create_institution():
    data = request.get_json() or {}
    errors = validate_institution_data(data)
    if errors:
        return jsonify({"error": "Validation failed", "errors": errors}), 400

    dup_email = Institution.query.filter_by(email=data["email"].strip().lower()).first()
    if dup_email:
        return jsonify({"error": "Duplicate email", "errors": {"email": "Email already exists"}}), 400

    dup_name = Institution.query.filter(
        Institution.name.ilike(data["name"].strip())
    ).first()
    warnings = {}
    if dup_name:
        warnings["name"] = "An institution with a similar name already exists"

    institution = Institution(
        name=data["name"].strip(),
        location=data["location"].strip(),
        contact_person=data["contact_person"].strip(),
        email=data["email"].strip().lower(),
        phone=data["phone"].strip(),
        institution_type=data["institution_type"],
        student_strength=int(data["student_strength"]),
        program_interest=data["program_interest"],
        lead_source=data["lead_source"],
        lead_status=data.get("lead_status", "New Lead"),
        previous_partnership=bool(data.get("previous_partnership", False)),
        notes=data.get("notes", ""),
    )

    assigned = assign_institution(institution, data.get("assigned_to_id"))
    db.session.add(institution)
    db.session.flush()

    analysis = AIAnalysis(institution_id=institution.id, status="Pending")
    db.session.add(analysis)
    db.session.commit()

    log_activity(
        institution.id, "Lead created",
        f"New lead {institution.name} was created.",
        get_current_user_id()
    )

    if assigned:
        create_notification(
            assigned.id, "Lead assigned",
            f"You have been assigned lead: {institution.name}",
            institution.id
        )
        log_activity(
            institution.id, "Sales owner assigned",
            f"{assigned.name} assigned to {institution.name}.",
            get_current_user_id()
        )

    create_notification(
        get_current_user_id(), "Lead created",
        f"New lead created: {institution.name}",
        institution.id
    )

    result, ai_status = analyze_lead(institution)
    analysis = save_analysis(institution, result, ai_status)

    if ai_status == "Completed":
        create_notification(
            institution.assigned_to_id or get_current_user_id(),
            "AI analysis completed",
            f"AI analysis completed for {institution.name} (Score: {analysis.score})",
            institution.id
        )
        log_activity(
            institution.id, "AI analysis generated",
            f"AI score: {analysis.score}, Priority: {analysis.priority}",
            get_current_user_id()
        )
    else:
        create_notification(
            institution.assigned_to_id or get_current_user_id(),
            "AI analysis failed",
            f"AI analysis failed for {institution.name}. Retry available.",
            institution.id
        )
        log_activity(
            institution.id, "AI analysis failed",
            f"AI analysis failed for {institution.name}.",
            get_current_user_id()
        )

    due = date.today() + timedelta(days=1)
    follow_up = FollowUp(
        institution_id=institution.id,
        title=f"Initial contact - {institution.name}",
        task_type="Phone Call",
        description=analysis.next_best_action or "Make initial contact with the institution.",
        due_date=due,
        priority=analysis.priority if analysis.priority else "Medium",
        assigned_to_id=institution.assigned_to_id,
        status="Pending",
    )
    db.session.add(follow_up)
    db.session.commit()

    log_activity(
        institution.id, "Follow-up created",
        f"Initial follow-up task created, due {due.isoformat()}.",
        get_current_user_id()
    )

    institution = Institution.query.get(institution.id)
    response = {"institution": institution.to_dict(), "warnings": warnings}
    if ai_status == "Failed":
        response["ai_error"] = "AI analysis failed. You can retry from lead details."
    return jsonify(response), 201


@institutions_bp.route("/<int:id>", methods=["PUT"])
@login_required
def update_institution(id):
    institution = Institution.query.get_or_404(id)
    data = request.get_json() or {}
    errors = validate_institution_data(data)
    if errors:
        return jsonify({"error": "Validation failed", "errors": errors}), 400

    if data["email"].strip().lower() != institution.email:
        dup = Institution.query.filter_by(email=data["email"].strip().lower()).first()
        if dup:
            return jsonify({"error": "Duplicate email", "errors": {"email": "Email already exists"}}), 400

    institution.name = data["name"].strip()
    institution.location = data["location"].strip()
    institution.contact_person = data["contact_person"].strip()
    institution.email = data["email"].strip().lower()
    institution.phone = data["phone"].strip()
    institution.institution_type = data["institution_type"]
    institution.student_strength = int(data["student_strength"])
    institution.program_interest = data["program_interest"]
    institution.lead_source = data["lead_source"]
    institution.lead_status = data["lead_status"]
    institution.previous_partnership = bool(data.get("previous_partnership", False))
    institution.notes = data.get("notes", "")
    institution.updated_at = datetime.utcnow()

    if data.get("assigned_to_id"):
        institution.assigned_to_id = int(data["assigned_to_id"])

    db.session.commit()
    log_activity(institution.id, "Lead edited", f"Lead {institution.name} was updated.", get_current_user_id())
    return jsonify({"institution": institution.to_dict()})


@institutions_bp.route("/<int:id>", methods=["DELETE"])
@login_required
def delete_institution(id):
    institution = Institution.query.get_or_404(id)
    name = institution.name
    # Cascade deletes related records via model relationships
    db.session.delete(institution)
    db.session.commit()
    log_activity(None, "Lead deleted", f"Lead {name} was deleted.", get_current_user_id())
    return jsonify({"message": f"Institution {name} and related records deleted."})


@institutions_bp.route("/<int:id>/status", methods=["PATCH"])
@login_required
def update_status(id):
    institution = Institution.query.get_or_404(id)
    data = request.get_json() or {}
    new_status = data.get("lead_status")
    if not new_status:
        return jsonify({"error": "lead_status is required"}), 400

    old_status = institution.lead_status
    institution.lead_status = new_status
    institution.updated_at = datetime.utcnow()
    db.session.commit()

    log_activity(
        institution.id, "Lead status changed",
        f"Status changed from {old_status} to {new_status}.",
        get_current_user_id()
    )
    notify_assigned_user(
        institution, "Lead status changed",
        f"{institution.name} status: {old_status} → {new_status}"
    )
    return jsonify({"institution": institution.to_dict()})


@institutions_bp.route("/<int:id>/assign", methods=["PATCH"])
@login_required
def assign_owner(id):
    institution = Institution.query.get_or_404(id)
    data = request.get_json() or {}
    user_id = data.get("assigned_to_id")
    if not user_id:
        return jsonify({"error": "assigned_to_id is required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    institution.assigned_to_id = user.id
    institution.updated_at = datetime.utcnow()
    db.session.commit()

    create_notification(
        user.id, "Lead assigned",
        f"You have been assigned: {institution.name}",
        institution.id
    )
    log_activity(
        institution.id, "Sales owner assigned",
        f"{user.name} assigned to {institution.name}.",
        get_current_user_id()
    )
    return jsonify({"institution": institution.to_dict()})


@institutions_bp.route("/<int:id>/analyze", methods=["POST"])
@login_required
def retry_analysis(id):
    institution = Institution.query.get_or_404(id)
    result, ai_status = analyze_lead(institution)
    analysis = save_analysis(institution, result, ai_status)

    if ai_status == "Completed":
        create_notification(
            institution.assigned_to_id or get_current_user_id(),
            "AI analysis completed",
            f"AI analysis completed for {institution.name} (Score: {analysis.score})",
            institution.id
        )
        log_activity(
            institution.id, "AI analysis generated",
            f"AI score: {analysis.score}, Priority: {analysis.priority}",
            get_current_user_id()
        )
        return jsonify({"institution": institution.to_dict(), "message": "Analysis completed"})
    else:
        create_notification(
            institution.assigned_to_id or get_current_user_id(),
            "AI analysis failed",
            f"AI analysis failed for {institution.name}.",
            institution.id
        )
        log_activity(
            institution.id, "AI analysis failed",
            f"AI analysis retry failed for {institution.name}.",
            get_current_user_id()
        )
        return jsonify({
            "error": "AI analysis failed. Please retry.",
            "institution": institution.to_dict()
        }), 200


@institutions_bp.route("/<int:id>/regenerate-outreach", methods=["POST"])
@login_required
def regenerate_outreach_message(id):
    institution = Institution.query.get_or_404(id)
    message, success = regenerate_outreach(institution)
    if institution.ai_analysis:
        institution.ai_analysis.outreach_message = message
        db.session.commit()
    return jsonify({"outreach_message": message, "success": success})
