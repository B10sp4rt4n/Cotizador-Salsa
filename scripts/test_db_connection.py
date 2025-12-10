import os
import sys

BASE_DIR = os.path.dirname(__file__)
sys.path.append(os.path.join(BASE_DIR, "..", "salsa_cotizador"))

from modules.db import get_engine

engine = get_engine()

try:
    with engine.connect() as conn:
        print("Conexión exitosa a Neon:", conn)
except Exception as e:
    print("Error en conexión:", e)
