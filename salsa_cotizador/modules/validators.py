# Módulo: Validadores

def validar_item(item):
    return "precio" in item and item.get("precio", 0) >= 0
