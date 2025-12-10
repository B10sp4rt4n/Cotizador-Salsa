import streamlit as st
from modules.auth import validar_mfa

st.title("🔐 Verificación MFA")

if "mfa_user" not in st.session_state:
    st.error("No hay usuario en MFA.")
    st.stop()

token = st.text_input("Código MFA (app Google Authenticator)", max_chars=6)

if st.button("Verificar"):
    secret = st.session_state.mfa_user["secret"]
    if validar_mfa(secret, token):
        st.session_state.usuario = st.session_state.mfa_user["nombre"]
        st.session_state.rol = st.session_state.mfa_user["rol"]
        del st.session_state.mfa_user
        st.success("Acceso concedido.")
        st.rerun()
    else:
        st.error("Código incorrecto.")
