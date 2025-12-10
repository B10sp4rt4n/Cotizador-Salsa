import streamlit as st
import pandas as pd
from scripts.detectar_cambios import detectar_cambios
import altair as alt

st.title("🧾 Auditoría del Catálogo")

tipo = st.selectbox("Seleccione tipo de lista:", ["EQUIPOS", "REFACCIONES"])

subido = st.file_uploader("Sube la nueva lista XLSX", type=["xlsx"])

if subido:
    df_nuevo = pd.read_excel(subido)
    df_nuevo.columns = [c.strip() for c in df_nuevo.columns]

    cambios = detectar_cambios(df_nuevo, tipo)

    st.header("📌 Resumen de Cambios")
    st.write(f"- Nuevos productos: **{len(cambios['nuevos'])}**")
    st.write(f"- Eliminados: **{len(cambios['eliminados'])}**")
    st.write(f"- Cambios de precio: **{len(cambios['cambios_precio'])}**")

    # ---- Gráfica ----
    resumen = pd.DataFrame({
        "categoria": ["Nuevos", "Eliminados", "Precio cambiado"],
        "cantidad": [
            len(cambios["nuevos"]),
            len(cambios["eliminados"]),
            len(cambios["cambios_precio"]) 
        ]
    })

    chart = alt.Chart(resumen).mark_bar().encode(
        x="categoria:N",
        y="cantidad:Q",
        color="categoria:N"
    )
    st.altair_chart(chart, use_container_width=True)

    # ---- Alertas ----
    from scripts.detectar_cambios import generar_alertas
    alertas = generar_alertas(cambios)
    for a in alertas:
        st.warning(a)

    # ---- Detalles ----
    st.subheader("Detalles de nuevos productos")
    st.dataframe(cambios["nuevos"], use_container_width=True)

    st.subheader("Detalles de eliminados")
    st.dataframe(cambios["eliminados"], use_container_width=True)

    st.subheader("Cambios de precio")
    st.dataframe(cambios["cambios_precio"], use_container_width=True)
