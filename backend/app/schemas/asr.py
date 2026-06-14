from typing import Literal

from pydantic import BaseModel, Field


class ASRMetrics(BaseModel):
    wer: float = Field(description="Word Error Rate, or -1 when no reference is provided.")
    cer: float = Field(description="Character Error Rate, or -1 when no reference is provided.")


class ASRResponse(BaseModel):
    status: Literal["success"]
    transcription: str
    language: Literal["es"]
    audio_duration_seconds: float
    inference_time_ms: float
    metrics: ASRMetrics
    word_count: int
    confidence: float

