import sqlite3
import os
from werkzeug.security import generate_password_hash

# Create database directory if it doesn't exist
os.makedirs("database", exist_ok=True)

# Connect to database
conn = sqlite3.connect("database/data_source.db")
cursor = conn.cursor()

# Drop existing tables if they exist
cursor.execute("DROP TABLE IF EXISTS LIKE")
cursor.execute("DROP TABLE IF EXISTS FOLLOW")
cursor.execute("DROP TABLE IF EXISTS POST")
cursor.execute("DROP TABLE IF EXISTS USER")

# Create USER table with additional profile fields
cursor.execute(
    """
CREATE TABLE USER (
    userID INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    bio TEXT DEFAULT '',
    profile_picture TEXT DEFAULT 'avatar.jpg',
    banner_picture TEXT DEFAULT '',
    role TEXT DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
)

# Create POST table with media support
cursor.execute(
    """
CREATE TABLE POST (
    postID INTEGER PRIMARY KEY AUTOINCREMENT,
    userID INTEGER NOT NULL,
    content TEXT NOT NULL,
    media_url TEXT DEFAULT NULL,
    media_type TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (userID) REFERENCES USER(userID) ON DELETE CASCADE
)
"""
)

# Create LIKE table
cursor.execute(
    """
CREATE TABLE LIKE (
    likeID INTEGER PRIMARY KEY AUTOINCREMENT,
    userID INTEGER NOT NULL,
    postID INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (userID) REFERENCES USER(userID) ON DELETE CASCADE,
    FOREIGN KEY (postID) REFERENCES POST(postID) ON DELETE CASCADE,
    UNIQUE(userID, postID)
)
"""
)

# Create FOLLOW table
cursor.execute(
    """
CREATE TABLE FOLLOW (
    followID INTEGER PRIMARY KEY AUTOINCREMENT,
    follower_id INTEGER NOT NULL,
    following_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (follower_id) REFERENCES USER(userID) ON DELETE CASCADE,
    FOREIGN KEY (following_id) REFERENCES USER(userID) ON DELETE CASCADE,
    UNIQUE(follower_id, following_id)
)
"""
)

# Create test users
test_password = generate_password_hash("test123")
cursor.execute(
    """
INSERT INTO USER (name, username, email, password, bio, role)
VALUES (?, ?, ?, ?, ?, ?)
""",
    (
        "Test User",
        "testuser",
        "test@example.com",
        test_password,
        "Just a test user exploring this awesome platform! 🚀",
        "user",
    ),
)

test_user_id = cursor.lastrowid

cursor.execute(
    """
INSERT INTO USER (name, username, email, password, bio, role)
VALUES (?, ?, ?, ?, ?, ?)
""",
    (
        "John Doe",
        "johndoe",
        "john@example.com",
        test_password,
        "Tech enthusiast | Developer | Coffee lover ☕",
        "user",
    ),
)

john_id = cursor.lastrowid

cursor.execute(
    """
INSERT INTO USER (name, username, email, password, bio, role)
VALUES (?, ?, ?, ?, ?, ?)
""",
    (
        "Jane Smith",
        "janesmith",
        "jane@example.com",
        test_password,
        "Designer | Traveler | Making the web beautiful ✨",
        "user",
    ),
)

jane_id = cursor.lastrowid

# Create sample posts
sample_posts = [
    (
        test_user_id,
        "Just set up my new Twitter clone! This is pretty cool 🚀",
        None,
        None,
    ),
    (
        test_user_id,
        "Learning Flask has been an amazing journey. The framework is so intuitive!",
        None,
        None,
    ),
    (
        test_user_id,
        "Remember: Clean code is not just about making it work, it's about making it maintainable!",
        None,
        None,
    ),
    (john_id, "Hello world! First post on this platform.", None, None),
    (john_id, "Building something amazing today. Stay tuned! 💻", None, None),
    (
        jane_id,
        "Design is not just what it looks like. Design is how it works. - Steve Jobs",
        None,
        None,
    ),
    (
        jane_id,
        "Just finished a new project. Can't wait to share it with everyone!",
        None,
        None,
    ),
]

for user_id, content, media_url, media_type in sample_posts:
    cursor.execute(
        """
    INSERT INTO POST (userID, content, media_url, media_type)
    VALUES (?, ?, ?, ?)
    """,
        (user_id, content, media_url, media_type),
    )

# Create some sample follows
follows = [
    (test_user_id, john_id),
    (test_user_id, jane_id),
    (john_id, test_user_id),
    (jane_id, test_user_id),
    (john_id, jane_id),
]

for follower_id, following_id in follows:
    cursor.execute(
        """
    INSERT INTO FOLLOW (follower_id, following_id)
    VALUES (?, ?)
    """,
        (follower_id, following_id),
    )

# Create some sample likes
cursor.execute("SELECT postID FROM POST LIMIT 3")
posts = cursor.fetchall()

for post in posts:
    cursor.execute(
        """
    INSERT INTO LIKE (userID, postID)
    VALUES (?, ?)
    """,
        (john_id, post[0]),
    )

conn.commit()
conn.close()

print("Database initialized successfully!")
print("\nTest users created:")
print("  Email: test@example.com | Password: test123")
print("  Email: john@example.com | Password: test123")
print("  Email: jane@example.com | Password: test123")
print(f"\nSample posts created: {len(sample_posts)}")
print(f"Sample follows created: {len(follows)}")
