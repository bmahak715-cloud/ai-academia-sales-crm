import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "academia-crm-dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///academia_crm.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_HTTPONLY"] = True

    CORS(app, supports_credentials=True, origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ])

    db.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.institutions import institutions_bp
    from app.routes.follow_ups import follow_ups_bp
    from app.routes.meetings import meetings_bp
    from app.routes.communications import communications_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.notifications import notifications_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(institutions_bp, url_prefix="/api/institutions")
    app.register_blueprint(follow_ups_bp, url_prefix="/api/follow-ups")
    app.register_blueprint(meetings_bp, url_prefix="/api/meetings")
    app.register_blueprint(communications_bp, url_prefix="/api/communications")
    app.register_blueprint(dashboard_bp, url_prefix="/api")
    app.register_blueprint(notifications_bp, url_prefix="/api/notifications")

    with app.app_context():
        db.create_all()
        from app.services.seed import seed_if_empty
        seed_if_empty()

    return app
