import schedule
from datetime import date,datetime
import time
from summary import * # import your workflow from summary.py

def task1():
    print("📌 Running daily expense workflow...")
    # today_date = date.today().strftime("%Y-%m-%d")
    # try:
    #     print(type(today_date))
    #     final_state = workflow.invoke({
    #     'date':today_date
    #     })
    #     # final_state = workflow.invoke({})
    #     print("✅ Workflow finished:", final_state)
    # except Exception as e:
    #     print("❌ Error while running workflow:", e)


    today_date = date.today().strftime("%Y-%m-%d")
    print(type(today_date))
    final_state = workflow.invoke({
    'date':today_date
    })

    print("Final State:", final_state)
    print("Daily expense summary sent to WhatsApp ✅")

task1()


 # today_date = date.today().strftime("%Y-%m-%d")
    # # print(type(today_date))
    # final_state = workflow.invoke({
    # 'date':today_date
    # })

    # print("Final State:", final_state)
    # print("Daily expense summary sent to WhatsApp ✅")

# Run every day at 9:00 AM
# schedule.every().day.at("09:00").do(task1)

# print("⏳ Scheduler started... Waiting for 09:00 AM every day.")
# while True:  #it's like staying awake to check the clock.
#     schedule.run_pending()   
#     time.sleep(60)
