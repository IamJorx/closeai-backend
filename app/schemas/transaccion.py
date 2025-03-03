from datetime import datetime
from typing import Dict, Optional
from decimal import Decimal

from pydantic import BaseModel, Field


# Esquema base para Transaccion
class TransaccionBase(BaseModel):
    id_transaccion: str
    fecha: datetime
    cuenta_origen: str
    cuenta_destino: str
    monto: Decimal
    estado: str
    extra_data: Optional[Dict] = None


# Esquema para crear una Transaccion
class TransaccionCreate(TransaccionBase):
    archivo_id: int


# Esquema para actualizar una Transaccion
class TransaccionUpdate(TransaccionBase):
    pass


# Esquema para respuesta de Transaccion
class Transaccion(TransaccionBase):
    id: int
    archivo_id: int
    
    class Config:
        from_attributes = True


# Esquema para comparación de transacciones
class TransaccionComparacion(BaseModel):
    id_transaccion: str
    fecha: datetime
    cuenta_origen: str
    cuenta_destino: str
    monto_archivo_1: Optional[Decimal] = None
    monto_archivo_2: Optional[Decimal] = None
    estado_archivo_1: Optional[str] = None
    estado_archivo_2: Optional[str] = None
    tipo_coincidencia: str = Field(..., description="Coincidencia exacta, Diferencia en monto, Diferencia en estado, Solo en Archivo 1, Solo en Archivo 2") 