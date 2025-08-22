from fastapi import APIRouter
from pydantic import BaseModel

from nlp_analysis import analyze_mental_state


router = APIRouter()


class TextRequest(BaseModel):
    text: str


@router.post("/api/nlp/analyze")
async def analyze(request: TextRequest):
    return analyze_mental_state(request.text)


@router.get("/api/nlp/models")
async def models():
    return {"models": ["sentiment-analysis"]}
