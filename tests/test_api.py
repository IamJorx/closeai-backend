import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.base import Base
from app.db.session import get_db
from main import app


# Configurar base de datos de prueba
TEST_DATABASE_URI = "postgresql+asyncpg://postgres:postgres@localhost/test_closeai"

engine = create_async_engine(TEST_DATABASE_URI)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Fixture para crear y eliminar tablas en la base de datos de prueba
@pytest.fixture(scope="function")
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Fixture para obtener una sesión de base de datos de prueba
@pytest.fixture(scope="function")
async def db_session():
    async with TestingSessionLocal() as session:
        yield session


# Fixture para obtener un cliente de prueba
@pytest.fixture(scope="function")
def client(db_session):
    async def override_get_db():
        try:
            yield db_session
        finally:
            await db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


# Prueba para verificar que la API está funcionando
def test_api_status(client):
    response = client.get("/api/v1/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"} 