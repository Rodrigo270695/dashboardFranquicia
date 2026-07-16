"""
Efectividad Post-Atención

Atenciones = tickets de esa categoría en la tienda (por botón)
Q_post     = ventas en la tienda con estado y operación válidos, cuyo DNI/RUC
             existe en tickets de ESA misma categoría (Consulta / Compras / Reclamos)
Efectividad = Q_post / Atenciones × 100

Cruce de tiendas: normalizando los nombres (UPPER TRIM sin espacios dobles).
"""

from datetime import date
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import text

CONSULTA_BOTONES = ["consulta", "consulta hogar"]
COMPRAS_BOTONES = ["compras", "compras hogar", "compras ruc 20"]
RECLAMOS_BOTONES = ["reclamo", "reclamo hogar"]

CATEGORIAS = {
    "consulta": CONSULTA_BOTONES,
    "compras": COMPRAS_BOTONES,
    "reclamos": RECLAMOS_BOTONES,
}

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
    """Deja solo dígitos para comparar DNI/RUC entre ventas y tickets."""
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


def _qpost_por_categoria(
    db: Session,
    botones: list[str],
    params_base: dict,
    filtro_ventas: str,
    filtro_tickets_dni: str,
    estados_placeholders: str,
    operaciones_placeholders: str,
) -> dict[str, int]:
    """
    Q_post por tienda para una categoría:
    ventas con estado/operación válidos cuyo DNI existe en tickets
    de los botones de esa categoría.
    """
    params = dict(params_base)
    botones_placeholders = ", ".join(f":boton_{i}" for i in range(len(botones)))
    for i, boton in enumerate(botones):
        params[f"boton_{i}"] = boton.lower()

    dni_venta = _sql_dni_limpio("v.dni_ruc")
    dni_ticket = _sql_dni_limpio("t.numero_identificacion")

    sql = text(f"""
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
                AND LOWER(TRIM(t.boton)) IN ({botones_placeholders})
                {filtro_tickets_dni}
                AND {dni_ticket} = {dni_venta}
          )
        GROUP BY v.punto_de_venta
    """)

    return {
        _norm_tienda(row.punto_de_venta): int(row.total)
        for row in db.execute(sql, params).fetchall()
        if row.punto_de_venta
    }


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

    aten_idx: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for r in ticket_rows:
        aten_idx[_norm_tienda(r.oficina)][r.boton] += r.total

    # ── Q_post por categoría (cruce DNI solo con tickets de esa categoría) ─
    estados_placeholders = ", ".join(f":estado_{i}" for i in range(len(ESTADOS_QPOST)))
    for i, estado in enumerate(ESTADOS_QPOST):
        params[f"estado_{i}"] = estado
    operaciones_placeholders = ", ".join(
        f":operacion_{i}" for i in range(len(OPERACIONES_QPOST))
    )
    for i, operacion in enumerate(OPERACIONES_QPOST):
        params[f"operacion_{i}"] = operacion.upper()

    qpost_por_cat: dict[str, dict[str, int]] = {}
    for cat, botones in CATEGORIAS.items():
        qpost_por_cat[cat] = _qpost_por_categoria(
            db=db,
            botones=botones,
            params_base=params,
            filtro_ventas=filtro_ventas,
            filtro_tickets_dni=filtro_tickets_dni,
            estados_placeholders=estados_placeholders,
            operaciones_placeholders=operaciones_placeholders,
        )

    # Nombres completos de tienda desde ventas
    filtro_nombres = ""
    if fecha_inicio:
        filtro_nombres += " AND fecha >= :fi"
    if fecha_fin:
        filtro_nombres += " AND fecha <= :ff"
    sql_nombres = text(f"""
        SELECT DISTINCT punto_de_venta
        FROM ventas
        WHERE punto_de_venta IS NOT NULL
        {filtro_nombres}
    """)
    nombres_ventas: dict[str, str] = {
        _norm_tienda(r.punto_de_venta): r.punto_de_venta
        for r in db.execute(sql_nombres, params).fetchall()
        if r.punto_de_venta
    }

    def _cat_aten(norm: str, botones: list[str]) -> int:
        d = aten_idx.get(norm, {})
        return sum(d.get(b, 0) for b in botones)

    def _buscar_q(norm: str, qmap: dict[str, int]) -> int:
        if norm in qmap:
            return qmap[norm]
        for vnorm, total in qmap.items():
            if vnorm.startswith(norm) or norm.startswith(vnorm):
                return total
        return 0

    def _metricas(aten: int, q: int) -> dict:
        ef = round(q * 100.0 / aten, 1) if aten > 0 else 0.0
        return {"atenciones": aten, "q_post": q, "efectividad": ef}

    all_norms = set(aten_idx.keys())
    resultado = []

    for norm in sorted(all_norms):
        nombre = nombres_ventas.get(norm)
        if not nombre:
            for vnorm, vnombre in nombres_ventas.items():
                if vnorm.startswith(norm) or norm.startswith(vnorm):
                    nombre = vnombre
                    break
        nombre_display = nombre.title() if nombre else (
            next(
                (r.oficina for r in ticket_rows if _norm_tienda(r.oficina) == norm),
                norm,
            ).title()
        )

        resultado.append({
            "tienda": nombre_display,
            "region": "",
            "consulta": _metricas(
                _cat_aten(norm, CONSULTA_BOTONES),
                _buscar_q(norm, qpost_por_cat["consulta"]),
            ),
            "compras": _metricas(
                _cat_aten(norm, COMPRAS_BOTONES),
                _buscar_q(norm, qpost_por_cat["compras"]),
            ),
            "reclamos": _metricas(
                _cat_aten(norm, RECLAMOS_BOTONES),
                _buscar_q(norm, qpost_por_cat["reclamos"]),
            ),
        })

    return resultado
