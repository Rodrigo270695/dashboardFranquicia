from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.turno import Turno
from app.schemas.turno import TurnosPaginados

router = APIRouter()


@router.get("", response_model=TurnosPaginados)
def listar_turnos(
    fecha_inicio: date | None = Query(None),
    fecha_fin: date | None = Query(None),
    oficina: str | None = Query(None),
    segmento: str | None = Query(None),
    servicio: str | None = Query(None),
    boton: str | None = Query(None),
    pagina: int = Query(1, ge=1),
    pagina_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(Turno)

    if fecha_inicio:
        q = q.filter(Turno.fecha >= fecha_inicio)
    if fecha_fin:
        q = q.filter(Turno.fecha <= fecha_fin)
    if oficina:
        q = q.filter(Turno.oficina == oficina)
    if segmento:
        q = q.filter(Turno.segmento == segmento)
    if servicio:
        q = q.filter(Turno.servicio == servicio)
    if boton:
        q = q.filter(Turno.boton == boton)

    total = q.count()
    datos = q.order_by(Turno.fecha.desc(), Turno.ini_espera).offset((pagina - 1) * pagina_size).limit(pagina_size).all()

    return {
        "total": total,
        "pagina": pagina,
        "pagina_size": pagina_size,
        "datos": datos,
    }
