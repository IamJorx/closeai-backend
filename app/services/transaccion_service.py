from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaccion import Transaccion


class TransaccionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_transacciones(self, skip: int = 0, limit: int = 100) -> List[Transaccion]:
        """
        Obtiene una lista de transacciones con paginación.
        """
        query = select(Transaccion).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_transaccion(self, transaccion_id: int) -> Optional[Transaccion]:
        """
        Obtiene una transacción por su ID.
        """
        query = select(Transaccion).where(Transaccion.id == transaccion_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_transacciones_by_archivo(self, archivo_id: int) -> List[Transaccion]:
        """
        Obtiene todas las transacciones de un archivo específico.
        """
        query = select(Transaccion).where(Transaccion.archivo_id == archivo_id)
        result = await self.db.execute(query)
        return result.scalars().all() 