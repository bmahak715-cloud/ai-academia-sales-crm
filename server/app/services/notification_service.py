from app import db
from app.models.notification import Notification
from app.models.user import User


def create_notification(user_id, notification_type, message, institution_id=None):
    notification = Notification(
        user_id=user_id,
        institution_id=institution_id,
        notification_type=notification_type,
        message=message,
    )
    db.session.add(notification)
    db.session.commit()
    return notification


def notify_user_and_managers(user_id, notification_type, message, institution_id=None):
    create_notification(user_id, notification_type, message, institution_id)
    managers = User.query.filter(User.role.in_(["Admin", "Sales Manager"])).all()
    for mgr in managers:
        if mgr.id != user_id:
            create_notification(mgr.id, notification_type, message, institution_id)


def notify_assigned_user(institution, notification_type, message):
    if institution.assigned_to_id:
        create_notification(
            institution.assigned_to_id, notification_type, message, institution.id
        )
