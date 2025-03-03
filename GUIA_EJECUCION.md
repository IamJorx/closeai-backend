# Guía de Ejecución del Backend de CloseAI

Esta guía te ayudará a configurar y ejecutar el backend de CloseAI junto con su base de datos PostgreSQL de manera segura, utilizando Docker Compose y variables de entorno para proteger la información sensible.

## Requisitos Previos

- [Docker](https://docs.docker.com/get-docker/) y [Docker Compose](https://docs.docker.com/compose/install/) instalados
- Git para clonar el repositorio

## Pasos para la Ejecución

### 1. Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd closeai-backend
```

### 2. Configurar las Variables de Entorno

El proyecto utiliza variables de entorno para manejar información sensible como credenciales de base de datos. Sigue estos pasos:

1. Copia el archivo de ejemplo a un nuevo archivo `.env`:

```bash
cp .env.example .env
```

2. Edita el archivo `.env` con tus propias credenciales:

```
# API
API_V1_STR=/api/v1
PROJECT_NAME=Close AI

# PostgreSQL
POSTGRES_SERVER=postgres
POSTGRES_USER=tu_usuario
POSTGRES_PASSWORD=tu_contraseña_segura
POSTGRES_DB=closeai
POSTGRES_PORT=5432

# CORS
CORS_ORIGINS=["http://localhost:3000", "https://tu-frontend.com"]

# PGAdmin
PGADMIN_EMAIL=tu_email@ejemplo.com
PGADMIN_PASSWORD=tu_contraseña_segura_pgadmin
```

> ⚠️ **IMPORTANTE**: Nunca compartas tu archivo `.env` ni lo subas al repositorio. Este archivo contiene información sensible.

### 3. Iniciar los Servicios con Docker Compose

Una vez configuradas las variables de entorno, puedes iniciar todos los servicios:

```bash
docker-compose up -d
```

Este comando iniciará tres servicios:

- **API**: El backend de CloseAI en http://localhost:8000
- **PostgreSQL**: La base de datos (accesible internamente)
- **PGAdmin**: Interfaz web para administrar la base de datos en http://localhost:5050

### 4. Verificar que los Servicios Estén Funcionando

```bash
docker-compose ps
```

Deberías ver los tres servicios en estado "Up".

### 5. Acceder a la API

La API estará disponible en:

- http://localhost:8000
- Documentación de la API: http://localhost:8000/docs

### 6. Acceder a PGAdmin (Administración de Base de Datos)

1. Abre http://localhost:5050 en tu navegador
2. Inicia sesión con las credenciales que configuraste en el archivo `.env`:

   - Email: el valor de `PGADMIN_EMAIL`
   - Contraseña: el valor de `PGADMIN_PASSWORD`

3. Configura la conexión a la base de datos:
   - Haz clic en "Add New Server"
   - En la pestaña "General", asigna un nombre como "CloseAI DB"
   - En la pestaña "Connection", configura:
     - Host: `postgres` (nombre del servicio en docker-compose)
     - Port: `5432`
     - Maintenance database: el valor de `POSTGRES_DB` (por defecto "closeai")
     - Username: el valor de `POSTGRES_USER`
     - Password: el valor de `POSTGRES_PASSWORD`

### 7. Detener los Servicios

Cuando hayas terminado de trabajar, puedes detener los servicios:

```bash
docker-compose down
```

Para detener los servicios y eliminar los volúmenes (esto borrará los datos de la base de datos):

```bash
docker-compose down -v
```

## Solución de Problemas

### Los servicios no inician correctamente

Verifica los logs para identificar el problema:

```bash
docker-compose logs
```

Para ver los logs de un servicio específico:

```bash
docker-compose logs api
docker-compose logs postgres
docker-compose logs pgadmin
```

### Problemas de conexión a la base de datos

Si la API no puede conectarse a la base de datos, verifica:

1. Que las variables de entorno en el archivo `.env` sean correctas
2. Que el servicio de PostgreSQL esté funcionando: `docker-compose ps`
3. Los logs de la API y PostgreSQL para identificar errores específicos

## Consideraciones de Seguridad

1. **Nunca uses las credenciales de ejemplo en producción**. Cambia todas las contraseñas por valores seguros.
2. **No compartas tu archivo `.env`** con nadie ni lo subas al repositorio.
3. En entornos de producción, considera usar un gestor de secretos como Docker Secrets o HashiCorp Vault.
4. Limita el acceso a los puertos expuestos (5432 para PostgreSQL, 5050 para PGAdmin) mediante un firewall si el servidor es accesible públicamente.

## Desarrollo Local sin Docker

Si prefieres ejecutar la aplicación localmente sin Docker:

1. Configura una base de datos PostgreSQL en tu máquina
2. Actualiza el archivo `.env` con la configuración de tu base de datos local
3. Crea un entorno virtual e instala las dependencias:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. Ejecuta las migraciones de la base de datos:

```bash
alembic upgrade head
```

5. Inicia la aplicación:

```bash
uvicorn main:app --reload
```

La API estará disponible en http://localhost:8000.
