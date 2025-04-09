from flask import Flask,render_template,request,session
from asignaturas.models import db, Tema, Pregunta, Respuesta,Asignatura

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
@app.route('/elegir-tema/<codigo_asignatura>')
def elegir_tema(codigo_asignatura):
    asignatura = Asignatura.query.filter_by(codigo=codigo_asignatura).first()
    temas = Tema.query.filter_by(nombre=codigo_asignatura).all()
    return render_template('seleccionarTemas.html',
                           temas = temas,
                           asignatura=asignatura)
@app.route('/test/<codigo_asignatura>',methods=["GET","POST"])
def showTest(codigo_asignatura):
    # No es necesario el 'with app.app_context()' dentro de una ruta
    asignatura = Asignatura.query.filter_by(codigo=codigo_asignatura).first_or_404()
    preguntas = Pregunta.query.filter_by(asignatura_id=asignatura.id).all()
    
    if not preguntas:
        return "No hay preguntas disponibles para esta asignatura", 404
        
    pregunta = preguntas[0]
    print(asignatura)
    
    # Guardar en sesión
    pregunta_ids = [p.id for p in preguntas]
    session['pregunta_ids'] = pregunta_ids
    session['total_preguntas'] = len(pregunta_ids)

    # Verificar que se ha guardado correctamente
    print(f"DEBUG - session['pregunta_ids']: {session.get('pregunta_ids', 'No existe')}")
    print(f"DEBUG - session['total_preguntas']: {session.get('total_preguntas', 'No existe')}")
    return render_template('test.html',
                          asignatura=asignatura,
                          pregunta=pregunta,
                          preguntaActual=1,
                          total_preguntas=len(preguntas),
                          mostrar_explicacion=False,
                          hay_siguiente=len(preguntas) > 1)


@app.route('/test/<codigo_asignatura>/verificar/<int:pregunta_id>',methods=["GET","POST"])
def validar_test(codigo_asignatura, pregunta_id):
    # Buscar asignatura por código (consistente con showTest)
    asignatura = Asignatura.query.filter_by(codigo=codigo_asignatura).first_or_404()
    respuesta = Respuesta.query.filter_by(pregunta_id=pregunta_id).first()
    pregunta = Pregunta.query.get(pregunta_id)
    
    # Obtener siguientes preguntas
    preguntas = Pregunta.query.filter_by(asignatura_id=asignatura.id).filter(Pregunta.id > pregunta_id).all()
    
    # Verificar respuesta
    respuesta_elegida = request.form.get('respuesta')
    respuesta_correcta = int(respuesta_elegida) == int(respuesta.indice_correcto)
    
    if respuesta_correcta:
        print("Has elegido bien")
    else:
        print("Has elegido mal")   
    
    # Calcular posición actual
    pregunta_ids = session.get('pregunta_ids', [])
    print(f"pregunta_ids: {pregunta_ids}")  # Debug
    print(f"pregunta_id: {pregunta_id}, tipo: {type(pregunta_id)}")  # Debug

    pregunta_actual = pregunta_ids.index(pregunta_id) + 1
    total_preguntas = len(pregunta_ids)
    
    # Calcular el porcentaje para la barra de progreso
    width_percentage = (pregunta_actual / total_preguntas) * 100
    
    return render_template('test.html',
                          asignatura=asignatura,
                          pregunta=pregunta,  # Objeto pregunta, no número
                          pregunta_actual=pregunta_actual,  # Número de pregunta actual
                          total_preguntas=total_preguntas,  # Total desde la sesión
                          mostrar_explicacion=True,  # Ahora queremos mostrar la explicación
                          respuesta_elegida=respuesta_elegida,
                          respuesta_correcta=respuesta_correcta,
                          hay_siguiente=len(preguntas) > 0,
                          width_percentage=width_percentage)  # Añadido para la barra de progreso

@app.route('/test/<codigo_asignatura>/siguiente/<int:pregunta_id>',methods=["GET","POST"])
def siguiente_pregunta(codigo_asignatura, pregunta_id):
    # Buscar asignatura por código
    asignatura = Asignatura.query.filter_by(codigo=codigo_asignatura).first_or_404()
    
    # Obtener lista de IDs de preguntas de la sesión
    pregunta_ids = session.get('pregunta_ids', [])
    print(f"pregunta_ids: {pregunta_ids}")  # Debug
    print(f"pregunta_id actual: {pregunta_id}")  # Debug
    
    # Encontrar la posición actual y calcular la siguiente
    indice_actual = pregunta_ids.index(pregunta_id)
    indice_siguiente = indice_actual + 1
    
    # Obtener la siguiente pregunta
    siguiente_id = pregunta_ids[indice_siguiente]
    siguiente_pregunta = Pregunta.query.get(siguiente_id)
    
    # Calcular el número de pregunta y el porcentaje de la barra
    pregunta_actual = indice_siguiente + 1  # +1 para numeración humana
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

@app.route('/features')
def features():
    return render_template('features.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)