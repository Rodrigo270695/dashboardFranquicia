"""
Efectividad Post-Atención

Atenciones = tickets de esa categoría en la tienda (por botón)
Q_post     = ventas en la tienda con estado y operación válidos, cuyo DNI/RUC
             exista como Número de identificación en tickets del mismo período
Efectividad = Q_post / Atenciones × 100

Cruce de tiendas: normalizando los nombres (UPPER TRIM sin espacios dobles).
"""

from datetime import date
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import text

CONSULTA_BOTONES = ["consulta", "consulta hogar"]
COMPRAS_BOTONES  = ["compras", "compras hogar", "compras ruc 20"]
RECLAMOS_BOTONES = ["reclamo", "reclamo hogar"]

# Estados de venta válidos para Q_post
ESTADOS_QPOST = [
    "ACTIVADO MOVISTAR",
    "ENTREGADO ALMACEN",
    "VISADO CAJA",
    "PREVENTA",
]

# Operaciones válidas para Q_post
OPERACIONES_QPOST = [
    "Postpago Alta",
    "Postpago Migracion M4",
    "Postpago Migración M4",
    "Postpago Portabilidad Migración M4 (Or. Postpago)",
    "Postpago Portabilidad Migracion M4 (Or. Postpago)",
    "Postpago Portabilidad Migración M4 (Or. Prepago)",
    "Postpago Portabilidad Migracion M4 (Or. Prepago)",
    "Postpago Portabilidad ( Origen Postpago )",
    "Postpago Portabilidad ( Origen Prepago )",
]


def _sql_dni_limpio(campo: str) -> str:
    """
    Normaliza DNI/RUC en SQL:
    - Quita espacios y comillas.
    - Quita sufijo .0 cuando Excel lo convirtió a decimal.
    - Deja solo dígitos.
    """
    return (
        "regexp_replace("
        "regexp_replace("
        f"regexp_replace(COALESCE({campo}, ''), '[[:space:]\"'']', '', 'g'), "
        "'\\.0+$', '', 'g'"
        "), "
        "'[^0-9]', '', 'g'"
        ")"
    )


def _norm_tienda(name: str) -> str:
    """Clave canónica para comparar nombres de tienda."""
    if not name:
        return ""
    return " ".join(name.upper().split())


def calcular_efectividad(
    db: Session,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
) -> list[dict]:

    params: dict = {}
    filtro = ""
    filtro_ventas = ""
    filtro_tickets_dni = ""
    if fecha_inicio:
        params["fi"] = fecha_inicio
        filtro += " AND fecha >= :fi"
        filtro_ventas += " AND v.fecha >= :fi"
        filtro_tickets_dni += " AND t.fecha >= :fi"
    if fecha_fin:
        params["ff"] = fecha_fin
        filtro += " AND fecha <= :ff"
        filtro_ventas += " AND v.fecha <= :ff"
        filtro_tickets_dni += " AND t.fecha <= :ff"

    # ── Atenciones por tienda y botón ──────────────────────────────────────
    sql_tickets = text(f"""
        SELECT oficina, LOWER(TRIM(boton)) AS boton, COUNT(*) AS total
        FROM turnos
        WHERE boton IS NOT NULL
        {filtro}
        GROUP BY oficina, LOWER(TRIM(boton))
    """)
    ticket_rows = db.execute(sql_tickets, params).fetchall()

    # Índice: {norm_tienda: {boton: count}}
    aten_idx: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for r in ticket_rows:
        aten_idx[_norm_tienda(r.oficina)][r.boton] += r.total

    # ── Ventas por tienda (solo estados y operaciones válidas para Q_post) ─
    estados_placeholders = ", ".join(f":estado_{i}" for i in range(len(ESTADOS_QPOST)))
    for i, estado in enumerate(ESTADOS_QPOST):
        params[f"estado_{i}"] = estado
    operaciones_placeholders = ", ".join(
        f":operacion_{i}" for i in range(len(OPERACIONES_QPOST))
    )
    for i, operacion in enumerate(OPERACIONES_QPOST):
        params[f"operacion_{i}"] = operacion.upper()

    dni_venta = _sql_dni_limpio("v.dni_ruc")
    dni_ticket = _sql_dni_limpio("t.numero_identificacion")

    sql_ventas = text(f"""
        SELECT v.punto_de_venta, COUNT(*) AS total
        FROM ventas v
        WHERE v.punto_de_venta IS NOT NULL
          AND UPPER(TRIM(v.estado)) IN ({estados_placeholders})
          AND UPPER(TRIM(v.operacion)) IN ({operaciones_placeholders})
          {filtro_ventas}
          AND {dni_venta} <> ''
          AND EXISTS (
              SELECT 1
              FROM turnos t
              WHERE t.numero_identificacion IS NOT NULL
                {filtro_tickets_dni}
                AND {dni_ticket} = {dni_venta}
          )
        GROUP BY v.punto_de_venta
    """)
    ventas_rows = db.execute(sql_ventas, params).fetchall()

    # Índice: {norm_tienda: (nombre_completo, total_ventas)}
    ventas_idx: dict[str, tuple[str, int]] = {}
    for r in ventas_rows:
        ventas_idx[_norm_tienda(r.punto_de_venta)] = (r.punto_de_venta, r.total)

    # ── Construir resultado ────────────────────────────────────────────────
    # Nombre de display: se prefiere el nombre completo de ventas
    nombre_display: dict[str, str] = {}
    for norm, oficina in {_norm_tienda(r.oficina): r.oficina for r in ticket_rows}.items():
        # Buscar match en ventas por prefijo común
        mejor: str | None = None
        mejor_len = 0
        for vnorm, (vnombre, _) in ventas_idx.items():
            # Coincidencia si uno empieza con el otro o viceversa
            if vnorm.startswith(norm) or norm.startswith(vnorm):
                if len(vnorm) > mejor_len:
                    mejor = vnombre
                    mejor_len = len(vnorm)
        nombre_display[norm] = mejor.title() if mejor else oficina.title()

    def _cat_aten(norm: str, botones: list[str]) -> int:
        d = aten_idx.get(norm, {})
        return sum(d.get(b, 0) for b in botones)

    def _metricas(aten: int, q: int) -> dict:
        ef = round(q * 100.0 / aten, 1) if aten > 0 else 0.0
        return {"atenciones": aten, "q_post": q, "efectividad": ef}

    all_norms = set(aten_idx.keys())
    resultado = []

    for norm in sorted(all_norms):
        # Q_post = ventas en la tienda (mismo período)
        _, q_total = ventas_idx.get(norm, ("", 0))
        # Si no hay match exacto, buscar por prefijo
        if q_total == 0:
            for vnorm, (_, vq) in ventas_idx.items():
                if vnorm.startswith(norm) or norm.startswith(vnorm):
                    q_total = vq
                    break

        consulta_aten = _cat_aten(norm, CONSULTA_BOTONES)
        compras_aten  = _cat_aten(norm, COMPRAS_BOTONES)
        reclamos_aten = _cat_aten(norm, RECLAMOS_BOTONES)

        resultado.append({
            "tienda": nombre_display.get(norm, norm.title()),
            "region": "",
            "consulta": _metricas(consulta_aten, q_total),
            "compras":  _metricas(compras_aten,  q_total),
            "reclamos": _metricas(reclamos_aten, q_total),
        })

    return resultado
