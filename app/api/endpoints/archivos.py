from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse

from app.db.session import get_db
from app.services.archivo_service import ArchivoService
from app.schemas.archivo import Archivo, ArchivoWithTransacciones

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    try:
        # Validar el archivo
        if not file.filename.endswith(('.xlsx', '.xls')):
            return JSONResponse(
                status_code=400,
                content={"detail": "El archivo debe ser un Excel (.xlsx o .xls)"}
            )
        
        # Guardar el archivo temporalmente para debugging
        temp_file_path = f"/tmp/{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # Reposicionar el puntero del archivo
        await file.seek(0)
        
        # Intentar procesar el archivo con más logging
        print(f"Procesando archivo: {file.filename}")
        archivo_service = ArchivoService(db)
        result = await archivo_service.procesar_archivo(file)
        print(f"Archivo procesado exitosamente, ID: {result}")
        return {"archivo_id": result}
    except Exception as e:
        # Loguear el error con detalles
        import traceback
        error_details = traceback.format_exc()
        print(f"Error al procesar archivo: {str(e)}\n{error_details}")
        
        # Devolver un mensaje de error más informativo
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error al procesar el archivo: {str(e)}"}
        )


@router.get("/comparar-excel/")
async def comparar_excel(
    archivo_id_1: int,
    archivo_id_2: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Compara transacciones entre dos archivos y genera un Excel con los resultados.
    """
    archivo_service = ArchivoService(db)
    
    try:
        excel_bytes = await archivo_service.comparar_archivos_excel(archivo_id_1, archivo_id_2)
        
        return excel_bytes
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al comparar archivos: {str(e)}"
        )


@router.get("/{archivo_id}", response_model=ArchivoWithTransacciones)
async def get_archivo(
    archivo_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene un archivo con sus transacciones.
    """
    archivo_service = ArchivoService(db)
    archivo = await archivo_service.get_archivo_with_transacciones(archivo_id)
    
    if not archivo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Archivo con ID {archivo_id} no encontrado"
        )
    
    return archivo 