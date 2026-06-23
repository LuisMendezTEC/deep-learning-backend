from fastapi import APIRouter, File, Request, UploadFile

from app.schemas.audio import AudioTranscriptionResponse
from app.schemas.common import ErrorResponse
from app.services.audio_service import AudioService

router = APIRouter()


@router.post(
    "/transcribe",
    response_model=AudioTranscriptionResponse,
    responses={413: {"model": ErrorResponse}, 422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
    summary="Transcribe audio en espanol usando CNN + BiLSTM + CTC",
)
async def transcribe_audio(
    request: Request,
    audio: UploadFile = File(..., description="Archivo de audio WAV, MP3, FLAC u OGG."),
) -> AudioTranscriptionResponse:
    audio_bytes = await audio.read()
    service = AudioService(model=request.app.state.asr_model, settings=request.app.state.settings)
    return await service.transcribe(audio_bytes=audio_bytes)
