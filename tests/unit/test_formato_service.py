import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock
from decimal import Decimal
from datetime import datetime

from app.services.archivo_service import ArchivoService


# Clase auxiliar para probar la conversión de formatos
class FormatoService:
    @staticmethod
    def convertir_fecha(fecha_str):
        """
        Convierte una cadena de fecha a un objeto datetime.
        Soporta múltiples formatos de fecha.
        """
        formatos = [
            '%Y-%m-%d',  # 2023-01-01
            '%d/%m/%Y',  # 01/01/2023
            '%m/%d/%Y',  # 01/01/2023 (US)
            '%d-%m-%Y',  # 01-01-2023
            '%d.%m.%Y',  # 01.01.2023
        ]
        
        for formato in formatos:
            try:
                return datetime.strptime(fecha_str, formato)
            except ValueError:
                continue
        
        raise ValueError(f"No se pudo convertir la fecha: {fecha_str}")
    
    @staticmethod
    def convertir_monto(monto_str):
        """
        Convierte una cadena de monto a un objeto Decimal.
        Soporta múltiples formatos de moneda.
        """
        if isinstance(monto_str, (int, float, Decimal)):
            return Decimal(str(monto_str))
        
        # Eliminar símbolos de moneda y espacios
        monto_limpio = monto_str.replace('$', '').replace('€', '').replace(' ', '')
        
        # Reemplazar coma como separador de miles
        monto_limpio = monto_limpio.replace(',', '')
        
        # Reemplazar punto como separador decimal si es necesario
        if '.' in monto_limpio:
            monto_limpio = monto_limpio.replace('.', '.')
        
        return Decimal(monto_limpio)


# Pruebas para la conversión de fechas
def test_conversion_fechas():
    # Probar diferentes formatos de fecha
    assert FormatoService.convertir_fecha('2023-01-01') == datetime(2023, 1, 1)
    assert FormatoService.convertir_fecha('01/01/2023') == datetime(2023, 1, 1)
    assert FormatoService.convertir_fecha('01-01-2023') == datetime(2023, 1, 1)
    assert FormatoService.convertir_fecha('01.01.2023') == datetime(2023, 1, 1)
    
    # Probar con fechas inválidas
    with pytest.raises(ValueError):
        FormatoService.convertir_fecha('fecha_invalida')


# Pruebas para la conversión de montos
def test_conversion_montos():
    # Probar diferentes formatos de monto
    assert FormatoService.convertir_monto('100.50') == Decimal('100.50')
    assert FormatoService.convertir_monto('$100.50') == Decimal('100.50')
    assert FormatoService.convertir_monto('€100.50') == Decimal('100.50')
    assert FormatoService.convertir_monto('1,234.56') == Decimal('1234.56')
    assert FormatoService.convertir_monto('1,234') == Decimal('1234')
    assert FormatoService.convertir_monto(100.50) == Decimal('100.5')
    
    # Probar con montos inválidos
    with pytest.raises(Exception):
        FormatoService.convertir_monto('monto_invalido')


# Pruebas para la normalización de columnas en DataFrames
def test_normalizar_columnas_dataframe():
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
    
    # Normalizar columnas
    df.columns = [col.lower().strip() for col in df.columns]
    
    # Verificar que las columnas se normalizaron correctamente
    expected_columns = ['id_transaccion', 'fecha', 'cuenta_origen', 'cuenta_destino', 'monto', 'estado']
    normalized_columns = ['id_transaccion', 'fecha', 'cuenta_origen', 'cuenta_destino', 'monto', 'estado']
    
    # Verificar que todas las columnas esperadas están presentes
    for col in normalized_columns:
        assert col in df.columns or any(c.startswith(col) for c in df.columns)


# Pruebas para la conversión de formatos en DataFrames
def test_conversion_formatos_dataframe():
    # Crear un DataFrame con diferentes formatos
    data = {
        'id_transaccion': ['TXN001', 'TXN002', 'TXN003'],
        'fecha': ['2023-01-01', '01/02/2023', '03-01-2023'],
        'cuenta_origen': ['123456', '234567', '345678'],
        'cuenta_destino': ['654321', '765432', '876543'],
        'monto': ['$100.50', '1,200.75', '€300.25'],
        'estado': ['Exitosa', 'Fallida', 'Exitosa']
    }
    df = pd.DataFrame(data)
    
    # Convertir fechas
    df['fecha_convertida'] = df['fecha'].apply(FormatoService.convertir_fecha)
    
    # Convertir montos
    df['monto_convertido'] = df['monto'].apply(FormatoService.convertir_monto)
    
    # Verificar que las conversiones se realizaron correctamente
    assert isinstance(df['fecha_convertida'].iloc[0], datetime)
    assert isinstance(df['monto_convertido'].iloc[0], Decimal)
    
    # Verificar valores específicos
    assert df['fecha_convertida'].iloc[0] == datetime(2023, 1, 1)
    assert df['monto_convertido'].iloc[0] == Decimal('100.50')
    assert df['monto_convertido'].iloc[1] == Decimal('1200.75')
    assert df['monto_convertido'].iloc[2] == Decimal('300.25')


# Pruebas para el manejo de valores nulos o faltantes
def test_manejo_valores_nulos():
    # Crear un DataFrame con valores nulos
    data = {
        'id_transaccion': ['TXN001', 'TXN002', None],
        'fecha': ['2023-01-01', None, '03-01-2023'],
        'cuenta_origen': ['123456', '234567', None],
        'cuenta_destino': [None, '765432', '876543'],
        'monto': ['$100.50', None, '€300.25'],
        'estado': ['Exitosa', 'Fallida', None]
    }
    df = pd.DataFrame(data)
    
    # Contar valores nulos antes de la limpieza
    nulos_antes = df.isna().sum().sum()
    
    # Limpiar valores nulos
    df_limpio = df.fillna({
        'id_transaccion': 'DESCONOCIDO',
        'fecha': '2023-01-01',
        'cuenta_origen': '000000',
        'cuenta_destino': '000000',
        'monto': '0.00',
        'estado': 'Desconocido'
    })
    
    # Contar valores nulos después de la limpieza
    nulos_despues = df_limpio.isna().sum().sum()
    
    # Verificar que se eliminaron todos los valores nulos
    assert nulos_antes > 0
    assert nulos_despues == 0
    
    # Verificar que los valores de reemplazo son correctos
    assert df_limpio['id_transaccion'].iloc[2] == 'DESCONOCIDO'
    assert df_limpio['fecha'].iloc[1] == '2023-01-01'
    assert df_limpio['cuenta_origen'].iloc[2] == '000000'
    assert df_limpio['cuenta_destino'].iloc[0] == '000000'
    assert df_limpio['monto'].iloc[1] == '0.00'
    assert df_limpio['estado'].iloc[2] == 'Desconocido'


# Integrar FormatoService con ArchivoService para las pruebas
def test_integrar_formato_service():
    # Crear una instancia de ArchivoService con una base de datos simulada
    archivo_service = ArchivoService(MagicMock())
    
    # Verificar que los métodos estáticos ya existen en ArchivoService
    assert hasattr(ArchivoService, 'convertir_fecha')
    assert hasattr(ArchivoService, 'convertir_monto')
    
    # Probar los métodos estáticos
    assert ArchivoService.convertir_fecha('2023-01-01') == datetime(2023, 1, 1)
    assert ArchivoService.convertir_monto('$1,234.56') == Decimal('1234.56') 