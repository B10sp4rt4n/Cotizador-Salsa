# modules/logger.py
# Registro centralizado de eventos del sistema SALSA Cotizador

from sqlalchemy import text
from modules.db import get_engine
from modules.notificaciones import enviar_alerta
from modules.recordia_bridge import enviar_recordia

engine = get_engine()

def registrar_evento(usuario, evento, ip=""):
    """
    Guarda un evento en la tabla accesos.
    usuario = string
    evento = string: login_ok, fail, bloqueado, mfa_ok, reset_pwd, etc.
    ip = string opcional
    """
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO accesos (usuario, evento, fecha, ip)
            VALUES (:u, :e, NOW(), :ip)
        """), {"u": usuario, "e": evento, "ip": ip})

    # Enviar a canal externo Recordia para trazabilidad extendida
    try:
        enviar_recordia(usuario, evento, ip)
    except Exception:
        pass

    # Alertas por correo para eventos críticos
    if evento in ["bloqueado", "mfa_fail", "reset_pwd", "fail"]:
        try:
            enviar_alerta(
                f"Alerta de seguridad SALSA: {evento}",
                f"Usuario: {usuario}\nIP: {ip}\nEvento: {evento}"
            )
        except Exception:
            pass
