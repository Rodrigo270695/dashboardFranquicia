from datetime import datetime
from pydantic import BaseModel


class CargaBase(BaseModel):
    nombre_archivo: str
    registros_totales: int
    registros_nuevos: int
    registros_duplicados: int
    registros_con_error: int


class CargaResponse(CargaBase):
    id: int
    fecha_carga: datetime

    model_config = {"from_attributes": True}


class CargaResumen(BaseModel):
    mensaje: str
    carga_id: int
    nombre_archivo: str
    registros_totales: int
    registros_nuevos: int
    registros_duplicados: int
    registros_con_error: int
