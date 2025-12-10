from salsa_cotizador.modules.db import get_engine

engine = get_engine()

try:
    with engine.connect() as conn:
        print("Conexión exitosa a Neon:", conn)
except Exception as e:
    print("Error en conexión:", e)
