import pandas as pd
import numpy as np
import unicodedata
from datetime import date, time
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.models.turno import Turno
from app.models.carga import Carga

COLUMNAS_ESPERADAS = [
    "Oficina", "Date", "Ticket", "Ini.Espera", "Tiempos de Atencion",
    "Fin", "Tiempos del turno", "Llamado", "Atencion", "Codigo atendido",
    "BOTON", "Grupo", "Negocio", "Segmento", "Subsegmento", "Servicio",
    "DNI Auto", "Nombre de usuario", "Codigo modulo", "Tipo de identificacion",
    "Numero de identificacion", "Turno derivado", "CANTIDAD",
]

MAPA_COLUMNAS = {
    "Oficina": "oficina",
    "Date": "fecha",
    "Ticket": "ticket",
    "Ini.Espera": "ini_espera",
    "Tiempos de Atencion": "tiempo_atencion",
    "Fin": "fin",
    "Tiempos del turno": "tiempo_turno_seg",
    "Llamado": "llamado",
    "Atencion": "atencion",
    "Codigo atendido": "codigo_atendido",
    "BOTON": "boton",
    "Grupo": "grupo",
    "Negocio": "negocio",
    "Segmento": "segmento",
    "Subsegmento": "subsegmento",
    "Servicio": "servicio",
    "DNI Auto": "dni_auto",
    "Nombre de usuario": "nombre_usuario",
    "Codigo modulo": "codigo_modulo",
    "Tipo de identificacion": "tipo_identificacion",
    "Numero de identificacion": "numero_identificacion",
    "Turno derivado": "turno_derivado",
    "CANTIDAD": "cantidad",
}


def _normalizar_columna(valor: str) -> str:
    """Normaliza encabezados Excel: sin tildes, espacios dobles ni signos."""
    texto = str(valor)
    # Algunos XLS exportados desde web llegan con mojibake: "NÃºmero".
    try:
        texto = texto.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.lower().strip()
    for caracter in (".", "_", "\n", "\r", "\t", "-", "/"):
        texto = texto.replace(caracter, " ")
    return " ".join(texto.split())


def _resolver_columna_ticket(columna: str) -> str | None:
    normalizada = _normalizar_columna(columna)
    compacta = "".join(c for c in normalizada if c.isalnum())
    if normalizada in {
        "numero de identificacion",
        "nro de identificacion",
        "num de identificacion",
    }:
        return "numero_identificacion"
    if "numero" in normalizada and "identificacion" in normalizada:
        return "numero_identificacion"
    if "identific" in compacta and ("numero" in compacta or "nro" in compacta):
        return "numero_identificacion"
    return None


def _parsear_tiempo_a_segundos(valor) -> int | None:
    """Convierte HH:MM:SS (duración) a segundos."""
    if pd.isna(valor):
        return None
    try:
        if isinstance(valor, str):
            partes = valor.strip().split(":")
            if len(partes) == 3:
                h, m, s = int(partes[0]), int(partes[1]), int(float(partes[2]))
                return h * 3600 + m * 60 + s
        return None
    except Exception:
        return None


def _parsear_hora(valor) -> time | None:
    """Convierte una cadena HH:MM:SS a time."""
    if pd.isna(valor):
        return None
    try:
        if isinstance(valor, str):
            texto = valor.strip().lower().replace("am", "").replace("pm", "").strip()
            partes = texto.split(":")
            if len(partes) >= 2:
                h, m = int(partes[0]), int(partes[1])
                s = int(float(partes[2])) if len(partes) > 2 else 0
                return time(h % 24, m, s)
        if hasattr(valor, "hour"):
            return time(valor.hour, valor.minute, valor.second)
        return None
    except Exception:
        return None


def _parsear_fecha(valor) -> date | None:
    if pd.isna(valor):
        return None
    try:
        return pd.to_datetime(valor, dayfirst=True).date()
    except Exception:
        return None


def _limpiar_texto(valor) -> str | None:
    if pd.isna(valor):
        return None
    texto = str(valor).strip()
    return texto if texto else None


def _limpiar_identificacion(valor) -> str | None:
    if pd.isna(valor):
        return None
    if isinstance(valor, (int, np.integer)):
        return str(int(valor))
    if isinstance(valor, (float, np.floating)) and float(valor).is_integer():
        return str(int(valor))
    texto = str(valor).strip().replace('"', "").replace("'", "")
    if texto.endswith(".0"):
        texto = texto[:-2]
    digitos = "".join(c for c in texto if c.isdigit())
    return digitos or None


def _parsear_booleano(valor) -> bool | None:
    if pd.isna(valor):
        return None
    try:
        return bool(int(valor))
    except Exception:
        return None


