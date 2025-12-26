import sqlite3
import json
import os
import time
from app.db.fake_db import fake_users_db, fake_quizzes_db
import shutil
from pathlib import Path

DB_FILE = "exam_mate.db"
USER_UPLOAD_DIR = Path("user_upload")

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_tables(conn):
    try:
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                full_name TEXT,
                email TEXT,
                hashed_password TEXT,
                disabled BOOLEAN,
                created_at INTEGER
            );
        """)
        
        # Create quizzes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quizzes (
                quiz_id TEXT PRIMARY KEY,
                owned_by TEXT,
                access TEXT,
                quiz_title TEXT,
                created_at INTEGER,
                FOREIGN KEY (owned_by) REFERENCES users (username)
            );
        """)
        
        # Create questions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                unique_id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_id TEXT,
                id TEXT,
                question TEXT,
                options TEXT,
                answer_index INTEGER,
                correct_answer TEXT,
                why_correct TEXT,
                created_at INTEGER,
                FOREIGN KEY (quiz_id) REFERENCES quizzes (quiz_id)
            );
        """)

        # Create documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                filename TEXT,
                file_path TEXT,
                owner TEXT,
                summary TEXT,
                created_at INTEGER,
                disabled BOOLEAN,
                FOREIGN KEY (owner) REFERENCES users (username)
            );
        """)

        # Create schedule table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schedule (
                id TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                start_date INTEGER,
                end_date INTEGER,
                created_at INTEGER,
                updated_at INTEGER,
                owned_by TEXT,
                FOREIGN KEY (owned_by) REFERENCES users (username)
            );
        """)
        
        conn.commit()
    except sqlite3.Error as e:
        print(e)

def insert_data(conn):
    cursor = conn.cursor()
    current_time = int(time.time())
    
    # Insert users
    for username, user_data in fake_users_db.items():
        cursor.execute("""
            INSERT OR IGNORE INTO users (username, full_name, email, hashed_password, disabled, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_data["username"],
            user_data.get("full_name"),
            user_data.get("email"),
            user_data.get("hashed_password"),
            user_data.get("disabled"),
            current_time
        ))
        
    # Handle implicit users in quizzes (e.g. 'notjohndoe')
    existing_users = set(fake_users_db.keys())
    for quiz in fake_quizzes_db:
        owner = quiz["owned_by"]
        if owner not in existing_users:
            # Insert a placeholder user
            print(f"Adding implicit user: {owner}")
            cursor.execute("""
                INSERT OR IGNORE INTO users (username, full_name, email, hashed_password, disabled, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (owner, owner, None, "placeholder", False, current_time))
            existing_users.add(owner)

    # Insert quizzes and questions
    for quiz in fake_quizzes_db:
        cursor.execute("""
            INSERT OR IGNORE INTO quizzes (quiz_id, owned_by, access, quiz_title, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            quiz["quiz_id"],
            quiz["owned_by"],
            quiz["access"],
            quiz["quiz_title"],
            current_time
        ))
        
        for q in quiz["questions"]:
            cursor.execute("""
                INSERT INTO questions (quiz_id, id, question, options, answer_index, correct_answer, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                quiz["quiz_id"],
                q["id"],
                q["question"],
                json.dumps(q["options"]),
                q["answer_index"],
                q["correct_answer"],
                current_time
            ))
            
    conn.commit()
    print("Data inserted successfully.")

def main():
    if os.path.exists(DB_FILE):
        print("Database file exists. Removing...")
        try:
            os.remove(DB_FILE)
            print("Database file removed.")
        except PermissionError:
            print(f"Error: Could not remove {DB_FILE}. It might be in use.")
            return
    if USER_UPLOAD_DIR.exists() and USER_UPLOAD_DIR.is_dir():
        print("User upload directory exists. Removing...")
        shutil.rmtree(USER_UPLOAD_DIR)
        print("User upload directory removed.")

    conn = create_connection()
    if conn:
        create_tables(conn)
        # insert_data(conn)
        conn.close()

if __name__ == '__main__':
    main()
