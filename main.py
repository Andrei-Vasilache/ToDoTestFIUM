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
        randomizar_preguntas = request.form.get('randomizar_preguntas')
        session['current_pregunta_index'] = 0  # Iniciar en el primer índice

    # Selección aleatoria de preguntas
    preguntas = []
    for tema in temas_seleccionados:
        tema_preguntas = Pregunta.query.filter_by(asignatura_id=asignatura_id)\
        .filter_by(tema_num=tema)\
        .order_by(func.random())\
        .limit(npreguntas)\
        .all()    
        print(tema)
        preguntas.extend(tema_preguntas)
    if randomizar_preguntas:
        random.shuffle(preguntas)
           
    print(f"Tema preguntas: {tema_preguntas}")
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

@app.route('/test/<codigo_asignatura>/pregunta/<int:pregunta_id>', methods=["GET"])
def show_pregunta(codigo_asignatura, pregunta_id):
    """Muestra una pregunta específica del test."""
    # Recuperar datos necesarios
    asignatura = Asignatura.query.filter_by(codigo=codigo_asignatura).first_or_404()
    pregunta = Pregunta.query.get_or_404(pregunta_id)
    
    # Obtener datos de la sesión
    pregunta_ids = session.get('pregunta_ids', [])
    indice_actual = pregunta_ids.index(pregunta_id) if pregunta_id in pregunta_ids else 0
    session['indice_actual'] = indice_actual
    
    # Datos para la vista
    pregunta_actual = indice_actual + 1
    total_preguntas = len(pregunta_ids)
    width_percentage = (pregunta_actual / total_preguntas) * 100
    hay_siguiente = pregunta_actual < total_preguntas
    
    return render_template('test.html',
                          asignatura=asignatura,
                          pregunta=pregunta,
                          pregunta_actual=pregunta_actual,
                          total_preguntas=total_preguntas,
                          mostrar_explicacion=False,
                          hay_siguiente=hay_siguiente,
                          width_percentage=width_percentage,
                          pregunta_ids=pregunta_ids,
                          indice_actual=indice_actual)


@app.route('/test/<codigo_asignatura>/explicacion/<int:pregunta_id>', methods=["POST"])
def show_explicacion(codigo_asignatura, pregunta_id):
    """Procesa la respuesta y muestra la explicación."""
    # Recuperar datos necesarios
    asignatura = Asignatura.query.filter_by(codigo=codigo_asignatura).first_or_404()
    pregunta = Pregunta.query.get_or_404(pregunta_id)
    respuesta = Respuesta.query.filter_by(pregunta_id=pregunta_id).first()
    
    # Verificar respuesta
    respuesta_elegida = request.form.get('respuesta', '0')
    respuesta_correcta = int(respuesta_elegida) == int(respuesta.indice_correcto)
    
    # Datos para la vista
    pregunta_ids = session.get('pregunta_ids', [])
    indice_actual = session.get('indice_actual', 0)
    pregunta_actual = indice_actual + 1
    total_preguntas = len(pregunta_ids)
    width_percentage = (pregunta_actual / total_preguntas) * 100
    hay_siguiente = pregunta_actual < total_preguntas
    
    return render_template('test.html',
                          asignatura=asignatura,
                          pregunta=pregunta,
                          pregunta_actual=pregunta_actual,
                          total_preguntas=total_preguntas,
                          mostrar_explicacion=True,
                          respuesta_elegida=respuesta_elegida,
                          respuesta_correcta=respuesta_correcta,
                          hay_siguiente=hay_siguiente,
                          width_percentage=width_percentage,
                          pregunta_ids=pregunta_ids,
                          indice_actual=indice_actual)


@app.route('/test/<codigo_asignatura>/siguiente/<int:pregunta_actual>', methods=["GET"])
def siguiente_pregunta(codigo_asignatura, pregunta_actual):
    """Redirige a la siguiente pregunta o a la página de resultados."""
    # Obtener datos de la sesión y avanzar
    pregunta_ids = session.get('pregunta_ids', [])
    indice_actual = session.get('indice_actual', 0)
    indice_actual += 1
    session['indice_actual'] = indice_actual
    
    # Si ya terminamos, ir a la página de resultados
    if indice_actual >= len(pregunta_ids):
        return redirect(url_for('home'))  # O a tu página de resultados
    
    # Redirigir a la siguiente pregunta
    siguiente_id = pregunta_ids[indice_actual]
    return redirect(url_for('show_pregunta', 
                           codigo_asignatura=codigo_asignatura, 
                           pregunta_id=siguiente_id))
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