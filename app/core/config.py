from functools import lru_cache
from pathlib import Path

import torch
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = Field(default="Deep Learning API")
    app_version: str = Field(default="1.0.0")
    app_env: str = Field(default="development")

    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    data_dir: Path = Field(default=Path("data"))
    models_dir: Path = Field(default=Path("data/models"))
    docs_dir: Path = Field(default=Path("docs"))
    logs_dir: Path = Field(default=Path("logs"))

    cv_model_backbone: str = Field(default="efficientnet-b4")
    cv_model_checkpoint: Path = Field(default=Path("data/models/cv/unet_efficientnetb4_best.pth"))
    cv_norm_stats_path: Path = Field(default=Path("data/processed/lgg_mri/norm_stats.json"))
    asr_model_checkpoint: Path = Field(default=Path("data/models/asr/ctc_bilstm_best.pth"))
    asr_vocab_path: Path = Field(default=Path("data/models/asr/vocab.json"))
    asr_idx2char_path: Path = Field(default=Path("data/models/asr/idx2char.json"))
    asr_preprocessing_params_path: Path = Field(default=Path("docs/asr_preprocessing_params.json"))

    max_image_bytes: int = Field(default=10 * 1024 * 1024)
    max_audio_bytes: int = Field(default=25 * 1024 * 1024)
    max_audio_seconds: float = Field(default=30.0)
    device: str = Field(default="auto")

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def resolved_device(self) -> str:
        if self.device != "auto":
            return self.device
        return "cuda" if torch.cuda.is_available() else "cpu"


@lru_cache
def get_settings() -> Settings:
    return Settings()
