from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.turno import Turno

router = APIRouter()


def _valores_unicos(db: Session, columna):
    resultados = (
        db.query(columna)
        .filter(columna.isnot(None))
        .distinct()
        .order_by(columna)
        .all()
    )
    return [r[0] for r in resultados]


@router.get("/oficinas")
def listar_oficinas(db: Session = Depends(get_db)):
    return _valores_unicos(db, Turno.oficina)


@router.get("/servicios")
def listar_servicios(db: Session = Depends(get_db)):
    return _valores_unicos(db, Turno.servicio)


@router.get("/segmentos")
def listar_segmentos(db: Session = Depends(get_db)):
    return _valores_unicos(db, Turno.segmento)


@router.get("/negocios")
def listar_negocios(db: Session = Depends(get_db)):
    return _valores_unicos(db, Turno.negocio)


@router.get("/botones")
def listar_botones(db: Session = Depends(get_db)):
    return _valores_unicos(db, Turno.boton)


@router.get("/grupos")
def listar_grupos(db: Session = Depends(get_db)):
    return _valores_unicos(db, Turno.grupo)
