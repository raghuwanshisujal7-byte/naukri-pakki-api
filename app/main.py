# app/main.py
from flask import Flask, request, jsonify, session
from flask_cors import CORS

# 🔥 IMPORTANT: correct imports for nested structure
from app.app.models import users, create_user, get_user, increment_resume
from app.app.auth import auth_bp

app = Flask(__name__)
app.secret_key = "naukri-pakki-secret-key"

CORS(app, supports_credentials=True)

# register auth blueprint
app.register_blueprint(auth_bp)

# ------------------------------
# HELPER: resume access logic
# ------------------------------
def can_analyze():
    user_email = session.get("user")

    # CASE 1: NOT LOGGED IN
    if not user_email:
        if "free_used" not in session:
            session["free_used"] = True
            return True
        return False

    # CASE 2: LOGGED IN
    user = get_user(user_email)
    if user and user["resume_count"] < 1:
        increment_resume(user_email)
        return True

    return False

# ------------------------------
# HEALTH CHECK
# ------------------------------
@app.route("/", methods=["GET"])
def home():
    return {"status": "backend running"}

# ------------------------------
# ANALYZE RESUME
# ------------------------------
@app.route("/analyze", methods=["POST"])
def analyze_resume():
    if not can_analyze():
        return jsonify({
            "success": False,
            "error": "LIMIT_REACHED",
            "message": "Login or upgrade to continue"
        }), 403

    # ⚠️ existing analyze.py logic already working on Render
    # yahan dummy wrapper hai, actual response analyze.py se aa raha hai

    return jsonify({
        "success": True,
        "note": "Analysis allowed"
    })

# ------------------------------
# DEBUG (OPTIONAL)
# ------------------------------
@app.route("/debug", methods=["GET"])
def debug():
    return {
        "session": dict(session),
        "users": users
    }

# ------------------------------
# RUN
# ------------------------------
if __name__ == "__main__":
    app.run(debug=True)
