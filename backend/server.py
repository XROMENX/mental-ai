import os
import random
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr

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
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is not set")
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


class PHQ9Response(BaseModel):
    responses: Dict[int, int]


class MoodEntry(BaseModel):
    mood_level: int
    note: Optional[str] = ""


class ChatMessage(BaseModel):
    message: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]


# Helper functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(data: dict):
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
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
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
        if score <= 9:
            return "عادی"
        elif score <= 13:
            return "خفیف"
        elif score <= 20:
            return "متوسط"
        elif score <= 27:
            return "شدید"
        else:
            return "بسیار شدید"

    def get_anxiety_level(score):
        if score <= 7:
            return "عادی"
        elif score <= 9:
            return "خفیف"
        elif score <= 14:
            return "متوسط"
        elif score <= 19:
            return "شدید"
        else:
            return "بسیار شدید"

    def get_stress_level(score):
        if score <= 14:
            return "عادی"
        elif score <= 18:
            return "خفیف"
        elif score <= 25:
            return "متوسط"
        elif score <= 33:
            return "شدید"
        else:
            return "بسیار شدید"

    depression_level = get_depression_level(depression_score)
    anxiety_level = get_anxiety_level(anxiety_score)
    stress_level = get_stress_level(stress_score)

    # Generate AI analysis
    ai_analysis = generate_ai_analysis(
        depression_score,
        anxiety_score,
        stress_score,
        depression_level,
        anxiety_level,
        stress_level,
    )

    # Generate recommendations
    recommendations = generate_recommendations(
        depression_level, anxiety_level, stress_level
    )

    return {
        "depression_score": depression_score,
        "anxiety_score": anxiety_score,
        "stress_score": stress_score,
        "depression_level": depression_level,
        "anxiety_level": anxiety_level,
        "stress_level": stress_level,
        "ai_analysis": ai_analysis,
        "recommendations": recommendations,
    }


def calculate_phq9_score(responses: Dict[int, int]) -> Dict[str, Any]:
    total_score = sum(responses.values())

    def get_severity_level(score):
        if score <= 4:
            return "حداقل"
        elif score <= 9:
            return "خفیف"
        elif score <= 14:
            return "متوسط"
        elif score <= 19:
            return "نسبتاً شدید"
        else:
            return "شدید"

    severity_level = get_severity_level(total_score)

    # Generate analysis
    analysis = generate_phq9_analysis(total_score, severity_level)

    # Generate recommendations
    recommendations = generate_phq9_recommendations(severity_level)

    return {
        "total_score": total_score,
        "severity_level": severity_level,
        "analysis": analysis,
        "recommendations": recommendations,
    }


def generate_ai_analysis(
    dep_score, anx_score, stress_score, dep_level, anx_level, stress_level
):
    analysis = "بر اساس تجزیه و تحلیل پاسخ‌های شما: "

    if dep_level == "عادی" and anx_level == "عادی" and stress_level == "عادی":
        analysis += "نتایج شما در محدوده طبیعی قرار دارد. شما وضعیت روحی مناسبی دارید."
    elif any(
        level in ["شدید", "بسیار شدید"]
        for level in [dep_level, anx_level, stress_level]
    ):
        analysis += "نتایج نشان می‌دهد که شما در حال حاضر با چالش‌های قابل توجه سلامت روان مواجه هستید. توصیه می‌شود با یک متخصص مشورت کنید."
    else:
        analysis += "نتایج نشان می‌دهد که شما نیاز به توجه بیشتر به سلامت روان خود دارید. با اعمال تکنیک‌های مدیریت استرس می‌توانید بهبود یابید."

    return analysis


def generate_phq9_analysis(total_score, severity_level):
    if severity_level == "حداقل":
        return "علائم افسردگی شما در سطح حداقل است. این وضعیت طبیعی محسوب می‌شود."
    elif severity_level == "خفیف":
        return "علائم افسردگی خفیفی دارید. با تکنیک‌های خودمراقبتی می‌توانید این وضعیت را بهبود بخشید."
    elif severity_level == "متوسط":
        return (
            "علائم افسردگی متوسطی دارید. توصیه می‌شود با یک مشاور یا روان‌شناس صحبت کنید."
        )
    elif severity_level == "نسبتاً شدید":
        return "علائم افسردگی نسبتاً شدیدی دارید. مراجعه به متخصص ضروری است."
    else:
        return "علائم افسردگی شدیدی دارید. فوراً با یک روان‌پزشک یا متخصص سلامت روان تماس بگیرید."


