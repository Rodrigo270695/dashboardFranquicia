from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.estadisticas import ResumenKPI, PuntoTendencia, ItemDimension, PuntoHora
from app.services import stats_service
from app.services import efectividad_service

router = APIRouter()


@router.get("/resumen", response_model=ResumenKPI)
def resumen_kpi(
    fecha_inicio: date | None = Query(None),
    fecha_fin: date | None = Query(None),
    oficina: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return stats_service.obtener_resumen(db, fecha_inicio, fecha_fin, oficina)


@router.get("/tendencia", response_model=list[PuntoTendencia])
def tendencia(
    fecha_inicio: date | None = Query(None),
    fecha_fin: date | None = Query(None),
    agrupacion: str = Query("dia", pattern="^(dia|semana|mes)$"),
    db: Session = Depends(get_db),
):
    return stats_service.obtener_tendencia(db, fecha_inicio, fecha_fin, agrupacion)


@router.get("/por-oficina", response_model=list[ItemDimension])
def por_oficina(
    fecha_inicio: date | None = Query(None),
    fecha_fin: date | None = Query(None),
    db: Session = Depends(get_db),
):
    return stats_service.obtener_por_dimension(db, "oficina", fecha_inicio, fecha_fin)


@router.get("/por-servicio", response_model=list[ItemDimension])
def por_servicio(
    fecha_inicio: date | None = Query(None),
    fecha_fin: date | None = Query(None),
    db: Session = Depends(get_db),
):
    return stats_service.obtener_por_dimension(db, "servicio", fecha_inicio, fecha_fin)


@router.get("/por-segmento", response_model=list[ItemDimension])
def por_segmento(
    fecha_inicio: date | None = Query(None),
    fecha_fin: date | None = Query(None),
    db: Session = Depends(get_db),
):
    return stats_service.obtener_por_dimension(db, "segmento", fecha_inicio, fecha_fin)


@router.get("/por-boton", response_model=list[ItemDimension])
def por_boton(
    fecha_inicio: date | None = Query(None),
    fecha_fin: date | None = Query(None),
    db: Session = Depends(get_db),
):
    return stats_service.obtener_por_dimension(db, "boton", fecha_inicio, fecha_fin)


@router.get("/por-negocio", response_model=list[ItemDimension])
def por_negocio(
    fecha_inicio: date | None = Query(None),
    fecha_fin: date | None = Query(None),
    db: Session = Depends(get_db),
):
    return stats_service.obtener_por_dimension(db, "negocio", fecha_inicio, fecha_fin)


@router.get("/por-hora", response_model=list[PuntoHora])
def por_hora(
    fecha_inicio: date | None = Query(None),
    fecha_fin: date | None = Query(None),
    oficina: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return stats_service.obtener_por_hora(db, fecha_inicio, fecha_fin, oficina)


@router.get("/efectividad")
def efectividad(
    fecha_inicio: date | None = Query(None),
    fecha_fin: date | None = Query(None),
    db: Session = Depends(get_db),
):
    return efectividad_service.calcular_efectividad(db, fecha_inicio, fecha_fin)


@router.get("/validacion")
def validacion(
    fecha_inicio: date | None = Query(None),
    fecha_fin: date | None = Query(None),
    db: Session = Depends(get_db),
):
    """Desglose de tickets por tienda y botón para validar contra el Excel."""
    from sqlalchemy import text as _text
    params: dict = {}
    filtro = ""
    if fecha_inicio:
        params["fi"] = fecha_inicio
        filtro += " AND fecha >= :fi"
    if fecha_fin:
        params["ff"] = fecha_fin
        filtro += " AND fecha <= :ff"

    sql = _text(f"""
        SELECT
            oficina,
            INITCAP(LOWER(TRIM(boton))) AS boton,
            COUNT(*) AS total,
            MIN(fecha) AS desde,
            MAX(fecha) AS hasta,
            COUNT(DISTINCT fecha) AS dias_con_datos
        FROM turnos
        WHERE boton IS NOT NULL
        {filtro}
        GROUP BY oficina, LOWER(TRIM(boton))
        ORDER BY oficina, total DESC
    """)
    rows = db.execute(sql, params).fetchall()

    # Agrupar por tienda
    tiendas: dict = {}
    for r in rows:
        t = r.oficina
        if t not in tiendas:
            tiendas[t] = {"tienda": t, "total_tickets": 0, "botones": [], "desde": str(r.desde), "hasta": str(r.hasta)}
        tiendas[t]["total_tickets"] += r.total
        tiendas[t]["botones"].append({"boton": r.boton, "total": r.total})

    return list(tiendas.values())
