# Pruebas Manuales para CloseAI API

Este directorio contiene scripts para realizar pruebas manuales de la API de CloseAI.

## Estructura

```
manual_tests/
├── test_files/              # Directorio donde se guardan los archivos de prueba
│   ├── transacciones_prueba.xlsx
│   ├── transacciones_prueba_2.xlsx
│   └── comparacion_resultado.xlsx
├── create_test_files.py     # Script para generar archivos Excel de prueba
├── test_api.sh             # Script para probar la API
└── README.md               # Este archivo
```

## Requisitos

- Python 3.9+
- pandas
- openpyxl
- curl
- bash

## Instalación de dependencias

```bash
pip install pandas openpyxl
```

## Uso

1. Asegúrate de que la API esté en ejecución:

```bash
docker-compose up -d
```

2. Dale permisos de ejecución al script de pruebas:

```bash
chmod +x test_api.sh
```

3. Ejecuta el script de pruebas:

```bash
./test_api.sh
```

## Descripción de los datos de prueba

### Primer archivo (transacciones_prueba.xlsx)

- 5 transacciones (TX001-TX005)
- 3 transacciones exitosas, 2 fallidas
- Fechas: 1 y 2 de marzo de 2024

### Segundo archivo (transacciones_prueba_2.xlsx)

- 5 transacciones (TX001-TX002, TX006-TX008)
- 4 transacciones exitosas, 1 fallida
- Fechas: 1 y 3 de marzo de 2024

### Casos de prueba incluidos

- TX001: Coincidencia exacta entre ambos archivos
- TX002: Mismo ID pero diferente estado
- TX003-TX005: Solo presentes en el primer archivo
- TX006-TX008: Solo presentes en el segundo archivo

## Resultados esperados

El script generará un archivo `comparacion_resultado.xlsx` con cuatro hojas:

1. Coincidencias Exactas
2. Coincidencias con Diferencias
3. Solo en Archivo 1
4. Solo en Archivo 2

## Solución de problemas

Si encuentras algún error, verifica:

1. Que la API esté en ejecución
2. Que tengas todas las dependencias instaladas
3. Que los puertos necesarios (8000) estén disponibles
4. Que tengas permisos de escritura en el directorio `test_files`
