#!/bin/bash

# Obtener el directorio del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
TEST_FILES_DIR="$SCRIPT_DIR/test_files"

# Colores para la salida
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con formato
print_step() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Función para extraer el ID del archivo de la respuesta JSON
get_file_id() {
    echo $1 | python3 -c "import sys, json; print(json.loads(sys.stdin.read())['id'])"
}

# Verificar que la API está funcionando
print_step "Verificando que la API está en funcionamiento"
if curl -s -f -X GET http://localhost:8000/docs > /dev/null; then
    print_success "API está funcionando"
else
    print_error "API no está respondiendo"
    exit 1
fi

# Crear archivos de prueba usando Python
print_step "Creando archivos de prueba"
python3 "$SCRIPT_DIR/create_test_files.py"

# Verificar que los archivos de prueba existen
if [ ! -f "$TEST_FILES_DIR/transacciones_prueba.xlsx" ] || [ ! -f "$TEST_FILES_DIR/transacciones_prueba_2.xlsx" ]; then
    print_error "No se encontraron los archivos de prueba"
    exit 1
fi

# Cargar el primer archivo
print_step "Cargando el primer archivo de transacciones"
RESPONSE1=$(curl -s -X POST \
    http://localhost:8000/api/v1/archivos/upload \
    -H "Content-Type: multipart/form-data" \
    -F "file=@$TEST_FILES_DIR/transacciones_prueba.xlsx")
echo $RESPONSE1
ARCHIVO_ID_1=$(get_file_id "$RESPONSE1")
print_success "Primer archivo cargado con ID: $ARCHIVO_ID_1"

# Verificar la carga del primer archivo
print_step "Verificando la carga del primer archivo"
curl -s -X GET http://localhost:8000/api/v1/archivos/$ARCHIVO_ID_1

# Cargar el segundo archivo
print_step "Cargando el segundo archivo de transacciones"
RESPONSE2=$(curl -s -X POST \
    http://localhost:8000/api/v1/archivos/upload \
    -H "Content-Type: multipart/form-data" \
    -F "file=@$TEST_FILES_DIR/transacciones_prueba_2.xlsx")
echo $RESPONSE2
ARCHIVO_ID_2=$(get_file_id "$RESPONSE2")
print_success "Segundo archivo cargado con ID: $ARCHIVO_ID_2"

# Verificar la carga del segundo archivo
print_step "Verificando la carga del segundo archivo"
curl -s -X GET http://localhost:8000/api/v1/archivos/$ARCHIVO_ID_2

# Obtener lista de transacciones
print_step "Obteniendo lista de todas las transacciones"
curl -s -X GET http://localhost:8000/api/v1/transacciones/

# Comparar los archivos
print_step "Comparando los dos archivos"
curl -s -X GET \
    "http://localhost:8000/api/v1/archivos/comparar-excel/?archivo_id_1=$ARCHIVO_ID_1&archivo_id_2=$ARCHIVO_ID_2" \
    -o "$TEST_FILES_DIR/comparacion_resultado.xlsx"

if [ -f "$TEST_FILES_DIR/comparacion_resultado.xlsx" ]; then
    print_success "Archivo de comparación generado exitosamente: $TEST_FILES_DIR/comparacion_resultado.xlsx"
else
    print_error "Error al generar el archivo de comparación"
fi

print_step "Pruebas completadas" 