import logging
import time
from pathlib import Path

import torch
from torch import nn

logger = logging.getLogger(__name__)


class UNetInferenceModel:
    """Loads and runs the EfficientNet-B4 U-Net checkpoint produced by Module A."""

    def __init__(self, checkpoint_path: Path, device: str, backbone: str = "efficientnet-b4") -> None:
        self.checkpoint_path = checkpoint_path
        self.device = torch.device(device)
        self.backbone = backbone
        self.model: nn.Module | None = None
        self.load_error: str | None = None
        self._load()

    @property
    def is_loaded(self) -> bool:
        return self.model is not None

    def _load(self) -> None:
        if not self.checkpoint_path.exists() or self.checkpoint_path.stat().st_size == 0:
            self.load_error = f"Checkpoint not found or empty: {self.checkpoint_path}"
            logger.warning(self.load_error)
            return

        try:
            checkpoint = torch.load(self.checkpoint_path, map_location=self.device)
            if isinstance(checkpoint, nn.Module):
                model = checkpoint
            else:
                model = self._build_unet()
                state_dict = checkpoint.get("state_dict", checkpoint) if isinstance(checkpoint, dict) else checkpoint
                model.load_state_dict(state_dict)
            model.to(self.device)
            model.eval()
            self.model = model
            logger.info("Loaded vision model from %s", self.checkpoint_path)
        except Exception as exc:  # noqa: BLE001
            self.load_error = str(exc)
            logger.exception("Could not load vision model")

    def _build_unet(self) -> nn.Module:
        try:
            import segmentation_models_pytorch as smp
        except ImportError as exc:
            raise RuntimeError("segmentation-models-pytorch is required to build the U-Net.") from exc

        return smp.Unet(
            encoder_name=self.backbone,
            encoder_weights=None,
            in_channels=1,
            classes=1,
        )

    def predict(self, image_tensor: torch.Tensor) -> tuple[torch.Tensor, float]:
        if self.model is None:
            raise RuntimeError(self.load_error or "Vision model is not loaded.")

        started = time.perf_counter()
        with torch.no_grad():
            logits = self.model(image_tensor.to(self.device))
        latency_ms = (time.perf_counter() - started) * 1000
        return logits, latency_ms
