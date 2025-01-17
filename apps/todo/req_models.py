from pydantic import BaseModel

class RegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TaskRequest(BaseModel):
    title: str | None = None
    description: str | None = None