### all helper functions are defined here ###
import sqlite3 

DB_NAME = "sample.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)  # allow cross-thread use
    conn.row_factory = sqlite3.Row
    return conn


conn=get_db_connection() # create a cursor object to execute SQL commands
cursor=conn.cursor()
cursor.execute('''
     CREATE TABLE IF NOT EXISTS expenses (
          id TEXT PRIMARY KEY, 
          category TEXT NOT NULL,
          amount FLOAT NOT NULL CHECK (amount > 0.0),
          expense_description TEXT NOT NULL,
          date TEXT NOT NULL)
            ''')


def calculate_total_expense():
     conn=get_db_connection()
     cursor=conn.cursor()
     cursor.execute("SELECT SUM(amount) FROM expenses")
     total=cursor.fetchone()[0]
     conn.close()
     print('***'*10)
     print("Total Expense:", total)
     return total if total else 0.0 