
from utils import *
import json 
from datetime import date
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.schema.messages import SystemMessage, HumanMessage
import os
from dotenv import load_dotenv

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")



  
today_date = date.today().strftime("%Y-%m-%d")  # to get todays time
def expense_by_date(date):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row  # important: rows as dict-like
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM expenses WHERE date=?', (date,))
    rows = cursor.fetchall()

     # for row in rows:
     #      print(row['id'])
     #      print(row['amount'])
     #      print(row['expense_description'])
     #      print(row['category'])
     #      print('*'*30)

    # Convert rows to list of dicts
    data = [dict(row) for row in rows]

    # Convert to JSON string
    data_json = json.dumps(data, indent=4)

    conn.close()
    return data_json

payload=expense_by_date(today_date)
print(payload)



llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.0,
    max_retries=2,
    # other params...
)

messages = [
    ("system", "You are a helpful expense summarizer. plaese make a summary of my daily expense data"),
    ("human", f"{payload}"),
]

result=llm.invoke(messages)
print(result)


