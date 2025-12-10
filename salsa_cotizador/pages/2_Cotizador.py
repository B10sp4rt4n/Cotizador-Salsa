import streamlit as st
from modules.catalogo import buscar_productos
from modules.cotizador import calcular_linea
from modules.cotizaciones import crear_cotizacion, insertar_detalle

st.title("Cotizador SALSA")

if "lineas" not in st.session_state:
    st.session_state.lineas = []

# --- BUSCADOR ---
st.subheader("Buscar producto")
texto = st.text_input("Buscar por modelo, número de parte o descripción")

resultados = []
if texto:
    resultados = buscar_productos(texto)

for r in resultados:
    if st.button(f"Agregar {r['modelo']} ({r['numero_parte']})"):
        st.session_state.lineas.append({
            "numero_parte": r["numero_parte"],
            "descripcion": r["descripcion"],
            "modelo": r["modelo"],
            "precio_lista": float(r["precio_lista"]),
            "margen": 20.0,
            "descuento": 0.0,
            "cantidad": 1,
            "override_flag": False
        })
        st.rerun()

# --- TABLA DE LÍNEAS ---
st.subheader("Líneas de cotización")

total_global = 0

for i, linea in enumerate(st.session_state.lineas):
    st.write(f"### Línea {i + 1}")

    col1, col2, col3, col4 = st.columns(4)
    linea["margen"] = col1.number_input("Margen %", value=linea["margen"], key=f"margen{i}")
    linea["descuento"] = col2.number_input("Descuento %", value=linea["descuento"], key=f"descuento{i}")
    linea["cantidad"] = col3.number_input("Cantidad", value=linea["cantidad"], key=f"cantidad{i}", min_value=1)

    # cálculo
    calc = calcular_linea(linea["precio_lista"], linea["margen"], linea["descuento"], linea["cantidad"])
    linea["precio_final"] = calc["precio_final"]
    linea["total_linea"] = calc["total_linea"]

    col4.metric("Total línea", f"${linea['total_linea']:,}")

    total_global += linea["total_linea"]

st.write("---")
st.metric("TOTAL GLOBAL", f"${total_global:,.2f}")

# --- GUARDAR COTIZACIÓN ---
st.write("### Guardar cotización")

cliente = st.text_input("Cliente")
notas = st.text_area("Notas adicionales")

if st.button("Guardar cotización"):
    if not cliente:
        st.error("Debe ingresar el nombre del cliente.")
    else:
        cot_id = crear_cotizacion("usuario", cliente, notas, total_global)

        for linea in st.session_state.lineas:
            insertar_detalle(cot_id, {
                "cot": cot_id,
                "np": linea["numero_parte"],
                "des": linea["descripcion"],
                "mod": linea["modelo"],
                "pl": linea["precio_lista"],
                "mar": linea["margen"],
                "desc": linea["descuento"],
                "pf": linea["precio_final"],
                "cant": linea["cantidad"],
                "tot": linea["total_linea"],
                "ov": linea["override_flag"]
            })

        st.success(f"Cotización guardada con ID {cot_id}")
        st.session_state.lineas = []
        st.rerun()
