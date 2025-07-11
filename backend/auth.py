from datetime import datetime, timedelta
import os
import uuid
from typing import Any, Dict

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr

from database import db
from gamification_utils import calculate_level_and_badges

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is required")

security = HTTPBearer()


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    confirmPassword: str
    fullName: str
    age: int
    studentLevel: str
    consentGiven: bool


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]


router = APIRouter()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(data: Dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        user = await db.users.find_one({"user_id": user_id})
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )
        return user
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


async def award_xp(user_id: str, amount: int):
    user = await db.users.find_one({"user_id": user_id})
    if not user:
        return
    xp = user.get("xp", 0) + amount
    level, badges = calculate_level_and_badges(xp)
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"xp": xp, "level": level, "badges": badges}},
    )
    return {"xp": xp, "level": level, "badges": badges}


@router.post("/api/register", response_model=Token)
async def register_user(user_data: UserRegister):
    if not user_data.consentGiven:
        raise HTTPException(status_code=400, detail="رضایت‌نامه باید تایید شود")
    if user_data.password != user_data.confirmPassword:
        raise HTTPException(status_code=400, detail="رمز عبور و تکرار آن یکسان نیستند")
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=400, detail="کاربری با این ایمیل قبلاً ثبت‌نام کرده است"
        )
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(user_data.password)
    user_doc = {
        "user_id": user_id,
        "email": user_data.email,
        "password": hashed_password,
        "full_name": user_data.fullName,
        "age": user_data.age,
        "student_level": user_data.studentLevel,
        "consent_given": user_data.consentGiven,
        "created_at": datetime.utcnow(),
        "last_login": datetime.utcnow(),
        "xp": 0,
        "level": 1,
        "memory": {},
        "badges": [],
    }
    await db.users.insert_one(user_doc)
    access_token = create_access_token(data={"sub": user_id})
    user_response = {
        "user_id": user_id,
        "email": user_data.email,
        "full_name": user_data.fullName,
        "age": user_data.age,
        "student_level": user_data.studentLevel,
        "xp": 0,
        "level": 1,
        "memory": {},
        "badges": [],
    }
    return {"access_token": access_token, "token_type": "bearer", "user": user_response}


@router.post("/api/login", response_model=Token)
async def login_user(user_data: UserLogin):
    user = await db.users.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="ایمیل یا رمز عبور اشتباه است")
    await db.users.update_one(
        {"user_id": user["user_id"]}, {"$set": {"last_login": datetime.utcnow()}}
    )
    access_token = create_access_token(data={"sub": user["user_id"]})
    user_response = {
        "user_id": user["user_id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "age": user["age"],
        "student_level": user["student_level"],
        "xp": user.get("xp", 0),
        "level": user.get("level", 1),
        "memory": user.get("memory", {}),
        "badges": user.get("badges", []),
    }
    return {"access_token": access_token, "token_type": "bearer", "user": user_response}


@router.get("/api/profile")
async def get_profile(current_user=Depends(get_current_user)):
    return {
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "age": current_user["age"],
        "student_level": current_user["student_level"],
        "xp": current_user.get("xp", 0),
        "level": current_user.get("level", 1),
        "memory": current_user.get("memory", {}),
        "badges": current_user.get("badges", []),
    }
