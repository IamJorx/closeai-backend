from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.transaccion_service import TransaccionService
from app.schemas.transaccion import Transaccion

router = APIRouter()


@router.get("/", response_model=List[Transaccion])
async def get_transacciones(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene una lista de transacciones.
    """
    transaccion_service = TransaccionService(db)
    return await transaccion_service.get_transacciones(skip=skip, limit=limit)


@router.get("/{transaccion_id}", response_model=Transaccion)
async def get_transaccion(
    transaccion_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene una transacción por su ID.
    """
    transaccion_service = TransaccionService(db)
    transaccion = await transaccion_service.get_transaccion(transaccion_id)
    
    if not transaccion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transacción con ID {transaccion_id} no encontrada"
        )
    
    return transaccion 