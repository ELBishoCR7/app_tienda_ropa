from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from datetime import datetime


def generar_pdf(nombre_archivo: str, titulo: str, encabezados: list, datos: list):
    """
    Genera un reporte en PDF con los datos proporcionados.

    :param nombre_archivo: Nombre del archivo de salida (ej: 'reporte.pdf')
    :param titulo: Título del reporte
    :param encabezados: Lista con los nombres de las columnas
    :param datos: Lista de tuplas o listas con los registros
    """
    try:
        # Crear PDF
        c = canvas.Canvas(nombre_archivo, pagesize=landscape(letter))
        width, height = landscape(letter)

        # Encabezado
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - 40, titulo)

        # Fecha de generación
        c.setFont("Helvetica", 10)
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        c.drawRightString(width - 40, height - 60, f"Generado: {fecha}")

        # Posiciones iniciales
        x_inicial = 50
        y_inicial = height - 100
        espacio_col = 120
        espacio_fila = 20

        # Dibujar encabezados
        c.setFont("Helvetica-Bold", 12)
        for i, encabezado in enumerate(encabezados):
            c.drawString(x_inicial + i * espacio_col, y_inicial, encabezado)

        # Dibujar datos
        c.setFont("Helvetica", 10)
        y = y_inicial - espacio_fila
        for fila in datos:
            for i, valor in enumerate(fila):
                c.drawString(x_inicial + i * espacio_col, y, str(valor))
            y -= espacio_fila

            # Si la página se llena, crear nueva
            if y < 50:
                c.showPage()
                y = height - 100
                c.setFont("Helvetica-Bold", 12)
                for i, encabezado in enumerate(encabezados):
                    c.drawString(x_inicial + i * espacio_col, y, encabezado)
                c.setFont("Helvetica", 10)
                y -= espacio_fila

        # Guardar PDF
        c.save()
        return nombre_archivo

    except Exception as e:
        print(f"Error al generar PDF: {e}")
        return None
    