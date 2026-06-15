from __future__ import annotations

"""
app/api/routes/health.py
Endpoints de diagnóstico del sistema.

GET /api/v1/health/     → estado general de la API
GET /api/v1/health/gpu  → diagnóstico completo de GPU y librerías de Deep Learning
"""
import platform
import sys
from typing import Any, Optional

import torch
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


# --- Schemas de respuesta ---

class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    environment: str


class GpuDevice(BaseModel):
    index: int
    name: str
    vram_total_gb: float
    vram_free_gb: float
    compute_capability: str


class GpuDiagnosticsResponse(BaseModel):
    status: str
    python_version: str
    platform: str
    torch_version: str
    cuda_available: bool
    cuda_version: Optional[str]
    cudnn_version: Optional[str]
    active_device: str
    gpu_count: int
    gpus: list[GpuDevice]
    torchaudio_available: bool
    torchvision_available: bool
    segmentation_models_available: bool
    recommendation: str


def _get_gpu_devices() -> list[GpuDevice]:
    """Recolecta información de cada GPU disponible vía CUDA."""
    devices: list[GpuDevice] = []
    for i in range(torch.cuda.device_count()):
        props = torch.cuda.get_device_properties(i)
        free_bytes, total_bytes = torch.cuda.mem_get_info(i)
        devices.append(
            GpuDevice(
                index=i,
                name=props.name,
                vram_total_gb=round(total_bytes / 1024**3, 2),
                vram_free_gb=round(free_bytes / 1024**3, 2),
                compute_capability=f"{props.major}.{props.minor}",
            )
        )
    return devices


def _check_library(module_name: str) -> bool:
    """Verifica si un módulo Python está instalado y es importable."""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False


def _build_recommendation(cuda_available: bool, gpus: list[GpuDevice]) -> str:
    """Genera una recomendación accionable según el estado detectado."""
    if not cuda_available:
        return (
            "⚠️  CUDA no está disponible. Verifica que instalaste PyTorch con soporte "
            "GPU (pip install torch+cuXXX). El entrenamiento correrá en CPU y será "
            "significativamente más lento."
        )
    if not gpus:
        return "⚠️  CUDA disponible pero no se detectaron GPUs. Revisa los drivers de NVIDIA."
    low_vram = [g for g in gpus if g.vram_total_gb < 6]
    if low_vram:
        return (
            f"✅ GPU detectada ({gpus[0].name}). VRAM limitada ({gpus[0].vram_total_gb} GB): "
            "ajusta el batch_size a 4–8 para segmentación de IRM."
        )
    return (
        f"✅ GPU lista para entrenamiento ({gpus[0].name}, "
        f"{gpus[0].vram_total_gb} GB VRAM). "
        "Puedes usar batch_size ≥ 16 para U-Net."
    )


# --- Endpoints ---

@router.get("/", response_model=HealthResponse, summary="Estado general de la API")
async def health_check() -> Any:
    """Verifica que la API está corriendo correctamente."""
    from app.core.config import get_settings
    settings = get_settings()
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
    )


@router.get(
    "/gpu",
    response_model=GpuDiagnosticsResponse,
    summary="Diagnóstico completo de GPU y librerías de Deep Learning",
)
async def gpu_diagnostics() -> Any:
    """
    Retorna información detallada sobre:
    - Disponibilidad de CUDA y versión
    - Nombre, VRAM total y libre de cada GPU detectada
    - Disponibilidad de librerías clave (torchaudio, torchvision, segmentation-models)
    - Recomendación de configuración de batch_size
    """
    cuda_available = torch.cuda.is_available()
    gpus = _get_gpu_devices() if cuda_available else []

    active_device = "cpu"
    if cuda_available and gpus:
        active_device = f"cuda:{torch.cuda.current_device()} ({gpus[0].name})"

    return GpuDiagnosticsResponse(
        status="ok",
        python_version=sys.version,
        platform=platform.platform(),
        torch_version=torch.__version__,
        cuda_available=cuda_available,
        cuda_version=torch.version.cuda if cuda_available else None,
        cudnn_version=str(torch.backends.cudnn.version()) if cuda_available else None,
        active_device=active_device,
        gpu_count=len(gpus),
        gpus=gpus,
        torchaudio_available=_check_library("torchaudio"),
        torchvision_available=_check_library("torchvision"),
        segmentation_models_available=_check_library("segmentation_models_pytorch"),
        recommendation=_build_recommendation(cuda_available, gpus),
    )
