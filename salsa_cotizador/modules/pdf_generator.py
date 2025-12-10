from io import BytesIO
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

def generar_propuesta(cotizacion: dict) -> bytes:
    """Genera un PDF simple con encabezado, tabla de líneas y totales."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER)
    styles = getSampleStyleSheet()
    elems = []

    header = cotizacion.get("header", {})
    lineas = cotizacion.get("lineas", [])
    totales = cotizacion.get("totales", {})

    elems.append(Paragraph("Cotización SALSA", styles["Title"]))
    elems.append(Spacer(1, 12))
    cliente_txt = f"Cliente: {header.get('nombre','')} ({header.get('tipo','')})"
    contacto_txt = f"Contacto: {header.get('contacto_nombre','')} — {header.get('contacto_email','')} — {header.get('contacto_tel','')}"
    direccion_txt = f"Dirección: {header.get('direccion','')}"
    elems.extend([
        Paragraph(cliente_txt, styles["Normal"]),
        Paragraph(contacto_txt, styles["Normal"]),
        Paragraph(direccion_txt, styles["Normal"]),
        Spacer(1, 12),
    ])

    # Tabla de líneas
    data = [["Parte", "Descripción", "Cant.", "P. Lista", "Desc %", "Marg %", "Precio", "Total"]]
    for ln in lineas:
        data.append([
            ln.get("parte",""),
            ln.get("descripcion",""),
            int(ln.get("cantidad",1) or 1),
            f"{float(ln.get('precio_lista',0) or 0):,.2f}",
            f"{float(ln.get('descuento',0) or 0):.2f}",
            f"{float(ln.get('margen',0) or 0):.2f}",
            f"{float(ln.get('precio_venta',0) or 0):,.2f}",
            f"{float(ln.get('total_linea',0) or 0):,.2f}",
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ALIGN', (2,1), (-1,-1), 'RIGHT'),
    ]))
    elems.extend([table, Spacer(1, 12)])

    # Totales
    elems.append(Paragraph(f"Subtotal: {float(totales.get('subtotal',0)):,.2f} MXN", styles['Heading4']))
    elems.append(Paragraph(f"IVA (16%): {float(totales.get('iva',0)):,.2f} MXN", styles['Heading4']))
    elems.append(Paragraph(f"Total: {float(totales.get('total',0)):,.2f} MXN", styles['Heading4']))

    # Notas
    if header.get('notas'):
        elems.extend([Spacer(1, 12), Paragraph("Notas:", styles['Heading4']), Paragraph(header['notas'], styles['Normal'])])

    doc.build(elems)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
