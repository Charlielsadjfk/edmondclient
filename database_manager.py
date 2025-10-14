import sqlite3 as sql
import os


def get_connection():
    db_path = os.path.join(os.path.dirname(__file__), "database", "data_source.db")
    con = sql.connect(db_path)
    con.row_factory = sql.Row
    return con


# USER FUNCTIONS


def list_users():
    con = get_connection()
    cur = con.cursor()
    data = cur.execute("SELECT * FROM USER").fetchall()
    con.close()
    return data


def get_user_by_email(email):
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM USER WHERE email = ?", (email,))
    u = cur.fetchone()
    con.close()
    return u


def get_user_by_username(username):
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM USER WHERE username = ?", (username,))
    u = cur.fetchone()
    con.close()
    return u


def get_user_by_id(userID):
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM USER WHERE userID = ?", (userID,))
    u = cur.fetchone()
    con.close()
    return u


def create_user(name, username, email, password, role="user"):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO USER (name, username, email, password, role) VALUES (?, ?, ?, ?, ?)",
        (name, username, email, password, role),
    )
    con.commit()
    user_id = cur.lastrowid
    con.close()
    return user_id


def update_user(
    userID,
    name=None,
    username=None,
    email=None,
    password=None,
    bio=None,
    profile_picture=None,
    banner_picture=None,
):
    con = get_connection()
    cur = con.cursor()

    if name:
        cur.execute("UPDATE USER SET name = ? WHERE userID = ?", (name, userID))
    if username:
        cur.execute("UPDATE USER SET username = ? WHERE userID = ?", (username, userID))
    if email:
        cur.execute("UPDATE USER SET email = ? WHERE userID = ?", (email, userID))
    if password:
        cur.execute("UPDATE USER SET password = ? WHERE userID = ?", (password, userID))
    if bio is not None:
        cur.execute("UPDATE USER SET bio = ? WHERE userID = ?", (bio, userID))
    if profile_picture:
        cur.execute(
            "UPDATE USER SET profile_picture = ? WHERE userID = ?",
            (profile_picture, userID),
        )
    if banner_picture is not None:
        cur.execute(
            "UPDATE USER SET banner_picture = ? WHERE userID = ?",
            (banner_picture, userID),
        )

    con.commit()
    con.close()


def delete_user(userID):
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM USER WHERE userID = ?", (userID,))
    con.commit()
    con.close()


# POST FUNCTIONS


def create_post(userID, content, media_url=None, media_type=None):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO POST (userID, content, media_url, media_type) VALUES (?, ?, ?, ?)",
        (userID, content, media_url, media_type),
    )
    con.commit()
    post_id = cur.lastrowid
    con.close()
    return post_id


def get_all_posts():
    con = get_connection()
    cur = con.cursor()
    data = cur.execute(
        """
        SELECT POST.*, USER.name, USER.username, USER.profile_picture,
               (SELECT COUNT(*) FROM LIKE WHERE LIKE.postID = POST.postID) as like_count
        FROM POST 
        JOIN USER ON POST.userID = USER.userID 
        ORDER BY POST.created_at DESC
        """
    ).fetchall()
    con.close()
    return data


def get_posts_by_user(userID):
    con = get_connection()
    cur = con.cursor()
    data = cur.execute(
        """
        SELECT POST.*, USER.name, USER.username, USER.profile_picture,
               (SELECT COUNT(*) FROM LIKE WHERE LIKE.postID = POST.postID) as like_count
        FROM POST 
        JOIN USER ON POST.userID = USER.userID 
        WHERE POST.userID = ?
        ORDER BY POST.created_at DESC
        """,
        (userID,),
    ).fetchall()
    con.close()
    return data


def get_posts_with_media_by_user(userID):
    con = get_connection()
    cur = con.cursor()
    data = cur.execute(
        """
        SELECT POST.*, USER.name, USER.username, USER.profile_picture,
               (SELECT COUNT(*) FROM LIKE WHERE LIKE.postID = POST.postID) as like_count
        FROM POST 
        JOIN USER ON POST.userID = USER.userID 
        WHERE POST.userID = ? AND POST.media_url IS NOT NULL
        ORDER BY POST.created_at DESC
        """,
        (userID,),
    ).fetchall()
    con.close()
    return data


