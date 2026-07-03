from datetime import date, datetime
from sqlalchemy import Integer, String, Date, Numeric, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Venta(Base):
    __tablename__ = "ventas"

    id_pk: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # A - B
    id_venta: Mapped[str | None] = mapped_column(String(50), index=True)
    fecha: Mapped[date | None] = mapped_column(Date, index=True)

    # C - L
    tipo: Mapped[str | None] = mapped_column(String(100))
    operacion: Mapped[str | None] = mapped_column(String(150), index=True)
    tipo_duplicado: Mapped[str | None] = mapped_column(String(100))
    modelo: Mapped[str | None] = mapped_column(String(200))
    fabricante: Mapped[str | None] = mapped_column(String(100))
    categoria: Mapped[str | None] = mapped_column(String(100))
    imei: Mapped[str | None] = mapped_column(String(50))
    telefono: Mapped[str | None] = mapped_column(String(30))
    icc: Mapped[str | None] = mapped_column(String(50))
    nombre: Mapped[str | None] = mapped_column(String(255))

    # M - Z
    col_m: Mapped[str | None] = mapped_column(String(255))
    tipo_documento: Mapped[str | None] = mapped_column(String(50))
    dni_ruc: Mapped[str | None] = mapped_column(String(30), index=True)
    segmento: Mapped[str | None] = mapped_column(String(100), index=True)
    firma_digital: Mapped[str | None] = mapped_column(String(10))
    contrato_digital: Mapped[str | None] = mapped_column(String(10))
    forma_registro: Mapped[str | None] = mapped_column(String(150))
    consiente_rg: Mapped[str | None] = mapped_column(String(10))
    id_auto: Mapped[str | None] = mapped_column(String(50))
    autor: Mapped[str | None] = mapped_column(String(255), index=True)
    codigo_ff: Mapped[str | None] = mapped_column(String(50))
    id_contrato: Mapped[str | None] = mapped_column(String(50))
    grupo: Mapped[str | None] = mapped_column(String(100))
    punto_de_venta: Mapped[str | None] = mapped_column(String(200), index=True)

    # AA - AK
    sfin: Mapped[str | None] = mapped_column(String(50))
    codigo_biometrico: Mapped[str | None] = mapped_column(String(100))
    codigo_tm: Mapped[str | None] = mapped_column(String(100))
    tarifa: Mapped[str | None] = mapped_column(String(200))
    consumo: Mapped[str | None] = mapped_column(String(100))
    contrato_antiguo: Mapped[str | None] = mapped_column(String(100))
    promocion: Mapped[str | None] = mapped_column(String(255))
    operador_donante: Mapped[str | None] = mapped_column(String(100))
    operador_cedente: Mapped[str | None] = mapped_column(String(100))
    compromiso: Mapped[str | None] = mapped_column(String(100))
    nro_contrato: Mapped[str | None] = mapped_column(String(50))

    # AL - AW
    tarifa_servicio: Mapped[str | None] = mapped_column(String(100))
    accesorio: Mapped[str | None] = mapped_column(String(200))
    inei_s: Mapped[str | None] = mapped_column(String(50))
    estado: Mapped[str | None] = mapped_column(String(100), index=True)
    sub_estado: Mapped[str | None] = mapped_column(String(200))
    col_ap: Mapped[str | None] = mapped_column(String(255))
    factura_boleta: Mapped[str | None] = mapped_column(String(50))
    nota_credito: Mapped[str | None] = mapped_column(String(50))
    forma_pago: Mapped[str | None] = mapped_column(String(100))
    f_pago: Mapped[str | None] = mapped_column(String(50))
    banco: Mapped[str | None] = mapped_column(String(100))
    c_sin_interes: Mapped[str | None] = mapped_column(Numeric(12, 2))
    a_pagar_factura: Mapped[str | None] = mapped_column(Numeric(12, 2))
    a_pagar_otro: Mapped[str | None] = mapped_column(Numeric(12, 2))

    # AX - BC
    cuota: Mapped[str | None] = mapped_column(Numeric(12, 2))
    cuota_inicial: Mapped[str | None] = mapped_column(Numeric(12, 2))
    col_az: Mapped[str | None] = mapped_column(String(100))
    puntos: Mapped[str | None] = mapped_column(Numeric(12, 2))
    num_puntos: Mapped[str | None] = mapped_column(Numeric(12, 2))
    col_bc: Mapped[str | None] = mapped_column(String(100))

    # BD - BM
    observaciones: Mapped[str | None] = mapped_column(String(500))
    codigo_promo: Mapped[str | None] = mapped_column(String(100))
    td_order: Mapped[str | None] = mapped_column(String(50))
    td_order_action: Mapped[str | None] = mapped_column(String(50))
    anexo: Mapped[str | None] = mapped_column(String(100))
    codigo_ht: Mapped[str | None] = mapped_column(String(50))
    dnt_att: Mapped[str | None] = mapped_column(String(50))
    entrega_delivery: Mapped[str | None] = mapped_column(String(100))
    tipo_ht: Mapped[str | None] = mapped_column(String(100))
    descuento: Mapped[str | None] = mapped_column(Numeric(12, 2))

    # BN - BX
    descuento_cargo_fijo: Mapped[str | None] = mapped_column(Numeric(12, 2))
    cliente_potencial: Mapped[str | None] = mapped_column(String(10))
    declaracion_jurada: Mapped[str | None] = mapped_column(String(10))
    col_bq: Mapped[str | None] = mapped_column(String(100))
    tipo_registro_b: Mapped[str | None] = mapped_column(String(100))
    col_bs: Mapped[str | None] = mapped_column(String(100))
    tipo_devolucion: Mapped[str | None] = mapped_column(String(100))
    motivo_devolucion: Mapped[str | None] = mapped_column(String(255))
    motivo_valorado: Mapped[str | None] = mapped_column(String(255))
    codigo_t: Mapped[str | None] = mapped_column(String(50))
    codigo_suscripcion: Mapped[str | None] = mapped_column(String(50))

    # BY - CE
    desc_accesorios: Mapped[str | None] = mapped_column(String(255))
    cod_accesorios: Mapped[str | None] = mapped_column(String(100))
    cant_accesorios: Mapped[str | None] = mapped_column(Numeric(10, 2))
    pvp_accesorios: Mapped[str | None] = mapped_column(Numeric(12, 2))
    scoring_flex: Mapped[str | None] = mapped_column(Numeric(12, 2))
    sharepoint_op: Mapped[str | None] = mapped_column(String(200))
    porta_sin_chip: Mapped[str | None] = mapped_column(String(10))
    velocidad_ba: Mapped[str | None] = mapped_column(String(50))

    # Auditoría
    carga_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("cargas.id"))
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    carga: Mapped["Carga"] = relationship("Carga")

    __table_args__ = (
        UniqueConstraint("id_venta", name="uq_venta_id"),
    )
