from enum import StrEnum
from typing import Any

from fastapi import HTTPException


class ErrorCode(StrEnum):
    INVALID_IMAGE_FORMAT = "INVALID_IMAGE_FORMAT"
    IMAGE_TOO_LARGE = "IMAGE_TOO_LARGE"
    INVALID_AUDIO_FORMAT = "INVALID_AUDIO_FORMAT"
    AUDIO_TOO_LONG = "AUDIO_TOO_LONG"
    AUDIO_TOO_LARGE = "AUDIO_TOO_LARGE"
    MODEL_NOT_LOADED = "MODEL_NOT_LOADED"
    INFERENCE_FAILED = "INFERENCE_FAILED"
    INVALID_BACKBONE = "INVALID_BACKBONE"
    INVALID_LANGUAGE = "INVALID_LANGUAGE"


ERROR_MESSAGES: dict[ErrorCode, str] = {
    ErrorCode.INVALID_IMAGE_FORMAT: "El archivo recibido no es una imagen valida (PNG/JPG/TIFF).",
    ErrorCode.IMAGE_TOO_LARGE: "La imagen supera el tamano maximo permitido de 10 MB.",
    ErrorCode.INVALID_AUDIO_FORMAT: "El archivo recibido no es un audio valido (WAV/MP3/FLAC/OGG).",
    ErrorCode.AUDIO_TOO_LONG: "El audio supera la duracion maxima permitida de 30 segundos.",
    ErrorCode.AUDIO_TOO_LARGE: "El audio supera el tamano maximo permitido de 25 MB.",
    ErrorCode.MODEL_NOT_LOADED: "El checkpoint del modelo no fue encontrado en disco.",
    ErrorCode.INFERENCE_FAILED: "Error interno durante la inferencia del modelo.",
    ErrorCode.INVALID_BACKBONE: "Backbone no soportado. Use 'resnet50' o 'efficientnet-b4'.",
    ErrorCode.INVALID_LANGUAGE: "Idioma no soportado. Use 'es'.",
}


def api_error(
    code: ErrorCode,
    status_code: int,
    detail: Any | None = None,
    message: str | None = None,
) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={
            "status": "error",
            "code": code.value,
            "message": message or ERROR_MESSAGES[code],
            "detail": detail,
        },
    )

