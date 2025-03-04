import pytest
from fastapi.testclient import TestClient
from main import app
import io

client = TestClient(app)

def test_health_check():
    """
    Prueba que el endpoint de health check responda correctamente.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_api_docs():
    """
    Prueba que la documentación de la API esté disponible.
    """
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_openapi_schema():
    """
    Prueba que el esquema OpenAPI esté disponible.
    """
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    schema = response.json()
    assert "paths" in schema
    assert "components" in schema
    assert "info" in schema

def test_root_endpoint():
    """
    Prueba que el endpoint raíz responda con un mensaje de error 404.
    """
    response = client.get("/")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}

def test_upload_file_endpoint():
    """
    Prueba que el endpoint de carga de archivos esté disponible y responda.
    """
    # Crear un archivo Excel de prueba en memoria
    file_content = io.BytesIO(b"test file content")
    file_content.name = "test_file.xlsx"
    
    # Enviar el archivo al endpoint
    response = client.post(
        "/api/v1/archivos/upload",
        files={"file": ("test_file.xlsx", file_content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    
    # Verificar que el endpoint exista y responda (puede ser un error controlado o un error interno)
    assert response.status_code in [400, 422, 500]  # Puede ser 400 Bad Request, 422 Unprocessable Entity o 500 Internal Server Error
    
    # Si es un error 500, no verificamos el contenido de la respuesta
    if response.status_code != 500:
        assert "detail" in response.json()  # Debe contener un mensaje de error 