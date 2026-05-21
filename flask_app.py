from flask import Flask, render_template, request, send_from_directory, make_response, url_for
import os
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_caching import Cache

app = Flask(__name__)
cache = Cache(config={
    "CACHE_TYPE": "SimpleCache",
    # Tune as needed
    "CACHE_DEFAULT_TIMEOUT": 60,
})
cache.init_app(app)


# Database file next to this script
DB_FILENAME = os.path.join(app.root_path, "data.sqlite3")
print(DB_FILENAME)

def init_db():
    """Create the users table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILENAME)
    try:
        conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT,
                        password TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                    """
                )
        conn.commit()
    except Exception as e:
        print("Database error:", e)

    finally:
       conn.close()


# Ensure the database table exists when the app module is loaded.
init_db()


@app.route("/")
def home():
    return render_template("index.html")


@cache.memoize(timeout=60)
def get_user_by_email(email: str):
    """Cached user lookup by email (used by /login)."""
    conn = sqlite3.connect(DB_FILENAME)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, full_name, password FROM users WHERE email = ?",
            (email,),
        )
        return cur.fetchone()
    finally:
        conn.close()


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        # Login by email + password
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            row = get_user_by_email(email)
        except Exception:
            return ("Failed to read from database"), 500

        if not row or not check_password_hash(row[2], password):
            return render_template("login.html", error="Invalid email or password")

        full_name = row[1] or email
        return render_template("success.html", username=full_name)




@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")
        hashed_password = generate_password_hash(password)
        try:
            conn = sqlite3.connect(DB_FILENAME)
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (full_name, email, password, created_at) VALUES (?, ?, ?, ?)",
                (full_name, email, hashed_password, datetime.utcnow().isoformat()),
            )
            conn.commit()

            # Invalidate cached user lookup for this email after write.
            try:
                get_user_by_email.delete_memoized(email)
            except Exception:
                pass
        except sqlite3.IntegrityError:
            return render_template("register.html", error="An account with that email already exists")
        except Exception:
            return ("Failed to save to database"), 500
        finally:
            try:
                conn.close()
            except Exception:
                pass

        return render_template("success.html", username=full_name, show_login=True)



@app.route('/download-documentation')
def download_documentation():
    resp = make_response(
        send_from_directory(app.root_path, 'project_documentation.pdf', as_attachment=True)
    )
    resp.headers['Cache-Control'] = 'public, max-age=3600'
    return resp



if __name__ == "__main__":
    init_db()
    app.run(debug=True)

    