from pydantic import BaseModel


class ResumenKPI(BaseModel):
    total_turnos: int
    turnos_atendidos: int
    turnos_derivados: int
    promedio_espera_min: float | None
    promedio_atencion_min: float | None
    oficinas_activas: int


class PuntoTendencia(BaseModel):
    periodo: str
    total_turnos: int
    promedio_espera_min: float | None


class ItemDimension(BaseModel):
    nombre: str
    total: int
    promedio_espera_min: float | None


class PuntoHora(BaseModel):
    hora: int
    total: int
