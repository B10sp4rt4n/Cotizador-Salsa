# Módulo: Utilidades

def moneda(valor: float, codigo: str = "MXN") -> str:
    return f"{codigo} ${valor:,.2f}"
