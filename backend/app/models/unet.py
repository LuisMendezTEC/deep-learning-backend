import logging
import time
from pathlib import Path
from typing import Literal

import torch
from torch import nn

logger = logging.getLogger(__name__)


Backbone = Literal["resnet50", "efficientnet-b4"]


class UNetInferenceModel:
    """Thin inference wrapper for the U-Net checkpoints produced by Module A."""

    def __init__(self, checkpoint_path: Path, backbone: Backbone, device: str) -> None:
        self.checkpoint_path = checkpoint_path
        self.backbone = backbone
        self.device = torch.device(device)
        self.model: nn.Module | None = None
        self.load_error: str | None = None
        self._load()

    @property
    def is_loaded(self) -> bool:
        return self.model is not None

    def _load(self) -> None:
        if not self.checkpoint_path.exists():
            self.load_error = f"Checkpoint not found: {self.checkpoint_path}"
            logger.warning(self.load_error)
            return

        try:
            checkpoint = torch.load(self.checkpoint_path, map_location=self.device)
            if isinstance(checkpoint, nn.Module):
                model = checkpoint
            else:
                model = self._build_segmentation_model()
                state_dict = checkpoint.get("state_dict", checkpoint) if isinstance(checkpoint, dict) else checkpoint
                model.load_state_dict(state_dict)

            model.to(self.device)
            model.eval()
            self.model = model
            logger.info("Loaded %s vision checkpoint from %s", self.backbone, self.checkpoint_path)
        except Exception as exc:  # noqa: BLE001 - keep startup alive and return MODEL_NOT_LOADED at request time.
            self.load_error = str(exc)
            logger.exception("Failed loading vision checkpoint %s", self.checkpoint_path)

    def _build_segmentation_model(self) -> nn.Module:
        try:
            import segmentation_models_pytorch as smp
        except ImportError as exc:
            raise RuntimeError(
                "segmentation-models-pytorch is required when checkpoints only contain state_dict."
            ) from exc

        return smp.Unet(
            encoder_name=self.backbone,
            encoder_weights=None,
            in_channels=1,
            classes=1,
        )

    def predict(self, tensor: torch.Tensor) -> tuple[torch.Tensor, float]:
        if self.model is None:
            raise RuntimeError(self.load_error or "Vision model is not loaded.")

        start_event: torch.cuda.Event | None = None
        end_event: torch.cuda.Event | None = None
        if self.device.type == "cuda":
            start_event = torch.cuda.Event(enable_timing=True)
            end_event = torch.cuda.Event(enable_timing=True)
            start_event.record()

        started = time.perf_counter()
        with torch.no_grad():
            output = self.model(tensor.to(self.device))

        if self.device.type == "cuda" and start_event is not None and end_event is not None:
            end_event.record()
            torch.cuda.synchronize()
            inference_time_ms = float(start_event.elapsed_time(end_event))
        else:
            inference_time_ms = (time.perf_counter() - started) * 1000

        return output, inference_time_ms
