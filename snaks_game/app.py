from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
from contextlib import closing
import os

DB_PATH = "scores.db"

app = Flask(__name__, static_folder=None)
CORS(app)  # same-origin এ চললে লাগবে না, তবু রাখা হলো—কোনো ক্ষতি নেই

def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                score INTEGER NOT NULL CHECK(score >= 0),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    # index.html একই ফোল্ডারে আছে ধরে নেওয়া
    return send_file("index.html")

@app.route("/submit_score", methods=["POST"])
def submit_score():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    score = data.get("score")

    # ভ্যালিডেশন
    if not name:
        return jsonify({"ok": False, "error": "Name is required"}), 400
    if not isinstance(score, int) or score < 0:
        return jsonify({"ok": False, "error": "Score must be a non-negative integer"}), 400
    if len(name) > 30:
        name = name[:30]

    with closing(get_db()) as conn:
        conn.execute("INSERT INTO scores(name, score) VALUES (?, ?)", (name, score))
        conn.commit()

    return jsonify({"ok": True})

@app.route("/get_scores", methods=["GET"])
def get_scores():
    # ?limit=10 দিলে 10টা; ডিফল্ট 10
    try:
        limit = int(request.args.get("limit", 10))
    except ValueError:
        limit = 10
    limit = max(1, min(limit, 50))  # 1..50

    with closing(get_db()) as conn:
        rows = conn.execute("""
            SELECT name, score, created_at
            FROM scores
            ORDER BY score DESC, created_at ASC
            LIMIT ?
        """, (limit,)).fetchall()

    return jsonify({
        "ok": True,
        "scores": [{"name": r["name"], "score": r["score"], "created_at": r["created_at"]} for r in rows]
    })

if __name__ == "__main__":
    init_db()
    # Windows এ auto-reload সহ ডেভ সার্ভার
    app.run(host="127.0.0.1", port=5000, debug=True)
