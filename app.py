from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'emergencias123'

# Conexión pura y rápida
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
    
    emit('actualizar_grafico', votos_actuales, broadcast=True)
    emit('nueva_pregunta', broadcast=True)

@socketio.on('emitir_certificados')
def emitir_certificados():
    if not puntajes_alumnos:
        emit('error_premios', {"error": "Aún no hay jugadores registrados."})
        return

    # Calcular ganadores
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
            
        premios_asignados[alumno] = {"titulo": titulo}

    # Disparar la fiesta en los celulares y actualizar proyector
    emit('juego_terminado', premios_asignados, broadcast=True)
    emit('mostrar_ganadores', {"oro": p_oro, "neuro": neuro, "corazon": corazon, "ojo": ojo}, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)