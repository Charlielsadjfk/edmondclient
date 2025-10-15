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
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "replace_with_a_secure_secret_key_in_production"

# Configure upload folder
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/post", methods=["POST"])
def post():
    # Save the post to your database
    # ...
    return redirect(url_for("home"))


# Login page
@app.route("/")
@app.route("/login")
def login():
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

    user = dbHandler.get_user_by_email(email)

    if user:
        if check_password_hash(user["password"], password):
            session["user_id"] = user["userID"]
            session["name"] = user["name"]
            session["username"] = user["username"]
            session["email"] = user["email"]
            session["profile_picture"] = user["profile_picture"]
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

    if not all([name, username, email, password, confirm_password]):
        return jsonify({"success": False, "message": "All fields are required"})

    if password != confirm_password:
        return jsonify({"success": False, "message": "Passwords do not match"})

    if len(password) < 6:
        return jsonify(
            {"success": False, "message": "Password must be at least 6 characters"}
        )

    existing_user = dbHandler.get_user_by_username(username)
    if existing_user:
        return jsonify({"success": False, "message": "Username already exists"})

    existing_email = dbHandler.get_user_by_email(email)
    if existing_email:
        return jsonify({"success": False, "message": "Email already exists"})

    try:
        hashed_password = generate_password_hash(password)
        user_id = dbHandler.create_user(name, username, email, hashed_password)

        session["user_id"] = user_id
        session["name"] = name
        session["username"] = username
        session["email"] = email
        session["profile_picture"] = "avatar.jpg"

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


# Coming Soon page
@app.route("/coming-soon/<feature>")
def coming_soon(feature):
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Format feature name for display
    feature_names = {
        "explore": "Explore",
        "notifications": "Notifications",
        "messages": "Messages",
        "bookmarks": "Bookmarks",
        "lists": "Lists",
        "gif": "GIF Picker",
        "poll": "Polls",
        "emoji": "Emoji Picker",
        "search": "Search",
    }

    feature_display = feature_names.get(feature, feature.replace("-", " ").title())
    return render_template("coming_soon.html", feature_name=feature_display)


# API endpoint to get all posts
@app.route("/api/posts", methods=["GET"])
def api_get_posts():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    posts = dbHandler.get_all_posts()
    posts_list = []

    for post in posts:
        is_liked = dbHandler.is_post_liked_by_user(session["user_id"], post["postID"])
        posts_list.append(
            {
                "postID": post["postID"],
                "userID": post["userID"],
                "name": post["name"],
                "username": post["username"],
                "profile_picture": post["profile_picture"],
                "content": post["content"],
                "media_url": post["media_url"],
                "media_type": post["media_type"],
                "created_at": post["created_at"],
                "like_count": post["like_count"],
                "is_liked": is_liked,
            }
        )

    return jsonify({"success": True, "posts": posts_list})


# API endpoint to create a post
@app.route("/api/posts", methods=["POST"])
def api_create_post():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    data = request.get_json()
    content = data.get("content", "").strip()
    media_url = data.get("media_url")
    media_type = data.get("media_type")

    if not content:
        return jsonify({"success": False, "message": "Post content cannot be empty"})

    if len(content) > 280:
        return jsonify(
            {"success": False, "message": "Post cannot exceed 280 characters"}
        )

    try:
        post_id = dbHandler.create_post(
            session["user_id"], content, media_url, media_type
        )
        return jsonify(
            {"success": True, "message": "Post created successfully", "postID": post_id}
        )
    except Exception as e:
        return jsonify({"success": False, "message": f"Error creating post: {str(e)}"})


# API endpoint to delete a post
@app.route("/api/posts/<int:post_id>", methods=["DELETE"])
def api_delete_post(post_id):
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    post = dbHandler.get_post_by_id(post_id)
    if not post:
        return jsonify({"success": False, "message": "Post not found"}), 404

    if post["userID"] != session["user_id"]:
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    try:
        dbHandler.delete_post(post_id)
        return jsonify({"success": True, "message": "Post deleted successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error deleting post: {str(e)}"})


# API endpoint to get user's posts
@app.route("/api/posts/user/<int:user_id>", methods=["GET"])
def api_get_user_posts(user_id):
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    posts = dbHandler.get_posts_by_user(user_id)
    posts_list = []

    for post in posts:
        is_liked = dbHandler.is_post_liked_by_user(session["user_id"], post["postID"])
        posts_list.append(
            {
                "postID": post["postID"],
                "userID": post["userID"],
                "name": post["name"],
                "username": post["username"],
                "profile_picture": post["profile_picture"],
                "content": post["content"],
                "media_url": post["media_url"],
                "media_type": post["media_type"],
                "created_at": post["created_at"],
                "like_count": post["like_count"],
                "is_liked": is_liked,
            }
        )

    return jsonify({"success": True, "posts": posts_list})


# API endpoint to get user's media posts
@app.route("/api/posts/user/<int:user_id>/media", methods=["GET"])
def api_get_user_media_posts(user_id):
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    posts = dbHandler.get_posts_with_media_by_user(user_id)
    posts_list = []

    for post in posts:
        is_liked = dbHandler.is_post_liked_by_user(session["user_id"], post["postID"])
        posts_list.append(
            {
                "postID": post["postID"],
                "userID": post["userID"],
                "name": post["name"],
                "username": post["username"],
                "profile_picture": post["profile_picture"],
                "content": post["content"],
                "media_url": post["media_url"],
                "media_type": post["media_type"],
                "created_at": post["created_at"],
                "like_count": post["like_count"],
                "is_liked": is_liked,
            }
        )

    return jsonify({"success": True, "posts": posts_list})