def _leer_excel(ruta: str) -> pd.DataFrame:
    """Lee el archivo detectando el formato real por contenido, no por extensión."""
    with open(ruta, "rb") as f:
        cabecera = f.read(8)

    if cabecera[:4] == b"PK\x03\x04":
        return pd.read_excel(ruta, engine="openpyxl")

    if cabecera[:2] == b"\xd0\xcf":
        return pd.read_excel(ruta, engine="xlrd")

    try:
        tablas = pd.read_html(ruta, encoding="utf-8")
        if tablas:
            return tablas[0]
    except Exception:
        pass

    try:
        tablas = pd.read_html(ruta, encoding="latin-1")
        if tablas:
            return tablas[0]
    except Exception:
        pass

    raise ValueError("Formato de archivo no soportado. Por favor guarda el archivo como .xlsx desde Excel.")


def procesar_excel(ruta_archivo: str, nombre_archivo: str, db: Session) -> dict:
    """Lee el Excel, limpia los datos y hace upsert en PostgreSQL."""

    df = _leer_excel(ruta_archivo)

    df.columns = df.columns.str.strip()

    mapa_normalizado = {
        _normalizar_columna(col_excel): col_db
        for col_excel, col_db in MAPA_COLUMNAS.items()
    }
    columnas_normalizadas = {}
    for col_real in df.columns:
        col_db = mapa_normalizado.get(_normalizar_columna(col_real))
        col_db = col_db or _resolver_columna_ticket(str(col_real))
        if col_db:
            columnas_normalizadas[col_real] = col_db

    # Fallback por estructura fija del reporte: columna U = Número de identificación.
    # Esto evita perder el DNI si el encabezado llega truncado o con encoding raro.
    if "numero_identificacion" not in columnas_normalizadas.values() and len(df.columns) >= 21:
        columnas_normalizadas[df.columns[20]] = "numero_identificacion"

    df = df.rename(columns=columnas_normalizadas)

    columnas_presentes = [c for c in MAPA_COLUMNAS.values() if c in df.columns]
    df = df[columnas_presentes]

    df = df.replace({np.nan: None})

    registros = []
    errores = 0

    for _, fila in df.iterrows():
        try:
            registro = {
                "oficina": _limpiar_texto(fila.get("oficina")),
                "fecha": _parsear_fecha(fila.get("fecha")),
                "ticket": _limpiar_texto(fila.get("ticket")),
                "ini_espera": _parsear_hora(fila.get("ini_espera")),
                "tiempo_atencion": _parsear_hora(fila.get("tiempo_atencion")),
                "fin": _parsear_hora(fila.get("fin")),
                "tiempo_turno_seg": _parsear_tiempo_a_segundos(fila.get("tiempo_turno_seg")),
                "llamado": _parsear_hora(fila.get("llamado")),
                "atencion": _parsear_hora(fila.get("atencion")),
                "codigo_atendido": _limpiar_texto(fila.get("codigo_atendido")),
                "boton": _limpiar_texto(fila.get("boton")),
                "grupo": _limpiar_texto(fila.get("grupo")),
                "negocio": _limpiar_texto(fila.get("negocio")),
                "segmento": _limpiar_texto(fila.get("segmento")),
                "subsegmento": _limpiar_texto(fila.get("subsegmento")),
                "servicio": _limpiar_texto(fila.get("servicio")),
                "dni_auto": _limpiar_texto(fila.get("dni_auto")),
                "nombre_usuario": _limpiar_texto(fila.get("nombre_usuario")),
                "codigo_modulo": _limpiar_texto(fila.get("codigo_modulo")),
                "tipo_identificacion": _limpiar_texto(fila.get("tipo_identificacion")),
                "numero_identificacion": _limpiar_identificacion(fila.get("numero_identificacion")),
                "turno_derivado": _parsear_booleano(fila.get("turno_derivado")),
                "cantidad": int(fila["cantidad"]) if fila.get("cantidad") is not None else None,
            }

            if registro["oficina"] and registro["fecha"]:
                registros.append(registro)
            else:
                errores += 1

        except Exception:
            errores += 1
            continue

    carga = Carga(
        nombre_archivo=nombre_archivo,
        registros_totales=len(df),
        registros_nuevos=0,
        registros_duplicados=0,
        registros_con_error=errores,
    )
    db.add(carga)
    db.flush()

    nuevos = 0
    duplicados = 0

    for registro in registros:
        registro["carga_id"] = carga.id
        stmt = insert(Turno).values(**registro)
        columnas_actualizables = {
            col: getattr(stmt.excluded, col)
            for col in registro.keys()
            if col not in {"oficina", "fecha", "ticket", "ini_espera", "carga_id"}
        }
        stmt = stmt.on_conflict_do_update(
            constraint="uq_turno_identificador",
            set_=columnas_actualizables,
        )
        result = db.execute(stmt)
        if result.rowcount > 0:
            nuevos += 1

    carga.registros_nuevos = nuevos
    carga.registros_duplicados = duplicados

    db.commit()

    return {
        "carga_id": carga.id,
        "nombre_archivo": nombre_archivo,
        "registros_totales": len(df),
        "registros_nuevos": nuevos,
        "registros_duplicados": duplicados,
        "registros_con_error": errores,
    }
