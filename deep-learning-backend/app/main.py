from __future__ import annotations

import logging
import json
from contextlib import asynccontextmanager
from pathlib import Path
 
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
 
from app.api import api_router
from app.core.config import Settings, get_settings
from app.core.errors import ErrorCode
from app.core.snake_case import find_non_snake_case_fields
from app.models.ctc_audio import CTCInferenceModel
from app.models.unet import UNetInferenceModel
 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
 
 
def _ensure_directories(settings: Settings) -> None:
    """Crea los directorios de datos y modelos si no existen."""
    dirs: list[Path] = [
        settings.data_dir,
        settings.models_dir,
        settings.models_dir / "cv",
        settings.models_dir / "asr",
        settings.logs_dir,
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    logger.info("Directorios de datos verificados ✓")
 
 
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Ciclo de vida de la aplicación.
    - startup:  inicialización de recursos (directorios, modelos, etc.)
    - shutdown: liberación de recursos
    """
    settings: Settings = get_settings()
    logger.info("Iniciando %s v%s [%s]", settings.app_name, settings.app_version, settings.app_env)
    _ensure_directories(settings)
    device = settings.resolved_device
    app.state.settings = settings
    app.state.vision_model = UNetInferenceModel(
        checkpoint_path=settings.cv_model_checkpoint,
        device=device,
        backbone=settings.cv_model_backbone,
    )
    app.state.asr_model = CTCInferenceModel(
        checkpoint_path=settings.asr_model_checkpoint,
        vocab_path=settings.asr_vocab_path,
        idx2char_path=settings.asr_idx2char_path,
        device=device,
    )
    logger.info("Modelos inicializados en dispositivo: %s", device)
    yield
    logger.info("Apagando la aplicacion.")
 
 
def create_app() -> FastAPI:
    settings = get_settings()
 
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Backend de inferencia para el Proyecto Programado II — TEC. "
            "Módulos: Segmentación de IRM (U-Net) y Reconocimiento de Voz en Español (CTC)."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
 
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.is_development else ["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def enforce_snake_case_json(request: Request, call_next):  # type: ignore[no-untyped-def]
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            body = await request.body()
            try:
                payload = json.loads(body) if body else None
            except json.JSONDecodeError as exc:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status": "error",
                        "code": ErrorCode.INVALID_JSON.value,
                        "message": "El cuerpo de la solicitud no es un JSON valido.",
                        "detail": str(exc),
                    },
                )

            violations = find_non_snake_case_fields(payload)
            if violations:
                return JSONResponse(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    content={
                        "status": "error",
                        "code": ErrorCode.NON_SNAKE_CASE_FIELD.value,
                        "message": "Los campos enviados al backend deben usar snake_case.",
                        "detail": violations,
                    },
                )

            async def receive() -> dict[str, object]:
                return {"type": "http.request", "body": body, "more_body": False}

            request._receive = receive  # noqa: SLF001 - restore body for downstream FastAPI parsing.

        return await call_next(request)
 
    app.include_router(api_router, prefix="/api/v1")

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_, exc: HTTPException) -> JSONResponse:
        if isinstance(exc.detail, dict) and exc.detail.get("status") == "error":
            return JSONResponse(status_code=exc.status_code, content=exc.detail, headers=exc.headers)
        return JSONResponse(
            status_code=exc.status_code,
            content={"status": "error", "code": "HTTP_ERROR", "message": str(exc.detail), "detail": None},
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "status": "error",
                "code": "VALIDATION_ERROR",
                "message": "La solicitud no cumple con el contrato esperado.",
                "detail": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled application error: %s", exc)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "code": ErrorCode.INFERENCE_FAILED.value,
                "message": "Error interno durante la inferencia del modelo.",
                "detail": None,
            },
        )
 
    return app
 
 
app = create_app()
