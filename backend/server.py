from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
import os
import jwt
import bcrypt
import uuid
from datetime import datetime, timedelta
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Persian Mental Health Assessment API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "mental_health_db")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

# Pydantic models
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

class DASS21Response(BaseModel):
    responses: Dict[int, int]

class Token(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]

# Helper functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        user = await db.users.find_one({"user_id": user_id})
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return user
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

# DASS-21 scoring functions
def calculate_dass_scores(responses: Dict[int, int]) -> Dict[str, Any]:
    # Map questions to categories
    depression_questions = [3, 5, 10, 13, 16, 17, 21]
    anxiety_questions = [2, 4, 7, 9, 15, 19, 20]
    stress_questions = [1, 6, 8, 11, 12, 14, 18]
    
    # Calculate raw scores
    depression_score = sum(responses.get(q, 0) for q in depression_questions) * 2
    anxiety_score = sum(responses.get(q, 0) for q in anxiety_questions) * 2
    stress_score = sum(responses.get(q, 0) for q in stress_questions) * 2
    
    # Determine severity levels
    def get_depression_level(score):
        if score <= 9: return "عادی"
        elif score <= 13: return "خفیف"
        elif score <= 20: return "متوسط"
        elif score <= 27: return "شدید"
        else: return "بسیار شدید"
    
    def get_anxiety_level(score):
        if score <= 7: return "عادی"
        elif score <= 9: return "خفیف"
        elif score <= 14: return "متوسط"
        elif score <= 19: return "شدید"
        else: return "بسیار شدید"
    
    def get_stress_level(score):
        if score <= 14: return "عادی"
        elif score <= 18: return "خفیف"
        elif score <= 25: return "متوسط"
        elif score <= 33: return "شدید"
        else: return "بسیار شدید"
    
    depression_level = get_depression_level(depression_score)
    anxiety_level = get_anxiety_level(anxiety_score)
    stress_level = get_stress_level(stress_score)
    
    # Generate AI analysis
    ai_analysis = generate_ai_analysis(depression_score, anxiety_score, stress_score, 
                                     depression_level, anxiety_level, stress_level)
    
    # Generate recommendations
    recommendations = generate_recommendations(depression_level, anxiety_level, stress_level)
    
    return {
        "depression_score": depression_score,
        "anxiety_score": anxiety_score,
        "stress_score": stress_score,
        "depression_level": depression_level,
        "anxiety_level": anxiety_level,
        "stress_level": stress_level,
        "ai_analysis": ai_analysis,
        "recommendations": recommendations
    }

def generate_ai_analysis(dep_score, anx_score, stress_score, dep_level, anx_level, stress_level):
    analysis = "بر اساس تجزیه و تحلیل پاسخ‌های شما: "
    
    if dep_level == "عادی" and anx_level == "عادی" and stress_level == "عادی":
        analysis += "نتایج شما در محدوده طبیعی قرار دارد. شما وضعیت روحی مناسبی دارید."
    elif any(level in ["شدید", "بسیار شدید"] for level in [dep_level, anx_level, stress_level]):
        analysis += "نتایج نشان می‌دهد که شما در حال حاضر با چالش‌های قابل توجه سلامت روان مواجه هستید. توصیه می‌شود با یک متخصص مشورت کنید."
    else:
        analysis += "نتایج نشان می‌دهد که شما نیاز به توجه بیشتر به سلامت روان خود دارید. با اعمال تکنیک‌های مدیریت استرس می‌توانید بهبود یابید."
    
    return analysis

def generate_recommendations(dep_level, anx_level, stress_level):
    recommendations = []
    
    if dep_level != "عادی":
        recommendations.extend([
            "تمرین روزانه تنفس عمیق و مدیتیشن",
            "حفظ برنامه خواب منظم (7-8 ساعت)",
            "فعالیت بدنی منظم، حداقل 30 دقیقه در روز"
        ])
    
    if anx_level != "عادی":
        recommendations.extend([
            "تکنیک‌های آرام‌سازی عضلانی",
            "محدود کردن کافئین و مواد محرک",
            "تمرین ذهن‌آگاهی (Mindfulness)"
        ])
    
    if stress_level != "عادی":
        recommendations.extend([
            "مدیریت زمان و اولویت‌بندی کارها",
            "ایجاد تعادل بین کار و زندگی",
            "استفاده از تکنیک‌های حل مسئله"
        ])
    
    if all(level == "عادی" for level in [dep_level, anx_level, stress_level]):
        recommendations = [
            "ادامه سبک زندگی سالم فعلی",
            "حفظ روابط اجتماعی مثبت",
            "ارزیابی دوره‌ای سلامت روان"
        ]
    
    return recommendations[:5]  # Return top 5 recommendations

# API Routes
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Persian Mental Health API is running"}

@app.post("/api/register", response_model=Token)
async def register_user(user_data: UserRegister):
    # Validate input
    if not user_data.consentGiven:
        raise HTTPException(status_code=400, detail="رضایت‌نامه باید تایید شود")
    
    if user_data.password != user_data.confirmPassword:
        raise HTTPException(status_code=400, detail="رمز عبور و تکرار آن یکسان نیستند")
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="کاربری با این ایمیل قبلاً ثبت‌نام کرده است")
    
    # Create user
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
        "last_login": datetime.utcnow()
    }
    
    await db.users.insert_one(user_doc)
    
    # Create access token
    access_token = create_access_token(data={"sub": user_id})
    
    user_response = {
        "user_id": user_id,
        "email": user_data.email,
        "full_name": user_data.fullName,
        "age": user_data.age,
        "student_level": user_data.studentLevel
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }

@app.post("/api/login", response_model=Token)
async def login_user(user_data: UserLogin):
    # Find user
    user = await db.users.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="ایمیل یا رمز عبور اشتباه است")
    
    # Update last login
    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    # Create access token
    access_token = create_access_token(data={"sub": user["user_id"]})
    
    user_response = {
        "user_id": user["user_id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "age": user["age"],
        "student_level": user["student_level"]
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }

@app.get("/api/profile")
async def get_profile(current_user = Depends(get_current_user)):
    return {
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "age": current_user["age"],
        "student_level": current_user["student_level"]
    }

@app.post("/api/submit-dass21")
async def submit_dass21(dass_data: DASS21Response, current_user = Depends(get_current_user)):
    # Validate responses
    if len(dass_data.responses) != 21:
        raise HTTPException(status_code=400, detail="باید به تمام 21 سوال پاسخ داده شود")
    
    # Calculate scores
    results = calculate_dass_scores(dass_data.responses)
    
    # Save to database
    assessment_doc = {
        "assessment_id": str(uuid.uuid4()),
        "user_id": current_user["user_id"],
        "assessment_type": "DASS-21",
        "responses": dass_data.responses,
        "results": results,
        "completed_at": datetime.utcnow()
    }
    
    await db.assessments.insert_one(assessment_doc)
    
    return results

@app.get("/api/assessments")
async def get_user_assessments(current_user = Depends(get_current_user)):
    assessments = await db.assessments.find(
        {"user_id": current_user["user_id"]},
        {"_id": 0}
    ).sort("completed_at", -1).to_list(length=10)
    
    return assessments

@app.get("/api/admin/export-data")
async def export_research_data():
    # This would be protected by admin authentication in production
    assessments = await db.assessments.find(
        {},
        {
            "_id": 0,
            "user_id": 0,  # Remove personal identifiers
            "assessment_id": 0
        }
    ).to_list(length=None)
    
    return {"data": assessments, "count": len(assessments)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)