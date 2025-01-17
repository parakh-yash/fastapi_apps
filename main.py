from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
import apps.unit_converter.uc as uc
import apps.todo.todo as todo

description = """
Please find apis for different projects 
"""

app = FastAPI(
    title= "Yash Parakh FastAPI Projects",
    description= description
)
app.include_router(uc.router)
app.include_router(todo.router)

