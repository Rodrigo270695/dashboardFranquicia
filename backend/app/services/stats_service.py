from datetime import date
from sqlalchemy import func, cast, Integer, extract, text
from sqlalchemy.orm import Session
from app.models.turno import Turno


def _filtro_base(query, fecha_inicio: date | None, fecha_fin: date | None, oficina: str | None):
    if fecha_inicio:
        query = query.filter(Turno.fecha >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Turno.fecha <= fecha_fin)
    if oficina:
        query = query.filter(Turno.oficina == oficina)
    return query


def obtener_resumen(
    db: Session,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
    oficina: str | None = None,
) -> dict:
    q = db.query(Turno)
    q = _filtro_base(q, fecha_inicio, fecha_fin, oficina)

    total = q.count()
    atendidos = q.filter(Turno.cantidad == 1).count()
    derivados = q.filter(Turno.turno_derivado == True).count()
    oficinas = q.with_entities(func.count(func.distinct(Turno.oficina))).scalar()

    tiempo_espera = (
        db.query(
            func.avg(
                func.extract("epoch", Turno.llamado) - func.extract("epoch", Turno.ini_espera)
            )
        )
        .filter(Turno.llamado.isnot(None), Turno.ini_espera.isnot(None))
    )
    tiempo_espera = _filtro_base(tiempo_espera, fecha_inicio, fecha_fin, oficina)
    promedio_espera_seg = tiempo_espera.scalar()

    tiempo_atencion = (
        db.query(func.avg(Turno.tiempo_turno_seg))
        .filter(Turno.tiempo_turno_seg.isnot(None))
    )
    tiempo_atencion = _filtro_base(tiempo_atencion, fecha_inicio, fecha_fin, oficina)
    promedio_atencion_seg = tiempo_atencion.scalar()

    return {
        "total_turnos": total,
        "turnos_atendidos": atendidos,
        "turnos_derivados": derivados,
        "promedio_espera_min": round(promedio_espera_seg / 60, 2) if promedio_espera_seg else None,
        "promedio_atencion_min": round(promedio_atencion_seg / 60, 2) if promedio_atencion_seg else None,
        "oficinas_activas": oficinas or 0,
    }


def obtener_tendencia(
    db: Session,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
    agrupacion: str = "dia",
) -> list[dict]:
    if agrupacion == "mes":
        periodo = func.to_char(Turno.fecha, "YYYY-MM")
    elif agrupacion == "semana":
        periodo = func.to_char(Turno.fecha, "IYYY-IW")
    else:
        periodo = func.to_char(Turno.fecha, "YYYY-MM-DD")

    q = (
        db.query(
            periodo.label("periodo"),
            func.count(Turno.id).label("total_turnos"),
            func.avg(
                func.extract("epoch", Turno.llamado) - func.extract("epoch", Turno.ini_espera)
            ).label("promedio_espera_seg"),
        )
        .filter(Turno.fecha.isnot(None))
        .group_by("periodo")
        .order_by("periodo")
    )

    if fecha_inicio:
        q = q.filter(Turno.fecha >= fecha_inicio)
    if fecha_fin:
        q = q.filter(Turno.fecha <= fecha_fin)

    resultados = q.all()
    return [
        {
            "periodo": r.periodo,
            "total_turnos": r.total_turnos,
            "promedio_espera_min": round(r.promedio_espera_seg / 60, 2) if r.promedio_espera_seg else None,
        }
        for r in resultados
    ]


def obtener_por_dimension(
    db: Session,
    dimension: str,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
) -> list[dict]:
    columna_map = {
        "oficina": Turno.oficina,
        "servicio": Turno.servicio,
        "segmento": Turno.segmento,
        "boton": Turno.boton,
        "negocio": Turno.negocio,
        "grupo": Turno.grupo,
    }

    columna = columna_map.get(dimension)
    if not columna:
        return []

    q = (
        db.query(
            columna.label("nombre"),
            func.count(Turno.id).label("total"),
            func.avg(
                func.extract("epoch", Turno.llamado) - func.extract("epoch", Turno.ini_espera)
            ).label("promedio_espera_seg"),
        )
        .filter(columna.isnot(None))
        .group_by(columna)
        .order_by(func.count(Turno.id).desc())
    )

    if fecha_inicio:
        q = q.filter(Turno.fecha >= fecha_inicio)
    if fecha_fin:
        q = q.filter(Turno.fecha <= fecha_fin)

    resultados = q.all()
    return [
        {
            "nombre": r.nombre,
            "total": r.total,
            "promedio_espera_min": round(r.promedio_espera_seg / 60, 2) if r.promedio_espera_seg else None,
        }
        for r in resultados
    ]


def obtener_por_hora(
    db: Session,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
    oficina: str | None = None,
) -> list[dict]:
    q = (
        db.query(
            extract("hour", Turno.tiempo_atencion).label("hora"),
            func.count(Turno.id).label("total"),
        )
        .filter(Turno.tiempo_atencion.isnot(None))
        .group_by("hora")
        .order_by("hora")
    )

    q = _filtro_base(q, fecha_inicio, fecha_fin, oficina)

    resultados = q.all()
    return [{"hora": int(r.hora), "total": r.total} for r in resultados]
