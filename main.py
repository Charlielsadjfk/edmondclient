import database_manager as dbHandler
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
from werkzeug.security import check_password_hash, generate_password_hash
import os

app = Flask(__name__)
app.secret_key = "replace_with_a_secure_secret_key_in_production"


# Login page
@app.route("/")
@app.route("/login")
def login():
    # If already logged in, redirect to home
    if "user_id" in session:
        return redirect(url_for("home"))
    return render_template("login.html")


# API endpoint for login
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"})

    # Get user from database
    user = dbHandler.get_user_by_email(email)

    if user:
        # Check password
        if check_password_hash(user["password"], password):
            # Set session
            session["user_id"] = user["userID"]
            session["name"] = user["name"]
            session["username"] = user["username"]
            session["email"] = user["email"]
            return jsonify({"success": True, "message": "Login successful"})
        else:
            return jsonify({"success": False, "message": "Invalid email or password"})
    else:
        return jsonify({"success": False, "message": "Invalid email or password"})


# API endpoint for registration
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
        return jsonify({"success": False, "message": "All fields are required"})

    if password != confirm_password:
        return jsonify({"success": False, "message": "Passwords do not match"})

    if len(password) < 6:
        return jsonify(
            {"success": False, "message": "Password must be at least 6 characters"}
        )

    # Check if username already exists
    existing_user = dbHandler.get_user_by_username(username)
    if existing_user:
        return jsonify({"success": False, "message": "Username already exists"})

    # Check if email already exists
    existing_email = dbHandler.get_user_by_email(email)
    if existing_email:
        return jsonify({"success": False, "message": "Email already exists"})

    # Create user
    try:
        hashed_password = generate_password_hash(password)
        user_id = dbHandler.create_user(name, username, email, hashed_password)

        # Set session
        session["user_id"] = user_id
        session["name"] = name
        session["username"] = username
        session["email"] = email

        return jsonify({"success": True, "message": "Registration successful"})
    except Exception as e:
        return jsonify(
            {"success": False, "message": f"Error creating account: {str(e)}"}
        )


# Home page
@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("home_page.html")


# Profile page
@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("profile.html")


# Logout
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
