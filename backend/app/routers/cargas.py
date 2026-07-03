from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.carga import Carga
from app.schemas.carga import CargaResponse

router = APIRouter()


@router.get("", response_model=list[CargaResponse])
def listar_cargas(db: Session = Depends(get_db)):
    return db.query(Carga).order_by(Carga.fecha_carga.desc()).all()


@router.get("/{carga_id}", response_model=CargaResponse)
def detalle_carga(carga_id: int, db: Session = Depends(get_db)):
    carga = db.query(Carga).filter(Carga.id == carga_id).first()
    if not carga:
        raise HTTPException(status_code=404, detail="Carga no encontrada")
    return carga
