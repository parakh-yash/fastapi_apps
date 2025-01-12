from fastapi import FastAPI
import apps.unit_converter.uc as uc

app = FastAPI()
app.include_router(uc.router)
