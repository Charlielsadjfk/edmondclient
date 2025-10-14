import database_manager as dbHandler
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = "replace_with_a_secure_secret_key"


def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), "data_source.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM USER WHERE email = ?", (email,)).fetchone()
        conn.close()

        if user:
            if check_password_hash(user["password"], password):
                session["user_id"] = user["userID"]
                session["name"] = user["name"]
                flash("Logged in successfully!", "success")
                return redirect(url_for("profile"))
            else:
                flash("Invalid password.", "error")
        else:
            flash("No account found with that email.", "error")

    return render_template("login.html")


@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("profile.html", name=session.get("name"))


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
