"""
app/main.py
Punto de entrada de la aplicación FastAPI.
Factory pattern: create_app() permite instanciar la app en tests con configuraciones distintas.
"""
import logging
from contextlib import asynccontextmanager
from pathlib import Path
 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
 
from app.api import api_router
from app.core.config import Settings, get_settings
 
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
    logger.info("🚀 Iniciando %s v%s [%s]", settings.app_name, settings.app_version, settings.app_env)
    _ensure_directories(settings)
    yield
    logger.info("🛑 Apagando la aplicación.")
 
 
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
 
    # CORS — en producción reemplazar "*" con la URL del frontend Next.js
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.is_development else ["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
 
    app.include_router(api_router, prefix="/api/v1")
 
    return app
 
 
app = create_app()