import sqlite3
from datetime import datetime, date  

DB_NAME = "expenses.db"

def init_db():
    """
    Idempotent function: Creates the table if it doesn't exist.
    Safe to call multiple times.
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT NOT NULL,
                email_subject TEXT,
                amount REAL,
                currency TEXT,
                transaction_date DATE,
                email_id TEXT UNIQUE
            )
        ''')
        conn.commit()
    except Exception as e:
        print(f"DB Init Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def save_expense(service, subject, amount, currency, date_obj, email_id):
    """Transactional save to ensure data integrity."""
    init_db() # Ensure table exists before writing
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''
            INSERT OR IGNORE INTO expenses 
            (service_name, email_subject, amount, currency, transaction_date, email_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (service, subject, amount, currency, date_obj, email_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"[Critical Error] DB Save failed: {e}")
        return False
    finally:
        conn.close()

def get_all_expenses():
    """Fetches expenses, ensuring DB exists first."""
    init_db() 
    
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    try:
        c.execute("SELECT * FROM expenses ORDER BY transaction_date DESC")
        rows = c.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()

def get_latest_transaction_date(service_name):
    """
    Returns the latest transaction date for a specific service.
    If no data exists, returns Jan 1, 2024.
    """
    init_db()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        # We use LIKE to make it case-insensitive (Uber vs uber)
        c.execute('''
            SELECT MAX(transaction_date) FROM expenses 
            WHERE service_name LIKE ?
        ''', (f"{service_name}%",))
        
        result = c.fetchone()
        
        if result and result[0]:
            # Convert string date from DB back to date object
            # Because we imported 'datetime' from 'datetime', we use datetime.strptime
            return datetime.strptime(result[0], "%Y-%m-%d").date()
        else:
            # Default fallback if DB is empty for this service
            return date(2024, 1, 1)
            
    except Exception as e:
        print(f"Error fetching last date: {e}")
        # Default fallback on error
        return date(2024, 1, 1)
    finally:
        conn.close()