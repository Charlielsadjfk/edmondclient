from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
)
import sqlite3
import os
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = "replace_with_a_secure_secret_key_change_this_in_production"


def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), "database", "data_source.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("home"))


@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM USER WHERE userID = ?", (session["user_id"],)
    ).fetchone()
    conn.close()

    if not user:
        session.clear()
        return redirect(url_for("login"))

    return render_template("home.html", user=user)


@app.route("/login")
def login():
    if "user_id" in session:
        return redirect(url_for("home"))
    return render_template("login.html")


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return (
            jsonify({"success": False, "message": "Email and password are required"}),
            400,
        )

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM USER WHERE email = ?", (email,)).fetchone()
    conn.close()

    if user and check_password_hash(user["password"], password):
        session["user_id"] = user["userID"]
        session["name"] = user["name"]
        session["username"] = user["username"]
        return jsonify({"success": True, "message": "Logged in successfully"})
    else:
        return jsonify({"success": False, "message": "Invalid email or password"}), 401


@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json()
    name = data.get("name")
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    confirm_password = data.get("confirmPassword")

    # Validation
    if not all([name, username, email, password, confirm_password]):
        return jsonify({"success": False, "message": "All fields are required"}), 400

    if password != confirm_password:
        return jsonify({"success": False, "message": "Passwords do not match"}), 400

    if len(password) < 6:
        return (
            jsonify(
                {"success": False, "message": "Password must be at least 6 characters"}
            ),
            400,
        )

    # Check if user already exists
    conn = get_db_connection()
    existing_email = conn.execute(
        "SELECT * FROM USER WHERE email = ?", (email,)
    ).fetchone()
    existing_username = conn.execute(
        "SELECT * FROM USER WHERE username = ?", (username,)
    ).fetchone()

    if existing_email:
        conn.close()
        return jsonify({"success": False, "message": "Email already registered"}), 400

    if existing_username:
        conn.close()
        return jsonify({"success": False, "message": "Username already taken"}), 400

    # Create new user
    hashed_password = generate_password_hash(password)
    try:
        conn.execute(
            "INSERT INTO USER (name, username, email, password, role) VALUES (?, ?, ?, ?, ?)",
            (name, username, email, hashed_password, "user"),
        )
        conn.commit()

        # Get the newly created user
        user = conn.execute("SELECT * FROM USER WHERE email = ?", (email,)).fetchone()
        conn.close()

        # Auto-login after registration
        session["user_id"] = user["userID"]
        session["name"] = user["name"]
        session["username"] = user["username"]

        return jsonify({"success": True, "message": "Account created successfully"})
    except Exception as e:
        conn.close()
        return (
            jsonify({"success": False, "message": f"Error creating account: {str(e)}"}),
            500,
        )


@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM USER WHERE userID = ?", (session["user_id"],)
    ).fetchone()
    conn.close()

    if not user:
        session.clear()
        return redirect(url_for("login"))

    return render_template("profile.html", user=user)


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
