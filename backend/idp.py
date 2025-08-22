import os
from datetime import datetime, timedelta
from typing import Dict, Optional

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

SECRET_KEY = os.getenv("IDP_SECRET", "changeme")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

router = APIRouter()

# In-memory user store for demonstration purposes
fake_users_db: Dict[str, Dict[str, str]] = {
    "alice": {
        "username": "alice",
        "hashed_password": bcrypt.hashpw(b"password", bcrypt.gensalt()).decode("utf-8"),
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def authenticate_user(username: str, password: str) -> Optional[Dict[str, str]]:
    user = fake_users_db.get(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


def create_access_token(data: Dict[str, str]) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = create_access_token({"sub": user["username"]})
    return Token(access_token=token, token_type="bearer")
