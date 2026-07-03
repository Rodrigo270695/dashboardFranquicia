import pandas as pd
import numpy as np
from datetime import date
from decimal import Decimal, InvalidOperation
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.models.venta import Venta
from app.models.carga import Carga


def _leer_excel(ruta: str) -> pd.DataFrame:
    """Lee el archivo detectando el formato real por contenido, no por extensión."""
    with open(ruta, "rb") as f:
        cabecera = f.read(8)

    # Archivo XLSX real (formato ZIP)
    if cabecera[:4] == b"PK\x03\x04":
        return pd.read_excel(ruta, engine="openpyxl", dtype=str)

    # Archivo XLS binario real (formato BIFF, comienza con D0 CF)
    if cabecera[:2] == b"\xd0\xcf":
        return pd.read_excel(ruta, engine="xlrd", dtype=str)

    # HTML disfrazado de XLS (exportado desde sistemas web)
    try:
        tablas = pd.read_html(ruta, encoding="utf-8")
        if tablas:
            df = tablas[0]
            return df.astype(str)
    except Exception:
        pass

    # Último intento: leer como texto y procesar como CSV-like
    try:
        tablas = pd.read_html(ruta, encoding="latin-1")
        if tablas:
            return tablas[0].astype(str)
    except Exception:
        pass

    raise ValueError("Formato de archivo no soportado. Por favor guarda el archivo como .xlsx desde Excel.")

MAPA_COLUMNAS = {
    "Id": "id_venta",
    "Fecha": "fecha",
    "Tipo": "tipo",
    "Operación": "operacion",
    "Operacion": "operacion",
    "Tipo duplicado": "tipo_duplicado",
    "Modelo": "modelo",
    "Fabricante": "fabricante",
    "Categoría": "categoria",
    "Categoria": "categoria",
    "IMEI": "imei",
    "Teléfono": "telefono",
    "Telefono": "telefono",
    "ICC": "icc",
    "Nombre": "nombre",
    "Tipo Documento": "tipo_documento",
    "DNI/RUC": "dni_ruc",
    "Segmento": "segmento",
    "Firma Digital": "firma_digital",
    "Firma Digit": "firma_digital",
    "Contrato Digital": "contrato_digital",
    "Contrato Digit": "contrato_digital",
    "Forma Registro": "forma_registro",
    "Consiente RG": "consiente_rg",
    "Id auto": "id_auto",
    "Autor": "autor",
    "Código FF": "codigo_ff",
    "Codigo FF": "codigo_ff",
    "Id contrato": "id_contrato",
    "Id con": "id_contrato",
    "Grupo": "grupo",
    "Punto de venta": "punto_de_venta",
    "SFIN": "sfin",
    "Código Biométrico": "codigo_biometrico",
    "Codigo Biometrico": "codigo_biometrico",
    "Código TM": "codigo_tm",
    "Codigo TM": "codigo_tm",
    "Tarifa": "tarifa",
    "Consumo": "consumo",
    "Contrato antiguo": "contrato_antiguo",
    "Promoción": "promocion",
    "Promocion": "promocion",
    "Operador Donante": "operador_donante",
    "Operador Cedente": "operador_cedente",
    "Compromiso": "compromiso",
    "N° Contrato": "nro_contrato",
    "Nro Contrato": "nro_contrato",
    "Tarifa Servicio": "tarifa_servicio",
    "Servicio": "tarifa_servicio",
    "Accesorio": "accesorio",
    "INEI S": "inei_s",
    "Estado": "estado",
    "SubEstado": "sub_estado",
    "Fact./Boleta": "factura_boleta",
    "Fact Boleta": "factura_boleta",
    "Nota de crédito": "nota_credito",
    "Nota de credito": "nota_credito",
    "Forma Pago": "forma_pago",
    "F_pago": "f_pago",
    "Banco": "banco",
    "C. Sin Interés": "c_sin_interes",
    "C Sin Interes": "c_sin_interes",
    "A pagar factura": "a_pagar_factura",
    "A pagar otro": "a_pagar_otro",
    "Cuota": "cuota",
    "Cuota Inicial": "cuota_inicial",
    "Puntos": "puntos",
    "Núm. puntos": "num_puntos",
    "Num puntos": "num_puntos",
    "Observaciones": "observaciones",
    "Código Promo": "codigo_promo",
    "Codigo Promo": "codigo_promo",
    "tdOrder": "td_order",
    "tdOrderAction": "td_order_action",
    "Anexo": "anexo",
    "Código HT": "codigo_ht",
    "Codigo HT": "codigo_ht",
    "DNT Att": "dnt_att",
    "Entrega Delivery": "entrega_delivery",
    "Tipo HT": "tipo_ht",
    "Descuento": "descuento",
    "Descuento cargo fijo": "descuento_cargo_fijo",
    "Cliente Potencial": "cliente_potencial",
    "Declaración Jurada": "declaracion_jurada",
    "Declaracion Jurada": "declaracion_jurada",
    "Tipo Devolución": "tipo_devolucion",
    "Tipo Devolucion": "tipo_devolucion",
    "Motivo Devolución": "motivo_devolucion",
    "Motivo Devolucion": "motivo_devolucion",
    "Motivo Valorado": "motivo_valorado",
    "Código Suscripción": "codigo_suscripcion",
    "Codigo Suscripcion": "codigo_suscripcion",
    "Desc. Accesorios": "desc_accesorios",
    "Cod. Accesorios": "cod_accesorios",
    "Cant. Accesorios": "cant_accesorios",
    "PVP Accesorios": "pvp_accesorios",
    "Scoring Flex": "scoring_flex",
    "Sharepoint Op": "sharepoint_op",
    "Porta Sin Chip": "porta_sin_chip",
    "Velocidad_BA": "velocidad_ba",
}

