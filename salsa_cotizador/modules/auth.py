# modules/auth.py

import bcrypt
from sqlalchemy import text
from modules.db import get_engine

engine = get_engine()

def crear_usuario(usuario, password, nombre, rol="vendedor"):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO usuarios (usuario, password_hash, nombre, rol)
            VALUES (:u, :p, :n, :r)
        """), {"u": usuario, "p": hashed, "n": nombre, "r": rol})

def autenticar(usuario, password):
    with engine.begin() as conn:
        row = conn.execute(text("""
            SELECT id, password_hash, rol, nombre
            FROM usuarios
            WHERE usuario = :u AND activo = TRUE
        """), {"u": usuario}).fetchone()

    if not row:
        return None

    if bcrypt.checkpw(password.encode(), row.password_hash.encode()):
        return {"id": row.id, "nombre": row.nombre, "rol": row.rol}

    return None
