from pydantic import BaseModel, Field


class VisionSegmentResponse(BaseModel):
    has_tumor: bool
    segmented_image: str = Field(description="Overlay PNG encoded as base64.")
    mask: str = Field(description="Binary mask PNG encoded as base64.")
    model: str
    tumor_area_percentage: float
    average_tumor_probability: float
    latency_ms: float