# API endpoint to get user's liked posts
@app.route("/api/posts/user/<int:user_id>/likes", methods=["GET"])
def api_get_user_liked_posts(user_id):
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    posts = dbHandler.get_liked_posts_by_user(user_id)
    posts_list = []

    for post in posts:
        is_liked = dbHandler.is_post_liked_by_user(session["user_id"], post["postID"])
        posts_list.append(
            {
                "postID": post["postID"],
                "userID": post["userID"],
                "name": post["name"],
                "username": post["username"],
                "profile_picture": post["profile_picture"],
                "content": post["content"],
                "media_url": post["media_url"],
                "media_type": post["media_type"],
                "created_at": post["created_at"],
                "like_count": post["like_count"],
                "is_liked": is_liked,
            }
        )

    return jsonify({"success": True, "posts": posts_list})


# API endpoint to like a post
@app.route("/api/posts/<int:post_id>/like", methods=["POST"])
def api_like_post(post_id):
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    post = dbHandler.get_post_by_id(post_id)
    if not post:
        return jsonify({"success": False, "message": "Post not found"}), 404

    try:
        success = dbHandler.like_post(session["user_id"], post_id)
        if success:
            return jsonify({"success": True, "message": "Post liked successfully"})
        else:
            return jsonify({"success": False, "message": "Post already liked"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error liking post: {str(e)}"})


# API endpoint to unlike a post
@app.route("/api/posts/<int:post_id>/unlike", methods=["POST"])
def api_unlike_post(post_id):
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    try:
        dbHandler.unlike_post(session["user_id"], post_id)
        return jsonify({"success": True, "message": "Post unliked successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error unliking post: {str(e)}"})


# API endpoint to upload media
@app.route("/api/upload", methods=["POST"])
def api_upload_media():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    if "file" not in request.files:
        return jsonify({"success": False, "message": "No file part"})

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "message": "No selected file"})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        file_url = f"/static/uploads/{filename}"
        file_ext = filename.rsplit(".", 1)[1].lower()

        return jsonify({"success": True, "media_url": file_url, "media_type": file_ext})
    else:
        return jsonify({"success": False, "message": "File type not allowed"})


# API endpoint to get user profile
@app.route("/api/user/<int:user_id>", methods=["GET"])
def api_get_user_profile(user_id):
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    user = dbHandler.get_user_by_id(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    followers_count = dbHandler.get_followers_count(user_id)
    following_count = dbHandler.get_following_count(user_id)
    is_following = (
        dbHandler.is_following(session["user_id"], user_id)
        if session["user_id"] != user_id
        else False
    )

    return jsonify(
        {
            "success": True,
            "user": {
                "userID": user["userID"],
                "name": user["name"],
                "username": user["username"],
                "email": user["email"],
                "bio": user["bio"],
                "profile_picture": user["profile_picture"],
                "banner_picture": user["banner_picture"],
                "created_at": user["created_at"],
                "followers_count": followers_count,
                "following_count": following_count,
                "is_following": is_following,
            },
        }
    )


# API endpoint to update user profile
@app.route("/api/user/update", methods=["POST"])
def api_update_user():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    data = request.get_json()
    name = data.get("name")
    bio = data.get("bio")
    profile_picture = data.get("profile_picture")
    banner_picture = data.get("banner_picture")

    try:
        dbHandler.update_user(
            session["user_id"],
            name=name,
            bio=bio,
            profile_picture=profile_picture,
            banner_picture=banner_picture,
        )

        # Update session
        if name:
            session["name"] = name
        if profile_picture:
            session["profile_picture"] = profile_picture

        return jsonify({"success": True, "message": "Profile updated successfully"})
    except Exception as e:
        return jsonify(
            {"success": False, "message": f"Error updating profile: {str(e)}"}
        )


# API endpoint to follow user
@app.route("/api/user/<int:user_id>/follow", methods=["POST"])
def api_follow_user(user_id):
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    if session["user_id"] == user_id:
        return jsonify({"success": False, "message": "Cannot follow yourself"})

    user = dbHandler.get_user_by_id(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    try:
        success = dbHandler.follow_user(session["user_id"], user_id)
        if success:
            return jsonify({"success": True, "message": "User followed successfully"})
        else:
            return jsonify({"success": False, "message": "Already following this user"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error following user: {str(e)}"})


# API endpoint to unfollow user
@app.route("/api/user/<int:user_id>/unfollow", methods=["POST"])
def api_unfollow_user(user_id):
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    try:
        dbHandler.unfollow_user(session["user_id"], user_id)
        return jsonify({"success": True, "message": "User unfollowed successfully"})
    except Exception as e:
        return jsonify(
            {"success": False, "message": f"Error unfollowing user: {str(e)}"}
        )


# Profile page
@app.route("/profile")
@app.route("/profile/<username>")
def profile(username=None):
    if "user_id" not in session:
        return redirect(url_for("login"))

    # If no username provided, show current user's profile
    if username is None:
        username = session["username"]

    return render_template("profile.html", profile_username=username)


# Edit profile page
@app.route("/edit-profile")
def edit_profile():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("edit_profile.html")


# Logout
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully", "success")
    return redirect(url_for("login"))


@app.route("/manifest.json")
def manifest():
    return app.send_static_file("../manifest.json")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
