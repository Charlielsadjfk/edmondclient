import sqlite3 as sql
import os


def get_connection():
    db_path = os.path.join(os.path.dirname(__file__), "database", "data_source.db")
    con = sql.connect(db_path)
    con.row_factory = sql.Row
    return con


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


def update_user(userID, name=None, username=None, email=None, password=None):
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

    con.commit()
    con.close()


def delete_user(userID):
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM USER WHERE userID = ?", (userID,))
    con.commit()
    con.close()


# POST FUNCTIONS


def create_post(userID, content):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO POST (userID, content) VALUES (?, ?)",
        (userID, content),
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
        SELECT POST.*, USER.name, USER.username 
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
        SELECT POST.*, USER.name, USER.username 
        FROM POST 
        JOIN USER ON POST.userID = USER.userID 
        WHERE POST.userID = ?
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
        SELECT POST.*, USER.name, USER.username 
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
