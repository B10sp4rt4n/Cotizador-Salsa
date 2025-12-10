# scripts/detectar_cambios.py
# Detección de cambios entre catálogo actual y nueva lista antes de ingestar

import sys
import pandas as pd
from sqlalchemy import text
from modules.db import get_engine


def detectar_cambios(df_nuevo, tipo_lista):
    engine = get_engine()

    # Convertir DataFrame a estructura clave-valor
    df_nuevo["clave"] = df_nuevo["numero_parte"].astype(str).str.upper()

    with engine.begin() as conn:
        df_actual = pd.read_sql(
            text(
                """
                SELECT numero_parte, descripcion, modelo, precio_lista
                FROM catalogo_productos
                WHERE tipo_lista = :tipo
            """
            ),
            conn,
            params={"tipo": tipo_lista},
        )

    df_actual["clave"] = df_actual["numero_parte"].astype(str).str.upper()

    # --------------------------
    # 1. Nuevos productos
    # --------------------------
    nuevos = df_nuevo[~df_nuevo["clave"].isin(df_actual["clave"])]

    # --------------------------
    # 2. Eliminados
    # --------------------------
    eliminados = df_actual[~df_actual["clave"].isin(df_nuevo["clave"])]

    # --------------------------
    # 3. Cambios de precio
    # --------------------------
    merged = df_actual.merge(df_nuevo, on="clave", suffixes=("_old", "_new"))
    cambios_precio = merged[
        merged["precio_lista_old"].astype(float)
        != merged["precio_lista_new"].astype(float)
    ]

    return {
        "nuevos": nuevos,
        "eliminados": eliminados,
        "cambios_precio": cambios_precio,
    }


def generar_alertas(dic):
    alertas = []

    if len(dic["cambios_precio"]) > 0:
        alertas.append("⚠ Cambios de precio detectados")

    if len(dic["eliminados"]) > 0:
        alertas.append("❌ Productos eliminados del catálogo")

    if len(dic["nuevos"]) > 0:
        alertas.append("🆕 Nuevos productos disponibles")

    return alertas


if __name__ == "__main__":
    # Uso: python scripts/detectar_cambios.py <archivo_excel> <TIPO_LISTA>
    if len(sys.argv) < 3:
        print("Uso: python scripts/detectar_cambios.py <archivo_excel> <TIPO_LISTA>")
        sys.exit(1)

    path = sys.argv[1]
    tipo = sys.argv[2]

    df_in = pd.read_excel(path)
    df_in.columns = [c.strip() for c in df_in.columns]

    # Normalizar columnas esperadas mínimas
    # Ajusta esto según tu layout real
    df_nuevo = pd.DataFrame(
        {
            "numero_parte": df_in.iloc[:, 3].astype(str),
            "modelo": df_in.iloc[:, 4].astype(str),
            "descripcion": df_in.iloc[:, 5].astype(str),
            "precio_lista": df_in.iloc[:, 6].astype(float),
        }
    )

    cambios = detectar_cambios(df_nuevo, tipo)

    print(f"Nuevos: {len(cambios['nuevos'])}")
    print(f"Eliminados: {len(cambios['eliminados'])}")
    print(f"Cambios de precio: {len(cambios['cambios_precio'])}")
