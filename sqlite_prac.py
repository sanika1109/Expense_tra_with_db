from fastapi import FastAPI,Path,HTTPException,Query
from datetime import datetime ,date 
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel,Field,computed_field
from typing import List,Dict,Optional,Annotated,Literal
import json, requests, time
import sqlite3  # import sqlite3 module to interact with SQLite database
from pyd_model import *
from utils import *

app=FastAPI()

# DB_NAME = "sample.db"


# def get_db_connection():
#     conn = sqlite3.connect(DB_NAME, check_same_thread=False)  # allow cross-thread use
#     conn.row_factory = sqlite3.Row
#     return conn


# conn=get_db_connection() # create a cursor object to execute SQL commands
# cursor=conn.cursor()
# cursor.execute('''
#      CREATE TABLE IF NOT EXISTS expenses (
#           id TEXT PRIMARY KEY, 
#           category TEXT NOT NULL,
#           amount FLOAT NOT NULL CHECK (amount > 0.0),
#           expense_description TEXT NOT NULL,
#           date TEXT NOT NULL)
#             ''')


# def calculate_total_expense():
#      conn=get_db_connection()
#      cursor=conn.cursor()
#      cursor.execute("SELECT SUM(amount) FROM expenses")
#      total=cursor.fetchone()[0]
#      conn.close()
#      print('***'*10)
#      print("Total Expense:", total)
#      return total if total else 0.0 

@app.get("/")
def welcome_page():
     return {'message':'WELCOME TO EXPENSE TRACKER'}

@app.get("/get_expenses")
def get_expenses(): 
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows] # return list of dicts


@app.post('/add_expense')
def add_expense(expense:Expense): # expense is an instance of Expense model
     conn = get_db_connection()
     cursor = conn.cursor()
     cursor.execute("SELECT * FROM expenses")
     rows = cursor.fetchall()
     print(rows)
     for row in rows:
          if expense.id == row['id']:
               raise HTTPException(status_code=400, detail="Expense with this id already exists")
     cursor.execute("INSERT INTO expenses(id,category,amount,expense_description,date) VALUES(?,?,?,?,?)"
                    ,(expense.id, expense.category, expense.amount, expense.expense_description, expense.date))
     
     total_expense=calculate_total_expense()
     conn.commit()
     conn.close()
     return JSONResponse(status_code=202,content={"message":"Expense added successfully","Your Total Expense ":total_expense})
     # return JSONResponse(status_code=202,content={"message":"Expense added successfully","Your Total Expense ":total_expense})

     #    data=load_data()
     #    print(data)
     #    if expense.id in data:
     #         raise HTTPException(status_code=400,detail="expense with this id already exists")
        
     #    data[expense.id]=expense.model_dump(exclude=['id']) #exclude id field from model_dump
     #    print('****'*15)
     #    print(data)
     #    save_to_json(data)
     #    total_expense=calculate_total_expenses(data)
     #    return {"message":"Expense added successfully","Your Total Expense ":total_expense}
     #    # return JSONResponse(status_code=202,content={"message":"Expense added successfully"})
    
@app.put('/update_expense/{expense_id}')
def update_expense(expense_id:str,expense_update:UpdateExpense):
     conn = get_db_connection()
     cursor = conn.cursor()
     cursor.execute("SELECT * FROM expenses WHERE id=?", (expense_id,))
     row = cursor.fetchone()
     print(dict(row))
     print('##########'*10)
     print(expense_update)
     print('##########'*10)
     if not row:
        raise HTTPException(status_code=404, detail="Expense not found")

     #### 
     # amount=expense_update.amount
     # if amount is not None :
     #      amount=expense_update.amount
     # else:
     #      amount=row['amount']

     #### OR SIMPLER WAY
     # amount=expense_update.amount if expense_update.amount is not None else row['amount']
     # category= expense_update.category if expense_update.category is not None else row['category']
     # expense_update_description=expense_update.expense_description if expense_update.expense_description is not None else row['expense_description']
     # date=expense_update.date if expense_update.date is not None else row['date']         

     # cursor.execute('''
     #      UPDATE expenses SET category=?,amount=?,expense_description=?,date=? WHERE id=?'''
     # ,(category,amount,expense_update_description,date,expense_id))

     ##### OR USE COALESCE FUNCTION OF SQLITE
     cursor.execute("""
          UPDATE expenses
          SET category = COALESCE(?, category),
              amount = COALESCE(?, amount),
              expense_description = COALESCE(?, expense_description),
              date = COALESCE(?, date)
          WHERE id = ?
     """, (
          expense_update.category,
          expense_update.amount,
          expense_update.expense_description,
          expense_update.date,
          expense_id
     ))

     conn.commit()

     total_expense=calculate_total_expense()
     conn.close()

     return {"message":"Expense updated successfully","Updated Expense Info":expense_update,"your total expense ":total_expense}



