import io
import pandas as pd
from fastapi import UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime
from decimal import Decimal

from app.models.archivo import Archivo
from app.models.transaccion import Transaccion
from app.schemas.transaccion import TransaccionComparacion


class ArchivoService:
    def __init__(self, db: AsyncSession):
        self.db = db

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
        Soporta múltiples formatos de monto.
        """
        if isinstance(monto_str, (int, float, Decimal)):
            return Decimal(str(monto_str))
        
        # Eliminar símbolos de moneda y separadores de miles
        monto_limpio = str(monto_str)
        monto_limpio = monto_limpio.replace('$', '').replace(',', '')
        
        # Reemplazar punto decimal si es necesario
        if '.' in monto_limpio:
            monto_limpio = monto_limpio.replace('.', '.')
        
        try:
            return Decimal(monto_limpio)
        except:
            raise ValueError(f"No se pudo convertir el monto: {monto_str}")

    async def procesar_archivo(self, file: UploadFile):
        """
        Procesa un archivo Excel y almacena sus transacciones en la base de datos.
        """
        # Crear registro de archivo
        archivo = Archivo(nombre_archivo=file.filename)
        self.db.add(archivo)
        await self.db.flush()
        
        # Leer archivo Excel
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # Normalizar columnas y procesar dataframe
        df = self._normalizar_columnas(df)
        df = self._procesar_dataframe(df)
        
        # Mapear columnas a nombres estándar
        column_mapping = {
            'id_transaccion': ['id_transaccion', 'id', 'identificador', 'codigo'],
            'fecha': ['fecha', 'date', 'fecha_transaccion'],
            'cuenta_origen': ['cuenta_origen', 'origen', 'source', 'from'],
            'cuenta_destino': ['cuenta_destino', 'destino', 'destination', 'to'],
            'monto': ['monto', 'amount', 'valor', 'value'],
            'estado': ['estado', 'status', 'state']
        }
        
        # Encontrar las columnas correspondientes
        mapped_columns = {}
        for target_col, possible_cols in column_mapping.items():
            for col in possible_cols:
                if col in df.columns:
                    mapped_columns[target_col] = col
                    break
            
            if target_col not in mapped_columns:
                raise ValueError(f"No se encontró columna para {target_col}")
        
        # Crear transacciones
        for _, row in df.iterrows():
            # Convertir fecha si es necesario
            fecha = row[mapped_columns['fecha']]
            if not isinstance(fecha, datetime):
                fecha = pd.to_datetime(fecha)
            
            # Convertir row a diccionario y asegurar que sea serializable a JSON
            extra_data = {}
            for col, val in row.items():
                if isinstance(val, (pd.Timestamp, datetime)):
                    extra_data[col] = val.isoformat()
                elif isinstance(val, Decimal):
                    extra_data[col] = float(val)
                else:
                    extra_data[col] = val
            
            # Crear transacción
            transaccion = Transaccion(
                archivo_id=archivo.id,
                id_transaccion=str(row[mapped_columns['id_transaccion']]),
                fecha=fecha,
                cuenta_origen=str(row[mapped_columns['cuenta_origen']]),
                cuenta_destino=str(row[mapped_columns['cuenta_destino']]),
                monto=Decimal(str(row[mapped_columns['monto']])),
                estado=str(row[mapped_columns['estado']]),
                extra_data=extra_data
            )
            self.db.add(transaccion)
        
        await self.db.commit()
        await self.db.refresh(archivo)
        
        return archivo

    def _normalizar_columnas(self, df):
        """
        Normaliza los nombres de las columnas del DataFrame.
        """
        # Convertir a minúsculas y eliminar espacios
        df.columns = [col.lower().strip() for col in df.columns]
        return df
    
    def _procesar_dataframe(self, df):
        """
        Procesa el DataFrame para normalizar formatos de fecha y monto.
        """
        # Procesar columnas de fecha si existen
        for col in df.columns:
            if 'fecha' in col.lower():
                df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Procesar columnas de monto si existen
            if 'monto' in col.lower() or 'amount' in col.lower() or 'valor' in col.lower():
                # Convertir a string primero para manejar formatos con símbolos
                df[col] = df[col].astype(str).str.replace('$', '', regex=False)
                df[col] = df[col].str.replace(',', '', regex=False)
                # Convertir a Decimal en lugar de float
                df[col] = df[col].apply(lambda x: Decimal(x) if x else None)
        
        return df

    async def get_archivo_with_transacciones(self, archivo_id: int):
        """
        Obtiene un archivo con sus transacciones.
        """
        query = select(Archivo).options(selectinload(Archivo.transacciones)).where(Archivo.id == archivo_id)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_transacciones_by_archivo_id(self, archivo_id: int):
        """
        Obtiene todas las transacciones de un archivo.
        """
        archivo = await self.get_archivo_with_transacciones(archivo_id)
        if not archivo:
            raise ValueError(f"Archivo con ID {archivo_id} no encontrado")
        return archivo.transacciones

    async def identificar_coincidencias_exactas(self, archivo_id_1: int, archivo_id_2: int):
        """
        Identifica transacciones que coinciden exactamente entre dos archivos.
        """
        transacciones1 = await self.get_transacciones_by_archivo_id(archivo_id_1)
        transacciones2 = await self.get_transacciones_by_archivo_id(archivo_id_2)
        
        # Crear diccionarios para facilitar la comparación
        dict_transacciones1 = {t.id_transaccion: t for t in transacciones1}
        dict_transacciones2 = {t.id_transaccion: t for t in transacciones2}
        
        # Identificar coincidencias exactas
        coincidencias = []
        for id_transaccion, t1 in dict_transacciones1.items():
            if id_transaccion in dict_transacciones2:
                t2 = dict_transacciones2[id_transaccion]
                if t1.monto == t2.monto and t1.estado == t2.estado:
                    coincidencias.append({
                        'id_transaccion': t1.id_transaccion,
                        'fecha': t1.fecha,
                        'cuenta_origen': t1.cuenta_origen,
                        'cuenta_destino': t1.cuenta_destino,
                        'monto': t1.monto,
                        'estado': t1.estado
                    })
        
        return coincidencias

    async def identificar_discrepancias(self, archivo_id_1: int, archivo_id_2: int):
        """
        Identifica transacciones con el mismo ID pero con diferencias en monto o estado.
        """
        transacciones1 = await self.get_transacciones_by_archivo_id(archivo_id_1)
        transacciones2 = await self.get_transacciones_by_archivo_id(archivo_id_2)
        
        # Crear diccionarios para facilitar la comparación
        dict_transacciones1 = {t.id_transaccion: t for t in transacciones1}
        dict_transacciones2 = {t.id_transaccion: t for t in transacciones2}
        
        # Identificar discrepancias
        discrepancias = []
        for id_transaccion, t1 in dict_transacciones1.items():
            if id_transaccion in dict_transacciones2:
                t2 = dict_transacciones2[id_transaccion]
                if t1.monto != t2.monto or t1.estado != t2.estado:
                    discrepancias.append({
                        'id_transaccion': t1.id_transaccion,
                        'fecha': t1.fecha,
                        'cuenta_origen': t1.cuenta_origen,
                        'cuenta_destino': t1.cuenta_destino,
                        'monto_archivo_1': t1.monto,
                        'monto_archivo_2': t2.monto,
                        'estado_archivo_1': t1.estado,
                        'estado_archivo_2': t2.estado
                    })
        
        return discrepancias

    async def identificar_transacciones_unicas(self, archivo_id_1: int, archivo_id_2: int):
        """
        Identifica transacciones que solo existen en uno de los archivos.
        """
        transacciones1 = await self.get_transacciones_by_archivo_id(archivo_id_1)
        transacciones2 = await self.get_transacciones_by_archivo_id(archivo_id_2)
        
        # Crear conjuntos de IDs para facilitar la comparación
        ids_transacciones1 = {t.id_transaccion for t in transacciones1}
        ids_transacciones2 = {t.id_transaccion for t in transacciones2}
        
        # Identificar transacciones únicas en cada archivo
        unicas_archivo_1 = []
        for t in transacciones1:
            if t.id_transaccion not in ids_transacciones2:
                unicas_archivo_1.append({
                    'id_transaccion': t.id_transaccion,
                    'fecha': t.fecha,
                    'cuenta_origen': t.cuenta_origen,
                    'cuenta_destino': t.cuenta_destino,
                    'monto': t.monto,
                    'estado': t.estado
                })
        
        unicas_archivo_2 = []
        for t in transacciones2:
            if t.id_transaccion not in ids_transacciones1:
                unicas_archivo_2.append({
                    'id_transaccion': t.id_transaccion,
                    'fecha': t.fecha,
                    'cuenta_origen': t.cuenta_origen,
                    'cuenta_destino': t.cuenta_destino,
                    'monto': t.monto,
                    'estado': t.estado
                })
        
        return unicas_archivo_1, unicas_archivo_2

    async def comparar_archivos_excel(self, archivo_id_1: int, archivo_id_2: int):
        """
        Compara transacciones entre dos archivos y genera un Excel con los resultados.
        """
        # Obtener archivos
        query1 = select(Archivo).options(selectinload(Archivo.transacciones)).where(Archivo.id == archivo_id_1)
        query2 = select(Archivo).options(selectinload(Archivo.transacciones)).where(Archivo.id == archivo_id_2)
        
        result1 = await self.db.execute(query1)
        result2 = await self.db.execute(query2)
        
        archivo1 = result1.scalars().first()
        archivo2 = result2.scalars().first()
        
        if not archivo1:
            raise ValueError(f"Archivo con ID {archivo_id_1} no encontrado")
        
        if not archivo2:
            raise ValueError(f"Archivo con ID {archivo_id_2} no encontrado")
        
        # Crear diccionarios para facilitar la comparación
        transacciones1 = {t.id_transaccion: t for t in archivo1.transacciones}
        transacciones2 = {t.id_transaccion: t for t in archivo2.transacciones}
        
        # Listas para almacenar resultados
        coincidencias_exactas = []
        coincidencias_con_diferencias = []
        solo_archivo1 = []
        solo_archivo2 = []
        
        # Comparar transacciones
        for id_transaccion, t1 in transacciones1.items():
            if id_transaccion in transacciones2:
                t2 = transacciones2[id_transaccion]
                
                # Verificar si hay diferencias
                if t1.monto == t2.monto and t1.estado == t2.estado:
                    # Coincidencia exacta
                    coincidencias_exactas.append(TransaccionComparacion(
                        id_transaccion=t1.id_transaccion,
                        fecha=t1.fecha,
                        cuenta_origen=t1.cuenta_origen,
                        cuenta_destino=t1.cuenta_destino,
                        monto_archivo_1=t1.monto,
                        monto_archivo_2=t2.monto,
                        estado_archivo_1=t1.estado,
                        estado_archivo_2=t2.estado,
                        tipo_coincidencia="Coincidencia exacta"
                    ))
                else:
                    # Coincidencia con diferencias
                    tipo = "Diferencia en monto" if t1.monto != t2.monto else "Diferencia en estado"
                    coincidencias_con_diferencias.append(TransaccionComparacion(
                        id_transaccion=t1.id_transaccion,
                        fecha=t1.fecha,
                        cuenta_origen=t1.cuenta_origen,
                        cuenta_destino=t1.cuenta_destino,
                        monto_archivo_1=t1.monto,
                        monto_archivo_2=t2.monto,
                        estado_archivo_1=t1.estado,
                        estado_archivo_2=t2.estado,
                        tipo_coincidencia=tipo
                    ))
            else:
                # Solo en archivo 1
                solo_archivo1.append(TransaccionComparacion(
                    id_transaccion=t1.id_transaccion,
                    fecha=t1.fecha,
                    cuenta_origen=t1.cuenta_origen,
                    cuenta_destino=t1.cuenta_destino,
                    monto_archivo_1=t1.monto,
                    estado_archivo_1=t1.estado,
                    tipo_coincidencia="Solo en Archivo 1"
                ))
        
        # Transacciones solo en archivo 2
        for id_transaccion, t2 in transacciones2.items():
            if id_transaccion not in transacciones1:
                solo_archivo2.append(TransaccionComparacion(
                    id_transaccion=t2.id_transaccion,
                    fecha=t2.fecha,
                    cuenta_origen=t2.cuenta_origen,
                    cuenta_destino=t2.cuenta_destino,
                    monto_archivo_2=t2.monto,
                    estado_archivo_2=t2.estado,
                    tipo_coincidencia="Solo en Archivo 2"
                ))
        
        # Crear Excel con resultados
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Hoja 1: Coincidencias exactas
            if coincidencias_exactas:
                df_exactas = pd.DataFrame([t.dict() for t in coincidencias_exactas])
                df_exactas.to_excel(writer, sheet_name='Coincidencias Exactas', index=False)
            
            # Hoja 2: Coincidencias con diferencias
            if coincidencias_con_diferencias:
                df_diferencias = pd.DataFrame([t.dict() for t in coincidencias_con_diferencias])
                df_diferencias.to_excel(writer, sheet_name='Coincidencias con Diferencias', index=False)
            
            # Hoja 3: Solo en archivo 1
            if solo_archivo1:
                df_solo1 = pd.DataFrame([t.dict() for t in solo_archivo1])
                df_solo1.to_excel(writer, sheet_name='Solo en Archivo 1', index=False)
            
            # Hoja 4: Solo en archivo 2
            if solo_archivo2:
                df_solo2 = pd.DataFrame([t.dict() for t in solo_archivo2])
                df_solo2.to_excel(writer, sheet_name='Solo en Archivo 2', index=False)
        
        output.seek(0)
        
        # Devolver archivo Excel
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=comparacion_{archivo_id_1}_{archivo_id_2}.xlsx"}
        ) 