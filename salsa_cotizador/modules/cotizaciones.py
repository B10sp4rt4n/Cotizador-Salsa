# modules/cotizaciones.py

from sqlalchemy import text
from modules.db import get_engine

engine = get_engine()

def crear_cotizacion(usuario, cliente, notas, total):
    with engine.begin() as conn:
        row = conn.execute(text("""
            INSERT INTO cotizacion (cliente, notas, total, fecha)
            VALUES (:cli, :nota, :tot, NOW())
            RETURNING id;
        """), {"cli": cliente, "nota": notas, "tot": total}).fetchone()
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