def generate_recommendations(dep_level, anx_level, stress_level):
    recommendations = []

    if dep_level != "عادی":
        recommendations.extend(
            [
                "تمرین روزانه تنفس عمیق و مدیتیشن",
                "حفظ برنامه خواب منظم (7-8 ساعت)",
                "فعالیت بدنی منظم، حداقل 30 دقیقه در روز",
            ]
        )

    if anx_level != "عادی":
        recommendations.extend(
            [
                "تکنیک‌های آرام‌سازی عضلانی",
                "محدود کردن کافئین و مواد محرک",
                "تمرین ذهن‌آگاهی (Mindfulness)",
            ]
        )

    if stress_level != "عادی":
        recommendations.extend(
            [
                "مدیریت زمان و اولویت‌بندی کارها",
                "ایجاد تعادل بین کار و زندگی",
                "استفاده از تکنیک‌های حل مسئله",
            ]
        )

    if all(level == "عادی" for level in [dep_level, anx_level, stress_level]):
        recommendations = [
            "ادامه سبک زندگی سالم فعلی",
            "حفظ روابط اجتماعی مثبت",
            "ارزیابی دوره‌ای سلامت روان",
        ]

    return recommendations[:5]  # Return top 5 recommendations


def generate_phq9_recommendations(severity_level):
    if severity_level == "حداقل":
        return ["ادامه فعالیت‌های مثبت فعلی", "حفظ روابط اجتماعی", "ورزش منظم"]
    elif severity_level == "خفیف":
        return [
            "افزایش فعالیت‌های لذت‌بخش",
            "برقراری ارتباط با دوستان و خانواده",
            "تمرین ذهن‌آگاهی",
            "نظم در خواب و تغذیه",
        ]
    elif severity_level == "متوسط":
        return [
            "مشورت با روان‌شناس یا مشاور",
            "شرکت در گروه‌های حمایتی",
            "تمرین تکنیک‌های درمان شناختی-رفتاری",
            "نظارت بر علائم",
        ]
    else:
        return [
            "مراجعه فوری به متخصص",
            "درنظرگیری درمان دارویی",
            "حمایت خانوادگی",
            "مراقبت ویژه از خود",
        ]


