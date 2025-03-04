import pandas as pd
from datetime import datetime

# Función para convertir fechas a formato string ISO
def format_date(dt):
    return dt.strftime('%Y-%m-%d %H:%M:%S')

# Datos para el primer archivo
data1 = {
    'id_transaccion': ['TX001', 'TX002', 'TX003', 'TX004', 'TX005'],
    'fecha': [
        format_date(datetime(2024, 3, 1)),
        format_date(datetime(2024, 3, 1)),
        format_date(datetime(2024, 3, 1)),
        format_date(datetime(2024, 3, 2)),
        format_date(datetime(2024, 3, 2))
    ],
    'cuenta_origen': ['1234567890', '2345678901', '3456789012', '4567890123', '5678901234'],
    'cuenta_destino': ['9876543210', '8765432109', '7654321098', '6543210987', '5432109876'],
    'monto': [1500.00, 2750.50, 500.25, 3000.00, 1250.75],
    'estado': ['Exitosa', 'Exitosa', 'Fallida', 'Exitosa', 'Fallida']
}

# Datos para el segundo archivo
data2 = {
    'id_transaccion': ['TX001', 'TX002', 'TX006', 'TX007', 'TX008'],
    'fecha': [
        format_date(datetime(2024, 3, 1)),
        format_date(datetime(2024, 3, 1)),
        format_date(datetime(2024, 3, 3)),
        format_date(datetime(2024, 3, 3)),
        format_date(datetime(2024, 3, 3))
    ],
    'cuenta_origen': ['1234567890', '2345678901', '6789012345', '7890123456', '8901234567'],
    'cuenta_destino': ['9876543210', '8765432109', '4321098765', '3210987654', '2109876543'],
    'monto': [1500.00, 2750.50, 800.00, 1750.25, 925.50],
    'estado': ['Exitosa', 'Fallida', 'Exitosa', 'Exitosa', 'Exitosa']
}

# Crear DataFrames
df1 = pd.DataFrame(data1)
df2 = pd.DataFrame(data2)

# Crear directorio para los archivos de prueba si no existe
import os
test_files_dir = os.path.join(os.path.dirname(__file__), 'test_files')
os.makedirs(test_files_dir, exist_ok=True)

# Guardar archivos Excel
file1_path = os.path.join(test_files_dir, 'transacciones_prueba.xlsx')
file2_path = os.path.join(test_files_dir, 'transacciones_prueba_2.xlsx')

df1.to_excel(file1_path, index=False)
df2.to_excel(file2_path, index=False)

print("Archivos de prueba creados exitosamente:")
print(f"- {file1_path}")
print(f"- {file2_path}") 