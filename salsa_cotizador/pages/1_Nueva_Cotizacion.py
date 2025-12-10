import streamlit as st
import pandas as pd

st.title("🧾 Nueva Cotización — Encabezado")

# Inicializa estructura de cotización en sesión
if "cotizacion" not in st.session_state or not isinstance(st.session_state["cotizacion"], dict):
    st.session_state["cotizacion"] = {"header": {}, "lineas": [], "totales": {}}

with st.form("form_header"):
    col1, col2 = st.columns(2)
    with col1:
        tipo = st.selectbox("Tipo de cliente", ["Empresa", "Persona"])
        nombre = st.text_input("Razón social / Nombre")
        rfc = st.text_input("RFC (opcional)")
    with col2:
        contacto_nombre = st.text_input("Contacto — Nombre")
        contacto_email = st.text_input("Contacto — Email")
        contacto_tel = st.text_input("Contacto — Teléfono")
    direccion = st.text_area("Dirección")
    notas = st.text_area("Notas de la cotización")

    submitted = st.form_submit_button("Guardar encabezado")

if submitted:
    st.session_state["cotizacion"]["header"] = {
        "tipo": tipo,
        "nombre": nombre,
        "rfc": rfc,
        "contacto_nombre": contacto_nombre,
        "contacto_email": contacto_email,
        "contacto_tel": contacto_tel,
        "direccion": direccion,
        "notas": notas,
    }
    st.success("Encabezado guardado en la sesión.")

# Vista rápida del encabezado actual
if st.session_state["cotizacion"].get("header"):
    st.subheader("Resumen del cliente")
    st.json(st.session_state["cotizacion"]["header"])