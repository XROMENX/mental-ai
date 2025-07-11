from datetime import datetime
import uuid
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth import award_xp, get_current_user
from database import db

router = APIRouter()


class DASS21Response(BaseModel):
    responses: Dict[int, int]


class PHQ9Response(BaseModel):
    responses: Dict[int, int]


# ----- DASS-21 utilities -----


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
    return recommendations[:5]


def calculate_dass_scores(responses: Dict[int, int]) -> Dict[str, Any]:
    depression_questions = [3, 5, 10, 13, 16, 17, 21]
    anxiety_questions = [2, 4, 7, 9, 15, 19, 20]
    stress_questions = [1, 6, 8, 11, 12, 14, 18]

    depression_score = sum(responses.get(q, 0) for q in depression_questions) * 2
    anxiety_score = sum(responses.get(q, 0) for q in anxiety_questions) * 2
    stress_score = sum(responses.get(q, 0) for q in stress_questions) * 2

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

    ai_analysis = generate_ai_analysis(
        depression_score,
        anxiety_score,
        stress_score,
        depression_level,
        anxiety_level,
        stress_level,
    )

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


# ----- PHQ-9 utilities -----


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
    analysis = generate_phq9_analysis(total_score, severity_level)
    recommendations = generate_phq9_recommendations(severity_level)

    return {
        "total_score": total_score,
        "severity_level": severity_level,
        "analysis": analysis,
        "recommendations": recommendations,
    }


@router.post("/api/submit-dass21")
async def submit_dass21(
    dass_data: DASS21Response, current_user=Depends(get_current_user)
):
    if len(dass_data.responses) != 21:
        raise HTTPException(
            status_code=400, detail="باید به تمام 21 سوال پاسخ داده شود"
        )
    results = calculate_dass_scores(dass_data.responses)
    responses_str_keys = {str(k): v for k, v in dass_data.responses.items()}
    assessment_doc = {
        "assessment_id": str(uuid.uuid4()),
        "user_id": current_user["user_id"],
        "assessment_type": "DASS-21",
        "responses": responses_str_keys,
        "results": results,
        "completed_at": datetime.utcnow(),
    }
    await db.assessments.insert_one(assessment_doc)
    await award_xp(current_user["user_id"], 10)
    return results


@router.post("/api/submit-phq9")
async def submit_phq9(phq_data: PHQ9Response, current_user=Depends(get_current_user)):
    if len(phq_data.responses) != 9:
        raise HTTPException(status_code=400, detail="باید به تمام 9 سوال پاسخ داده شود")
    results = calculate_phq9_score(phq_data.responses)
    responses_str_keys = {str(k): v for k, v in phq_data.responses.items()}
    assessment_doc = {
        "assessment_id": str(uuid.uuid4()),
        "user_id": current_user["user_id"],
        "assessment_type": "PHQ-9",
        "responses": responses_str_keys,
        "results": results,
        "completed_at": datetime.utcnow(),
    }
    await db.assessments.insert_one(assessment_doc)
    await award_xp(current_user["user_id"], 10)
    return results


@router.get("/api/assessments")
async def get_user_assessments(current_user=Depends(get_current_user)):
    assessments = (
        await db.assessments.find({"user_id": current_user["user_id"]}, {"_id": 0})
        .sort("completed_at", -1)
        .to_list(length=10)
    )
    return assessments


@router.get("/api/admin/export-data")
async def export_research_data():
    assessments = await db.assessments.find(
        {}, {"_id": 0, "user_id": 0, "assessment_id": 0}
    ).to_list(length=None)
    return {"data": assessments, "count": len(assessments)}
