# modules/cotizaciones.py

from sqlalchemy import text
from modules.db import get_engine

engine = get_engine()

def crear_cotizacion(usuario, cliente, notas, total, folio=None):
    with engine.begin() as conn:
        row = conn.execute(text("""
            INSERT INTO cotizacion (folio, cliente, notas, total, fecha)
            VALUES (:fol, :cli, :nota, :tot, NOW())
            RETURNING id;
        """), {"fol": folio, "cli": cliente, "nota": notas, "tot": total}).fetchone()
    return row.id

def insertar_detalle(cot_id, linea):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO cotizacion_detalle (
                cot_id, numero_parte, descripcion, modelo,
                precio_lista, margen, descuento, precio_final,
                cantidad, total_linea, override_flag
            ) VALUES (
                :cot, :np, :des, :mod,
                :pl, :mar, :desc, :pf,
                :cant, :tot, :ov
            )
        """), linea)

def guardar_cotizacion_en_neon(session_cot: dict, usuario: str = "admin") -> int:
    """Guarda la cotización completa (header + líneas) en Neon y devuelve el id."""
    header = session_cot.get("header", {})
    totales = session_cot.get("totales", {})
    lineas = session_cot.get("lineas", [])

    cliente = header.get("nombre") or header.get("razon_social") or "Cliente"
    notas = header.get("notas", "")
    total = float(totales.get("total", 0.0))

    cot_id = crear_cotizacion(usuario=usuario, cliente=cliente, notas=notas, total=total)

    for ln in lineas:
        payload = {
            "cot": cot_id,
            "np": ln.get("parte"),
            "des": ln.get("descripcion"),
            "mod": ln.get("modelo"),
            "pl": float(ln.get("precio_lista", 0) or 0),
            "mar": float(ln.get("margen", 0) or 0),
            "desc": float(ln.get("descuento", 0) or 0),
            "pf": float(ln.get("precio_venta", 0) or 0),
            "cant": int(ln.get("cantidad", 1) or 1),
            "tot": float(ln.get("total_linea", 0) or 0),
            "ov": False,
        }
        insertar_detalle(cot_id, payload)

    return cot_id

def listar_cotizaciones(limit: int = 100):
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT id, folio, cliente, total, fecha
            FROM cotizacion
            ORDER BY fecha DESC
            LIMIT :lim
        """), {"lim": limit}).fetchall()
    return rows

def obtener_detalles(cot_id: int):
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT id, numero_parte, descripcion, modelo, precio_lista,
                   margen, descuento, precio_final, cantidad, total_linea
            FROM cotizacion_detalle
            WHERE cot_id = :cot
            ORDER BY id
        """), {"cot": cot_id}).fetchall()
    return rows

def duplicar_cotizacion(cot_id: int, usuario: str = "admin") -> int:
    """Crea una copia de la cotización y sus detalles."""
    with engine.begin() as conn:
        # Obtener header original
        hdr = conn.execute(text("""
            SELECT cliente, notas, total FROM cotizacion WHERE id = :cot
        """), {"cot": cot_id}).fetchone()
    if not hdr:
        return 0
    nuevo_id = crear_cotizacion(usuario=usuario, cliente=hdr.cliente, notas=hdr.notas, total=hdr.total)
    # Copiar detalles
    detalles = obtener_detalles(cot_id)
    for d in detalles:
        payload = {
            "cot": nuevo_id,
            "np": d.numero_parte,
            "des": d.descripcion,
            "mod": d.modelo,
            "pl": float(d.precio_lista or 0),
            "mar": float(d.margen or 0),
            "desc": float(d.descuento or 0),
            "pf": float(d.precio_final or 0),
            "cant": int(d.cantidad or 1),
            "tot": float(d.total_linea or 0),
            "ov": False,
        }
        insertar_detalle(nuevo_id, payload)
    return nuevo_id
