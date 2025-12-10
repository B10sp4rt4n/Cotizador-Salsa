import streamlit as st
import pandas as pd
import altair as alt
from sqlalchemy import text
from modules.db import get_engine

st.title("🛡 Security Center – SALSA Cotizador")

engine = get_engine()

with engine.begin() as conn:
    logs = pd.read_sql(text(
        """
        SELECT usuario, evento, fecha, ip
        FROM accesos
        ORDER BY fecha DESC
        """
    ), conn)

# ==========================
# Resumen rápido tipo SIEM
# ==========================

st.subheader("📌 Resumen de actividad")
col1, col2, col3 = st.columns(3)
col1.metric("Logins exitosos", len(logs[logs["evento"] == "login_ok"]))
col2.metric("Intentos fallidos", len(logs[logs["evento"] == "fail"]))
col3.metric("Bloqueos", len(logs[logs["evento"] == "bloqueado"]))

# ==========================
# Tendencia actividades
# ==========================

st.subheader("📈 Tendencia por día")
if not logs.empty:
    logs["fecha_simple"] = pd.to_datetime(logs["fecha"]).dt.date
    chart = (
        alt.Chart(logs)
        .mark_area()
        .encode(
            x="fecha_simple:T",
            y="count():Q",
            color="evento:N",
            tooltip=["fecha_simple", "evento", "count()"]
        )
    )
    st.altair_chart(chart, use_container_width=True)
else:
    st.info("Sin datos de eventos aún.")

# ==========================
# Actividad por usuario
# ==========================

st.subheader("👤 Actividad por usuario")
if not logs.empty:
    chart2 = (
        alt.Chart(logs)
        .mark_bar()
        .encode(
            x="usuario:N",
            y="count():Q",
            color="evento:N",
            tooltip=["usuario", "evento", "count()"]
        )
    )
    st.altair_chart(chart2, use_container_width=True)
else:
    st.info("Sin actividad de usuarios registrada.")

# ==========================
# IP sospechosas
# ==========================

st.subheader("🚨 IP con mayor actividad")
if not logs.empty:
    sospechosas = logs["ip"].value_counts().head(10)
    st.write(sospechosas)
else:
    st.info("Sin actividad de IP registrada.")
