# scripts/ingest_refacciones.py
# Ingesta básica de lista de REFACCIONES en Neon
# Plantilla inicial

import pandas as pd
from sqlalchemy import text
from modules.db import get_engine

FILE_PATH = "data/refacciones.xlsx"   # cambiar por archivo real

def ingest_refacciones():
    engine = get_engine()

    df = pd.read_excel(FILE_PATH)
    df.columns = [c.strip() for c in df.columns]

    # Para refacciones, no siempre viene modelo
    df_final = pd.DataFrame({
        "tipo_lista": "REFACCIONES",
        "clase": df.iloc[:, 1],
        "subclase": df.iloc[:, 2],
        "numero_parte": df.iloc[:, 3],
        "modelo": None,   # no aplica
        "descripcion": df.iloc[:, 4],
        "precio_lista": df.iloc[:, 5]
    })

    payload = df_final.to_json(orient="records")

    with engine.begin() as conn:

        conn.execute(text("""
            INSERT INTO ingesta_raw (source, payload)
            VALUES ('refacciones', :p)
        """), {"p": payload})

        for _, row in df_final.iterrows():

            exists = conn.execute(text("""
                SELECT COUNT(*) 
                FROM catalogo_productos
                WHERE numero_parte = :np
                AND tipo_lista = 'REFACCIONES'
            """), {"np": row["numero_parte"]}).scalar()

            if exists == 0:
                conn.execute(text("""
                    INSERT INTO catalogo_productos (
                        tipo_lista, clase, subclase, numero_parte,
                        modelo, descripcion, precio_lista
                    ) VALUES (
                        'REFACCIONES', :clase, :subclase, :np,
                        :modelo, :descripcion, :precio_lista
                    )
                """), {
                    "clase": row["clase"],
                    "subclase": row["subclase"],
                    "np": row["numero_parte"],
                    "modelo": None,
                    "descripcion": row["descripcion"],
                    "precio_lista": row["precio_lista"]
                })

    print("Ingesta de REFACCIONES completada.")

if __name__ == "__main__":
    ingest_refacciones()
