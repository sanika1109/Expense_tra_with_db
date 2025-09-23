
from utils import *
import json 
from datetime import date
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.schema.messages import SystemMessage, HumanMessage
import os
from dotenv import load_dotenv
from typing import TypedDict
from twilio.rest import Client
from langgraph.graph import StateGraph,START,END
import os, requests, gspread
from google.oauth2.service_account import Credentials

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")


# state schema 
class ExpenseState(TypedDict):
    date:str
    summary:str
    data_json:str


# define llm model 
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.0,
    max_retries=2,
    # max_tokens=30,
    # other params...
)



def expense_by_date(state:ExpenseState):
    
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row  # important: rows as dict-like
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM expenses WHERE date=?', (state["date"],))
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
    json_data = json.dumps(data, indent=4)

    conn.close()
    return {'data_json':json_data}



##### Twilio setup for sending summary to whatsapp
_account_sid=os.getenv("TWILIO_ACCOUNT_SID")
_auth_token=os.getenv("TWILIO_AUTH_TOKEN")
_from_wa=os.getenv("TWILIO_WHATSAPP_FROM")
_to_wa=os.getenv("TWILIO_WHATSAPP_TO")

_twilio=Client(_account_sid,_auth_token)

# fuction to send actual summary to WB
def send_whatsapp_text(body:str,to:str=None):
    "send the Whatsapp message via Twilio"
    msg=_twilio.messages.create(from_=_from_wa,to=_to_wa,body=body)
    print("Twilio SID:",msg.sid)

# node for send summary to whatsapp 
def send_to_whatsapp_node(state:ExpenseState):
    "LangGraph node:to send whatsapp messages"
    # print("###"*12)
    # print(state["summary"])
    send_whatsapp_text(state["summary"])
    return {}

# node to generate summary from json data using LLM
def summarize_expenses(state:ExpenseState):
    "lanngraph node to summarize_expenses"
    payload=state["data_json"]
    # print(payload)
    messages = [
    (
        "system",
        "You are a helpful assistant that creates clear and concise daily expense summaries. "
         "Your tasks:\n"
        "1. Group expenses by category.\n"
        "2. Show totals per category and the grand total.\n"
        "3. Provide a short, friendly summary description.\n"
        "4. Use simple, WhatsApp-friendly language with emojis.\n"
        "5. Do NOT use symbols like *, #, $, or bullet points. "
        "Instead, keep formatting natural (plain text + emojis).\n"
        "6. Make it short and easy to read in a single WhatsApp message."
        "7.also provide a short description of each expense"
    ),
    (

        "human",
        f"Here is my daily expense data:\n\n{payload}\n\nPlease summarize the expenses clearly."
    ),
]
    result=llm.invoke(messages)
    # print(result)

    return {'summary':result.content}


# def log_to_news_google_sheet(state:ExpenseState):
#     """Log message to Google Sheet"""
#     # Google Sheets setup
#     SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
#     creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPE)
#     client = gspread.authorize(creds)
#     sheet_id = os.getenv("SHEET_ID") # os.getenv("SHEET_NAME")
#     workbook = client.open_by_key(sheet_id)  # First sheet
#     users_sheet = workbook.worksheet("sept_sheet")

#       # ✅ Ensure headers exist
#     headers = users_sheet.row_values(1)  # first row
#     if headers != ["Date", "Expense_summary"]:
#         users_sheet.update("A1:B1", [["Date", "Expense_summary"]])
    
#     users_sheet.append_row([state['date'],state['summary']])

#     return {}

#     # Current date
#     # date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#     # Each row will be: [Date, Message]
#     # for msg in messages:
#     #     users_sheet.append_row([date_str, msg])


def log_to_news_google_sheet(state:ExpenseState):
    """Log message to Google Sheet"""
    # Google Sheets setup
    SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPE)
    client = gspread.authorize(creds)
    sheet_id = os.getenv("SHEET_ID") # os.getenv("SHEET_NAME")
    workbook = client.open_by_key(sheet_id)  # First sheet


    sheet_name=state["date"].split('-')[1]+"_sheet"
    print('######'*30)
    print(sheet_name)
    try:
        users_sheet = workbook.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        users_sheet = workbook.add_worksheet(title=sheet_name, rows=100, cols=2)
        # users_sheet.update("A1:B1", [["Date", "Expense_summary"]])  # add headers
        headers = users_sheet.row_values(1)  # first row
        if headers != ["Date", "Expense_summary"]:
            users_sheet.update("A1:B1", [["Date", "Expense_summary"]])

    #Check if date already exists in first column
    existing_dates = users_sheet.col_values(1)  # all values in column A
    if state['date'] not in existing_dates:
        users_sheet.append_row([state['date'],state["summary"]])
        print(f"Added new entry for {state['date']}")
    else:
        print(f"{state['date']} Already exists,skipping entry...")
        
        
    return {}



graph=StateGraph(ExpenseState)

# add nodes
graph.add_node('expense_by_date',expense_by_date)
graph.add_node('summarize_expenses',summarize_expenses)
graph.add_node('send_to_whatsapp_node',send_to_whatsapp_node)
graph.add_node('log_to_news_google_sheet',log_to_news_google_sheet)

# add Edges
graph.add_edge(START,"expense_by_date")
graph.add_edge('expense_by_date','summarize_expenses')
graph.add_edge('summarize_expenses','send_to_whatsapp_node')
graph.add_edge('send_to_whatsapp_node','log_to_news_google_sheet')
graph.add_edge('log_to_news_google_sheet',END)

# compile
workflow=graph.compile()

# execute
if __name__=="__main__":
    today_date = date.today().strftime("%Y-%m-%d")
    # print(type(today_date))
    final_state = workflow.invoke({
    'date':today_date
    })

    print("Final State:", final_state)
    print("Daily expense summary sent to WhatsApp ✅")
    

















