# modules/catalogo.py

from sqlalchemy import text
from modules.db import get_engine

engine = get_engine()

def obtener_clases(tipo_lista="EQUIPOS"):
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT DISTINCT clase FROM catalogo_productos
            WHERE tipo_lista = :t
            ORDER BY clase
        """), {"t": tipo_lista}).fetchall()
    return [r.clase for r in rows]

def obtener_subclases(clase, tipo_lista="EQUIPOS"):
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT DISTINCT subclase FROM catalogo_productos
            WHERE clase = :c AND tipo_lista = :t
            ORDER BY subclase
        """), {"c": clase, "t": tipo_lista}).fetchall()
    return [r.subclase for r in rows]

def buscar_productos(texto, tipo_lista="EQUIPOS"):
    t = f"%{texto.lower()}%"
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT id, numero_parte, modelo, descripcion, precio_lista, clase, subclase
            FROM catalogo_productos
            WHERE tipo_lista = :tipo
            AND (
                LOWER(numero_parte) LIKE :t OR
                LOWER(modelo) LIKE :t OR
                LOWER(descripcion) LIKE :t
            )
            ORDER BY modelo
            LIMIT 20
        """), {"t": t, "tipo": tipo_lista}).fetchall()
    return [dict(r) for r in rows]
