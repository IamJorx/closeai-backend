from fastapi import APIRouter

from app.api.endpoints import archivos, transacciones

api_router = APIRouter()

# Endpoint raíz
@api_router.get("/")
async def root():
    return {"status": "ok"}

api_router.include_router(archivos.router, prefix="/archivos", tags=["archivos"])
api_router.include_router(transacciones.router, prefix="/transacciones", tags=["transacciones"]) 