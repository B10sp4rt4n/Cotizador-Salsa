import os
import sys
from sqlalchemy import text

# Permitir import desde paquete salsa_cotizador
BASE_DIR = os.path.dirname(__file__)
sys.path.append(os.path.join(BASE_DIR, "..", "salsa_cotizador"))

from modules.db import get_engine

engine = get_engine()

def init_db():
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS ingesta_raw (
            id SERIAL PRIMARY KEY,
            source TEXT NOT NULL,
            payload JSONB NOT NULL,
            usuario TEXT DEFAULT 'admin',
            fecha TIMESTAMP DEFAULT NOW()
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            usuario TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nombre TEXT,
            rol TEXT CHECK (rol IN ('vendedor','admin')) DEFAULT 'vendedor',
            activo BOOLEAN DEFAULT TRUE,
            intentos_fallidos INTEGER DEFAULT 0,
            requiere_reset BOOLEAN DEFAULT FALSE,
            secret_mfa TEXT,
            ultimo_login TIMESTAMP,
            fecha_alta TIMESTAMP DEFAULT NOW()
        );
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS catalogo_productos (
            id SERIAL PRIMARY KEY,
            tipo_lista TEXT,
            clase TEXT,
            subclase TEXT,
            numero_parte TEXT,
            modelo TEXT,
            descripcion TEXT,
            precio_lista NUMERIC,
            activo BOOLEAN DEFAULT TRUE,
            fecha_actualizacion TIMESTAMP DEFAULT NOW()
        );
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS cotizacion (
            id SERIAL PRIMARY KEY,
            folio TEXT,
            cliente TEXT,
            notas TEXT,
            total NUMERIC,
            version INTEGER DEFAULT 1,
            fecha TIMESTAMP DEFAULT NOW()
        );
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS cotizacion_detalle (
            id SERIAL PRIMARY KEY,
            cot_id INTEGER REFERENCES cotizacion(id) ON DELETE CASCADE,
            numero_parte TEXT,
            descripcion TEXT,
            modelo TEXT,
            precio_lista NUMERIC,
            margen NUMERIC,
            descuento NUMERIC,
            precio_final NUMERIC,
            cantidad INTEGER,
            total_linea NUMERIC,
            override_flag BOOLEAN,
            fecha TIMESTAMP DEFAULT NOW()
        );
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS modificaciones_cotizacion (
            id SERIAL PRIMARY KEY,
            cot_det_id INTEGER REFERENCES cotizacion_detalle(id),
            usuario TEXT,
            campo TEXT,
            valor_original TEXT,
            valor_nuevo TEXT,
            motivo TEXT,
            fecha TIMESTAMP DEFAULT NOW()
        );
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS accesos (
            id SERIAL PRIMARY KEY,
            usuario TEXT,
            evento TEXT,
            fecha TIMESTAMP DEFAULT NOW(),
            ip TEXT
        );
        """))

    print("Base SALSA inicializada correctamente.")

if __name__ == "__main__":
    init_db()
