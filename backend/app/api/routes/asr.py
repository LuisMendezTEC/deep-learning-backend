from fastapi import APIRouter, File, Form, Request, UploadFile

from app.core.errors import ErrorCode, api_error
from app.schemas.asr import ASRResponse
from app.schemas.common import ErrorResponse
from app.services.audio_service import AudioService

router = APIRouter(prefix="/asr", tags=["asr"])


@router.post(
    "/transcribe",
    response_model=ASRResponse,
    responses={413: {"model": ErrorResponse}, 422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
async def transcribe_audio(
    request: Request,
    audio: UploadFile = File(..., description="Spanish audio. Accepted formats: WAV, MP3, FLAC, OGG. Max 25 MB, 30 seconds."),
    reference: str | None = Form(default=None, description="Optional ground truth text to calculate WER and CER."),
    language: str = Form(default="es", description="Language code. Only 'es' is supported."),
) -> ASRResponse:
    if language != "es":
        raise api_error(ErrorCode.INVALID_LANGUAGE, 422)

    service = AudioService(model=request.app.state.asr_model, settings=request.app.state.settings)
    audio_bytes = await audio.read()
    return await service.run_transcription(audio_bytes=audio_bytes, reference=reference, language=language)

