from flask import Flask, request, jsonify
from flask_cors import CORS
import json, os

app = Flask(__name__)
CORS(app)  # allow frontend to connect

SCORES_FILE = "scores.json"

# --- Helpers ---
def load_scores():
    if not os.path.exists(SCORES_FILE):
        return []
    with open(SCORES_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_scores(scores):
    with open(SCORES_FILE, "w") as f:
        json.dump(scores, f, indent=2)

# --- Routes ---
@app.route("/")
def index():
    return "🎮 Bloom Snake Backend is running!"

@app.route("/favicon.ico")
def favicon():
    return "", 204  # prevents 404 spam in logs

@app.route("/add_score", methods=["POST"])
def add_score():
    data = request.get_json()
    name = data.get("name", "").strip()
    points = int(data.get("points", 0))

    if not name:
        return jsonify({"error": "Name required"}), 400

    scores = load_scores()
    scores.append({"name": name, "points": points})
    save_scores(scores)

    return jsonify({"status": "ok", "message": "Score saved"})

@app.route("/scores", methods=["GET"])
def get_scores():
    scores = load_scores()
    # Sort descending and return top 10
    scores = sorted(scores, key=lambda x: x["points"], reverse=True)[:10]
    return jsonify(scores)

# --- Run server ---
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
