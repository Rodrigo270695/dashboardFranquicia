from datetime import datetime
from sqlalchemy import Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Carga(Base):
    __tablename__ = "cargas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre_archivo: Mapped[str] = mapped_column(String(255), nullable=False)
    registros_totales: Mapped[int] = mapped_column(Integer, default=0)
    registros_nuevos: Mapped[int] = mapped_column(Integer, default=0)
    registros_duplicados: Mapped[int] = mapped_column(Integer, default=0)
    registros_con_error: Mapped[int] = mapped_column(Integer, default=0)
    fecha_carga: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    turnos: Mapped[list["Turno"]] = relationship("Turno", back_populates="carga")
