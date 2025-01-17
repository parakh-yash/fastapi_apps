
from apps.todo.db import execute_query
from passlib.context import CryptContext
from apps.todo.models import UserInDB, User, Token
from datetime import timedelta, datetime, timezone
import jwt
from jwt.exceptions import InvalidTokenError
import os
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status, APIRouter
from typing import Annotated
from psycopg.errors import UniqueViolation

from apps.todo.req_models import RegisterRequest, LoginRequest

auth_router = APIRouter()

SECRET_KEY = os.environ.get('SECRET_KEY')
ALGORITHM = os.environ.get('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES'))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/todo/token")

@auth_router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    data = {
        "email": user.email
    }
    access_token = create_access_token(data=data)
    return Token(access_token=access_token, token_type="bearer")

@auth_router.post('/register')
def register_user(user: RegisterRequest):
    q = f"""
        INSERT INTO todo.users
        (email, full_name, password)
        VALUES(%s, %s, %s)
        RETURNING email;
    """
    hashed_password = pwd_context.hash(user.password)
    d = (user.email, user.full_name, hashed_password)
    try:
        execute_query(q, User, d)
    except UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exist",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data = {"email": user.email})
    return Token(access_token=access_token, token_type="bearer")

@auth_router.post('/login')
def login_user(user: LoginRequest):
    user = authenticate_user(user.email, user.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    data = {
        "email": user.email
    }
    access_token = create_access_token(data=data)
    return Token(access_token=access_token, token_type="bearer")


def authenticate_user(email: str, password: str):
    q = f"""SELECT email, password 
            FROM todo.users u
            WHERE u.email = '{email}'
        """
    user = execute_query(q, UserInDB)[0]
    if user.email == email:
        if pwd_context.verify(password, user.password):
            return User(email=user.email, full_name=user.full_name)
        
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_active_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    q = f"""SELECT email, full_name 
            FROM todo.users u
            WHERE u.email = '{email}'
        """
    user = execute_query(q, User)[0]
    if user is None:
        raise credentials_exception
    return user

