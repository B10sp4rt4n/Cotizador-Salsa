import streamlit as st
import pandas as pd

st.title("🧮 Cotizador SALSA - MVP")

# Utilidad: detección robusta de columna de precio
def detectar_columna_precio(df: pd.DataFrame) -> str | None:
    candidatos = [
        "PRECIO LISTA",
        "PRECIO",
        "LIST PRICE",
        "PRECIO_LISTA",
        "PRICE",
        "PRECIO UNITARIO",
        "PRECIO UNIT",
        "PVP",
    ]
    cols_map = {str(c).strip().upper(): c for c in df.columns}
    for nombre in candidatos:
        if nombre in cols_map:
            return cols_map[nombre]
    # heurística adicional: buscar columnas numéricas con valores positivos típicos
    for c in df.columns:
        serie = df[c]
        if pd.api.types.is_numeric_dtype(serie):
            positivos = serie.dropna()
            if len(positivos) > 0 and (positivos > 0).mean() > 0.7:
                return c
    return None

# ===========================================
# 1. Subir lista de precios
# ===========================================
st.subheader("📤 Cargar Lista de Precios (Excel)")

archivo = st.file_uploader("Sube la lista de precios (.xlsx)", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    st.success("Lista de precios cargada.")

    # Limpieza mínima
    df.columns = [str(c).strip() for c in df.columns]
    # Normalización de nombres esperados (case-insensitive)
    rename_map = {}
    cols_up = {c.upper(): c for c in df.columns}
    def pick(*options):
        for opt in options:
            if opt in cols_up:
                return cols_up[opt]
        return None
    c_clase = pick("CLASE")
    c_subclase = pick("SUBCLASE")
    c_np = pick("NO. DE PARTE", "NUMERO DE PARTE", "NÚMERO DE PARTE", "NUMERO_PARTE", "PART NUMBER", "PARTNUMBER")
    c_modelo = pick("MODELO")
    c_desc = pick("DESCRIPCION", "DESCRIPCIÓN", "DESCRIPCION", "DESCRIPTION")
    c_precio = pick("PRECIO LISTA", "PRECIO", "LIST PRICE", "PRECIO_LISTA")

    for key, val in {
        "CLASE": c_clase,
        "SUBCLASE": c_subclase,
        "NO. DE PARTE": c_np,
        "MODELO": c_modelo,
        "DESCRIPCIÓN": c_desc,
        "PRECIO LISTA": c_precio,
    }.items():
        if val and val != key:
            rename_map[val] = key

    if rename_map:
        df = df.rename(columns=rename_map)

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

    # ==============================
    # FILTRO 1: CLASE
    # ==============================
    clases = sorted(df_lista["CLASE"].dropna().unique().tolist())
    clase_sel = st.selectbox("Clase", ["Todas"] + clases)

    df_filtrado = df_lista.copy()

    if clase_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["CLASE"] == clase_sel]

    # ==============================
    # FILTRO 2: SUBCLASE
    # ==============================
    subclases = sorted(df_filtrado["SUBCLASE"].dropna().unique().tolist())
    subclase_sel = st.selectbox("Subclase", ["Todas"] + subclases)

    if subclase_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["SUBCLASE"] == subclase_sel]

    # ==============================
    # FILTRO 3: NÚMERO DE PARTE
    # ==============================
    partes = sorted(df_filtrado["NO. DE PARTE"].astype(str).unique().tolist())
    parte_sel = st.selectbox("Número de parte", partes)

    df_final = df_filtrado[df_filtrado["NO. DE PARTE"] == parte_sel]

    st.write("Productos filtrados:")
    st.dataframe(df_filtrado, use_container_width=True)

    # Selección del item para uso posterior
    if df_final.empty:
        st.warning("No se encontró el número de parte seleccionado en el filtro actual.")
        st.stop()
    item = df_final.iloc[0]

    # =====================================
    # 3. Seleccionar un producto
    # =====================================
    st.subheader("➕ Agregar línea a la cotización")

    st.info(f"Seleccionado: {item['DESCRIPCIÓN']}")

    # =====================================
    # 4. Editar descuento y margen
    # =====================================
    # Detectar columna de precio de forma robusta
    col_precio = detectar_columna_precio(df_lista)
    if not col_precio:
        st.error("No se pudo detectar la columna de precio en el Excel. Renombra o mapea encabezados (ej. 'PRECIO LISTA').")
        st.stop()
    valor_precio = item.get(col_precio)
    precio_lista = float(valor_precio) if pd.notna(valor_precio) else 0.0

    descuento_pct = st.number_input("Descuento (%)", value=0.0, min_value=0.0, max_value=100.0)
    margen_pct = st.number_input("Margen (%) sobre precio de venta", value=20.0, min_value=0.0, max_value=200.0)

    costo = precio_lista * (1 - descuento_pct / 100)
    precio_venta = costo / (1 - margen_pct / 100)  # margen sobre precio final

    st.write(f"💲 Precio lista: {precio_lista:,.2f}")
    st.write(f"💲 Costo con descuento: {costo:,.2f}")
    st.write(f"💲 Precio de venta: {precio_venta:,.2f}")

    # =====================================
    # 5. Agregar línea a cotización (estructura: header/lineas/totales)
    # =====================================
    if st.button("Agregar a cotización"):

        if "cotizacion" not in st.session_state or not isinstance(st.session_state["cotizacion"], dict):
            st.session_state["cotizacion"] = {"header": {}, "lineas": [], "totales": {}}

        st.session_state["cotizacion"]["lineas"].append({
            "clase": item.get("CLASE", ""),
            "subclase": item.get("SUBCLASE", ""),
            "parte": parte_sel,
            "descripcion": item.get("DESCRIPCIÓN", ""),
            "cantidad": 1,
            "precio_lista": precio_lista,
            "descuento": descuento_pct,
            "costo": costo,
            "margen": margen_pct,
            "precio_venta": precio_venta,
            "total_linea": precio_venta * 1,
        })

        st.success("Línea agregada.")

