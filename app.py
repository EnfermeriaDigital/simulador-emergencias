from flask import Flask, render_template, jsonify, send_file
from flask_socketio import SocketIO, emit
import os
import base64
import fitz  # PyMuPDF: Necesario para convertir el PDF a Imagen
from generador_certificados import crear_certificado_premio

# Creamos la carpeta automáticamente para que no dé error en Render al ganar
os.makedirs('certificados_emitidos', exist_ok=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'emergencias123'

# CORRECCIÓN CLAVE: Permitir conexiones desde cualquier origen (CORS)
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*", logger=True, engineio_logger=True)

puntajes_alumnos = {}
modulo_actual = 'nervioso'
votos_actuales = {"A": 0, "B": 0, "C": 0}
respuesta_correcta = "B"

@app.route('/')
def presentacion():
    return render_template('presentacion.html')

@app.route('/alumno')
def alumno():
    return render_template('alumno.html')

@app.route('/descargar_certificado/<nombre_archivo>')
def descargar_certificado(nombre_archivo):
    ruta_pdf = f"certificados_emitidos/Certificado_{nombre_archivo}.pdf"
    if os.path.exists(ruta_pdf):
        return send_file(ruta_pdf, as_attachment=True)
    return "Certificado no encontrado o aún generándose, intenta de nuevo en unos segundos.", 404

@socketio.on('enviar_respuesta')
def manejar_respuesta(data):
    global votos_actuales
    opcion = data['opcion']
    nombre = data['nombre']
    
    if nombre not in puntajes_alumnos:
        puntajes_alumnos[nombre] = {"nervioso": 0, "cardio": 0, "metabolico": 0, "total": 0}
        
    if opcion in votos_actuales:
        votos_actuales[opcion] += 1
        
    if opcion == respuesta_correcta:
        puntajes_alumnos[nombre][modulo_actual] += 100
        puntajes_alumnos[nombre]["total"] += 100
        
    emit('actualizar_grafico', votos_actuales, broadcast=True)

@socketio.on('cambiar_modulo')
def cambiar_modulo(data):
    global modulo_actual, respuesta_correcta, votos_actuales
    modulo_actual = data['nuevo_modulo']
    respuesta_correcta = data['nueva_respuesta']
    votos_actuales = {"A": 0, "B": 0, "C": 0}
    
    # Esto limpia las barras en el proyector
    emit('actualizar_grafico', votos_actuales, broadcast=True)
    # Esto envía la señal al alumno.html para desbloquear los botones
    emit('nueva_pregunta', broadcast=True)

@app.route('/calcular_premios', methods=['POST'])
def calcular_premios():
    if not puntajes_alumnos:
        return jsonify({"error": "Nadie jugó"})

    p_oro = max(puntajes_alumnos.items(), key=lambda x: x[1]['total'])[0]
    neuro = max(puntajes_alumnos.items(), key=lambda x: x[1]['nervioso'])[0]
    corazon = max(puntajes_alumnos.items(), key=lambda x: x[1]['cardio'])[0]
    ojo = max(puntajes_alumnos.items(), key=lambda x: x[1]['metabolico'])[0]

    premios_asignados = {}
    for alumno in puntajes_alumnos.keys():
        if alumno == p_oro: titulo = 'Paramédico de Oro'
        elif alumno == neuro: titulo = 'Neurólogo Relámpago'
        elif alumno == corazon: titulo = 'Corazón de Hierro'
        elif alumno == ojo: titulo = 'Ojo Clínico'
        else: titulo = 'Especialista en Emergencias'
            
        # 1. Creamos el PDF llamando a tu función
        ruta_pdf = crear_certificado_premio(alumno, titulo)
        
        # 2. Convertimos el PDF a una Imagen (PNG) en Base64 para el celular
        imagen_base64 = ""
        # Forzamos la ruta por si la función no devuelve la ruta exacta
        ruta_esperada = f"certificados_emitidos/Certificado_{alumno.replace(' ', '_')}.pdf"
        
        if os.path.exists(ruta_esperada):
            try:
                doc = fitz.open(ruta_esperada)
                pagina = doc.load_page(0)
                pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2))  # Calidad alta (escala 2x)
                imagen_base64 = base64.b64encode(pix.tobytes("png")).decode("utf-8")
                doc.close()
            except Exception as e:
                print("Error convirtiendo PDF a imagen:", e)

        # 3. Guardamos los datos para enviarlos por Socket
        premios_asignados[alumno] = {
            "titulo": titulo,
            "imagen": imagen_base64
        }

    # Enviamos los datos (con la imagen incluida) a los celulares
    socketio.emit('juego_terminado', premios_asignados, broadcast=True)
    
    return jsonify({"oro": p_oro, "neuro": neuro, "corazon": corazon, "ojo": ojo})

if __name__ == '__main__':
    # Render asigna el puerto automáticamente
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)