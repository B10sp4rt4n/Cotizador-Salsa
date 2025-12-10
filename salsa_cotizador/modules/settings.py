import os
from dotenv import load_dotenv

# Cargar archivo .env si existe
load_dotenv()

# SMTP CONFIG
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

# RECORDIA CONFIG
RECORDIA_ENDPOINT = os.getenv("RECORDIA_ENDPOINT")
RECORDIA_TOKEN = os.getenv("RECORDIA_TOKEN")

# OTROS TOKENS FUTUROS
API_KEY = os.getenv("API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
