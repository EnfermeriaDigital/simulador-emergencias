import os
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas

def crear_certificado_premio(nombre_alumno, tipo_premio):
    if not os.path.exists('certificados_emitidos'):
        os.makedirs('certificados_emitidos')
        
    archivo_pdf = f"certificados_emitidos/Premio_{tipo_premio.replace(' ', '_')}_{nombre_alumno.replace(' ', '_')}.pdf"
    c = canvas.Canvas(archivo_pdf, pagesize=landscape(A4))
    ancho, alto = landscape(A4)
    
    # Diseño
    c.setLineWidth(8)
    c.setStrokeColorRGB(0.7, 0.1, 0.1) # Borde Rojo
    c.rect(30, 30, ancho - 60, alto - 60)
    
    c.setFont("Helvetica-Bold", 36)
    c.setFillColorRGB(1, 0.84, 0) # Dorado
    c.drawCentredString(ancho / 2, alto - 120, "RECONOCIMIENTO DE EXCELENCIA")
    
    c.setFont("Helvetica", 18)
    c.setFillColorRGB(0.1, 0.1, 0.1)
    c.drawCentredString(ancho / 2, alto - 180, "Otorgado a:")
    
    c.setFont("Helvetica-Bold", 42)
    c.drawCentredString(ancho / 2, alto - 250, nombre_alumno.upper())
    
    c.setFont("Helvetica", 16)
    c.drawCentredString(ancho / 2, alto - 320, "Por obtener el mayor puntaje y ser galardonado como:")
    
    c.setFont("Helvetica-Bold", 28)
    c.setFillColorRGB(0.7, 0.1, 0.1) # Rojo
    c.drawCentredString(ancho / 2, alto - 360, tipo_premio.upper())
    
    # Firma
    c.setLineWidth(1)
    c.setStrokeColorRGB(0, 0, 0)
    c.line(ancho / 2 - 120, 100, ancho / 2 + 120, 100)
    c.setFont("Helvetica", 14)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(ancho / 2, 80, "Lic. Alejandra Ortiz")
    c.drawCentredString(ancho / 2, 60, "Instructora Especialista")
    
    c.save()
    return archivo_pdf