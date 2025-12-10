# Cotizador de Salsa

Esqueleto inicial del proyecto de cotizador. Estructura por páginas y módulos.

## Ejecutar

```bash
python3 salsa_cotizador/app.py
```

## Estructura

- `app.py`: punto de entrada.
- `pages/`: vistas por funcionalidad.
- `modules/`: lógica de negocio.
- `config/`: configuración y roles.
- `static/`: plantillas y recursos.
- `data/`: archivos de datos.

## Operación y Mantenimiento (Administradores)

- Desinstalar "Makefile Tools": no es necesaria para este flujo.
- Mantener el `Makefile` minimalista y ordenado.
- Ejecutar siempre desde terminal:
	- `make install`
	- `make init_db`
	- `make run`
- Documentar comandos clave y buenas prácticas en este README.