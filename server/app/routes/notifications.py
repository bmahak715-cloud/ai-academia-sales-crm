from flask import Blueprint, jsonify
from app.models.notification import Notification
from app.utils.auth import login_required, get_current_user_id
from app import db

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.route("", methods=["GET"])
@login_required
def list_notifications():
    user_id = get_current_user_id()
    notifications = Notification.query.filter_by(user_id=user_id).order_by(
        Notification.created_at.desc()
    ).limit(50).all()
    unread = Notification.query.filter_by(user_id=user_id, is_read=False).count()
    return jsonify({
        "notifications": [n.to_dict() for n in notifications],
        "unread_count": unread,
    })


@notifications_bp.route("/<int:id>/read", methods=["PATCH"])
@login_required
def mark_read(id):
    notification = Notification.query.get_or_404(id)
    notification.is_read = True
    db.session.commit()
    return jsonify({"notification": notification.to_dict()})


@notifications_bp.route("/read-all", methods=["PATCH"])
@login_required
def mark_all_read():
    user_id = get_current_user_id()
    Notification.query.filter_by(user_id=user_id, is_read=False).update({"is_read": True})
    db.session.commit()
    return jsonify({"message": "All notifications marked as read"})