@app.delete('/delete_expense/{expense_id}')
def delete_expense(expense_id:str):
     conn = get_db_connection()
     cursor = conn.cursor()
     cursor.execute("SELECT * FROM expenses WHERE id=?", (expense_id,))
     row = cursor.fetchone()
     if not row:
          raise HTTPException(status_code=404, detail="Expense not found")
     
     cursor.execute("DELETE FROM expenses WHERE id=?",(expense_id,))
     conn.commit()
     total_expense=calculate_total_expense()
     conn.close()
     return {'message':'Expenes deleted successfully ','your total expense':total_expense}

@app.get('/get_expense_by_id/{expense_id}')
def get_expense__by_id(expense_id:str=Path(...,title="id of expense",description="Enter the id of expense to get the details of expense",min_length=1)):
     conn = get_db_connection()
     cursor = conn.cursor()
     cursor.execute("SELECT * FROM expenses WHERE id=?", (expense_id,))
     row = cursor.fetchone()
     conn.close()
     if row:
          return dict(row)
     else:
          raise HTTPException(status_code=404, detail="Expense not found")
          # return {'error':'Expense not found'}

@app.get('/get_expense_by_range')
def get_expense_by_range(
    start_date: str = Query(..., description="Enter the start date in YYYY-MM-DD format"),
    end_date: str = Query( date.today().strftime("%Y-%m-%d"), description="Enter the end date in YYYY-MM-DD format"),
):

     try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
     except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
     conn = get_db_connection()
     cursor=conn.cursor()
     cursor.execute("SELECT amount FROM expenses WHERE date BETWEEN ? AND ?", (start_date, end_date))
     rows=cursor.fetchall()
     total_expense=sum(row['amount'] for row in rows)
     print('Total expense in this date range:', total_expense)
     conn.close()

    
     return JSONResponse(status_code=200,content={'messges':'Expense fetched successfully',
                                                  f'your total expense in {start_date} to {end_date} is':total_expense})

@app.get('/get_expense_by_month')
def get_expense_by_month(
     month: str = Query(..., description="Enter the month in MM format"),
     year: str = Query(..., description="Enter the year in YYYY format"),
):
     conn=get_db_connection()
     cursor=conn.cursor()
     cursor.execute("SELECT amount FROM expenses WHERE strftime('%m', date)=? AND strftime('%Y', date)=?", (month, year))
     rows=cursor.fetchall()
     total_expense=sum(row['amount'] for row in rows)
     print('Total expense in this month:', total_expense)
     conn.commit()
     conn.close()
     return JSONResponse(status_code=200, content={'messages':'Expense fetched successfully',
                                                   f'Your total expense in month {month} of year {year} is ':total_expense})
@app.get('/get_expnese_by_category')
def get_expense_by_category(
     category:str=Query(...,description="Enter the valid category")
):   
     try:
          conn=get_db_connection()
          cursor=conn.cursor()
          cursor.execute("SELECT category FROM expenses")
          rows=cursor.fetchall()
          conn.close
          cat_list=[]
          for row in rows:
               cat_dict=dict(row)
               cat_list.append(cat_dict)
          # return f'{cat_list}'
          
     except:
          HTTPException(status_code=500,detail="Unable to conntect the database")
     
    
     final_cat_list=[item["category"] for item in cat_list]
     display_cat_list=set(final_cat_list)
     if category not in final_cat_list:
          return JSONResponse(status_code=404,content={"messsges":"enter valid cat ","Please select category from this":f"{display_cat_list}"})

     
     cursor.execute("SELECT amount FROM expenses WHERE category=?",(category,))
     amounts=cursor.fetchall()
     # amount_list=[]
     # for amount in amounts:
     #      amount_dict=dict(amount)
     #      amount_list.append(amount_dict)
     conn.commit()
     total_amount=sum(amount['amount'] for amount in amounts)
     conn.close()
     return f'{total_amount}'


     
@app.get('/get_expense_by_date')
def get_expense_by_date(
     date:str=Query(...,description='Enter the date in form of YYYY-MM-DD')
):
     conn=get_db_connection()
     cursor=conn.cursor()
     cursor.execute('SELECT amount from expenses where date=?',(date,))
     rows=cursor.fetchall()
     conn.commit()
   
     total_expense=sum(row['amount'] for row in rows)
     conn.close()
     return JSONResponse(status_code=200,content={'messgae':f'your total expense of {date} is  {total_expense}',})




if __name__=='__main__':
     uvicorn.run("sqlite_prac:app",host='127.0.0.1',port=8000,reload=True) 