COLUMNAS_NUMERICAS = {
    "c_sin_interes", "a_pagar_factura", "a_pagar_otro", "cuota",
    "cuota_inicial", "puntos", "num_puntos", "descuento",
    "descuento_cargo_fijo", "cant_accesorios", "pvp_accesorios", "scoring_flex",
}


def _limpiar(valor) -> str | None:
    if valor is None or (isinstance(valor, float) and np.isnan(valor)):
        return None
    texto = str(valor).strip()
    return texto if texto and texto.lower() not in ("nan", "none", "") else None


def _parsear_fecha(valor) -> date | None:
    if valor is None or (isinstance(valor, float) and np.isnan(valor)):
        return None
    try:
        return pd.to_datetime(valor, dayfirst=True).date()
    except Exception:
        return None


def _parsear_decimal(valor):
    if valor is None or (isinstance(valor, float) and np.isnan(valor)):
        return None
    try:
        return Decimal(str(valor).replace(",", ".").strip())
    except (InvalidOperation, ValueError):
        return None


def procesar_excel_ventas(ruta_archivo: str, nombre_archivo: str, db: Session) -> dict:
    df = _leer_excel(ruta_archivo)
    df.columns = df.columns.str.strip()

    columnas_mapeadas = {}
    for col_real in df.columns:
        col_clean = col_real.strip()
        if col_clean in MAPA_COLUMNAS:
            columnas_mapeadas[col_real] = MAPA_COLUMNAS[col_clean]

    df = df.rename(columns=columnas_mapeadas)
    df = df.replace({np.nan: None, "nan": None, "None": None})

    carga = Carga(
        nombre_archivo=nombre_archivo,
        registros_totales=len(df),
        registros_nuevos=0,
        registros_duplicados=0,
        registros_con_error=0,
    )
    db.add(carga)
    db.flush()

    nuevos = 0
    duplicados = 0
    errores = 0

    for _, fila in df.iterrows():
        try:
            registro = {"carga_id": carga.id}

            for col_db in MAPA_COLUMNAS.values():
                if col_db not in fila:
                    continue
                valor = fila[col_db]
                if col_db == "fecha":
                    registro[col_db] = _parsear_fecha(valor)
                elif col_db in COLUMNAS_NUMERICAS:
                    registro[col_db] = _parsear_decimal(valor)
                else:
                    registro[col_db] = _limpiar(valor)

            if not registro.get("id_venta"):
                errores += 1
                continue

            stmt = (
                insert(Venta)
                .values(**registro)
                .on_conflict_do_nothing(constraint="uq_venta_id")
            )
            result = db.execute(stmt)
            if result.rowcount > 0:
                nuevos += 1
            else:
                duplicados += 1

        except Exception:
            errores += 1
            continue

    carga.registros_nuevos = nuevos
    carga.registros_duplicados = duplicados
    carga.registros_con_error = errores
    db.commit()

    return {
        "carga_id": carga.id,
        "nombre_archivo": nombre_archivo,
        "registros_totales": len(df),
        "registros_nuevos": nuevos,
        "registros_duplicados": duplicados,
        "registros_con_error": errores,
    }
