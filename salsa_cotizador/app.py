# app.py

import streamlit as st
from modules.auth import autenticar
from config.roles import ROLES

st.set_page_config(page_title="SALSA Cotizador", layout="wide")

if "usuario" not in st.session_state:
    st.session_state.usuario = None
if "rol" not in st.session_state:
    st.session_state.rol = None

def login_ui():
    st.title("Iniciar Sesión - SALSA Cotizador")

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Entrar"):
        user = autenticar(usuario, password)
        if user:
            st.session_state.usuario = user["nombre"]
            st.session_state.rol = user["rol"]
            st.success("Acceso concedido.")
            st.experimental_rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")

if st.session_state.usuario is None:
    login_ui()
else:
    st.sidebar.title("Menú Principal")
    st.sidebar.write(f"👤 {st.session_state.usuario} ({st.session_state.rol})")

    if st.session_state.rol == "vendedor":
        st.sidebar.page_link("pages/2_Cotizador.py", label="Cotizador")
        st.sidebar.page_link("pages/4_Historial_Cotizaciones.py", label="Mis Cotizaciones")
        st.sidebar.page_link("pages/8_Exportar_Propuesta_PDF.py", label="Generar PDF")

    if st.session_state.rol == "admin":
        st.sidebar.markdown("## 🧮 Cotizador")
        st.sidebar.page_link("pages/2_Cotizador.py", label="📄 Generar Cotización")
        st.sidebar.page_link("pages/4_Historial_Cotizaciones.py", label="📚 Historial")

        st.sidebar.markdown("---")
        st.sidebar.markdown("## 🛠 Administración")

        st.sidebar.page_link("pages/5_Admin_Usuarios.py", label="👥 Usuarios")
        st.sidebar.page_link("pages/6_Admin_Catalogo.py", label="📂 Catálogo / Ingesta")
        st.sidebar.page_link("pages/6_Admin_Ingestas.py", label="📥 Ingestas")
        st.sidebar.page_link("pages/7_Historial_Modificaciones.py", label="📝 Modificaciones")

        st.sidebar.markdown("---")
        st.sidebar.markdown("## 📄 Documentos")
        st.sidebar.page_link("pages/8_Exportar_Propuesta_PDF.py", label="🖨 Generar PDF")
        st.sidebar.page_link("pages/9_Auditoria_Catalogo.py", label="🧾 Auditoría Catálogo")

    st.title("SALSA Cotizador - Panel Principal")
    st.write("Sistema listo. Usa el menú lateral para navegar.")
