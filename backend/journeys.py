from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict

from auth import get_current_user
from database import db
from journeys_utils import get_default_journeys


router = APIRouter()


@router.get("/api/journeys")
async def list_journeys() -> List[Dict[str, object]]:
    return get_default_journeys()


@router.get("/api/journeys/{journey_id}")
async def get_journey(journey_id: str) -> Dict[str, object]:
    for journey in get_default_journeys():
        if journey["id"] == journey_id:
            return journey
    raise HTTPException(status_code=404, detail="Journey not found")


@router.post("/api/journeys/{journey_id}/start")
async def start_journey(journey_id: str, current_user=Depends(get_current_user)):
    progress = {
        "user_id": current_user["user_id"],
        "journey_id": journey_id,
        "current_step": 0,
    }
    await db.journey_progress.update_one(
        {"user_id": current_user["user_id"], "journey_id": journey_id},
        {"$set": progress},
        upsert=True,
    )
    return progress


@router.get("/api/journeys/{journey_id}/progress")
async def get_progress(journey_id: str, current_user=Depends(get_current_user)):
    progress = await db.journey_progress.find_one(
        {"user_id": current_user["user_id"], "journey_id": journey_id},
        {"_id": 0},
    )
    if not progress:
        raise HTTPException(status_code=404, detail="Journey not started")
    return progress
