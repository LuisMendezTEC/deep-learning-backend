import base64
import io
import json
import logging

import numpy as np
import torch
from fastapi import status
from PIL import Image, ImageOps, UnidentifiedImageError

from app.core.config import Settings
from app.core.errors import ErrorCode, api_error
from app.models.unet import UNetInferenceModel
from app.schemas.vision import VisionSegmentResponse

logger = logging.getLogger(__name__)

SUPPORTED_FORMATS = {"PNG", "JPEG", "JPG", "TIFF"}


class VisionService:
    def __init__(self, model: UNetInferenceModel, settings: Settings) -> None:
        self.model = model
        self.settings = settings

    async def segment(self, image_bytes: bytes) -> VisionSegmentResponse:
        if len(image_bytes) > self.settings.max_image_bytes:
            raise api_error(ErrorCode.IMAGE_TOO_LARGE, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        if not self.model.is_loaded:
            raise api_error(ErrorCode.MODEL_NOT_LOADED, status.HTTP_503_SERVICE_UNAVAILABLE, detail=self.model.load_error)

        try:
            original = self._decode_image(image_bytes)
            norm_stats = self._load_norm_stats()
            tensor = self._preprocess(original, norm_stats)
            logits, latency_ms = self.model.predict(tensor)
            probabilities, mask = self._postprocess(logits, original_size=original.size)
            segmented_image = self._overlay_to_base64(original, mask)
            mask_base64 = self._mask_to_base64(mask)
        except UnidentifiedImageError as exc:
            raise api_error(ErrorCode.INVALID_IMAGE_FORMAT, status.HTTP_422_UNPROCESSABLE_ENTITY) from exc
        except FileNotFoundError as exc:
            raise api_error(ErrorCode.PREPROCESSING_CONFIG_MISSING, status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
        except Exception as exc:  # noqa: BLE001
            logger.exception("Vision inference failed")
            raise api_error(ErrorCode.INFERENCE_FAILED, status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

        tumor_pixels = mask > 0
        tumor_area_percentage = float(tumor_pixels.mean() * 100.0)
        average_probability = float(probabilities[tumor_pixels].mean()) if tumor_pixels.any() else 0.0

        return VisionSegmentResponse(
            has_tumor=bool(tumor_pixels.any()),
            segmented_image=segmented_image,
            mask=mask_base64,
            model="unet_efficientnet-b4",
            tumor_area_percentage=round(tumor_area_percentage, 4),
            average_tumor_probability=round(average_probability, 4),
            latency_ms=round(latency_ms, 2),
        )

    def _decode_image(self, image_bytes: bytes) -> Image.Image:
        image = Image.open(io.BytesIO(image_bytes))
        if image.format not in SUPPORTED_FORMATS:
            raise UnidentifiedImageError(f"Unsupported image format: {image.format}")
        return ImageOps.exif_transpose(image).convert("RGB")

    def _load_norm_stats(self) -> dict[str, float]:
        if not self.settings.cv_norm_stats_path.exists():
            raise FileNotFoundError(self.settings.cv_norm_stats_path)
        raw = json.loads(self.settings.cv_norm_stats_path.read_text(encoding="utf-8"))
        return {
            "mean": float(raw.get("mean", 0.5)),
            "std": float(raw.get("std", 0.5)),
        }

    def _preprocess(self, image: Image.Image, norm_stats: dict[str, float]) -> torch.Tensor:
        gray = image.convert("L")
        resized = gray.resize((256, 256), Image.Resampling.BILINEAR)
        pixels = np.asarray(resized, dtype=np.float32) / 255.0
        normalized = (pixels - norm_stats["mean"]) / (norm_stats["std"] + 1e-8)
        return torch.from_numpy(normalized).unsqueeze(0).unsqueeze(0).float()

    def _postprocess(self, logits: torch.Tensor, original_size: tuple[int, int]) -> tuple[np.ndarray, np.ndarray]:
        probabilities = torch.sigmoid(logits).squeeze().detach().cpu().numpy().astype(np.float32)
        mask = (probabilities > 0.5).astype(np.uint8) * 255
        prob_image = Image.fromarray((probabilities * 255).astype(np.uint8), mode="L").resize(
            original_size,
            Image.Resampling.BILINEAR,
        )
        mask_image = Image.fromarray(mask, mode="L").resize(original_size, Image.Resampling.NEAREST)
        return np.asarray(prob_image, dtype=np.float32) / 255.0, np.asarray(mask_image, dtype=np.uint8)

    def _overlay_to_base64(self, image: Image.Image, mask: np.ndarray) -> str:
        base = image.convert("RGBA")
        overlay = Image.new("RGBA", base.size, (255, 0, 0, 0))
        alpha = Image.fromarray((mask > 0).astype(np.uint8) * 120, mode="L")
        overlay.putalpha(alpha)
        return self._image_to_base64(Image.alpha_composite(base, overlay))

    def _mask_to_base64(self, mask: np.ndarray) -> str:
        return self._image_to_base64(Image.fromarray(mask, mode="L"))

    @staticmethod
    def _image_to_base64(image: Image.Image) -> str:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("ascii")