def generate_chat_response(message: str) -> str:
    """Simple rule-based chatbot for Persian mental health support"""
    message_lower = message.lower()

    # Greeting responses
    if any(word in message_lower for word in ["سلام", "درود", "hi", "hello"]):
        responses = [
            "سلام! امیدوارم حال شما خوب باشد. چطور می‌توانم کمکتان کنم؟",
            "درود بر شما! من اینجا هستم تا گوش دهم. امروز چطور احساس می‌کنید؟",
            "سلام عزیز! خوشحالم که اینجا هستید. چه چیزی در ذهنتان است؟",
        ]
        return random.choice(responses)

    # Mood-related responses
    elif any(word in message_lower for word in ["غمگین", "ناراحت", "افسرده", "بد"]):
        responses = [
            "متأسفم که این‌طور احساس می‌کنید. این احساسات گاهی طبیعی هستند. می‌خواهید درباره‌اش صحبت کنیم؟",
            "درک می‌کنم که حال شما خوب نیست. چه چیزی باعث این احساس شده؟",
            "احساسات شما مهم هستند. آیا امروز اتفاق خاصی افتاده؟",
        ]
        return random.choice(responses)

    elif any(word in message_lower for word in ["خوب", "عالی", "خوشحال", "شاد"]):
        responses = [
            "چه خبر خوبی! خوشحالم که حالتان خوب است. این انرژی مثبت را حفظ کنید.",
            "فوق‌العاده! چه چیزی باعث این حس خوب شده؟",
            "عالی است! این لحظات خوب را قدر بدانید.",
        ]
        return random.choice(responses)

    # Anxiety-related responses
    elif any(word in message_lower for word in ["نگران", "اضطراب", "ترس", "استرس"]):
        responses = [
            "اضطراب و نگرانی بخش طبیعی زندگی هستند. بیایید روی تکنیک‌های تنفس کار کنیم. ۴ ثانیه نفس بکشید، ۷ ثانیه نگه دارید، ۸ ثانیه آرام بدهید.",
            "درک می‌کنم که احساس نگرانی دارید. گاهی کمک می‌کند که روی چیزهایی که می‌توانید کنترل کنید تمرکز کنید.",
            "استرس می‌تواند سخت باشد. آیا تا الان تکنیک‌های آرام‌سازی امتحان کرده‌اید؟",
        ]
        return random.choice(responses)

    # Study/work stress
    elif any(
        word in message_lower for word in ["درس", "امتحان", "کار", "دانشگاه", "مطالعه"]
    ):
        responses = [
            "فشار تحصیلی و کاری چالش بزرگی است. مهم این است که تعادل داشته باشید. برنامه‌ریزی و استراحت منظم کمک می‌کند.",
            "درک می‌کنم که فشار درسی سنگین است. آیا زمان کافی برای استراحت و تفریح در نظر گرفته‌اید؟",
            "موفقیت تحصیلی مهم است، اما سلامتی شما مهم‌تر است. چگونه از خودتان مراقبت می‌کنید؟",
        ]
        return random.choice(responses)

    # Sleep issues
    elif any(word in message_lower for word in ["خواب", "بیدار", "خستگی"]):
        responses = [
            "خواب خوب برای سلامت روان ضروری است. آیا قبل از خواب از گوشی و صفحه نمایش دوری می‌کنید؟",
            "مشکلات خواب می‌تواند روی حال و احوال تأثیر بگذارد. آیا برنامه ثابت خواب دارید؟",
            "برای خواب بهتر، می‌توانید قبل از خواب مدیتیشن یا تنفس عمیق انجام دهید.",
        ]
        return random.choice(responses)

    # General support
    else:
        responses = [
            "درک می‌کنم. گاهی صحبت کردن کمک می‌کند. چه چیز دیگری در ذهنتان است؟",
            "ممنون که با من در میان گذاشتید. چگونه می‌توانم بهتر کمکتان کنم؟",
            "احساسات شما مهم هستند. آیا تکنیک‌های آرام‌سازی یاد گرفته‌اید؟",
            "هر چه احساس می‌کنید طبیعی است. مهم این است که مراقب خودتان باشید.",
            "اگر احساس کردید نیاز به کمک حرفه‌ای دارید، لطفاً با مشاور یا روان‌شناس صحبت کنید.",
        ]
        return random.choice(responses)


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
        raise HTTPException(
            status_code=400, detail="کاربری با این ایمیل قبلاً ثبت‌نام کرده است"
        )

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
        "last_login": datetime.utcnow(),
    }

    await db.users.insert_one(user_doc)

    # Create access token
    access_token = create_access_token(data={"sub": user_id})

    user_response = {
        "user_id": user_id,
        "email": user_data.email,
        "full_name": user_data.fullName,
        "age": user_data.age,
        "student_level": user_data.studentLevel,
    }

    return {"access_token": access_token, "token_type": "bearer", "user": user_response}


