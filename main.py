from flask import Flask,render_template,request,session,redirect,url_for
from asignaturas.models import db, Tema, Pregunta, Respuesta,Asignatura
from sqlalchemy import func
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todotest.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
app.secret_key = 'una_clave_secreta_muy_segura'
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/test')
def tests():
    return render_template('rutaTest.html')
@app.route('/elegir-tema/<codigo_asignatura>',methods=["POST","GET"])
def elegir_tema(codigo_asignatura):
    asignatura = Asignatura.query.filter_by(codigo=codigo_asignatura).first()
    temas = Tema.query.filter_by(nombre=codigo_asignatura).all()

    return render_template('seleccionarTemas.html',
                           temas = temas,
                           asignatura=asignatura)
@app.route('/test/<codigo_asignatura>', methods=["GET","POST"])
def show_test(codigo_asignatura):
    asignatura = Asignatura.query.filter_by(codigo=codigo_asignatura).first_or_404()
    asignatura_id = asignatura.id
    session.pop('pregunta_ids', None)
    session.pop('indice_actual', None)
    if request.method == 'POST':
        temas_seleccionados = request.form.getlist('temas_seleccionados')
        npreguntas = request.form['num_preguntas']
        session['current_pregunta_index'] = 0  # Iniciar en el primer índice

    # Selección aleatoria de preguntas
    preguntas = []
    for tema in temas_seleccionados:
        tema_preguntas = Pregunta.query.filter_by(asignatura_id=asignatura_id)\
        .filter_by(tema_num=tema)\
        .order_by(func.random())\
        .limit(npreguntas)\
        .all()    
        preguntas.extend(tema_preguntas)   
    
    # Guardar en sesión los IDs de las preguntas en el orden aleatorio
    pregunta_ids = [p.id for p in preguntas]
    session['pregunta_ids'] = pregunta_ids
    session['current_pregunta_index'] = 0  # Iniciar en el primer índice
    session['max_preguntas']=len(pregunta_ids)
    # Obtener la primera pregunta
    primera_pregunta = Pregunta.query.get(pregunta_ids[0])
    width_percentage = (1 / len(pregunta_ids)) * 100

    return render_template('test.html',
                          asignatura=asignatura,
                          pregunta=primera_pregunta,
                          pregunta_actual=1,
                          total_preguntas=len(pregunta_ids),
                          width_percentage=width_percentage,
                          mostrar_explicacion=False,
                          hay_siguiente=len(pregunta_ids) > 1,)

@app.route('/test/<codigo_asignatura>/verificar/<int:pregunta_id>',methods=["GET","POST"])
def validar_test(codigo_asignatura, pregunta_id):
    # Buscar asignatura por código
    asignatura = Asignatura.query.filter_by(codigo=codigo_asignatura).first_or_404()
    respuesta = Respuesta.query.filter_by(pregunta_id=pregunta_id).first()
    pregunta = Pregunta.query.get(pregunta_id)
    
        
    # Verificar respuesta
    respuesta_elegida = request.form.get('respuesta')
    respuesta_correcta = int(respuesta_elegida) == int(respuesta.indice_correcto)
    #obtener preguntas
    pregunta_ids = session.get('pregunta_ids', [])
    indice_actual = session.get('indice_actual', 0)
    # Progress bar 
    pregunta_actual = indice_actual + 1
    total_preguntas = len(pregunta_ids)
    width_percentage = (pregunta_actual / total_preguntas) * 100

    return render_template('test.html',
                          asignatura=asignatura,
                          pregunta=pregunta,  # Objeto pregunta, no número
                          pregunta_actual=pregunta_actual,  # Número de pregunta actual
                          total_preguntas=total_preguntas,  # Total desde la sesión
                          mostrar_explicacion=True,  # Ahora queremos mostrar la explicación
                          respuesta_elegida=respuesta_elegida,
                          respuesta_correcta=respuesta_correcta,
                          hay_siguiente=len(pregunta_ids) > 0,
                          width_percentage=width_percentage)  # Añadido para la barra de progreso

@app.route('/test/<codigo_asignatura>/siguiente/<int:pregunta_id>',methods=["GET","POST"])
def siguiente_pregunta(codigo_asignatura,pregunta_id):
    # Buscar asignatura por código
    asignatura = Asignatura.query.filter_by(codigo=codigo_asignatura).first_or_404()
    
    # Obtener lista de IDs de preguntas de la sesión
    pregunta_ids = session.get('pregunta_ids', [])
    indice_actual = session.get('indice_actual', 0)
    
    # Incrementar el índice
    indice_actual += 1
    print(indice_actual)
    print(len(pregunta_ids))
    if indice_actual+1 > len(pregunta_ids):
        return render_template('home.html')
    # Actualizar el índice en la sesión
    session['indice_actual'] = indice_actual
    
    # Obtener la siguiente pregunta
    siguiente_id = pregunta_ids[indice_actual]
    siguiente_pregunta = Pregunta.query.get(siguiente_id)
    
    # Calcular el número de pregunta y el porcentaje de la barra
    pregunta_actual = indice_actual + 1
    total_preguntas = len(pregunta_ids)
    width_percentage = (pregunta_actual / total_preguntas) * 100
    
    # Verificar si hay más preguntas después de esta
    hay_siguiente = pregunta_actual < total_preguntas
    
    return render_template('test.html',
                          asignatura=asignatura,
                          pregunta=siguiente_pregunta,
                          pregunta_actual=pregunta_actual,
                          total_preguntas=total_preguntas,
                          mostrar_explicacion=False,
                          hay_siguiente=hay_siguiente,
                          width_percentage=width_percentage)
@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/procesar_formulario', methods=['POST'])
def procesar_formulario():
    if request.method == 'POST':
        nombre = request.form['user_name']
        email = request.form['user_mail']
        contenido_mensaje = request.form['user_message']
        
        # Crear nueva entrada en la base de datos
        print(email)
        print(contenido_mensaje)
        # Guardar en la base de datos

        return render_template('contacto.html', mensaje=f"¡Gracias {nombre}! Tu mensaje ha sido guardado en nuestra base de datos.")

@app.route('/procesar_formulario-temas/<codigo_asignatura>', methods=['POST'])
def procesar_formulario_temas(codigo_asignatura):
    if request.method == 'POST':
        temas_seleccionados = request.form.getlist('temas_seleccionados')
        print(temas_seleccionados)
    return redirect(url_for('elegir_tema',codigo_asignatura=codigo_asignatura))
@app.route('/features')
def features():
    return render_template('features.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)