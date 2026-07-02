"""
Idempotent script to add is_admin column to the users table in SQLite database.
"""

import os
import sqlite3
import sys

def main():
    # Set search path to current script dir to resolve relative configs
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Load dotenv if exists
    if os.path.exists(".env"):
        from dotenv import load_dotenv
        load_dotenv()
        
    db_url = os.getenv("DATABASE_URL", "sqlite:///./learning_insight.db")
    
    # Parse SQLite db path
    if not db_url.startswith("sqlite:///"):
        print(f"Error: DATABASE_URL must be sqlite:/// database. Found: {db_url}")
        sys.exit(1)
        
    db_path = db_url.replace("sqlite:///", "")
    print(f"Target database file: {os.path.abspath(db_path)}")
    
    if not os.path.exists(db_path):
        print(f"Error: Database file does not exist at {db_path}")
        sys.exit(1)
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        if not cursor.fetchone():
            print("Error: 'users' table does not exist in the database.")
            conn.close()
            sys.exit(1)
            
        # Check for is_admin column using PRAGMA
        cursor.execute("PRAGMA table_info(users);")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "is_admin" not in columns:
            print("Column 'is_admin' not found. Altering table...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0 NOT NULL;")
            conn.commit()
            print("SUCCESS: Column 'is_admin' added to 'users' table.")
        else:
            print("Column 'is_admin' already exists in 'users' table (Idempotent: skipping ALTER).")
            
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
