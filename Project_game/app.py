from flask import Flask, request, jsonify
from flask_cors import CORS
import json, os

app = Flask(__name__)
CORS(app)  # allow frontend to connect

SCORES_FILE = "scores.json"

# --- Helpers ---
def load_scores():
    """Load scores from JSON file, auto-fix missing ids."""
    if not os.path.exists(SCORES_FILE):
        return []

    with open(SCORES_FILE, "r") as f:
        try:
            scores = json.load(f)
        except json.JSONDecodeError:
            scores = []

    # Auto-migrate: assign ids if missing
    changed = False
    for idx, s in enumerate(scores, start=1):
        if "id" not in s:
            s["id"] = idx
            changed = True
    if changed:
        save_scores(scores)

    return scores


def save_scores(scores):
    with open(SCORES_FILE, "w") as f:
        json.dump(scores, f, indent=2)


def next_id(scores):
    if not scores:
        return 1
    return max(s.get("id", 0) for s in scores) + 1


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
    new_entry = {"id": next_id(scores), "name": name, "points": points}
    scores.append(new_entry)
    save_scores(scores)

    return jsonify({"status": "ok", "message": "Score saved", "score": new_entry})


@app.route("/scores", methods=["GET"])
def get_scores():
    scores = load_scores()
    # Sort descending and return top 10
    scores = sorted(scores, key=lambda x: x["points"], reverse=True)[:10]
    return jsonify(scores)


@app.route("/delete_score/<int:score_id>", methods=["DELETE"])
def delete_score(score_id):
    scores = load_scores()
    updated = [s for s in scores if s.get("id") != score_id]

    if len(updated) == len(scores):
        return jsonify({"error": "Score not found"}), 404

    save_scores(updated)
    return jsonify({"status": "ok", "message": f"Score {score_id} deleted"})


# --- Run server ---
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
