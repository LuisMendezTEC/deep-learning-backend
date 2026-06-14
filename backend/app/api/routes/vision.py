from fastapi import APIRouter, File, Form, Request, UploadFile

from app.core.errors import ErrorCode, api_error
from app.schemas.common import ErrorResponse
from app.schemas.vision import VisionResponse
from app.services.vision_service import VisionService

router = APIRouter(prefix="/vision", tags=["vision"])


@router.post(
    "/segment",
    response_model=VisionResponse,
    responses={413: {"model": ErrorResponse}, 422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
async def segment_image(
    request: Request,
    image: UploadFile = File(..., description="MRI image. Accepted formats: PNG, JPG, TIFF. Max 10 MB."),
    backbone: str = Form(default="resnet50", description="Model backbone: resnet50 or efficientnet-b4."),
    overlay: bool = Form(default=True, description="Return original image with segmentation mask overlay."),
) -> VisionResponse:
    if backbone == "resnet50":
        model = request.app.state.cv_model_resnet
    elif backbone == "efficientnet-b4":
        model = request.app.state.cv_model_efficient
    else:
        raise api_error(ErrorCode.INVALID_BACKBONE, 422)

    service = VisionService(model=model, settings=request.app.state.settings)
    image_bytes = await image.read()
    return await service.run_segmentation(image_bytes=image_bytes, backbone=backbone, overlay=overlay)

