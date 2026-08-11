import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template, abort

load_dotenv(Path(__file__).parent / ".env")

import db as cloudant

app = Flask(__name__)

# Bootstrap Cloudant on first import (works for both gunicorn and python start.py)
with app.app_context():
    try:
        cloudant.bootstrap()
    except Exception as e:
        print(f"Warning: Cloudant bootstrap failed: {e}")


def now_str():
    d = datetime.now()
    return f"{d.strftime('%b')} {d.day}, {d.year} {d.strftime('%H:%M')}"


# ── Pages ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/ping")
def ping():
    return jsonify({"status": "ok"}), 200


# ── Users API ─────────────────────────────────────────────────────────────────

@app.route("/api/users")
def get_users():
    dept   = request.args.get("dept", "")
    status = request.args.get("status", "")
    return jsonify(cloudant.get_users(dept=dept, status=status))


@app.route("/api/users/<user_id>")
def get_user(user_id):
    user = cloudant.get_user(user_id)
    if not user:
        abort(404)
    return jsonify(user)


@app.route("/api/users", methods=["POST"])
def add_user():
    body = request.get_json(force=True)
    for field in ["name", "role", "dept"]:
        if not body.get(field, "").strip():
            return jsonify({"error": f"Missing required field: {field}"}), 400

    new_user = {
        "name":    body["name"].strip(),
        "role":    body["role"].strip(),
        "dept":    body["dept"].strip(),
        "status":  body.get("status", "available").strip(),
        "task":    "",
        "updated": now_str(),
    }
    return jsonify(cloudant.add_user(new_user)), 201


@app.route("/api/users/<user_id>", methods=["PATCH"])
def update_user(user_id):
    body = request.get_json(force=True)
    allowed = {"name", "role", "dept", "status", "task"}
    fields  = {k: v for k, v in body.items() if k in allowed}

    if "status" in fields:
        valid = {"available", "busy", "on-break", "on-leave"}
        if fields["status"] not in valid:
            return jsonify({"error": f"status must be one of: {', '.join(valid)}"}), 400

    fields["updated"] = now_str()
    result = cloudant.update_user(user_id, fields)
    if not result:
        abort(404)
    return jsonify(result)


@app.route("/api/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    if not cloudant.get_user(user_id):
        abort(404)
    cloudant.delete_user(user_id)
    return jsonify({"deleted": user_id}), 200


# ── Dashboard summary API ─────────────────────────────────────────────────────

@app.route("/api/dashboard")
def dashboard():
    users  = cloudant.get_users()
    counts = {"available": 0, "busy": 0, "on-break": 0, "on-leave": 0}
    for u in users:
        s = u.get("status", "available")
        counts[s] = counts.get(s, 0) + 1
    return jsonify({
        "totalUsers":  len(users),
        "counts":      counts,
        "activeTasks": sum(1 for u in users if u.get("task")),
    })


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cloudant.bootstrap()
    port = int(os.environ.get("PORT", 5052))
    app.run(debug=False, host="0.0.0.0", port=port)
