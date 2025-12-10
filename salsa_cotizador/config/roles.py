# config/roles.py

ROLES = {
    "vendedor": [
        "cotizador",
        "historial_mio",
        "exportar_pdf"
    ],
    "admin": [
        "cotizador",
        "historial_mio",
        "historial_global",
        "admin_catalogo",
        "admin_usuarios",
        "exportar_pdf",
        "ingest"
    ]
}
