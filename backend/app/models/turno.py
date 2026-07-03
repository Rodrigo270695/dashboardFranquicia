from datetime import date, time, datetime
from sqlalchemy import (
    Integer, String, Date, Time, Boolean, SmallInteger,
    ForeignKey, UniqueConstraint, DateTime, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Turno(Base):
    __tablename__ = "turnos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    oficina: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    ticket: Mapped[str | None] = mapped_column(String(30))
    ini_espera: Mapped[time | None] = mapped_column(Time)

    tiempo_atencion: Mapped[time | None] = mapped_column(Time)
    fin: Mapped[time | None] = mapped_column(Time)
    tiempo_turno_seg: Mapped[int | None] = mapped_column(Integer)

    llamado: Mapped[time | None] = mapped_column(Time)
    atencion: Mapped[time | None] = mapped_column(Time)

    codigo_atendido: Mapped[str | None] = mapped_column(String(50))
    boton: Mapped[str | None] = mapped_column(String(100), index=True)
    grupo: Mapped[str | None] = mapped_column(String(50))
    negocio: Mapped[str | None] = mapped_column(String(100), index=True)
    segmento: Mapped[str | None] = mapped_column(String(100), index=True)
    subsegmento: Mapped[str | None] = mapped_column(String(200))
    servicio: Mapped[str | None] = mapped_column(String(100), index=True)

    dni_auto: Mapped[str | None] = mapped_column(String(20))
    nombre_usuario: Mapped[str | None] = mapped_column(String(255))
    codigo_modulo: Mapped[str | None] = mapped_column(String(50))
    tipo_identificacion: Mapped[str | None] = mapped_column(String(10))
    numero_identificacion: Mapped[str | None] = mapped_column(String(30))

    turno_derivado: Mapped[bool | None] = mapped_column(Boolean, default=False)
    cantidad: Mapped[int | None] = mapped_column(SmallInteger, default=0)

    carga_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("cargas.id"))
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    carga: Mapped["Carga"] = relationship("Carga", back_populates="turnos")

    __table_args__ = (
        UniqueConstraint("oficina", "fecha", "ticket", "ini_espera", name="uq_turno_identificador"),
    )
