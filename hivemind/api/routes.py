from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..debate.engine import DebateEngine

router = APIRouter()
engine = DebateEngine()

class DebateRequest(BaseModel):
    topic: str
    rounds: int = 3

@router.post("/debate")
async def start_debate(req: DebateRequest):
    try:
        result = await engine.start_debate(req.topic, req.rounds)
        return result
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/debate/{debate_id}")
async def get_debate(debate_id: str):
    result = engine.get_debate(debate_id)
    if not result:
        raise HTTPException(404, "Debate not found")
    return result

@router.get("/debates")
async def list_debates():
    return engine.list_debates()

@router.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
