# modules/auth.py

import bcrypt
from sqlalchemy import text
from modules.db import get_engine
import pyotp

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
            SELECT id, password_hash, rol, nombre, intentos_fallidos, requiere_reset, secret_mfa
            FROM usuarios
            WHERE usuario = :u AND activo = TRUE
        """), {"u": usuario}).fetchone()

    if not row:
        return None

    if row.intentos_fallidos is not None and row.intentos_fallidos >= 5:
        return "bloqueado"

    if bcrypt.checkpw(password.encode(), row.password_hash.encode()):
        with engine.begin() as conn:
            conn.execute(text("""
                UPDATE usuarios
                SET intentos_fallidos = 0,
                    ultimo_login = NOW()
                WHERE usuario = :u
            """), {"u": usuario})

        if row.requiere_reset:
            return {"id": row.id, "requiere_reset": True}

        if row.secret_mfa:
            return {"mfa": True, "secret": row.secret_mfa, "usuario": usuario, "rol": row.rol, "nombre": row.nombre}

        return {"id": row.id, "rol": row.rol, "nombre": row.nombre}
    else:
        with engine.begin() as conn:
            conn.execute(text("""
                UPDATE usuarios
                SET intentos_fallidos = COALESCE(intentos_fallidos, 0) + 1
                WHERE usuario = :u
            """), {"u": usuario})

        return None

def generar_mfa_secret():
    return pyotp.random_base32()

def validar_mfa(secret, token):
    totp = pyotp.TOTP(secret)
    return totp.verify(token)
