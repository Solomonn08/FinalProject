import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)
DB_FILE = "assignments.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                title TEXT NOT NULL,
                due_date TEXT NOT NULL
            )
        """)

@app.route('/')
def index():
    today = datetime.now().date()
    with sqlite3.connect(DB_FILE) as conn:
        # Sorting by due_date ASC so the most urgent is at the top
        cursor = conn.execute("SELECT * FROM assignments ORDER BY due_date ASC")
        rows = cursor.fetchall()
    
    # We pass 'today' to the template to highlight overdue items
    return render_template('index.html', assignments=rows, today=str(today))

@app.route('/add', methods=['POST'])
def add_assignment():
    subject = request.form.get('subject')
    title = request.form.get('title')
    due_date = request.form.get('due_date') # Format: YYYY-MM-DD from HTML5 date picker

    if subject and title and due_date:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("INSERT INTO assignments (subject, title, due_date) VALUES (?, ?, ?)",
                         (subject, title, due_date))
    return redirect(url_for('index'))

@app.route('/delete/<int:item_id>')
def delete_assignment(item_id):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("DELETE FROM assignments WHERE id = ?", (item_id,))
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)