import sqlite3
import os
from werkzeug.security import generate_password_hash

# Create database directory if it doesn't exist
os.makedirs("database", exist_ok=True)

# Connect to database
conn = sqlite3.connect("database/data_source.db")
cursor = conn.cursor()

# Drop existing tables if they exist
cursor.execute("DROP TABLE IF EXISTS POST")
cursor.execute("DROP TABLE IF EXISTS USER")

# Create USER table
cursor.execute(
    """
CREATE TABLE USER (
    userID INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
)

# Create POST table
cursor.execute(
    """
CREATE TABLE POST (
    postID INTEGER PRIMARY KEY AUTOINCREMENT,
    userID INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (userID) REFERENCES USER(userID) ON DELETE CASCADE
)
"""
)

# Create a test user
test_password = generate_password_hash("test123")
cursor.execute(
    """
INSERT INTO USER (name, username, email, password, role)
VALUES (?, ?, ?, ?, ?)
""",
    ("Test User", "testuser", "test@example.com", test_password, "user"),
)

# Get the test user ID
test_user_id = cursor.lastrowid

# Create some sample posts for the test user
sample_posts = [
    "Just set up my new Twitter clone! This is pretty cool 🚀",
    "Learning Flask has been an amazing journey. The framework is so intuitive!",
    "Remember: Clean code is not just about making it work, it's about making it maintainable!",
]

for post_content in sample_posts:
    cursor.execute(
        """
    INSERT INTO POST (userID, content)
    VALUES (?, ?)
    """,
        (test_user_id, post_content),
    )

conn.commit()
conn.close()

print("Database initialized successfully!")
print("Test user created:")
print("  Email: test@example.com")
print("  Password: test123")
print(f"  Sample posts created: {len(sample_posts)}")
