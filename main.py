from flask import Flask
from flask import render_template
from flask import request
import database_manager as dbHandler

app = Flask(__name__)


@app.route("/index.html", methods=["GET"])
@app.route("/", methods=["POST", "GET"])
def index():
    data = dbHandler.listExtension()
    return render_template("index.html", content=data)


@app.route("/main")
def profile():
    return render_template("profile.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # ✅ Example check (replace with real authentication logic)
        if username == "admin" and password == "password":
            return redirect(url_for("index"))  # or your home/profile route
        else:
            # Normally you’d flash an error message or re-render with error
            return render_template("login.html", error="Invalid credentials")

    # GET request → just show the login page
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
