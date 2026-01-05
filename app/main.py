# app/main.py
# ==============================
# MAIN SERVER FILE
# ==============================

from flask import Flask, request, jsonify, session
from flask_cors import CORS

# IMPORTANT: current structure ke hisaab se import
from app.models import users

app = Flask(__name__)
app.secret_key = "naukri-pakki-secret-key"

CORS(app, supports_credentials=True)

# ------------------------------
# HELPER: check free resume usage
# ------------------------------
def can_use_free_resume():
    if "free_used" not in session:
        session["free_used"] = True
        return True
    return False

# ------------------------------
# TEST ROUTE
# ------------------------------
@app.route("/", methods=["GET"])
def home():
    return {"status": "backend running"}

# ------------------------------
# RESUME ANALYZE (FREE 1 TIME)
# ------------------------------
@app.route("/analyze", methods=["POST"])
def analyze_resume():
    # login nahi hai abhi
    if not can_use_free_resume():
        return jsonify({
            "error": "Free limit reached",
            "message": "Login or upgrade to continue"
        }), 403

    # dummy analysis (abhi existing logic baad me add hoga)
    return jsonify({
        "result": "Resume analyzed successfully",
        "note": "This was your 1 free attempt"
    })

# ------------------------------
# CHECK SESSION
# ------------------------------
@app.route("/check-session", methods=["GET"])
def check_session():
    return {
        "free_used": session.get("free_used", False),
        "users": users
    }

# ------------------------------
# RUN SERVER
# ------------------------------
if __name__ == "__main__":
    app.run(debug=True)
