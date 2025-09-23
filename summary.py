
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

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")


# state schema 
class ExpenseState(TypedDict):
    id:str
    category:str
    amount:float
    expense_description:str
    date:date
    summary:str
    data_json:str


# define llm model 
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.0,
    max_retries=2,
    max_tokens=30,
    # other params...
)

  
# today_date = date.today().strftime("%Y-%m-%d").date  # to get todays time
# today_date = date.today()  
# print(type(today_date))
# print(today_date)



def expense_by_date(state:ExpenseState):
    
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row  # important: rows as dict-like
    cursor = conn.cursor()
    today_date = date.today().strftime("%Y-%m-%d")
    print(today_date)
    cursor.execute('SELECT * FROM expenses WHERE date=?', (today_date,))
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


def send_whatsapp_text(body:str,to:str=None):
    "send the Whatsapp message via Twilio"
    # to=to or _to_wa
    msg=_twilio(body=body,to=_to_wa,from_=_from_wa)
    print("Twilio SID:",msg.sid)

def send_to_whatsapp_node(state:ExpenseState):
    "LangGraph node:to send whatsapp messages"
    send_whatsapp_text(state["summary"])
    return {}

def summarize_expenses(state:ExpenseState):
    "lanngraph node to summarize_expenses"
    today_date = date.today().strftime("%Y-%m-%d")
    print(today_date)
    print(type(today_date))
    payload=expense_by_date(today_date)
    print(payload)
    messages = [
    (
        "system",
        "You are a helpful assistant that creates clear and concise daily expense summaries. "
        "Always group expenses by category, show totals, and provide a short overall summary. "
        "Keep the tone simple and friendly, suitable for sending as a WhatsApp message."
    ),
    (

        "human",
        f"Here is my daily expense data:\n\n{payload}\n\nPlease summarize the expenses clearly."
    ),
]
    result=llm.invoke(messages)
    print(result)

    return {'summary':result}



graph=StateGraph(ExpenseState)

# add nodes
graph.add_node('summarize_expenses',summarize_expenses)
# graph.add_node('send_to_whatsapp_node',send_to_whatsapp_node)

# add Edges
graph.add_edge(START,"summarize_expenses")
# graph.add_edge(summarize_expenses,END)
graph.add_edge('summarize_expenses',END)
# graph.add_edge("send_to_whatsapp_node",END)

# compile
workflow=graph.compile()

# execute
if __name__=="__main__":
     # Run the LangGraph workflow
    # today_date = date.today().strftime("%Y-%m-%d").date()
    # print(type(today_date))
    final_state = workflow.invoke({
    
    })

    print("Final State:", final_state)
    print("Daily expense summary sent to WhatsApp ✅")
    

















