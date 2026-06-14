import torch
from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/gpu")
async def gpu_health() -> dict[str, bool | str | int | None]:
    cuda_available = torch.cuda.is_available()
    return {
        "status": "ok",
        "cuda_available": cuda_available,
        "device_count": torch.cuda.device_count() if cuda_available else 0,
        "device_name": torch.cuda.get_device_name(0) if cuda_available else None,
    }

