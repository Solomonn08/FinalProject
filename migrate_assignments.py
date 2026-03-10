import sqlite3
import json

# 1. YOUR JSON DATA
# Replace the content between the triple quotes with your actual JSON
json_data = '''
[
    {
        "subject": "Mathematics",
        "title": "Calculus Problem Set 4",
        "due_date": "2026-03-15"
    },
    {
        "subject": "History",
        "title": "French Revolution Essay",
        "due_date": "2026-03-20"
    },
    {
        "subject": "Computer Science",
        "title": "SQLite Migration Lab",
        "due_date": "2026-03-04"
    }
]
'''

DB_FILE = "assignments.db"

def migrate():
    # Load the JSON
    try:
        data = json.loads(json_data)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
        return

    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Ensure the table exists (matching the structure in your app-1.py)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            title TEXT NOT NULL,
            due_date TEXT NOT NULL
        )
    """)

    print(f"Migrating {len(data)} assignments...")

    # Insert the data using parameterized queries (Security best practice)
    for item in data:
        cursor.execute(
            "INSERT INTO assignments (subject, title, due_date) VALUES (?, ?, ?)",
            (item['subject'], item['title'], item['due_date'])
        )

    conn.commit()
    conn.close()
    print("Migration complete! You can now run 'python app-1.py'.")

if __name__ == "__main__":
    migrate()