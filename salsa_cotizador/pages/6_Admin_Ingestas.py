import streamlit as st
import pandas as pd
import altair as alt
from sqlalchemy import text
from modules.db import get_engine

st.title("📥 Dashboard de Ingestas - SALSA Cotizador")

engine = get_engine()

with engine.begin() as conn:
    rows = conn.execute(text("""
        SELECT id, source, fecha, usuario, payload
        FROM ingesta_raw
        ORDER BY fecha DESC
    """)).fetchall()

df = pd.DataFrame(rows, columns=["id", "source", "fecha", "usuario", "payload"])

if df.empty:
    st.warning("No existen ingestas registradas.")
    st.stop()

# ---- Tabla resumen ----
st.subheader("📋 Ingestas registradas")
st.dataframe(df[["id", "source", "fecha", "usuario"]], use_container_width=True)

# ---- Gráfica por tipo de ingesta ----
st.subheader("📊 Ingestas por tipo de fuente")
chart1 = (
    alt.Chart(df)
    .mark_bar()
    .encode(
        x="source:N",
        y="count():Q",
        color="source:N"
    )
)
st.altair_chart(chart1, use_container_width=True)

# ---- Gráfica por día ----
df["solo_fecha"] = pd.to_datetime(df["fecha"]).dt.date

st.subheader("📈 Actividad diaria de ingestas")
chart2 = (
    alt.Chart(df)
    .mark_area()
    .encode(
        x="solo_fecha:T",
        y="count():Q",
        color="source:N",
    )
)
st.altair_chart(chart2, use_container_width=True)

# ---- Ver detalle payload ----
st.subheader("🔍 Ver detalle de payload")
registro = st.number_input("ID de ingesta:", min_value=1, step=1)

btn = st.button("Mostrar payload")
if btn:
    r = df[df["id"] == registro]
    if r.empty:
        st.error("ID no encontrado.")
    else:
        st.json(r.iloc[0]["payload"]) 
