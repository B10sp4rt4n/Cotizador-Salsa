# modules/cotizador.py

def calcular_linea(precio_lista, margen, descuento, cantidad):
    """
    precio_lista: float
    margen: porcentaje sobre precio de lista
    descuento: porcentaje sobre precio ya marginado
    cantidad: unidades
    """
    precio_venta = precio_lista * (1 + margen / 100)
    precio_desc = precio_venta * (1 - descuento / 100)
    total = precio_desc * cantidad

    return {
        "precio_venta": round(precio_venta, 2),
        "precio_final": round(precio_desc, 2),
        "total_linea": round(total, 2),
    }
