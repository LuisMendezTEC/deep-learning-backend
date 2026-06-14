from typing import Literal

from pydantic import BaseModel, Field


class VisionMetrics(BaseModel):
    iou: float = Field(description="Intersection over Union, or -1 when no ground truth is provided.")
    dice_score: float = Field(description="Dice score, or -1 when no ground truth is provided.")


class VisionResponse(BaseModel):
    status: Literal["success"]
    backbone: Literal["resnet50", "efficientnet-b4"]
    inference_time_ms: float
    metrics: VisionMetrics
    mask_base64: str
    overlay_base64: str | None
    tumor_area_percentage: float

