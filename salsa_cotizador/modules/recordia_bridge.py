import requests
from modules.settings import RECORDIA_ENDPOINT, RECORDIA_TOKEN


def enviar_recordia(usuario, evento, ip, metadata=None):
    payload = {
        "usuario": usuario,
        "evento": evento,
        "ip": ip,
        "metadata": metadata or {},
    }

    headers = {
        "Authorization": f"Bearer {RECORDIA_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        requests.post(RECORDIA_ENDPOINT, json=payload, headers=headers, timeout=3)
    except Exception:
        # Fallback silencioso
        pass
