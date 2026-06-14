from functools import lru_cache
from pathlib import Path

import torch
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "Deep Learning Backend"
    api_prefix: str = "/api/v1"
    models_dir: Path = Field(default=Path("data/models"))
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    max_image_bytes: int = 10 * 1024 * 1024
    max_audio_bytes: int = 25 * 1024 * 1024
    max_audio_seconds: float = 30.0
    vision_image_size: int = 256
    sample_rate: int = 16_000
    n_mels: int = 80
    n_fft: int = 400
    hop_length: int = 160
    device: str = Field(default="auto")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="BACKEND_",
        case_sensitive=False,
    )

    @property
    def resolved_device(self) -> str:
        if self.device != "auto":
            return self.device
        return "cuda" if torch.cuda.is_available() else "cpu"

    @property
    def resolved_models_dir(self) -> Path:
        return self.models_dir.resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()

