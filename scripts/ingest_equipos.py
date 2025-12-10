# scripts/ingest_equipos.py
# Ingesta básica de lista de EQUIPOS en Neon
# Plantilla para administrador SALSA Cotizador

import pandas as pd
from sqlalchemy import text
from salsa_cotizador.modules.db import get_engine

FILE_PATH = "data/equipos.xlsx"   # cambiar por tu archivo real

def ingest_equipos():
    engine = get_engine()

    # Leer archivo
    df = pd.read_excel(FILE_PATH)
    df.columns = [c.strip() for c in df.columns]

    # Homologación mínima (puedes ajustar según columnas reales)
    df_final = pd.DataFrame({
        "tipo_lista": "EQUIPOS",
        "clase": df.iloc[:, 1],
        "subclase": df.iloc[:, 2],
        "numero_parte": df.iloc[:, 3],
        "modelo": df.iloc[:, 4],
        "descripcion": df.iloc[:, 5],
        "precio_lista": df.iloc[:, 6]
    })

    # Guardar copia cruda en ingesta_raw
    payload = df_final.to_json(orient="records")

    with engine.begin() as conn:

        conn.execute(text("""
            INSERT INTO ingesta_raw (source, payload)
            VALUES ('equipos', :p)
        """), {"p": payload})

        # Ingesta incremental
        for _, row in df_final.iterrows():

            exists = conn.execute(text("""
                SELECT COUNT(*) 
                FROM catalogo_productos
                WHERE numero_parte = :np
                AND tipo_lista = 'EQUIPOS'
            """), {"np": row["numero_parte"]}).scalar()

            if exists == 0:
                conn.execute(text("""
                    INSERT INTO catalogo_productos (
                        tipo_lista, clase, subclase, numero_parte,
                        modelo, descripcion, precio_lista
                    ) VALUES (
                        'EQUIPOS', :clase, :subclase, :np,
                        :modelo, :descripcion, :precio_lista
                    )
                """), {
                    "clase": row["clase"],
                    "subclase": row["subclase"],
                    "np": row["numero_parte"],
                    "modelo": row["modelo"],
                    "descripcion": row["descripcion"],
                    "precio_lista": row["precio_lista"]
                })

    print("Ingesta de EQUIPOS completada.")

if __name__ == "__main__":
    ingest_equipos()
