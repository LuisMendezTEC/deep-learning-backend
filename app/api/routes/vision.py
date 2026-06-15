from fastapi import APIRouter, File, Request, UploadFile

from app.schemas.common import ErrorResponse
from app.schemas.vision import VisionSegmentResponse
from app.services.vision_service import VisionService

router = APIRouter()


@router.post(
    "/segment",
    response_model=VisionSegmentResponse,
    responses={413: {"model": ErrorResponse}, 422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
    summary="Segmenta tumores cerebrales en imagenes MRI",
)
async def segment_image(
    request: Request,
    image: UploadFile = File(..., description="Imagen MRI en PNG, JPG o TIFF."),
) -> VisionSegmentResponse:
    image_bytes = await image.read()
    service = VisionService(model=request.app.state.vision_model, settings=request.app.state.settings)
    return await service.segment(image_bytes=image_bytes)
