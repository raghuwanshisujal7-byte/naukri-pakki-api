# app/app/auth.py
from flask import Blueprint, request, session, jsonify
from app.models import create_user, get_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/auth/google", methods=["POST"])
def google_login():
    data = request.json
    email = data.get("email")

    if not email:
        return {"error": "Email required"}, 400

    create_user(email)
    session["user"] = email

    return {
        "success": True,
        "message": "Google login successful",
        "email": email
    }

@auth_bp.route("/auth/me", methods=["GET"])
def me():
    email = session.get("user")
    if not email:
        return {"logged_in": False}
    return {
        "logged_in": True,
        "email": email
    }
