import streamlit as st
import pandas as pd

st.title("🧮 Cotizador SALSA - MVP")

# ===========================================
# 1. Subir lista de precios
# ===========================================
st.subheader("📤 Cargar Lista de Precios (Excel)")

archivo = st.file_uploader("Sube la lista de precios (.xlsx)", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    st.success("Lista de precios cargada.")

    # Limpieza mínima
    df.columns = [c.strip() for c in df.columns]

    # Mostrar un preview
    st.write("Vista previa:")
    st.dataframe(df.head(20), use_container_width=True)

    # Guardar en sesión
    st.session_state["lista"] = df

# ====================================================
# 2. Lógica de Cotización (solo si existe lista cargada)
# ====================================================
if "lista" in st.session_state:

    st.subheader("🛒 Construir Cotización")

    df_lista = st.session_state["lista"]

    # Filtros
    clase = st.selectbox("Clase", ["Todas"] + sorted(df_lista["CLASE"].dropna().unique().tolist()))
    subclase = st.selectbox("Subclase", ["Todas"] + sorted(df_lista["SUBCLASE"].dropna().unique().tolist()))

    filtrado = df_lista.copy()

    if clase != "Todas":
        filtrado = filtrado[filtrado["CLASE"] == clase]

    if subclase != "Todas":
        filtrado = filtrado[filtrado["SUBCLASE"] == subclase]

    st.write("Productos filtrados:")
    st.dataframe(filtrado, use_container_width=True)


    # =====================================
    # 3. Seleccionar un producto
    # =====================================
    st.subheader("➕ Agregar línea a la cotización")

    # Partes
    partes = filtrado["NO. DE PARTE"].astype(str).unique().tolist()
    parte_sel = st.selectbox("Número de parte", partes)

    item = filtrado[filtrado["NO. DE PARTE"] == parte_sel].iloc[0]

    st.info(f"Seleccionado: {item['DESCRIPCIÓN']}")

    # =====================================
    # 4. Editar descuento y margen
    # =====================================
    precio_lista = float(item["PRECIO LISTA"])

    descuento_pct = st.number_input("Descuento (%)", value=0.0, min_value=0.0, max_value=100.0)
    margen_pct = st.number_input("Margen (%) sobre precio de venta", value=20.0, min_value=0.0, max_value=200.0)

    costo = precio_lista * (1 - descuento_pct / 100)
    precio_venta = costo / (1 - margen_pct / 100)  # margen sobre precio final

    st.write(f"💲 Precio lista: {precio_lista:,.2f}")
    st.write(f"💲 Costo con descuento: {costo:,.2f}")
    st.write(f"💲 Precio de venta: {precio_venta:,.2f}")

    # =====================================
    # 5. Agregar línea a cotización
    # =====================================
    if st.button("Agregar a cotización"):

        if "cotizacion" not in st.session_state:
            st.session_state["cotizacion"] = []

        st.session_state["cotizacion"].append({
            "parte": parte_sel,
            "descripcion": item["DESCRIPCIÓN"],
            "precio_lista": precio_lista,
            "descuento": descuento_pct,
            "costo": costo,
            "margen": margen_pct,
            "precio_venta": precio_venta,
        })

        st.success("Línea agregada.")

# ===========================================
# 6. Mostrar cotización completa
# ===========================================
if "cotizacion" in st.session_state:

    st.subheader("📄 Cotización Actual")

    df_cot = pd.DataFrame(st.session_state["cotizacion"])

    st.dataframe(df_cot, use_container_width=True)

    total = df_cot["precio_venta"].sum()

    st.success(f"💰 Total cotización: {total:,.2f} MXN")

