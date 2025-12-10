import streamlit as st
from sqlalchemy import text
from modules.db import get_engine
import pandas as pd

st.title("Histórico de Ingestas - SALSA Cotizador")

engine = get_engine()

with engine.begin() as conn:
    rows = conn.execute(text("""
        SELECT id, source, fecha, usuario, payload
        FROM ingesta_raw
        ORDER BY fecha DESC
    """)).fetchall()

# Convertir filas a DataFrame
if rows:
    df = pd.DataFrame(rows, columns=["id", "source", "fecha", "usuario", "payload"])
else:
    df = pd.DataFrame(columns=["id", "source", "fecha", "usuario", "payload"])

st.dataframe(df[["id", "source", "fecha", "usuario"]])

registro = st.number_input("Ver payload de ID:", min_value=1, step=1)

if st.button("Mostrar"):
    r = df[df["id"] == registro]
    if r.empty:
        st.warning("No existe ese ID.")
    else:
        st.json(r.iloc[0]["payload"]) 
