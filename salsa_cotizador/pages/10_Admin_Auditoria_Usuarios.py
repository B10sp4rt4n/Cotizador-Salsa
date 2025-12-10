import streamlit as st
import pandas as pd
import altair as alt
import pydeck as pdk
from sqlalchemy import text
from modules.db import get_engine
from modules.geo import geolocalizar_ip

st.title("🛡 Auditoría de Usuarios - Seguridad SALSA")

engine = get_engine()

# Tabla usuarios
with engine.begin() as conn:
    df_users = pd.read_sql(text(
        """
        SELECT id, usuario, nombre, rol, activo,
               intentos_fallidos, ultimo_login, requiere_reset
        FROM usuarios
        ORDER BY id
        """
    ), conn)

# Tabla eventos
with engine.begin() as conn:
    df_logs = pd.read_sql(text(
        """
        SELECT id, usuario, evento, fecha, ip
        FROM accesos
        ORDER BY fecha DESC
        """
    ), conn)

# Mostrar usuarios
st.subheader("👥 Estado de Usuarios")
st.dataframe(df_users, use_container_width=True)

# Mostrar tabla accesos
st.subheader("📅 Registro de Accesos (Eventos)")
st.dataframe(df_logs, use_container_width=True)

# ==========================
# Gráficas de eventos
# ==========================

if not df_logs.empty:
    st.subheader("📊 Eventos por Tipo")
    chart_eventos = (
        alt.Chart(df_logs)
        .mark_bar()
        .encode(
            x="evento:N",
            y="count():Q",
            color="evento:N",
            tooltip=["evento", "count()"]
        )
    )
    st.altair_chart(chart_eventos, use_container_width=True)

    st.subheader("🌐 Frecuencia por IP")
    chart_ip = (
        alt.Chart(df_logs)
        .mark_bar()
        .encode(
            x="ip:N",
            y="count():Q",
            color="ip:N",
            tooltip=["ip", "count()"]
        )
    )
    st.altair_chart(chart_ip, use_container_width=True)

    st.subheader("📈 Accesos por Fecha")
    df_logs["fecha_simple"] = pd.to_datetime(df_logs["fecha"]).dt.date

    chart_date = (
        alt.Chart(df_logs)
        .mark_area()
        .encode(
            x="fecha_simple:T",
            y="count():Q",
            color="evento:N",
            tooltip=["fecha_simple", "count()", "evento"]
        )
    )
    st.altair_chart(chart_date, use_container_width=True)

    # Alertas básicas
    st.subheader("🚨 Alertas detectadas")
    alertas = []
    vc_eventos = df_logs["evento"].value_counts()
    if vc_eventos.get("bloqueado", 0) > 0:
        alertas.append("⚠ Se han detectado cuentas bloqueadas recientemente.")
    if vc_eventos.get("fail", 0) > 10:
        alertas.append("❗ Actividad sospechosa: múltiples intentos fallidos.")
    if df_logs["ip"].nunique() > 10:
        alertas.append("🌐 Múltiples IPs accediendo al sistema en un periodo corto.")
    if not alertas:
        st.success("No hay alertas de seguridad.")
    else:
        for a in alertas:
            st.warning(a)

    # Mapa mundial de actividad por IP
    st.subheader("🗺 Mapa de actividad por IP")
    coords = []
    for _, row in df_logs.iterrows():
        info = geolocalizar_ip(row["ip"])
        if info and info.get("lat") and info.get("lon"):
            coords.append({
                "usuario": row["usuario"],
                "evento": row["evento"],
                "ip": row["ip"],
                "lat": info["lat"],
                "lon": info["lon"],
            })

    if coords:
        df_geo = pd.DataFrame(coords)
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v9',
            initial_view_state=pdk.ViewState(latitude=20, longitude=-100, zoom=2),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=df_geo,
                    get_position='[lon, lat]',
                    get_radius=200000,
                    get_color='[255, 0, 0, 160]',
                    pickable=True,
                )
            ],
            tooltip={"text": "Usuario: {usuario}\nEvento: {evento}\nIP: {ip}"}
        ))
    else:
        st.info("No hay IPs geolocalizables registradas aún.")
else:
    st.info("No hay eventos registrados en accesos.")
