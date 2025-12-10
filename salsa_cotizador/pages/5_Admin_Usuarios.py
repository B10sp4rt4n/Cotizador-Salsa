import streamlit as st
import pandas as pd
import bcrypt
from sqlalchemy import text
from modules.db import get_engine
from modules.passwords import generar_password
import pyotp
import qrcode
from io import BytesIO

st.title("👥 Administración de Usuarios")

engine = get_engine()

with engine.begin() as conn:
    usuarios = conn.execute(text("""
        SELECT id, usuario, nombre, rol, activo, fecha_alta
        FROM usuarios
        ORDER BY id
    """)).fetchall()

df = pd.DataFrame(usuarios, columns=["ID", "Usuario", "Nombre", "Rol", "Activo", "Fecha Alta"])

st.subheader("Lista de Usuarios")
st.dataframe(df, use_container_width=True)

st.subheader("🔐 Resetear contraseña de usuario")

user_to_reset = st.selectbox(
    "Seleccione usuario",
    df["Usuario"].tolist() if not df.empty else []
)

if st.button("Generar nueva contraseña"):
    nueva = generar_password()
    st.session_state["pwd_reset"] = nueva
    st.success(f"Nueva contraseña generada: **{nueva}** (cópiala ahora)")

if "pwd_reset" in st.session_state and user_to_reset:
    if st.button("Aplicar cambio de contraseña"):
        hashed = bcrypt.hashpw(st.session_state["pwd_reset"].encode(), bcrypt.gensalt()).decode()

        with engine.begin() as conn:
            conn.execute(text("""
                UPDATE usuarios
                SET password_hash = :pwd
                WHERE usuario = :u
            """), {"pwd": hashed, "u": user_to_reset})

        st.success(f"La contraseña del usuario **{user_to_reset}** fue actualizada correctamente.")
        del st.session_state["pwd_reset"]

st.subheader("🔐 Activar / Desactivar MFA (Google Authenticator)")

usuario_mfa = st.selectbox("Seleccione usuario:", df["Usuario"].tolist() if not df.empty else [], key="mfa_user")

if usuario_mfa:
    with engine.begin() as conn:
        row = conn.execute(text("""
            SELECT secret_mfa FROM usuarios WHERE usuario = :u
        """), {"u": usuario_mfa}).fetchone()

    tiene_mfa = row and row.secret_mfa is not None

    if not tiene_mfa:
        if st.button("Activar MFA"):
            secret = pyotp.random_base32()
            with engine.begin() as conn2:
                conn2.execute(text("""
                    UPDATE usuarios SET secret_mfa = :s
                    WHERE usuario = :u
                """), {"s": secret, "u": usuario_mfa})

            st.success("MFA activado. Escanea el siguiente código:")

            totp = pyotp.TOTP(secret)
            url = totp.provisioning_uri(name=usuario_mfa, issuer_name="SALSA Cotizador")

            qr = qrcode.make(url)
            buf = BytesIO()
            qr.save(buf, format="PNG")
            st.image(buf.getvalue())
    else:
        st.info("El usuario ya tiene MFA activado.")
        if st.button("Desactivar MFA"):
            with engine.begin() as conn2:
                conn2.execute(text("""
                    UPDATE usuarios SET secret_mfa = NULL
                    WHERE usuario = :u
                """), {"u": usuario_mfa})

            st.success("MFA desactivado.")
