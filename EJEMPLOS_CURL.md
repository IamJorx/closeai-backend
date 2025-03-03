# Ejemplos de Comandos curl para Probar la API de CloseAI

A continuación, se presentan varios comandos curl para probar la conexión y funcionalidad de la API de CloseAI. Estos comandos asumen que la API está ejecutándose en `http://localhost:8000` con la configuración predeterminada.

## Verificar que la API está en funcionamiento

### 1. Verificar la documentación de la API

```bash
curl -X GET http://localhost:8000/docs -I
```

Respuesta esperada:

```
HTTP/1.1 200 OK
date: Mon, 03 Mar 2025 04:11:10 GMT
server: uvicorn
content-length: 940
content-type: text/html; charset=utf-8
```

Este comando devuelve los encabezados de la página HTML de la documentación Swagger de la API.

### 2. Verificar el estado de la API

```bash
curl -X GET http://localhost:8000/api/v1/
```

## Endpoints de Transacciones

### 1. Obtener lista de transacciones

```bash
curl -X GET http://localhost:8000/api/v1/transacciones/
```

Respuesta (si no hay transacciones):

```
[]
```

### 2. Obtener transacciones con paginación

```bash
curl -X GET "http://localhost:8000/api/v1/transacciones/?skip=0&limit=10"
```

### 3. Obtener una transacción específica por ID

```bash
curl -X GET http://localhost:8000/api/v1/transacciones/1
```

Respuesta (si no existe la transacción):

```
{"detail":"Transacción con ID 1 no encontrada"}
```

## Endpoints de Archivos

### 1. Obtener un archivo específico con sus transacciones

```bash
curl -X GET http://localhost:8000/api/v1/archivos/1
```

Respuesta (si no existe el archivo):

```
{"detail":"Archivo con ID 1 no encontrado"}
```

### 2. Subir un archivo Excel con transacciones

```bash
curl -X POST \
  http://localhost:8000/api/v1/archivos/upload \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/ruta/a/tu/archivo.xlsx"
```

Reemplaza `/ruta/a/tu/archivo.xlsx` con la ruta real a un archivo Excel en tu sistema.

### 3. Comparar transacciones entre dos archivos

```bash
curl -X GET "http://localhost:8000/api/v1/archivos/comparar-excel/?archivo_id_1=1&archivo_id_2=2" \
  -o comparacion.xlsx
```

Este comando descargará el archivo Excel generado con la comparación y lo guardará como `comparacion.xlsx`.

## Verificación de Conexión a la Base de Datos

Si la API responde correctamente a cualquiera de las solicitudes anteriores que requieren acceso a la base de datos (como obtener transacciones), significa que la conexión a la base de datos está funcionando correctamente.

## Solución de Problemas

### Problemas de CORS

Si estás accediendo a la API desde un navegador y encuentras errores de CORS, asegúrate de que el origen de tu aplicación frontend esté incluido en la configuración `CORS_ORIGINS` en el archivo `.env`.

### Problemas de Autenticación

Si en el futuro se implementa autenticación, los comandos curl deberán incluir un encabezado de autorización, por ejemplo:

```bash
curl -X GET http://localhost:8000/api/v1/transacciones/ \
  -H "Authorization: Bearer tu_token_de_acceso"
```

### Verificar Variables de Entorno

Si encuentras problemas de conexión a la base de datos, puedes verificar que las variables de entorno se estén cargando correctamente con:

```bash
curl -X GET http://localhost:8000/docs
```

Y revisar que la documentación muestre la información correcta sobre los endpoints disponibles.

## Conclusión

Estas pruebas confirman que:

1. La API está funcionando correctamente
2. La conexión a la base de datos está establecida
3. Las variables de entorno se están cargando correctamente
4. La seguridad de la información sensible está garantizada al usar variables de entorno en lugar de hardcodear credenciales

Para cargar datos en la base de datos, puedes usar el endpoint de subida de archivos con un archivo Excel que contenga transacciones.
