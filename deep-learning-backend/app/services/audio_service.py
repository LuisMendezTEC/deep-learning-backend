from __future__ import annotations

import io
import json
import logging
import re
from typing import Optional

import numpy as np
import soundfile as sf
import torch
import torchaudio.transforms as T
from fastapi import status

from app.core.config import Settings
from app.core.errors import ErrorCode, api_error
from app.models.ctc_audio import CTCInferenceModel
from app.schemas.audio import AudioTranscriptionResponse

logger = logging.getLogger(__name__)

SUPPORTED_SUFFIXES = (".wav", ".mp3", ".flac", ".ogg")


class AudioService:
    def __init__(self, model: CTCInferenceModel, settings: Settings) -> None:
        self.model = model
        self.settings = settings
        self.params = self._load_preprocessing_params()
        self.mel_transform = T.MelSpectrogram(
            sample_rate=self.params["sample_rate"],
            n_fft=self.params["n_fft"],
            hop_length=self.params["hop_length"],
            n_mels=self.params["n_mels"],
        )

    async def transcribe(self, audio_bytes: bytes) -> AudioTranscriptionResponse:
        if len(audio_bytes) > self.settings.max_audio_bytes:
            raise api_error(ErrorCode.AUDIO_TOO_LARGE, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        if not self.model.is_loaded:
            raise api_error(ErrorCode.MODEL_NOT_LOADED, status.HTTP_503_SERVICE_UNAVAILABLE, detail=self.model.load_error)

        try:
            waveform, sample_rate = self._load_audio(audio_bytes)
        except RuntimeError as exc:
            raise api_error(ErrorCode.INVALID_AUDIO_FORMAT, status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

        duration_s = waveform.shape[-1] / sample_rate
        if duration_s > self.settings.max_audio_seconds:
            raise api_error(ErrorCode.AUDIO_TOO_LONG, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

        try:
            features = self._preprocess(waveform, sample_rate)
            logits, latency_ms = self.model.predict(features)
            transcription, confidence = self.model.greedy_decode(logits)
            normalized = self._normalize_text(transcription)
        except Exception as exc:  # noqa: BLE001
            logger.exception("ASR inference failed")
            raise api_error(ErrorCode.INFERENCE_FAILED, status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

        return AudioTranscriptionResponse(
            transcription=transcription,
            normalized_transcription=normalized,
            duration_s=round(duration_s, 3),
            latency_ms=round(latency_ms, 2),
            confidence=confidence,
            model="cnn_bilstm_ctc",
        )

    def _load_preprocessing_params(self) -> dict[str, int]:
        if not self.settings.asr_preprocessing_params_path.exists():
            raise FileNotFoundError(self.settings.asr_preprocessing_params_path)
        raw = json.loads(self.settings.asr_preprocessing_params_path.read_text(encoding="utf-8"))
        return {
            "sample_rate": int(raw.get("sample_rate", 16_000)),
            "n_mels": int(raw.get("n_mels", 80)),
            "n_fft": int(raw.get("n_fft", 400)),
            "hop_length": int(raw.get("hop_length", 160)),
        }

    def _load_audio(self, audio_bytes: bytes) -> tuple[torch.Tensor, int]:
        try:
            data, sample_rate = sf.read(io.BytesIO(audio_bytes), dtype="float32", always_2d=True)
            # data shape: (samples, channels) → tensor: (channels, samples)
            waveform = torch.from_numpy(data.T)
            return waveform, sample_rate
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"Unsupported or invalid audio file: {exc}") from exc

    def _preprocess(self, waveform: torch.Tensor, sample_rate: int) -> torch.Tensor:
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
        target_rate = self.params["sample_rate"]
        if sample_rate != target_rate:
            waveform = T.Resample(sample_rate, target_rate)(waveform)

        mel_spec = self.mel_transform(waveform).squeeze(0)
        mel_spec = (mel_spec - mel_spec.mean()) / (mel_spec.std() + 1e-8)
        return mel_spec.unsqueeze(0).float()

    @staticmethod
    def _normalize_text(text: str) -> str:
        text = text.lower().strip()
        text = text.translate(str.maketrans("áéíóúüñ", "aeiouun"))
        text = re.sub(r"[^a-z' ]+", " ", text)
        return re.sub(r"\s+", " ", text).strip()