def get_post_by_id(postID):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        """
        SELECT POST.*, USER.name, USER.username, USER.profile_picture,
               (SELECT COUNT(*) FROM LIKE WHERE LIKE.postID = POST.postID) as like_count
        FROM POST 
        JOIN USER ON POST.userID = USER.userID 
        WHERE POST.postID = ?
        """,
        (postID,),
    )
    post = cur.fetchone()
    con.close()
    return post


def delete_post(postID):
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM POST WHERE postID = ?", (postID,))
    con.commit()
    con.close()


# LIKE FUNCTIONS


def like_post(userID, postID):
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute(
            "INSERT INTO LIKE (userID, postID) VALUES (?, ?)",
            (userID, postID),
        )
        con.commit()
        con.close()
        return True
    except sql.IntegrityError:
        con.close()
        return False


def unlike_post(userID, postID):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "DELETE FROM LIKE WHERE userID = ? AND postID = ?",
        (userID, postID),
    )
    con.commit()
    con.close()


def is_post_liked_by_user(userID, postID):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "SELECT * FROM LIKE WHERE userID = ? AND postID = ?",
        (userID, postID),
    )
    like = cur.fetchone()
    con.close()
    return like is not None


def get_liked_posts_by_user(userID):
    con = get_connection()
    cur = con.cursor()
    data = cur.execute(
        """
        SELECT POST.*, USER.name, USER.username, USER.profile_picture,
               (SELECT COUNT(*) FROM LIKE WHERE LIKE.postID = POST.postID) as like_count
        FROM POST 
        JOIN USER ON POST.userID = USER.userID 
        JOIN LIKE ON POST.postID = LIKE.postID
        WHERE LIKE.userID = ?
        ORDER BY LIKE.created_at DESC
        """,
        (userID,),
    ).fetchall()
    con.close()
    return data


# FOLLOW FUNCTIONS


def follow_user(follower_id, following_id):
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute(
            "INSERT INTO FOLLOW (follower_id, following_id) VALUES (?, ?)",
            (follower_id, following_id),
        )
        con.commit()
        con.close()
        return True
    except sql.IntegrityError:
        con.close()
        return False


def unfollow_user(follower_id, following_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "DELETE FROM FOLLOW WHERE follower_id = ? AND following_id = ?",
        (follower_id, following_id),
    )
    con.commit()
    con.close()


def is_following(follower_id, following_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "SELECT * FROM FOLLOW WHERE follower_id = ? AND following_id = ?",
        (follower_id, following_id),
    )
    follow = cur.fetchone()
    con.close()
    return follow is not None


def get_followers_count(userID):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "SELECT COUNT(*) as count FROM FOLLOW WHERE following_id = ?",
        (userID,),
    )
    result = cur.fetchone()
    con.close()
    return result["count"]


def get_following_count(userID):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "SELECT COUNT(*) as count FROM FOLLOW WHERE follower_id = ?",
        (userID,),
    )
    result = cur.fetchone()
    con.close()
    return result["count"]


def get_followers(userID):
    con = get_connection()
    cur = con.cursor()
    data = cur.execute(
        """
        SELECT USER.* FROM USER
        JOIN FOLLOW ON USER.userID = FOLLOW.follower_id
        WHERE FOLLOW.following_id = ?
        ORDER BY FOLLOW.created_at DESC
        """,
        (userID,),
    ).fetchall()
    con.close()
    return data


def get_following(userID):
    con = get_connection()
    cur = con.cursor()
    data = cur.execute(
        """
        SELECT USER.* FROM USER
        JOIN FOLLOW ON USER.userID = FOLLOW.following_id
        WHERE FOLLOW.follower_id = ?
        ORDER BY FOLLOW.created_at DESC
        """,
        (userID,),
    ).fetchall()
    con.close()
    return data
