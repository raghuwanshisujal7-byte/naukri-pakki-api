# app/main.py

from flask import Flask, request, jsonify, session
from flask_cors import CORS

# ✅ CORRECT IMPORTS (nested structure)
from app.app.models import users, create_user, get_user, increment_resume
from app.app.auth import auth_bp

app = Flask(__name__)

# 🔐 session secret
app.secret_key = "naukri-pakki-secret-key"

# 🌐 CORS
CORS(app, supports_credentials=True)

# 🔗 register auth routes
app.register_blueprint(auth_bp)

# ----------------------------------
# RESUME LIMIT LOGIC
# ----------------------------------
def can_analyze():
    user_email = session.get("user")

    # 🔹 Case 1: Not logged in → 1 free
    if not user_email:
        if "free_used" not in session:
            session["free_used"] = True
            return True
        return False

    # 🔹 Case 2: Logged in → 1 more free
    user = get_user(user_email)
    if user and user["resume_count"] < 1:
        increment_resume(user_email)
        return True

    return False


# ----------------------------------
# HEALTH CHECK
# ----------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "backend running"
    })


# ----------------------------------
# ANALYZE RESUME (GATE)
# ----------------------------------
@app.route("/analyze", methods=["POST"])
def analyze_resume():
    if not can_analyze():
        return jsonify({
            "success": False,
            "error": "LIMIT_REACHED",
            "message": "Login or upgrade to continue"
        }), 403

    # ⚠️ Actual resume analysis already handled elsewhere
    # This endpoint is only the gate

    return jsonify({
        "success": True,
        "note": "Analysis allowed"
    })


# ----------------------------------
# DEBUG (OPTIONAL)
# ----------------------------------
@app.route("/debug", methods=["GET"])
def debug():
    return jsonify({
        "session": dict(session),
        "users": users
    })


# ----------------------------------
# RUN (RENDER FIX)
# ----------------------------------
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=10000,
        debug=True
    )