# =====================================
# 6. Mostrar y editar cotización
# =====================================
if "cotizacion" in st.session_state and isinstance(st.session_state["cotizacion"], dict) and len(st.session_state["cotizacion"].get("lineas", [])) > 0:

    st.subheader("📄 Cotización Actual (Multi-línea)")

    df_cot = pd.DataFrame(st.session_state["cotizacion"]["lineas"]) if st.session_state["cotizacion"]["lineas"] else pd.DataFrame()

    # Editor interactivo (puedes editar cantidad y descuento)
    edited_df = st.data_editor(
        df_cot,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "cantidad": st.column_config.NumberColumn("Cantidad", min_value=1),
            "descuento": st.column_config.NumberColumn("Descuento (%)"),
            "margen": st.column_config.NumberColumn("Margen (%)"),
        }
    )

    # Recalcular totales después de edición
    for i, row in edited_df.iterrows():
        precio_lista = row.get("precio_lista", 0) or 0
        descuento = row.get("descuento", 0) or 0
        margen = row.get("margen", 0) or 0
        cantidad = int(row.get("cantidad", 1) or 1)

        costo = precio_lista * (1 - descuento / 100)
        precio_venta = costo / (1 - margen / 100) if (1 - margen / 100) != 0 else 0
        total_linea = precio_venta * cantidad

        edited_df.at[i, "costo"] = costo
        edited_df.at[i, "precio_venta"] = precio_venta
        edited_df.at[i, "total_linea"] = total_linea

    # Guardar datos actualizados en sesión
    st.session_state["cotizacion"]["lineas"] = edited_df.to_dict(orient="records")

    # Mostrar subtotal y total final
    subtotal = float(edited_df["total_linea"].sum()) if not edited_df.empty else 0.0
    iva = subtotal * 0.16
    total_final = subtotal + iva

    st.session_state["cotizacion"]["totales"] = {"subtotal": subtotal, "iva": iva, "total": total_final}

    st.info(f"Subtotal: {subtotal:,.2f} MXN")
    st.info(f"IVA (16%): {iva:,.2f} MXN")
    st.success(f"TOTAL: {total_final:,.2f} MXN")

    # =====================================
    # Botón para borrar todas las líneas
    # =====================================
    if st.button("🗑 Borrar cotización completa"):
        st.session_state["cotizacion"]["lineas"] = []
        st.session_state["cotizacion"]["totales"] = {"subtotal": 0.0, "iva": 0.0, "total": 0.0}
        st.warning("Cotización eliminada.")
        st.rerun()

