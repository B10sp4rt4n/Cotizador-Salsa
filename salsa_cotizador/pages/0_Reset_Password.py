import streamlit as st
from sqlalchemy import text
from modules.db import get_engine
import bcrypt

st.title("🔐 Cambiar contraseña")

engine = get_engine()

if "reset_user" not in st.session_state:
    st.error("No hay usuario en modo reset.")
    st.stop()

new1 = st.text_input("Nueva contraseña", type="password")
new2 = st.text_input("Confirmar nueva contraseña", type="password")

if st.button("Guardar nueva contraseña"):
    if new1 != new2:
        st.error("Las contraseñas no coinciden.")
    elif len(new1) < 10:
        st.error("Debe tener al menos 10 caracteres.")
    else:
        hashed = bcrypt.hashpw(new1.encode(), bcrypt.gensalt()).decode()
        with engine.begin() as conn:
            conn.execute(text("""
                UPDATE usuarios
                SET password_hash = :pwd, requiere_reset = FALSE
                WHERE usuario = :u
            """), {"pwd": hashed, "u": st.session_state.reset_user})

        st.success("Contraseña cambiada exitosamente.")
        del st.session_state.reset_user
        st.rerun()
