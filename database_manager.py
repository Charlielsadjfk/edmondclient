import sqlite3 as sql


def listExtension():
    con = sql.connect("database/data_source.db")
    cur = con.cursor()
    data = cur.execute("SELECT * FROM USER").fetchall()
    con.close()
    return data


def get_user_by_email(email):
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    u = cur.fetchone()
    con.close()
    return u


def get_user_by_id(userID):
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE userID = ?", (userID,))
    u = cur.fetchone()
    con.close()
    return u


def create_user(name, email, password, role):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
        (name, email, password, role),
    )
    con.commit()
    con.close()


def update_user(userID, name=None, email=None, password=None):
    # only update the provided fields
    con = get_connection()
    cur = con.cursor()
    if name:
        cur.execute("UPDATE users SET name = ? WHERE userID = ?", (name, userID))
    if email:
        cur.execute("UPDATE users SET email = ? WHERE userID = ?", (email, userID))
    if password:
        cur.execute(
            "UPDATE users SET password = ? WHERE userID = ?", (password, userID)
        )
    con.commit()
    con.close()
