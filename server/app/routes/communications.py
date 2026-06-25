import os
from datetime import datetime
from flask import Blueprint, request, jsonify
from app import db
from app.models.communication import Communication
from app.models.institution import Institution
from app.utils.auth import login_required, get_current_user_id
from app.services.ai_service import generate_follow_up_message, regenerate_outreach
from app.services.activity_service import log_activity
from app.services.notification_service import create_notification

communications_bp = Blueprint("communications", __name__)


@communications_bp.route("", methods=["GET"])
@login_required
def list_communications():
    institution_id = request.args.get("institution_id")
    query = Communication.query
    if institution_id:
        query = query.filter_by(institution_id=int(institution_id))
    comms = query.order_by(Communication.created_at.desc()).all()
    return jsonify({"communications": [c.to_dict() for c in comms]})


@communications_bp.route("/generate", methods=["POST"])
@login_required
def generate_message():
    data = request.get_json() or {}
    institution_id = data.get("institution_id")
    message_type = data.get("message_type", "outreach")

    if not institution_id:
        return jsonify({"error": "institution_id is required"}), 400

    institution = Institution.query.get(institution_id)
    if not institution:
        return jsonify({"error": "Institution not found"}), 404

    if message_type == "outreach":
        if institution.ai_analysis and institution.ai_analysis.outreach_message:
            body = institution.ai_analysis.outreach_message
        else:
            body, _ = regenerate_outreach(institution)
    else:
        body = generate_follow_up_message(institution, data.get("context", ""))

    subject = data.get("subject") or f"Partnership Opportunity - {institution.program_interest}"

    comm = Communication(
        institution_id=institution_id,
        message_type=message_type,
        subject=subject,
        body=body,
        status="Draft",
        created_by_id=get_current_user_id(),
    )
    db.session.add(comm)
    db.session.commit()

    return jsonify({"communication": comm.to_dict()})


@communications_bp.route("/send", methods=["POST"])
@login_required
def send_message():
    data = request.get_json() or {}
    institution_id = data.get("institution_id")
    if not institution_id:
        return jsonify({"error": "institution_id is required"}), 400

    institution = Institution.query.get(institution_id)
    if not institution:
        return jsonify({"error": "Institution not found"}), 404

    body = data.get("body", "")
    subject = data.get("subject", "")

    smtp_host = os.getenv("SMTP_HOST")
    smtp_sent = False
    if smtp_host and os.getenv("SMTP_USER") and os.getenv("SMTP_PASSWORD"):
        try:
            import smtplib
            from email.mime.text import MIMEText
            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = os.getenv("SMTP_FROM", os.getenv("SMTP_USER"))
            msg["To"] = institution.email
            with smtplib.SMTP(smtp_host, int(os.getenv("SMTP_PORT", 587))) as server:
                server.starttls()
                server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD"))
                server.send_message(msg)
            smtp_sent = True
        except Exception:
            pass

    comm = Communication(
        institution_id=institution_id,
        message_type=data.get("message_type", "outreach"),
        subject=subject,
        body=body,
        status="Sent",
        sent_at=datetime.utcnow(),
        created_by_id=get_current_user_id(),
    )
    db.session.add(comm)
    db.session.commit()

    log_activity(
        institution_id, "Message sent",
        f"Message sent to {institution.contact_person} ({'via SMTP' if smtp_sent else 'marked as sent'}).",
        get_current_user_id()
    )
    create_notification(
        get_current_user_id(), "Message marked as sent",
        f"Message sent to {institution.name}",
        institution_id
    )

    return jsonify({
        "communication": comm.to_dict(),
        "smtp_sent": smtp_sent,
        "message": "Message marked as sent" if not smtp_sent else "Message sent via SMTP",
    })


@communications_bp.route("/<int:id>/mark-sent", methods=["PATCH"])
@login_required
def mark_sent(id):
    comm = Communication.query.get_or_404(id)
    data = request.get_json() or {}

    if data.get("body"):
        comm.body = data["body"]
    if data.get("subject"):
        comm.subject = data["subject"]

    comm.status = "Sent"
    comm.sent_at = datetime.utcnow()
    db.session.commit()

    institution = Institution.query.get(comm.institution_id)
    log_activity(
        comm.institution_id, "Message sent",
        f"Message marked as sent to {institution.contact_person if institution else 'contact'}.",
        get_current_user_id()
    )
    create_notification(
        get_current_user_id(), "Message marked as sent",
        f"Message sent to {institution.name if institution else 'institution'}",
        comm.institution_id
    )
    return jsonify({"communication": comm.to_dict()})
