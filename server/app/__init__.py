import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    database_url = os.getenv("DATABASE_URL", "sqlite:///academia_crm.db")

    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql://",
            1
        )

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    is_production = os.getenv("FLASK_ENV") == "production"

    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        "academia-crm-dev-secret-key"
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SECURE"] = is_production
    app.config["SESSION_COOKIE_SAMESITE"] = (
        "None" if is_production else "Lax"
    )

    allowed_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    if frontend_url not in allowed_origins:
        allowed_origins.append(frontend_url)

    CORS(
        app,
        supports_credentials=True,
        origins=allowed_origins
    )

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
