from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.schemas.transaccion import Transaccion


# Esquema base para Archivo
class ArchivoBase(BaseModel):
    nombre_archivo: str


# Esquema para crear un Archivo
class ArchivoCreate(ArchivoBase):
    pass


# Esquema para actualizar un Archivo
class ArchivoUpdate(ArchivoBase):
    pass


# Esquema para respuesta de Archivo
class Archivo(ArchivoBase):
    id: int
    fecha_carga: datetime
    
    class Config:
        from_attributes = True


# Esquema para respuesta de Archivo con transacciones
class ArchivoWithTransacciones(Archivo):
    transacciones: List[Transaccion] = [] 