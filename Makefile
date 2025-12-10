# =======================================================
# SALSA COTIZADOR - Makefile
# Administrador técnico del proyecto
# =======================================================

# ---------- Variables ----------
PY=python
APP=salsa_cotizador/app.py

# ---------- Setup local ----------
install:
	$(PY) -m pip install -r requirements.txt

run:
	$(PY) -m streamlit run $(APP)

load-env:
	export $(shell cat .env | xargs)

test_db:
	$(PY) scripts/test_db_connection.py

init_db:
	$(PY) scripts/init_db.py

ingest_equipos:
	$(PY) scripts/ingest_equipos.py

ingest_refacciones:
	$(PY) scripts/ingest_refacciones.py

clean_cache:
	find . -name "__pycache__" -type d -exec rm -r {} +

# Detección de cambios y reconstrucción
detect_equipos:
	$(PY) scripts/detectar_cambios.py data/equipos.xlsx EQUIPOS

detect_refacciones:
	$(PY) scripts/detectar_cambios.py data/refacciones.xlsx REFACCIONES

rebuild_equipos:
	$(PY) scripts/reconstruir_catalogo.py EQUIPOS

rebuild_refacciones:
	$(PY) scripts/reconstruir_catalogo.py REFACCIONES

# ---------- Deploy ----------
deploy_streamlit:
	git add .
	git commit -m "actualización SALSA"
	git push

deploy_render:
	git add .
	git commit -m "deploy SALSA"
	git push origin main

# ---------- Utilidades ----------
freeze:
	pip freeze > requirements.txt
