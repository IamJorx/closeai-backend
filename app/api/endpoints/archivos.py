from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.archivo_service import ArchivoService
from app.schemas.archivo import Archivo, ArchivoWithTransacciones

router = APIRouter()


@router.post("/upload", response_model=Archivo, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Carga un archivo Excel con transacciones bancarias.
    """
    if not file.filename.endswith(('.xlsx')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten archivos Excel (.xlsx)"
        )
    
    try:
        archivo_service = ArchivoService(db)
        return await archivo_service.procesar_archivo(file)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar el archivo: {str(e)}"
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