import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.core.config import settings


# Configurar base de datos de prueba
TEST_DATABASE_URI = "postgresql+asyncpg://postgres:postgres@localhost/test_closeai"

engine = create_async_engine(TEST_DATABASE_URI)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Fixture para crear y eliminar tablas en la base de datos de prueba
@pytest.fixture(scope="session")
def event_loop():
    """
    Crear un nuevo event loop para las pruebas asíncronas.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def setup_database():
    """
    Crear y eliminar tablas en la base de datos de prueba.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def db_session(setup_database):
    """
    Obtener una sesión de base de datos de prueba.
    """
    async with TestingSessionLocal() as session:
        yield session


# Fixture para crear datos de prueba
@pytest.fixture(scope="function")
async def create_test_data(db_session):
    """
    Crear datos de prueba en la base de datos.
    """
    from app.models.archivo import Archivo
    from app.models.transaccion import Transaccion
    from datetime import datetime
    from decimal import Decimal
    
    # Crear archivos de prueba
    archivo1 = Archivo(nombre_archivo="archivo1.xlsx")
    archivo2 = Archivo(nombre_archivo="archivo2.xlsx")
    
    db_session.add(archivo1)
    db_session.add(archivo2)
    await db_session.flush()
    
    # Crear transacciones para el archivo 1
    transacciones_archivo1 = [
        Transaccion(
            archivo_id=archivo1.id,
            id_transaccion="TXN001",
            fecha=datetime(2023, 1, 1),
            cuenta_origen="123456",
            cuenta_destino="654321",
            monto=Decimal("100.50"),
            estado="Exitosa"
        ),
        Transaccion(
            archivo_id=archivo1.id,
            id_transaccion="TXN002",
            fecha=datetime(2023, 1, 2),
            cuenta_origen="234567",
            cuenta_destino="765432",
            monto=Decimal("200.75"),
            estado="Fallida"
        )
    ]
    
    # Crear transacciones para el archivo 2
    transacciones_archivo2 = [
        Transaccion(
            archivo_id=archivo2.id,
            id_transaccion="TXN001",
            fecha=datetime(2023, 1, 1),
            cuenta_origen="123456",
            cuenta_destino="654321",
            monto=Decimal("100.50"),
            estado="Exitosa"
        ),
        Transaccion(
            archivo_id=archivo2.id,
            id_transaccion="TXN003",
            fecha=datetime(2023, 1, 3),
            cuenta_origen="345678",
            cuenta_destino="876543",
            monto=Decimal("300.25"),
            estado="Exitosa"
        )
    ]
    
    for t in transacciones_archivo1 + transacciones_archivo2:
        db_session.add(t)
    
    await db_session.commit()
    
    return {
        "archivo1": archivo1,
        "archivo2": archivo2,
        "transacciones_archivo1": transacciones_archivo1,
        "transacciones_archivo2": transacciones_archivo2
    } 