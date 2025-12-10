# app.py

import streamlit as st
from modules.auth import autenticar
from modules.logger import registrar_evento
from config.roles import ROLES
import requests
from modules.settings import SMTP_USER, SMTP_PASS, RECORDIA_ENDPOINT, RECORDIA_TOKEN, ENVIRONMENT

st.set_page_config(page_title="SALSA Cotizador", layout="wide")
# Validación de entorno requerida
def validar_entorno():
    faltantes = []
    if not SMTP_USER: faltantes.append("SMTP_USER")
    if not SMTP_PASS: faltantes.append("SMTP_PASS")
    if not RECORDIA_ENDPOINT: faltantes.append("RECORDIA_ENDPOINT")
    if not RECORDIA_TOKEN: faltantes.append("RECORDIA_TOKEN")
    if faltantes:
        st.warning("⚠ Configuración incompleta. Faltan variables:")
        for x in faltantes:
            st.error(f" - {x}")
        if ENVIRONMENT != "development":
            st.stop()
        else:
            st.info("Entorno 'development' detectado: se permite continuar para pruebas del cotizador.")

# Validar variables solo en producción para no bloquear pruebas del cotizador
if ENVIRONMENT == "production":
    validar_entorno()

if "usuario" not in st.session_state:
    st.session_state.usuario = None
if "rol" not in st.session_state:
    st.session_state.rol = None

# Captura IP del usuario solo una vez por sesión
if "ip" not in st.session_state:
    try:
        headers = {"User-Agent": "SALSA Cotizador"}
        st.session_state["ip"] = requests.get(
            "https://api64.ipify.org",
            headers=headers,
            timeout=3
        ).text
    except Exception:
        st.session_state["ip"] = "unknown"

def login_ui():
    st.title("Iniciar Sesión - SALSA Cotizador")

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Entrar"):
        ip = st.session_state.get("ip", "unknown")
        result = autenticar(usuario, password)
        if result == "bloqueado":
            st.error("Cuenta bloqueada por intentos fallidos. Contacta al administrador.")
            registrar_evento(usuario, "bloqueado", ip)
        elif result is None:
            st.error("Credenciales incorrectas.")
            registrar_evento(usuario, "fail", ip)
        elif isinstance(result, dict) and "requiere_reset" in result:
            st.session_state.reset_user = usuario
            st.sidebar.page_link("pages/0_Reset_Password.py", label="🔐 Cambiar contraseña")
            st.rerun()
        elif isinstance(result, dict) and "mfa" in result:
            st.session_state.mfa_user = result
            st.sidebar.page_link("pages/0_MFA.py", label="🔐 Verificación MFA")
            st.rerun()
        else:
            st.session_state.usuario = result["nombre"]
            st.session_state.rol = result["rol"]
            st.success("Acceso exitoso")
            st.rerun()

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
        st.sidebar.page_link("pages/10_Admin_Auditoria_Usuarios.py", label="🛡 Auditoría Usuarios")
        st.sidebar.page_link("pages/11_Security_Center.py", label="🛡 Security Center")

        st.sidebar.markdown("---")
        st.sidebar.markdown("## 📄 Documentos")
        st.sidebar.page_link("pages/8_Exportar_Propuesta_PDF.py", label="🖨 Generar PDF")
        st.sidebar.page_link("pages/9_Auditoria_Catalogo.py", label="🧾 Auditoría Catálogo")

    st.title("SALSA Cotizador - Panel Principal")
    st.write("Sistema listo. Usa el menú lateral para navegar.")
