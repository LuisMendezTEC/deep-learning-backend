from pydantic import BaseModel


class AudioTranscriptionResponse(BaseModel):
    transcription: str
    normalized_transcription: str
    duration_s: float
    latency_ms: float
    confidence: float
    model: str
