from app import db
from app.models.activity import Activity
from app.utils.auth import get_current_user_id


def log_activity(institution_id, activity_type, description, user_id=None):
    uid = user_id or get_current_user_id()
    activity = Activity(
        institution_id=institution_id,
        activity_type=activity_type,
        description=description,
        user_id=uid,
    )
    db.session.add(activity)
    db.session.commit()
    return activity
