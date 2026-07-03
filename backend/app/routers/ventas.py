import os
import tempfile
from datetime import date
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.venta import Venta
from app.services.ventas_processor import procesar_excel_ventas
from app.schemas.venta import VentaResumen, EfectividadItem, VentasPorPeriodo

router = APIRouter()


@router.post("/upload", response_model=VentaResumen)
def subir_excel_ventas(
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
        resultado = procesar_excel_ventas(ruta_tmp, archivo.filename, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando ventas: {str(e)}")
    finally:
        os.unlink(ruta_tmp)

    return {**resultado, "mensaje": "Ventas procesadas correctamente"}


@router.get("/efectividad", response_model=list[EfectividadItem])
def efectividad_por_tienda(
    fecha_inicio: date | None = Query(None),
    fecha_fin: date | None = Query(None),
    operacion: str | None = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(
        Venta.punto_de_venta,
        Venta.operacion,
        func.count(Venta.id_pk).label("total_ventas"),
        func.sum(
            func.cast(Venta.estado == "ENTREGADO ALMACEN", func.Integer)
        ).label("entregadas"),
    ).filter(
        Venta.punto_de_venta.isnot(None),
        Venta.operacion.isnot(None),
    )

    if fecha_inicio:
        q = q.filter(Venta.fecha >= fecha_inicio)
    if fecha_fin:
        q = q.filter(Venta.fecha <= fecha_fin)
    if operacion:
        q = q.filter(Venta.operacion.ilike(f"%{operacion}%"))

    resultados = q.group_by(Venta.punto_de_venta, Venta.operacion).order_by(
        func.count(Venta.id_pk).desc()
    ).all()

    return [
        {
            "punto_de_venta": r.punto_de_venta,
            "operacion": r.operacion,
            "total_ventas": r.total_ventas,
            "entregadas": r.entregadas or 0,
            "efectividad_pct": round((r.entregadas or 0) / r.total_ventas * 100, 2) if r.total_ventas else 0,
        }
        for r in resultados
    ]


@router.get("/por-periodo", response_model=list[VentasPorPeriodo])
def ventas_por_periodo(
    fecha_inicio: date | None = Query(None),
    fecha_fin: date | None = Query(None),
    agrupacion: str = Query("dia", pattern="^(dia|semana|mes)$"),
    db: Session = Depends(get_db),
):
    if agrupacion == "mes":
        periodo = func.to_char(Venta.fecha, "YYYY-MM")
    elif agrupacion == "semana":
        periodo = func.to_char(Venta.fecha, "IYYY-IW")
    else:
        periodo = func.to_char(Venta.fecha, "YYYY-MM-DD")

    q = db.query(
        periodo.label("periodo"),
        func.count(Venta.id_pk).label("total"),
        func.sum(
            func.cast(Venta.estado == "ENTREGADO ALMACEN", func.Integer)
        ).label("entregadas"),
    ).filter(Venta.fecha.isnot(None)).group_by("periodo").order_by("periodo")

    if fecha_inicio:
        q = q.filter(Venta.fecha >= fecha_inicio)
    if fecha_fin:
        q = q.filter(Venta.fecha <= fecha_fin)

    return [
        {"periodo": r.periodo, "total": r.total, "entregadas": r.entregadas or 0}
        for r in q.all()
    ]


@router.get("/operaciones")
def listar_operaciones(db: Session = Depends(get_db)):
    resultados = (
        db.query(Venta.operacion)
        .filter(Venta.operacion.isnot(None))
        .distinct()
        .order_by(Venta.operacion)
        .all()
    )
    return [r[0] for r in resultados]
