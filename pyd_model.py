from datetime import date 
from pydantic import BaseModel,Field,computed_field
from typing import List,Dict,Optional,Annotated,Literal
import json, requests, time

### pydactic model for validation
class Expense(BaseModel):
    id:Annotated[str,Field(...,title="id of expense",strict=True)]
    category:Annotated[Literal['food','travel','entertainment','shopping','health','education','others'],Field(...,title ="category of expense",description="Enter the category of expense from food,travel,entertainment,shopping,health,education,others")]
    amount:Annotated[float,Field(...,gt=0.0,strict=True,title="amount of expense",description="Enter the amount of expense greater than 0.0")]
    expense_description:Annotated[str,Field(...,max_length=100,title='description of expense',description="enter the description of expense less than 100 chars")]
    date:Annotated[date,Field(...,title="date of expense",description="Enter the date of expense in YYYY-MM-DD format")]

class UpdateExpense(BaseModel):
    category:Annotated[Optional[Literal['food','travel','entertainment','shopping','health','education','others']],Field(default=None,title ="category of expense",description="Enter the category of expense from food,travel,entertainment,shopping,health,education,others")]
    amount:Annotated[Optional[float],Field(default=None,gt=0.0,strict=True,title="amount of expense",description="Enter the amount of expense greater than 0.0")]
    expense_description:Annotated[Optional[str],Field(default=None,max_length=100,title='description of expense',description="enter the description of expense less than 100 chars")]
    date:Annotated[Optional[date],Field(default=None,title="date of expense",description="Enter the date of expense in YYYY-MM-DD format")]

