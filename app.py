"""
EduSimplify – Flask Application Entry Point
=============================================
Routes:
  GET  /             → serve the main UI (index.html)
  GET  /health       → JSON health/status check
  POST /api/simplify → run the full agent pipeline
  GET  /api/status   → check credentials / demo mode status
"""

from flask import Flask, render_template, request, jsonify
from config import credentials_configured, demo_mode_active, FLASK_SECRET_KEY, FLASK_DEBUG, FLASK_PORT
from orchestrator import run_pipeline

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY


# ─────────────────────────────────────────────────────────────────────────────
#  Main page
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


# ─────────────────────────────────────────────────────────────────────────────
#  Health check
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "app": "EduSimplify",
        "credentials_configured": credentials_configured(),
        "demo_mode": demo_mode_active(),
    })


# ─────────────────────────────────────────────────────────────────────────────
#  Credential / mode status (used by the UI on page load)
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/api/status")
def status():
    creds_ok = credentials_configured()
    demo     = demo_mode_active()

    if creds_ok:
        message = "IBM watsonx credentials are configured. Running in LIVE mode."
    elif demo:
        message = (
            "Running in DEMO MODE — no IBM credentials required. "
            "The full 5-agent workflow is demonstrated with pre-written responses. "
            "To activate IBM Granite, set IBM_API_KEY and IBM_PROJECT_ID in .env."
        )
    else:
        message = (
            "IBM credentials are NOT configured and DEMO_MODE is disabled. "
            "Set IBM_API_KEY and IBM_PROJECT_ID in .env, or set DEMO_MODE=true."
        )

    return jsonify({
        "credentials_configured": creds_ok,
        "demo_mode": demo,
        "message": message,
    })


# ─────────────────────────────────────────────────────────────────────────────
#  Main simplification endpoint
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/api/simplify", methods=["POST"])
def simplify():
    data = request.get_json(force=True, silent=True) or {}

    content = data.get("content", "").strip()
    level   = data.get("level", "Beginner").strip()

    if not content:
        return jsonify({"error": True, "error_type": "input",
                        "message": "Please provide academic content to simplify."}), 400

    valid_levels = {"Beginner", "Intermediate", "Advanced"}
    if level not in valid_levels:
        return jsonify({"error": True, "error_type": "input",
                        "message": f"Level must be one of: {', '.join(valid_levels)}"}), 400

    result = run_pipeline(content, level)

    if result.get("error"):
        return jsonify(result), 500

    return jsonify(result), 200


# ─────────────────────────────────────────────────────────────────────────────
#  Run
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=FLASK_DEBUG, port=FLASK_PORT, host="0.0.0.0")
