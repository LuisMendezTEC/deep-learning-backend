from fastapi import APIRouter
from app.api.routes import audio, health, vision

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Diagnostic"])
api_router.include_router(vision.router, prefix="/vision", tags=["Vision"])
api_router.include_router(audio.router, prefix="/asr", tags=["ASR"])
