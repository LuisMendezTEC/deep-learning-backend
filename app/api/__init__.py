from fastapi import APIRouter
from app.api.routes import health

# Definimos el enrutador central de la API
api_router = APIRouter()

# Vinculamos las rutas de diagnóstico de salud
api_router.include_router(health.router, prefix="/health", tags=["Diagnostic"])