import io
import logging
import re
import tempfile
from pathlib import Path

import torch
import torchaudio
import torchaudio.transforms as T
from fastapi import status

from app.core.config import Settings
from app.core.errors import ErrorCode, api_error
from app.models.ctc_audio import CTCInferenceModel
from app.schemas.asr import ASRMetrics, ASRResponse
from app.services.file_validation import detect_mime
from app.services.metrics import character_error_rate, word_error_rate

logger = logging.getLogger(__name__)

SUPPORTED_AUDIO_SUFFIXES = {".wav", ".mp3", ".flac", ".ogg"}
SUPPORTED_AUDIO_MIME_TYPES = {
    "audio/mpeg",
    "audio/mp3",
    "audio/flac",
    "audio/ogg",
    "audio/wav",
    "audio/x-wav",
    "application/ogg",
}


class AudioService:
    def __init__(self, model: CTCInferenceModel, settings: Settings) -> None:
        self.model = model
        self.settings = settings
        self.mel_transform = T.MelSpectrogram(
            sample_rate=settings.sample_rate,
            n_fft=settings.n_fft,
            hop_length=settings.hop_length,
            n_mels=settings.n_mels,
        )

    async def run_transcription(self, audio_bytes: bytes, reference: str | None, language: str) -> ASRResponse:
        if len(audio_bytes) > self.settings.max_audio_bytes:
            raise api_error(ErrorCode.AUDIO_TOO_LARGE, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        mime_type = detect_mime(audio_bytes)
        if mime_type is not None and mime_type not in SUPPORTED_AUDIO_MIME_TYPES:
            raise api_error(ErrorCode.INVALID_AUDIO_FORMAT, status.HTTP_422_UNPROCESSABLE_ENTITY)
        if not self.model.is_loaded:
            raise api_error(ErrorCode.MODEL_NOT_LOADED, status.HTTP_503_SERVICE_UNAVAILABLE, detail=self.model.load_error)

        try:
            waveform, source_rate = self._load_audio(audio_bytes)
        except RuntimeError as exc:
            raise api_error(ErrorCode.INVALID_AUDIO_FORMAT, status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

        duration = waveform.shape[-1] / source_rate
        if duration > self.settings.max_audio_seconds:
            raise api_error(ErrorCode.AUDIO_TOO_LONG, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

        try:
            features = self._preprocess(waveform, source_rate)
            logits, inference_time_ms = self.model.predict(features)
            transcription, confidence = self.model.greedy_decode(logits)
            normalized_reference = self._normalize_text(reference) if reference else None
            wer = word_error_rate(normalized_reference, transcription) if normalized_reference is not None else -1.0
            cer = character_error_rate(normalized_reference, transcription) if normalized_reference is not None else -1.0
        except Exception as exc:  # noqa: BLE001
            if hasattr(exc, "status_code"):
                raise
            logger.exception("ASR inference failed")
            raise api_error(ErrorCode.INFERENCE_FAILED, status.HTTP_500_INTERNAL_SERVER_ERROR) from exc

        logger.info(
            "asr_inference input_bytes=%s duration=%.2f inference_time_ms=%.2f words=%s",
            len(audio_bytes),
            duration,
            inference_time_ms,
            len(transcription.split()),
        )
        return ASRResponse(
            status="success",
            transcription=transcription,
            language=language,  # type: ignore[arg-type]
            audio_duration_seconds=round(duration, 2),
            inference_time_ms=round(inference_time_ms, 2),
            metrics=ASRMetrics(wer=round(wer, 4), cer=round(cer, 4)),
            word_count=len(transcription.split()),
            confidence=confidence,
        )

    def _load_audio(self, audio_bytes: bytes) -> tuple[torch.Tensor, int]:
        # torchaudio needs a suffix for some codecs, so try known containers until one decodes.
        last_error: Exception | None = None
        for suffix in SUPPORTED_AUDIO_SUFFIXES:
            with tempfile.NamedTemporaryFile(suffix=suffix) as temp_file:
                temp_file.write(audio_bytes)
                temp_file.flush()
                try:
                    return torchaudio.load(Path(temp_file.name))
                except Exception as exc:  # noqa: BLE001
                    last_error = exc

        try:
            return torchaudio.load(io.BytesIO(audio_bytes))
        except Exception as exc:  # noqa: BLE001
            last_error = exc

        raise RuntimeError(f"Unsupported or invalid audio file: {last_error}")

    def _preprocess(self, waveform: torch.Tensor, source_rate: int) -> torch.Tensor:
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
        if source_rate != self.settings.sample_rate:
            waveform = T.Resample(source_rate, self.settings.sample_rate)(waveform)

        mel_spec = self.mel_transform(waveform)
        mel_spec = mel_spec.squeeze(0)
        mel_spec = (mel_spec - mel_spec.mean()) / (mel_spec.std() + 1e-8)
        return mel_spec.unsqueeze(0).float()

    @staticmethod
    def _normalize_text(text: str) -> str:
        text = text.lower().strip()
        replacements = str.maketrans("áéíóúüñ", "aeiouun")
        text = text.translate(replacements)
        text = re.sub(r"[^a-z' ]+", " ", text)
        return re.sub(r"\s+", " ", text).strip()
