# Módulo: Historial de Modificaciones

MODS = []

def registrar(cambio):
    MODS.append(cambio)

def listar():
    return MODS
