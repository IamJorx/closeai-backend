import io
import pytest
import pandas as pd
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import UploadFile
from decimal import Decimal
from datetime import datetime

from app.services.archivo_service import ArchivoService
from app.models.archivo import Archivo
from app.models.transaccion import Transaccion


# Fixture para crear un servicio de archivo con una base de datos simulada
@pytest.fixture
def archivo_service():
    mock_db = AsyncMock()
    return ArchivoService(mock_db)


# Fixture para crear un archivo Excel de prueba
@pytest.fixture
def sample_excel_file():
    # Crear un DataFrame de prueba
    data = {
        'id_transaccion': ['TXN001', 'TXN002', 'TXN003'],
        'fecha': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'cuenta_origen': ['123456', '234567', '345678'],
        'cuenta_destino': ['654321', '765432', '876543'],
        'monto': [100.50, 200.75, 300.25],
        'estado': ['Exitosa', 'Fallida', 'Exitosa']
    }
    df = pd.DataFrame(data)
    
    # Convertir a bytes para simular un archivo
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    
    # Crear un objeto UploadFile simulado
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test_transactions.xlsx"
    mock_file.read = AsyncMock(return_value=buffer.getvalue())
    
    return mock_file


# Prueba para verificar que el procesamiento de archivos funciona correctamente
@pytest.mark.asyncio
async def test_procesar_archivo(archivo_service, sample_excel_file):
    # Configurar el comportamiento del mock de la base de datos
    archivo_service.db.flush = AsyncMock()
    
    # Llamar al método a probar
    result = await archivo_service.procesar_archivo(sample_excel_file)
    
    # Verificar que se creó un registro de archivo
    assert archivo_service.db.add.called
    assert archivo_service.db.flush.called
    
    # Verificar que se agregaron transacciones a la base de datos
    # El número de llamadas a add debe ser 4 (1 para el archivo + 3 para las transacciones)
    assert archivo_service.db.add.call_count >= 4


# Prueba para verificar la normalización de columnas
@pytest.mark.asyncio
async def test_normalizar_columnas(archivo_service):
    # Crear un DataFrame con nombres de columnas variados
    data = {
        'ID_TRANSACCION ': ['TXN001'],
        ' fecha': ['2023-01-01'],
        'CUENTA_origen': ['123456'],
        'cuenta_DESTINO': ['654321'],
        'Monto ': [100.50],
        ' Estado': ['Exitosa']
    }
    df = pd.DataFrame(data)
    
    # Llamar al método privado para normalizar columnas (simulado)
    normalized_df = archivo_service._normalizar_columnas(df)
    
    # Verificar que las columnas se normalizaron correctamente
    expected_columns = ['id_transaccion', 'fecha', 'cuenta_origen', 'cuenta_destino', 'monto', 'estado']
    assert all(col in normalized_df.columns for col in expected_columns)


# Prueba para verificar la conversión de formatos de fecha y monto
@pytest.mark.asyncio
async def test_conversion_formatos(archivo_service):
    # Crear datos de prueba con diferentes formatos
    data = {
        'id_transaccion': ['TXN001'],
        'fecha': ['01/01/2023'],  # Formato diferente
        'cuenta_origen': ['123456'],
        'cuenta_destino': ['654321'],
        'monto': ['$1,234.56'],  # Formato con símbolo de moneda y separador de miles
        'estado': ['Exitosa']
    }
    df = pd.DataFrame(data)
    
    # Procesar el DataFrame (simulado)
    processed_df = archivo_service._procesar_dataframe(df)
    
    # Verificar que las fechas se convirtieron correctamente
    assert isinstance(processed_df['fecha'].iloc[0], datetime)
    
    # Verificar que los montos se convirtieron correctamente
    assert isinstance(processed_df['monto'].iloc[0], Decimal)
    assert processed_df['monto'].iloc[0] == Decimal('1234.56')


# Implementar el método _normalizar_columnas y _procesar_dataframe para las pruebas
def test_setup_archivo_service_methods():
    # Esta prueba es para verificar que los métodos necesarios existen
    # pero no sobrescribiremos los métodos reales
    
    # Verificar que los métodos existen
    assert hasattr(ArchivoService, '_normalizar_columnas')
    assert hasattr(ArchivoService, '_procesar_dataframe')
    
    # Crear una instancia mock para pruebas
    mock_db = AsyncMock()
    service = ArchivoService(mock_db)
    
    # Verificar que los métodos son llamables
    assert callable(service._normalizar_columnas)
    assert callable(service._procesar_dataframe) 