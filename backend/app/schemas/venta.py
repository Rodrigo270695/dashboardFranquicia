from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel


class VentaResumen(BaseModel):
    mensaje: str
    carga_id: int
    nombre_archivo: str
    registros_totales: int
    registros_nuevos: int
    registros_duplicados: int
    registros_con_error: int


class EfectividadItem(BaseModel):
    punto_de_venta: str
    operacion: str
    total_ventas: int
    entregadas: int
    efectividad_pct: float


class VentasPorPeriodo(BaseModel):
    periodo: str
    total: int
    entregadas: int