@app.post("/api/login", response_model=Token)
async def login_user(user_data: UserLogin):
    # Find user
    user = await db.users.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="ایمیل یا رمز عبور اشتباه است")

    # Update last login
    await db.users.update_one(
        {"user_id": user["user_id"]}, {"$set": {"last_login": datetime.utcnow()}}
    )

    # Create access token
    access_token = create_access_token(data={"sub": user["user_id"]})

    user_response = {
        "user_id": user["user_id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "age": user["age"],
        "student_level": user["student_level"],
    }

    return {"access_token": access_token, "token_type": "bearer", "user": user_response}


@app.get("/api/profile")
async def get_profile(current_user=Depends(get_current_user)):
    return {
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "age": current_user["age"],
        "student_level": current_user["student_level"],
    }


@app.post("/api/submit-dass21")
async def submit_dass21(
    dass_data: DASS21Response, current_user=Depends(get_current_user)
):
    # Validate responses
    if len(dass_data.responses) != 21:
        raise HTTPException(
            status_code=400, detail="باید به تمام 21 سوال پاسخ داده شود"
        )

    # Calculate scores
    results = calculate_dass_scores(dass_data.responses)

    # Convert integer keys to strings for MongoDB compatibility
    responses_str_keys = {str(k): v for k, v in dass_data.responses.items()}

    # Save to database
    assessment_doc = {
        "assessment_id": str(uuid.uuid4()),
        "user_id": current_user["user_id"],
        "assessment_type": "DASS-21",
        "responses": responses_str_keys,
        "results": results,
        "completed_at": datetime.utcnow(),
    }

    await db.assessments.insert_one(assessment_doc)

    return results


@app.post("/api/submit-phq9")
async def submit_phq9(phq_data: PHQ9Response, current_user=Depends(get_current_user)):
    # Validate responses
    if len(phq_data.responses) != 9:
        raise HTTPException(status_code=400, detail="باید به تمام 9 سوال پاسخ داده شود")

    # Calculate scores
    results = calculate_phq9_score(phq_data.responses)

    # Convert integer keys to strings for MongoDB compatibility
    responses_str_keys = {str(k): v for k, v in phq_data.responses.items()}

    # Save to database
    assessment_doc = {
        "assessment_id": str(uuid.uuid4()),
        "user_id": current_user["user_id"],
        "assessment_type": "PHQ-9",
        "responses": responses_str_keys,
        "results": results,
        "completed_at": datetime.utcnow(),
    }

    await db.assessments.insert_one(assessment_doc)

    return results


@app.post("/api/mood-entry")
async def save_mood_entry(mood_data: MoodEntry, current_user=Depends(get_current_user)):
    # Check if entry for today already exists
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)

    existing_entry = await db.mood_entries.find_one(
        {"user_id": current_user["user_id"], "date": {"$gte": today, "$lt": tomorrow}}
    )

    mood_doc = {
        "user_id": current_user["user_id"],
        "mood_level": mood_data.mood_level,
        "note": mood_data.note,
        "date": datetime.utcnow(),
    }

    if existing_entry:
        # Update existing entry
        await db.mood_entries.update_one(
            {"_id": existing_entry["_id"]}, {"$set": mood_doc}
        )
    else:
        # Create new entry
        mood_doc["entry_id"] = str(uuid.uuid4())
        await db.mood_entries.insert_one(mood_doc)

    return {"message": "خلق و خو با موفقیت ذخیره شد"}


@app.get("/api/mood-entries")
async def get_mood_entries(current_user=Depends(get_current_user)):
    entries = (
        await db.mood_entries.find({"user_id": current_user["user_id"]}, {"_id": 0})
        .sort("date", -1)
        .to_list(length=30)
    )  # Last 30 entries

    return entries


@app.post("/api/chat")
async def chat_with_bot(chat_data: ChatMessage, current_user=Depends(get_current_user)):
    response = generate_chat_response(chat_data.message)

    # Save chat to database
    chat_doc = {
        "chat_id": str(uuid.uuid4()),
        "user_id": current_user["user_id"],
        "user_message": chat_data.message,
        "bot_response": response,
        "timestamp": datetime.utcnow(),
    }

    await db.chat_history.insert_one(chat_doc)

    return {"response": response}


@app.get("/api/mental-health-plan")
async def get_mental_health_plan(current_user=Depends(get_current_user)):
    # This would ideally be generated based on user's assessment results
    # For now, returning a static plan
    plan = {
        "daily_habits": [
            "تنفس عمیق ۱۰ دقیقه صبحگاهی",
            "پیاده‌روی ۳۰ دقیقه در طبیعت",
            "نوشتن ۳ چیز مثبت روز",
            "مدیتیشن ۵ دقیقه قبل خواب",
        ],
        "weekly_goals": [
            "شرکت در یک فعالیت اجتماعی",
            "یادگیری مهارت جدید",
            "ارتباط با دوست یا خانواده",
        ],
        "emergency_contacts": {"crisis_line": "۱۴۸۰", "emergency": "۱۱۵"},
    }

    return plan


@app.get("/api/assessments")
async def get_user_assessments(current_user=Depends(get_current_user)):
    assessments = (
        await db.assessments.find({"user_id": current_user["user_id"]}, {"_id": 0})
        .sort("completed_at", -1)
        .to_list(length=10)
    )

    return assessments


@app.get("/api/admin/export-data")
async def export_research_data():
    # This would be protected by admin authentication in production
    assessments = await db.assessments.find(
        {}, {"_id": 0, "user_id": 0, "assessment_id": 0}  # Remove personal identifiers
    ).to_list(length=None)

    return {"data": assessments, "count": len(assessments)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
