import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import asr, health, vision
from app.core.config import get_settings
from app.core.errors import ErrorCode
from app.core.logging import configure_logging
from app.models.ctc_audio import CTCInferenceModel
from app.models.unet import UNetInferenceModel

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    settings = get_settings()
    device = settings.resolved_device

    app.state.settings = settings
    app.state.cv_model_resnet = UNetInferenceModel(
        checkpoint_path=settings.resolved_models_dir / "cv/unet_resnet50_best.pth",
        backbone="resnet50",
        device=device,
    )
    app.state.cv_model_efficient = UNetInferenceModel(
        checkpoint_path=settings.resolved_models_dir / "cv/unet_efficientnetb4_best.pth",
        backbone="efficientnet-b4",
        device=device,
    )
    app.state.asr_model = CTCInferenceModel(
        checkpoint_path=settings.resolved_models_dir / "asr/ctc_bilstm_best.pth",
        vocab_path=settings.resolved_models_dir / "asr/vocab.json",
        device=device,
    )
    logger.info("Modelos inicializados en dispositivo: %s", device)
    yield
    logger.info("Apagando aplicacion.")


app = FastAPI(
    title="Deep Learning Backend",
    description="Modulo B: FastAPI inference endpoints for MRI segmentation and Spanish ASR.",
    version="1.0.0",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict) and exc.detail.get("status") == "error":
        return JSONResponse(status_code=exc.status_code, content=exc.detail, headers=exc.headers)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "code": "HTTP_ERROR",
            "message": str(exc.detail),
            "detail": None,
        },
        headers=exc.headers,
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


app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(vision.router, prefix=settings.api_prefix)
app.include_router(asr.router, prefix=settings.api_prefix)
