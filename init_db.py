import sqlite3
import os
from werkzeug.security import generate_password_hash

# Create database directory if it doesn't exist
os.makedirs("database", exist_ok=True)

# Connect to database
conn = sqlite3.connect("database/data_source.db")
cursor = conn.cursor()

# Drop existing USER table if it exists
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

# Create a test user (optional)
test_password = generate_password_hash("test123")
cursor.execute(
    """
INSERT INTO USER (name, username, email, password, role)
VALUES (?, ?, ?, ?, ?)
""",
    ("Test User", "testuser", "test@example.com", test_password, "user"),
)

conn.commit()
conn.close()

print("Database initialized successfully!")
print("Test user created:")
print("  Email: test@example.com")
print("  Password: test123")
