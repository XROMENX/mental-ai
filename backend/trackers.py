from datetime import datetime, timedelta
import random
import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from auth import get_current_user, award_xp
from database import db
from journeys_utils import get_default_journeys
from nlp_analysis import analyze_mental_state

router = APIRouter()


class MoodEntry(BaseModel):
    mood_level: int
    note: Optional[str] = ""


class ChatMessage(BaseModel):
    message: str


class SleepEntry(BaseModel):
    hours: float
    quality: int
    note: Optional[str] = ""


class DailyReflection(BaseModel):
    text: str


class MemoryUpdate(BaseModel):
    memory: Dict[str, Any]


# ----- Helpers -----


def generate_chat_response(
    message: str, memory: Optional[Dict[str, Any]] = None
) -> str:
    message_lower = message.lower()
    nickname = None
    if memory:
        nickname = memory.get("name") or memory.get("nickname")
    if any(word in message_lower for word in ["سلام", "درود", "hi", "hello"]):
        base_responses = [
            "امیدوارم حال شما خوب باشد. چطور می‌توانم کمکتان کنم؟",
            "من اینجا هستم تا گوش دهم. امروز چطور احساس می‌کنید؟",
            "خوشحالم که اینجا هستید. چه چیزی در ذهنتان است؟",
        ]
        greeting = f"سلام {nickname}!" if nickname else "سلام!"
        return f"{greeting} {random.choice(base_responses)}"
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
    elif any(word in message_lower for word in ["نگران", "اضطراب", "ترس", "استرس"]):
        responses = [
            "اضطراب و نگرانی بخش طبیعی زندگی هستند. بیایید روی تکنیک‌های تنفس کار کنیم. ۴ ثانیه نفس بکشید، ۷ ثانیه نگه دارید، ۸ ثانیه آرام بدهید.",
            "درک می‌کنم که احساس نگرانی دارید. گاهی کمک می‌کند که روی چیزهایی که می‌توانید کنترل کنید تمرکز کنید.",
            "استرس می‌تواند سخت باشد. آیا تا الان تکنیک‌های آرام‌سازی امتحان کرده‌اید؟",
        ]
        return random.choice(responses)
    elif any(
        word in message_lower for word in ["درس", "امتحان", "کار", "دانشگاه", "مطالعه"]
    ):
        responses = [
            "فشار تحصیلی و کاری چالش بزرگی است. مهم این است که تعادل داشته باشید. برنامه‌ریزی و استراحت منظم کمک می‌کند.",
            "درک می‌کنم که فشار درسی سنگین است. آیا زمان کافی برای استراحت و تفریح در نظر گرفته‌اید؟",
            "موفقیت تحصیلی مهم است، اما سلامتی شما مهم‌تر است. چگونه از خودتان مراقبت می‌کنید؟",
        ]
        return random.choice(responses)
    elif any(word in message_lower for word in ["خواب", "بیدار", "خستگی"]):
        responses = [
            "خواب خوب برای سلامت روان ضروری است. آیا قبل از خواب از گوشی و صفحه‌نمایش دوری می‌کنید؟",
            "مشکلات خواب می‌تواند روی حال و احوال تأثیر بگذارد. آیا برنامه ثابت خواب دارید؟",
            "برای خواب بهتر، می‌توانید قبل از خواب مدیتیشن یا تنفس عمیق انجام دهید.",
        ]
        return random.choice(responses)
    else:
        responses = [
            "درک می‌کنم. گاهی صحبت کردن کمک می‌کند. چه چیز دیگری در ذهنتان است؟",
            "ممنون که با من در میان گذاشتید. چگونه می‌توانم بهتر کمکتان کنم؟",
            "احساسات شما مهم هستند. آیا تکنیک‌های آرام‌سازی یاد گرفته‌اید؟",
            "هر چه احساس می‌کنید طبیعی است. مهم این است که مراقب خودتان باشید.",
            "اگر احساس کردید نیاز به کمک حرفه‌ای دارید، لطفاً با مشاور یا روان‌شناس صحبت کنید.",
        ]
        return random.choice(responses)


# ----- Endpoints -----


