from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.models.base import Base


class Archivo(Base):
    __tablename__ = "archivos"

    id = Column(Integer, primary_key=True, index=True)
    nombre_archivo = Column(String, nullable=False)
    fecha_carga = Column(DateTime, default=datetime.utcnow)

    # Relación con transacciones
    transacciones = relationship("Transaccion", back_populates="archivo", cascade="all, delete-orphan") 