import streamlit as st
import pandas as pd
from sqlalchemy import text
from modules.db import get_engine

st.title("🛡 Auditoría de Usuarios")

engine = get_engine()

with engine.begin() as conn:
    df_users = pd.read_sql(
        text(
            """
            SELECT id, usuario, nombre, rol, activo, intentos_fallidos,
                   ultimo_login, requiere_reset
            FROM usuarios
            ORDER BY id
        """
        ),
        conn,
    )

    df_logs = pd.read_sql(
        text(
            """
            SELECT id, usuario, evento, fecha, ip
            FROM accesos
            ORDER BY fecha DESC
        """
        ),
        conn,
    )

st.subheader("👥 Estado de usuarios")
st.dataframe(df_users, use_container_width=True)

st.subheader("📅 Registro de accesos (logins, bloqueos, MFA)")
st.dataframe(df_logs, use_container_width=True)
