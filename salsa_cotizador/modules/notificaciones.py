import smtplib
from email.mime.text import MIMEText
from modules.settings import SMTP_USER, SMTP_PASS, SMTP_SERVER, SMTP_PORT

ADMIN_EMAIL = "admin@synappssys.com"  # cámbialo por el real


def enviar_alerta(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = ADMIN_EMAIL

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, ADMIN_EMAIL, msg.as_string())
    except Exception:
        # Fallback silencioso para no romper flujo de aplicación
        pass
