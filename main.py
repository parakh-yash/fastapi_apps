from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
import apps.unit_converter.uc as uc
import apps.todo.todo as todo

app = FastAPI()
app.include_router(uc.router)
app.include_router(todo.router)

