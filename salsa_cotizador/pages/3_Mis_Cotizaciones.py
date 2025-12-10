import streamlit as st
import pandas as pd
from modules.cotizaciones import listar_cotizaciones, obtener_detalles, duplicar_cotizacion
from modules.pdf_generator import generar_propuesta

st.title("📁 Mis Cotizaciones")

# Filtros simples
col1, col2 = st.columns(2)
with col1:
    cliente_filter = st.text_input("Filtrar por cliente contiene")
with col2:
    limit = st.number_input("Límite", min_value=10, max_value=500, value=100)

rows = listar_cotizaciones(limit=limit)

df = pd.DataFrame(rows, columns=["id", "folio", "cliente", "total", "fecha"])
if cliente_filter:
    df = df[df["cliente"].str.contains(cliente_filter, case=False, na=False)]

st.dataframe(df, use_container_width=True)

st.subheader("Acciones")
selected_id = st.number_input("ID de cotización", min_value=0, step=1)

colA, colB = st.columns(2)
with colA:
    if st.button("📄 Descargar PDF") and selected_id:
        # reconstruir estructura para PDF
        detalles = obtener_detalles(int(selected_id))
        lineas = []
        for d in detalles:
            lineas.append({
                "parte": d.numero_parte,
                "descripcion": d.descripcion,
                "cantidad": int(d.cantidad or 1),
                "precio_lista": float(d.precio_lista or 0),
                "descuento": float(d.descuento or 0),
                "margen": float(d.margen or 0),
                "precio_venta": float(d.precio_final or 0),
                "total_linea": float(d.total_linea or 0),
            })
        subtotal = sum(ln["total_linea"] for ln in lineas)
        iva = subtotal * 0.16
        total = subtotal + iva
        cot = {"header": {"nombre": "Cliente"}, "lineas": lineas, "totales": {"subtotal": subtotal, "iva": iva, "total": total}}
        pdf = generar_propuesta(cot)
        st.download_button("Descargar PDF", data=pdf, file_name=f"cotizacion_{int(selected_id)}.pdf", mime="application/pdf")

with colB:
    if st.button("🧬 Duplicar cotización") and selected_id:
        nuevo_id = duplicar_cotizacion(int(selected_id))
        if nuevo_id:
            st.success(f"Cotización duplicada con id {nuevo_id}")
        else:
            st.error("No se pudo duplicar dicha cotización.")
