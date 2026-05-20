"""
app/core/config.py
Configuración centralizada del proyecto usando Pydantic Settings.
Lee variables desde el archivo .env automáticamente.
"""
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Metadatos de la API
    app_name: str = Field(default="Deep Learning API")
    app_version: str = Field(default="1.0.0")
    app_env: str = Field(default="development")

    # Servidor
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    # Rutas de directorios (se resuelven desde la raíz del proyecto)
    data_dir: Path = Field(default=Path("data"))
    models_dir: Path = Field(default=Path("data/models"))
    logs_dir: Path = Field(default=Path("logs"))

    # Configuración de modelos
    cv_model_backbone: str = Field(default="resnet50")
    cv_model_checkpoint: Path = Field(default=Path("data/models/cv/best_model.pth"))
    asr_model_checkpoint: Path = Field(default=Path("data/models/asr/best_model.pth"))

    # Dispositivo de cómputo
    device: str = Field(default="cuda")

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache
def get_settings() -> Settings:
    """
    Singleton cacheado de Settings.
    Usar como dependencia en FastAPI: Depends(get_settings)
    """
    return Settings()