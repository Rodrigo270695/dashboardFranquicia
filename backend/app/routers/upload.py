import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.excel_processor import procesar_excel
from app.schemas.carga import CargaResumen

router = APIRouter()


@router.post("/cargas/upload", response_model=CargaResumen)
def subir_excel(
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not archivo.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos Excel (.xlsx o .xls)")

    sufijo = ".xls" if archivo.filename.endswith(".xls") and not archivo.filename.endswith(".xlsx") else ".xlsx"
    with tempfile.NamedTemporaryFile(delete=False, suffix=sufijo) as tmp:
        tmp.write(archivo.file.read())
        ruta_tmp = tmp.name

    try:
        resultado = procesar_excel(ruta_tmp, archivo.filename, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando el archivo: {str(e)}")
    finally:
        os.unlink(ruta_tmp)

    return {**resultado, "mensaje": "Archivo procesado correctamente"}
