from flask import Blueprint, request, jsonify, session
from app import db
from app.models.user import User
from app.utils.auth import login_required

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    if not user.is_active:
        return jsonify({"error": "Account is deactivated"}), 403

    session["user_id"] = user.id
    session.permanent = True
    return jsonify({"user": user.to_dict(), "message": "Login successful"})


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"})


@auth_bp.route("/me", methods=["GET"])
def me():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    user = User.query.get(user_id)
    if not user:
        session.clear()
        return jsonify({"error": "User not found"}), 401
    return jsonify({"user": user.to_dict()})


@auth_bp.route("/users", methods=["GET"])
@login_required
def list_users():
    users = User.query.filter_by(is_active=True).all()
    return jsonify({"users": [u.to_dict() for u in users]})
