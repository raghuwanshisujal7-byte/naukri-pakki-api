from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        if "resume" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["resume"]

        if file.filename == "":
            return jsonify({"error": "Empty file"}), 400

        if not file.filename.lower().endswith(".pdf"):
            return jsonify({"error": "Only PDF allowed"}), 400

        # TEMP STATIC RESULT (IMPORTANT)
        return jsonify({
            "score": 82,
            "skills": ["Python", "AI", "Data Analysis"],
            "missing_skills": ["Docker", "System Design"],
            "summary": "Good resume. Add more projects."
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()
