from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List

from auth import award_xp, get_current_user
from database import db


router = APIRouter()


class AwardRequest(BaseModel):
    xp: int = 0


@router.post("/api/gamification/award")
async def award_endpoint(request: AwardRequest, current_user=Depends(get_current_user)):
    return await award_xp(current_user["user_id"], request.xp)


@router.get("/api/gamification")
async def get_gamification(current_user=Depends(get_current_user)):
    user = await db.users.find_one({"user_id": current_user["user_id"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "xp": user.get("xp", 0),
        "level": user.get("level", 1),
        "badges": user.get("badges", []),
    }


@router.get("/api/gamification/leaderboard")
async def leaderboard() -> List[dict]:
    users = (
        await db.users.find({}, {"_id": 0, "user_id": 1, "xp": 1})
        .sort("xp", -1)
        .limit(10)
        .to_list(length=10)
    )
    return users


@router.get("/api/gamification/badges")
async def badges_catalog() -> List[str]:
    return ["Novice", "Expert"]
