# Close AI Backend

Backend para el sistema Close AI, una aplicación para análisis y comparación de transacciones bancarias.

## Tecnologías utilizadas

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pandas
- FAISS
- SentenceTransformers

## Requisitos

- Python 3.9+ (importante: no es compatible con Python 2.7)
- Docker y Docker Compose

## Instalación y Ejecución

Para una guía detallada sobre cómo configurar y ejecutar el backend de manera segura, consulta el archivo [GUIA_EJECUCION.md](GUIA_EJECUCION.md).

Esta guía incluye:

- Configuración segura de variables de entorno
- Ejecución con Docker Compose
- Acceso a la base de datos y PGAdmin
- Solución de problemas comunes
- Consideraciones de seguridad

## Instalación Manual

1. Clonar el repositorio:

```bash
git clone https://github.com/IamJorx/close-ai.git
cd close-ai/closeai-backend
```

2. Verificar la versión de Python:

```bash
python --version
```

Si muestra Python 2.7, use `python3` en su lugar:

```bash
python3 --version
```

Asegúrese de que la versión sea 3.9 o superior.

3. Crear un entorno virtual:

```bash
# Si usa python3 explícitamente:
python3 -m venv venv

# O si python ya apunta a Python 3.9+:
python -m venv venv

# Activar el entorno virtual
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

4. Instalar dependencias:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

5. Crear archivo .env:

```bash
cp .env.example .env
```

6. Iniciar la base de datos con Docker:

```bash
docker-compose up -d
```

7. Ejecutar migraciones:

```bash
alembic upgrade head
```

## Ejecución

Para iniciar el servidor de desarrollo:

```bash
uvicorn main:app --reload
```

La API estará disponible en http://localhost:8000

La documentación de la API estará disponible en http://localhost:8000/docs

## Estructura del proyecto

```
closeai-backend/
├── alembic/              # Migraciones de base de datos
├── app/                  # Código principal
│   ├── api/              # Endpoints de la API
│   │   ├── endpoints/    # Rutas específicas
│   ├── core/             # Configuraciones
│   ├── db/               # Configuración de base de datos
│   ├── models/           # Modelos SQLAlchemy
│   ├── schemas/          # Esquemas Pydantic
│   ├── services/         # Lógica de negocio
│   └── utils/            # Utilidades
├── tests/                # Pruebas
├── .env.example          # Ejemplo de variables de entorno
├── alembic.ini           # Configuración de Alembic
├── docker-compose.yml    # Configuración de Docker
├── main.py               # Punto de entrada
└── requirements.txt      # Dependencias
```

## Endpoints principales

- `POST /api/v1/archivos/upload`: Carga un archivo Excel con transacciones.
- `GET /api/v1/archivos/{archivo_id}`: Obtiene un archivo con sus transacciones.
- `GET /api/v1/archivos/comparar-excel/`: Compara transacciones entre dos archivos y genera un Excel.
- `GET /api/v1/transacciones/`: Obtiene una lista de transacciones.
- `GET /api/v1/transacciones/{transaccion_id}`: Obtiene una transacción por su ID.

## Solución de problemas comunes

- **Error "No module named 'pandas'"**: Asegúrese de haber activado el entorno virtual y de haber instalado todas las dependencias con `pip install -r requirements.txt`.
- **Error al instalar dependencias**: Verifique que está usando Python 3.9+ y no Python 2.7. Actualice pip con `pip install --upgrade pip` antes de instalar las dependencias.
- **Error "No such file or directory: venv/bin/activate"**: Asegúrese de estar en el directorio correcto (`closeai-backend`) y de haber creado el entorno virtual.

## Pruebas

Para ejecutar las pruebas:

```bash
pytest
```

## Licencia

MIT
