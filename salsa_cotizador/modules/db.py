# modules/db.py

from sqlalchemy import create_engine
from config.settings import NEON

def get_engine():
    url = (
        f"postgresql+psycopg2://{NEON['USER']}:{NEON['PASSWORD']}"
        f"@{NEON['HOST']}/{NEON['DB']}{NEON['OPTIONS']}"
    )
    return create_engine(url, echo=False)