@router.post("/api/mood-entry")
async def save_mood_entry(mood_data: MoodEntry, current_user=Depends(get_current_user)):
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    existing_entry = await db.mood_entries.find_one(
        {"user_id": current_user["user_id"], "date": {"$gte": today, "$lt": tomorrow}}
    )
    mood_doc = {
        "user_id": current_user["user_id"],
        "mood_level": mood_data.mood_level,
        "note": mood_data.note,
        "analysis": analyze_mental_state(mood_data.note or ""),
        "date": datetime.utcnow(),
    }
    if existing_entry:
        await db.mood_entries.update_one(
            {"_id": existing_entry["_id"]}, {"$set": mood_doc}
        )
    else:
        mood_doc["entry_id"] = str(uuid.uuid4())
        await db.mood_entries.insert_one(mood_doc)
    return {"message": "خلق و خو با موفقیت ذخیره شد"}


@router.get("/api/mood-entries")
async def get_mood_entries(current_user=Depends(get_current_user)):
    entries = (
        await db.mood_entries.find({"user_id": current_user["user_id"]}, {"_id": 0})
        .sort("date", -1)
        .to_list(length=30)
    )
    return entries


@router.post("/api/sleep-entry")
async def save_sleep_entry(
    sleep_data: SleepEntry, current_user=Depends(get_current_user)
):
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    existing = await db.sleep_entries.find_one(
        {"user_id": current_user["user_id"], "date": {"$gte": today, "$lt": tomorrow}}
    )
    doc = {
        "user_id": current_user["user_id"],
        "hours": sleep_data.hours,
        "quality": sleep_data.quality,
        "note": sleep_data.note,
        "date": datetime.utcnow(),
    }
    if existing:
        await db.sleep_entries.update_one({"_id": existing["_id"]}, {"$set": doc})
    else:
        doc["entry_id"] = str(uuid.uuid4())
        await db.sleep_entries.insert_one(doc)
    await award_xp(current_user["user_id"], 5)
    return {"message": "اطلاعات خواب ذخیره شد"}


@router.get("/api/sleep-entries")
async def get_sleep_entries(current_user=Depends(get_current_user)):
    entries = (
        await db.sleep_entries.find({"user_id": current_user["user_id"]}, {"_id": 0})
        .sort("date", -1)
        .to_list(length=30)
    )
    return entries


@router.post("/api/daily-reflection")
async def save_daily_reflection(
    reflection: DailyReflection, current_user=Depends(get_current_user)
):
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    existing = await db.reflections.find_one(
        {"user_id": current_user["user_id"], "date": {"$gte": today, "$lt": tomorrow}}
    )
    doc = {
        "user_id": current_user["user_id"],
        "text": reflection.text,
        "date": datetime.utcnow(),
    }
    if existing:
        await db.reflections.update_one({"_id": existing["_id"]}, {"$set": doc})
    else:
        doc["entry_id"] = str(uuid.uuid4())
        await db.reflections.insert_one(doc)
    await award_xp(current_user["user_id"], 5)
    return {"message": "یادداشت روزانه ذخیره شد"}


@router.get("/api/daily-reflections")
async def get_daily_reflections(current_user=Depends(get_current_user)):
    reflections = (
        await db.reflections.find({"user_id": current_user["user_id"]}, {"_id": 0})
        .sort("date", -1)
        .to_list(length=30)
    )
    return reflections


@router.post("/api/chat")
async def chat_with_bot(chat_data: ChatMessage, current_user=Depends(get_current_user)):
    response = generate_chat_response(chat_data.message, current_user.get("memory", {}))
    chat_doc = {
        "chat_id": str(uuid.uuid4()),
        "user_id": current_user["user_id"],
        "user_message": chat_data.message,
        "bot_response": response,
        "analysis": analyze_mental_state(chat_data.message),
        "timestamp": datetime.utcnow(),
    }
    await db.chat_history.insert_one(chat_doc)
    return {"response": response}


@router.get("/api/mental-health-plan")
async def get_mental_health_plan(current_user=Depends(get_current_user)):
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


@router.get("/api/journeys")
async def get_journeys(_: Any = Depends(get_current_user)):
    return get_default_journeys()


@router.get("/api/gamification")
async def get_gamification(current_user=Depends(get_current_user)):
    user = await db.users.find_one({"user_id": current_user["user_id"]})
    return {
        "xp": user.get("xp", 0),
        "level": user.get("level", 1),
        "badges": user.get("badges", []),
    }


@router.get("/api/memory")
async def get_memory(current_user=Depends(get_current_user)):
    return current_user.get("memory", {})


@router.put("/api/memory")
async def update_memory(update: MemoryUpdate, current_user=Depends(get_current_user)):
    memory = current_user.get("memory", {})
    memory.update(update.memory)
    await db.users.update_one(
        {"user_id": current_user["user_id"]}, {"$set": {"memory": memory}}
    )
    return {"memory": memory}
