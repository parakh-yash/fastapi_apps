from pydantic import BaseModel

class User(BaseModel):
    email: str | None = None
    full_name: str | None = None

class Token(BaseModel):
    access_token: str
    token_type: str

class UserInDB(User):
    password: str
