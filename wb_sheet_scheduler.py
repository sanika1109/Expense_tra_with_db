import schedule
from datetime import date,datetime
import time
from summary import * # import your workflow from summary.py

def task1():
   
    try:
        print("📌 Running daily expense workflow...")
        today_date = date.today().strftime("%Y-%m-%d")
        print(type(today_date))
        final_state = workflow.invoke({
        'date':today_date
        })

        print("Final State:", final_state)
        print("Daily expense summary sent to WhatsApp ✅")
    except Exception as e:
        print("❌ Error while running workflow:", e)

task1()
# Run every day at 11:00 PM
schedule.every().day.at("23:01").do(task1)
schedule.every().day.at("23:00").do(task1)


print("⏳ Scheduler started... Waiting for 11:00 PM every day.")
while True:  #it's like staying awake to check the clock.
    schedule.run_pending()   
    time.sleep(60)

