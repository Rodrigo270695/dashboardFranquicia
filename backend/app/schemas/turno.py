from datetime import date, time, datetime
from pydantic import BaseModel


class TurnoResponse(BaseModel):
    id: int
    oficina: str | None
    fecha: date | None
    ticket: str | None
    ini_espera: time | None
    tiempo_atencion: time | None
    fin: time | None
    tiempo_turno_seg: int | None
    llamado: time | None
    atencion: time | None
    codigo_atendido: str | None
    boton: str | None
    grupo: str | None
    negocio: str | None
    segmento: str | None
    subsegmento: str | None
    servicio: str | None
    dni_auto: str | None
    nombre_usuario: str | None
    codigo_modulo: str | None
    tipo_identificacion: str | None
    numero_identificacion: str | None
    turno_derivado: bool | None
    cantidad: int | None
    carga_id: int | None

    model_config = {"from_attributes": True}


class TurnosPaginados(BaseModel):
    total: int
    pagina: int
    pagina_size: int
    datos: list[TurnoResponse]
