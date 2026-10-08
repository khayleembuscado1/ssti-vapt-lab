from flask import Flask, request, render_template_string, render_template, redirect, url_for, flash
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "lab.db"

app = Flask(__name__)
app.secret_key = "local-lab-only-secret-key"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        );
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
    """)
    count = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
    if count == 0:
        conn.executemany(
            "INSERT INTO users (username, full_name, email, role) VALUES (?, ?, ?, ?)",
            [
                ("alice", "Alice Santos", "alice@example.local", "user"),
                ("bob", "Bob Reyes", "bob@example.local", "user"),
                ("admin", "Lab Administrator", "admin@example.local", "admin"),
            ],
        )
        conn.executemany(
            "INSERT INTO notes (user_id, title, body) VALUES (?, ?, ?)",
            [
                (1, "Alice's note", "Quarterly security review."),
                (2, "Bob's note", "Internal testing checklist."),
                (3, "Admin note", "Lab-only administrative record."),
            ],
        )
    conn.commit()
    conn.close()


@app.route("/")
def index():
    conn = get_db()
    users = conn.execute("SELECT id, username, full_name, email, role FROM users ORDER BY id").fetchall()
    conn.close()
    return render_template("index.html", users=users)


@app.route("/user/<int:user_id>")
def user_profile(user_id):
    conn = get_db()
    user = conn.execute("SELECT id, username, full_name, email, role FROM users WHERE id = ?", (user_id,)).fetchone()
    notes = conn.execute("SELECT id, title, body FROM notes WHERE user_id = ? ORDER BY id", (user_id,)).fetchall()
    conn.close()
    if not user:
        return render_template("error.html", message="User not found"), 404
    return render_template("profile.html", user=user, notes=notes)


@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    conn = get_db()
    rows = conn.execute(
        "SELECT id, username, full_name, email, role FROM users "
        "WHERE username LIKE ? OR full_name LIKE ? OR email LIKE ? ORDER BY id",
        (f"%{q}%", f"%{q}%", f"%{q}%"),
    ).fetchall()
    conn.close()
    return render_template("search.html", q=q, users=rows)


@app.route("/preview")
def preview():
    """
    INTENTIONALLY VULNERABLE SSTI LAB ENDPOINT.

    User input is inserted into the Jinja2 template source.
    This endpoint is for the controlled VAPT lab only.
    """
    name = request.args.get("name", "")

    template = f"""
    {{% extends "base.html" %}}
    {{% block content %}}
      <div class="card">
        <h2>Preview</h2>
        <p class="muted">This endpoint is intentionally vulnerable for the lab.</p>
        <div class="preview-box">
          <h3>Hello {name}</h3>
        </div>
      </div>
    {{% endblock %}}
    """

    return render_template_string(template)


@app.route("/safe-preview")
def safe_preview():
    name = request.args.get("name", "")
    return render_template("safe_preview.html", name=name)


@app.route("/health")
def health():
    return {"status": "ok", "application": "SSTI VAPT Lab"}


@app.route("/reset-db", methods=["POST"])
def reset_db():
    if DB_PATH.exists():
        DB_PATH.unlink()
    init_db()
    flash("Lab database has been reset.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
