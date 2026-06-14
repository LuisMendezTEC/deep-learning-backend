import base64
import io
import logging

import numpy as np
import torch
from fastapi import status
from PIL import Image, ImageOps, UnidentifiedImageError

from app.core.config import Settings
from app.core.errors import ErrorCode, api_error
from app.models.unet import UNetInferenceModel
from app.schemas.vision import VisionMetrics, VisionResponse
from app.services.file_validation import detect_mime

logger = logging.getLogger(__name__)

SUPPORTED_IMAGE_FORMATS = {"PNG", "JPEG", "JPG", "TIFF"}
SUPPORTED_IMAGE_MIME_TYPES = {"image/png", "image/jpeg", "image/tiff"}


class VisionService:
    def __init__(self, model: UNetInferenceModel, settings: Settings) -> None:
        self.model = model
        self.settings = settings

    async def run_segmentation(self, image_bytes: bytes, backbone: str, overlay: bool) -> VisionResponse:
        if len(image_bytes) > self.settings.max_image_bytes:
            raise api_error(ErrorCode.IMAGE_TOO_LARGE, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        mime_type = detect_mime(image_bytes)
        if mime_type is not None and mime_type not in SUPPORTED_IMAGE_MIME_TYPES:
            raise api_error(ErrorCode.INVALID_IMAGE_FORMAT, status.HTTP_422_UNPROCESSABLE_ENTITY)
        if not self.model.is_loaded:
            raise api_error(ErrorCode.MODEL_NOT_LOADED, status.HTTP_503_SERVICE_UNAVAILABLE, detail=self.model.load_error)

        try:
            original_image = self._decode_image(image_bytes)
            tensor = self._preprocess(original_image)
            logits, inference_time_ms = self.model.predict(tensor)
            mask = self._postprocess(logits, original_size=original_image.size)
            mask_base64 = self._mask_to_base64(mask)
            overlay_base64 = self._overlay_to_base64(original_image, mask) if overlay else None
            tumor_area_percentage = float(mask.mean() / 255.0 * 100.0)
        except UnidentifiedImageError as exc:
            raise api_error(ErrorCode.INVALID_IMAGE_FORMAT, status.HTTP_422_UNPROCESSABLE_ENTITY) from exc
        except RuntimeError as exc:
            raise api_error(ErrorCode.INFERENCE_FAILED, status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
        except Exception as exc:  # noqa: BLE001
            logger.exception("Vision inference failed")
            raise api_error(ErrorCode.INFERENCE_FAILED, status.HTTP_500_INTERNAL_SERVER_ERROR) from exc

        logger.info(
            "vision_inference backbone=%s input_bytes=%s inference_time_ms=%.2f tumor_area=%.2f",
            backbone,
            len(image_bytes),
            inference_time_ms,
            tumor_area_percentage,
        )
        return VisionResponse(
            status="success",
            backbone=backbone,  # type: ignore[arg-type]
            inference_time_ms=round(inference_time_ms, 2),
            metrics=VisionMetrics(iou=-1.0, dice_score=-1.0),
            mask_base64=mask_base64,
            overlay_base64=overlay_base64,
            tumor_area_percentage=round(tumor_area_percentage, 2),
        )

    def _decode_image(self, image_bytes: bytes) -> Image.Image:
        image = Image.open(io.BytesIO(image_bytes))
        if image.format not in SUPPORTED_IMAGE_FORMATS:
            raise UnidentifiedImageError(f"Unsupported image format: {image.format}")
        return ImageOps.exif_transpose(image).convert("RGB")

    def _preprocess(self, image: Image.Image) -> torch.Tensor:
        gray_image = image.convert("L")
        resized = gray_image.resize(
            (self.settings.vision_image_size, self.settings.vision_image_size),
            Image.Resampling.BILINEAR,
        )
        pixels = np.asarray(resized, dtype=np.float32) / 255.0
        normalized = (pixels - 0.5) / 0.5
        return torch.from_numpy(normalized).unsqueeze(0).unsqueeze(0).float()

    def _postprocess(self, logits: torch.Tensor, original_size: tuple[int, int]) -> np.ndarray:
        probabilities = torch.sigmoid(logits).squeeze().detach().cpu().numpy()
        binary_mask = (probabilities > 0.5).astype(np.uint8) * 255
        mask_image = Image.fromarray(binary_mask, mode="L").resize(original_size, Image.Resampling.NEAREST)
        return np.asarray(mask_image, dtype=np.uint8)

    def _mask_to_base64(self, mask: np.ndarray) -> str:
        mask_image = Image.fromarray(mask, mode="L")
        return self._image_to_base64(mask_image)

    def _overlay_to_base64(self, image: Image.Image, mask: np.ndarray) -> str:
        base = image.convert("RGBA")
        red_overlay = Image.new("RGBA", base.size, (255, 0, 0, 0))
        alpha = Image.fromarray((mask > 0).astype(np.uint8) * 110, mode="L")
        red_overlay.putalpha(alpha)
        composed = Image.alpha_composite(base, red_overlay)
        return self._image_to_base64(composed)

    @staticmethod
    def _image_to_base64(image: Image.Image) -> str:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("ascii")
