# scripts/reconstruir_catalogo.py
from sqlalchemy import text
import pandas as pd
from modules.db import get_engine


def reconstruir_catalogo(source):
    engine = get_engine()

    with engine.begin() as conn:
        raw = conn.execute(
            text(
                """
            SELECT payload FROM ingesta_raw
            WHERE source = :src
            ORDER BY fecha DESC
            LIMIT 1
        """
            ),
            {"src": source},
        ).fetchone()

        if not raw:
            print("No existe payload para ese source.")
            return

        df = pd.read_json(raw.payload)

        # Limpia catálogo actual del tipo
        conn.execute(
            text(
                """
            DELETE FROM catalogo_productos
            WHERE tipo_lista = :src
        """
            ),
            {"src": source.upper()},
        )

        # Inserta nuevamente
        for _, row in df.iterrows():
            conn.execute(
                text(
                    """
                INSERT INTO catalogo_productos (
                    tipo_lista, clase, subclase, numero_parte,
                    modelo, descripcion, precio_lista
                ) VALUES (
                    :t, :c, :s, :np, :m, :d, :p
                )
            """
                ),
                {
                    "t": source.upper(),
                    "c": row["clase"],
                    "s": row["subclase"],
                    "np": row["numero_parte"],
                    "m": row["modelo"],
                    "d": row["descripcion"],
                    "p": row["precio_lista"],
                },
            )

    print(f"Catálogo reconstruido para {source}.")


if __name__ == "__main__":
    reconstruir_catalogo("EQUIPOS")
