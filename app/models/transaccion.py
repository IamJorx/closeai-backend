from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, JSON, CheckConstraint
from sqlalchemy.orm import relationship

from app.models.base import Base


class Transaccion(Base):
    __tablename__ = "transacciones"

    id = Column(Integer, primary_key=True, index=True)
    archivo_id = Column(Integer, ForeignKey("archivos.id", ondelete="CASCADE"), nullable=False)
    id_transaccion = Column(String, nullable=False, index=True)
    fecha = Column(DateTime, nullable=False)
    cuenta_origen = Column(String, nullable=False)
    cuenta_destino = Column(String, nullable=False)
    monto = Column(Numeric(12, 2), nullable=False)
    estado = Column(String, nullable=False)
    extra_data = Column(JSON, nullable=True)

    # Relación con archivo
    archivo = relationship("Archivo", back_populates="transacciones")

    # Restricción para el estado
    __table_args__ = (
        CheckConstraint("estado IN ('Exitosa', 'Fallida')", name="check_estado"),
    ) 