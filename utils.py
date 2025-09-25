### all helper functions are defined here ###
import sqlite3 
from fastapi import HTTPException

DB_NAME = "sample.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)  # allow cross-thread use
    conn.row_factory = sqlite3.Row
    return conn


conn=get_db_connection() # create a cursor object to execute SQL commands
cursor=conn.cursor()
# cursor.execute("DROP TABLE IF EXISTS expenses")
cursor.execute('''
     CREATE TABLE IF NOT EXISTS users(
               u_id INTEGER PRIMARY KEY AUTOINCREMENT,
               user_name TEXT UNIQUE NOT NULL,
               user_pass TEXT NOT NULL
               )
''')

cursor.execute('''
     CREATE TABLE IF NOT EXISTS expenses(
          id INTEGER PRIMARY KEY AUTOINCREMENT, 
          category TEXT NOT NULL,
          amount FLOAT NOT NULL CHECK (amount > 0.0),
          expense_description TEXT NOT NULL,
          date TEXT NOT NULL,
          user_id INTERGER NOT NULL,
          FOREIGN KEY(user_id) REFERENCES users(u_id))
               
            ''')

cursor.execute('''
     CREATE TABLE IF NOT EXISTS sessions (
          session_id TEXT PRIMARY KEY,
          user_id INTEGER NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(user_id) REFERENCES users(u_id)
     )

''')



def calculate_total_expense(user_id:int):
     conn=get_db_connection()
     cursor=conn.cursor()
     cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id=?",(user_id,))
     total=cursor.fetchone()[0]
     # cursor.execute("SELECT * FROM expenses WHERE user_id=?",(user_id,) )
     conn.close()
     print('***'*10)
     print("Total Expense:", total)
     return total if total else 0.0 




def get_user_from_session(session_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM sessions WHERE session_id=?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return row["user_id"]
