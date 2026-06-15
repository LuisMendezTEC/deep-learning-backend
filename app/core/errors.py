from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from fastapi import HTTPException


class ErrorCode(str, Enum):
    INVALID_JSON = "INVALID_JSON"
    NON_SNAKE_CASE_FIELD = "NON_SNAKE_CASE_FIELD"
    INVALID_IMAGE_FORMAT = "INVALID_IMAGE_FORMAT"
    IMAGE_TOO_LARGE = "IMAGE_TOO_LARGE"
    INVALID_AUDIO_FORMAT = "INVALID_AUDIO_FORMAT"
    AUDIO_TOO_LONG = "AUDIO_TOO_LONG"
    AUDIO_TOO_LARGE = "AUDIO_TOO_LARGE"
    MODEL_NOT_LOADED = "MODEL_NOT_LOADED"
    PREPROCESSING_CONFIG_MISSING = "PREPROCESSING_CONFIG_MISSING"
    INFERENCE_FAILED = "INFERENCE_FAILED"


ERROR_MESSAGES: dict[ErrorCode, str] = {
    ErrorCode.INVALID_JSON: "El cuerpo de la solicitud no es un JSON valido.",
    ErrorCode.NON_SNAKE_CASE_FIELD: "Los campos enviados al backend deben usar snake_case.",
    ErrorCode.INVALID_IMAGE_FORMAT: "El archivo recibido no es una imagen valida.",
    ErrorCode.IMAGE_TOO_LARGE: "La imagen supera el tamano maximo permitido de 10 MB.",
    ErrorCode.INVALID_AUDIO_FORMAT: "El archivo recibido no es un audio valido.",
    ErrorCode.AUDIO_TOO_LONG: "El audio supera la duracion maxima permitida de 30 segundos.",
    ErrorCode.AUDIO_TOO_LARGE: "El audio supera el tamano maximo permitido de 25 MB.",
    ErrorCode.MODEL_NOT_LOADED: "El modelo entrenado no esta disponible en disco.",
    ErrorCode.PREPROCESSING_CONFIG_MISSING: "Faltan parametros de preprocesamiento del modulo A.",
    ErrorCode.INFERENCE_FAILED: "Error interno durante la inferencia del modelo.",
}


def api_error(
    code: ErrorCode,
    status_code: int,
    detail: Optional[Any] = None,
    message: Optional[str] = None,
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
