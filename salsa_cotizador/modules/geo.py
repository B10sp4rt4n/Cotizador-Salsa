import requests


def geolocalizar_ip(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
        data = r.json()
        return {
            "pais": data.get("country"),
            "ciudad": data.get("city"),
            "lat": data.get("lat"),
            "lon": data.get("lon"),
            "isp": data.get("isp"),
        }
    except Exception:
        return None
