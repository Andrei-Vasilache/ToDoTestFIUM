from flask import Flask,render_template,request,session,redirect,url_for
from asignaturas.models import db, Tema, Pregunta,Asignatura
from sqlalchemy import func
import random
import ast

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
    variables_sesion = ['pregunta_ids', 
                        'respuestas_acertadas',
                        'respuestas_usuario', 
                        'max_preguntas',
                        'indice_actual']
    for var in variables_sesion:
        session.pop(var, None)

    if request.method == 'POST':
        temas_seleccionados = request.form.getlist('temas_seleccionados')
        npreguntas = request.form['num_preguntas']
        randomizar_preguntas = request.form.get('randomizar_preguntas')
        session['indice_actual'] = 0  
        session['respuestas_acertadas'] = 0
        session['respuestas_usuario'] = []
        # Selección aleatoria de preguntas
        preguntas = []
        for tema in temas_seleccionados:
            tema_preguntas = Pregunta.query.filter_by(asignatura_id=asignatura_id)\
            .filter_by(tema_num=tema)\
            .order_by(func.random())\
            .limit(npreguntas)\
            .all()    
            preguntas.extend(tema_preguntas)
        if randomizar_preguntas:
            random.shuffle(preguntas)   
        # Guardamos diccionario preguntas    
        # Guardar en sesión los IDs de las preguntas en el orden aleatorio
        pregunta_ids = [p.id for p in preguntas]
        session['pregunta_ids'] = pregunta_ids
        session['max_preguntas']=len(pregunta_ids)
        # Obtener la primera pregunta
        primera_pregunta = Pregunta.query.get(pregunta_ids[0])
        width_percentage = (1 / len(pregunta_ids)) * 100
        # Crear las opciones de respuesta
        opciones = ast.literal_eval(primera_pregunta.opciones)
        return render_template('test.html',
                            asignatura=asignatura,
                            pregunta=primera_pregunta,
                            pregunta_actual=1,
                            total_preguntas=len(pregunta_ids),
                            width_percentage=width_percentage,
                            mostrar_explicacion=False,
                            opciones=opciones,
                            hay_siguiente=len(pregunta_ids) > 1,)
    return redirect(url_for('elegir_tema', codigo_asignatura=codigo_asignatura))

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
    opciones = ast.literal_eval(pregunta.opciones)
    
    return render_template('test.html',
                          asignatura=asignatura,
                          pregunta=pregunta,
                          opciones=opciones,
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
    
    # Verificar respuesta
    respuesta_elegida = request.form.get('respuesta', '0')
    respuesta_correcta = pregunta.indice_correcto
    if 'respuestas_usuario' not in session:
        session['respuestas_usuario'] = []
    session['respuestas_usuario'].append(int(respuesta_elegida))
    session.modified = True
    print(session['respuestas_usuario'])
    # Datos para la vista
    pregunta_ids = session.get('pregunta_ids', [])
    indice_actual = session.get('indice_actual', 0)
    pregunta_actual = indice_actual + 1
    total_preguntas = len(pregunta_ids)
    width_percentage = (pregunta_actual / total_preguntas) * 100
    hay_siguiente = pregunta_actual < total_preguntas
    opciones = ast.literal_eval(pregunta.opciones)
    #Guardar resultados
    if respuesta_correcta == int(respuesta_elegida):
        session['respuestas_acertadas'] = session.get('respuestas_acertadas',0)+1
    return render_template('test.html',
                          asignatura=asignatura,
                          pregunta=pregunta,
                          opciones=opciones,
                          pregunta_actual=pregunta_actual,
                          total_preguntas=total_preguntas,
                          respuesta_elegida=int(respuesta_elegida),
                          respuesta_correcta=respuesta_correcta,
                          mostrar_explicacion=True,
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

    print("Añadida")
    # Si ya terminamos, ir a la página de resultados
    if indice_actual >= len(pregunta_ids):
        return redirect(url_for('home'))  # O a tu página de resultados
    
    # Redirigir a la siguiente pregunta
    siguiente_id = pregunta_ids[indice_actual]
    return redirect(url_for('show_pregunta', 
                           codigo_asignatura=codigo_asignatura, 
                           pregunta_id=siguiente_id))
    
@app.route('/resultados/')
def show_resultados():
    pagina = request.args.get('pagina', 1, type=int)

    acertadas = session.get('respuestas_acertadas',0)
    lista_respondidas = session.get('respuestas_usuario',[])
    ids_preguntas = session.get('pregunta_ids',[])
    preguntas = []
    items_por_pagina = 5
    total_paginas = int(len(ids_preguntas)/items_por_pagina)+1
    if pagina > total_paginas:
        pagina=total_paginas
    if pagina < 1:
        pagina = 1
    for id_pregunta in ids_preguntas:
        temp_pregunta = Pregunta.query.filter_by(id=id_pregunta).first()
        preguntas.append(temp_pregunta)
    inicio = (pagina - 1) * items_por_pagina
    fin = pagina * items_por_pagina
    n_preguntas = int(len(ids_preguntas))
    if acertadas != 0:
        porcentaje = round((acertadas/n_preguntas)*100)
    else:
        porcentaje = 0
    return render_template('resultados.html',
                           acertadas=acertadas,
                           preguntas=preguntas[inicio:fin],
                           pagina=pagina,
                           n_preguntas=n_preguntas,
                           porcentaje = porcentaje,
                           total_paginas=total_paginas,
                           items_por_pagina=items_por_pagina,
                           lista_respondidas=lista_respondidas[inicio:fin])    
@app.route('/ver-pregunta/<int:id>',methods=["POST","GET"])    
def ver_pregunta(id):
    pregunta = Pregunta.query.filter_by(id=id).first()
    lista_respondidas = session.get('respuestas_usuario',[])
    lista_ids = session.get('pregunta_ids',[])
    index = lista_ids.index(pregunta.id)
    n_pregunta = index + 1 # Numero pregunta
    print(index)
    print(lista_respondidas)
    respuesta = lista_respondidas[index]
    opciones = ast.literal_eval(pregunta.opciones)
    return render_template('verPregunta.html',pregunta=pregunta,
                           respuesta=respuesta,n_pregunta=n_pregunta,
                           opciones=opciones
                           )
@app.route('/siguiente-pregunta/<int:id>')
def siguiente_resultado(id):
    ids_preguntas = session.get('pregunta_ids',[])
    print(ids_preguntas)
    index = ids_preguntas.index(id)
    if index+1 < len(ids_preguntas):
        sig_id = ids_preguntas[index+1]
    else:
        return redirect(url_for('ver_pregunta',id=id,index=index))
    return redirect(url_for('ver_pregunta',id=sig_id,index=index+1))

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
    return redirect(url_for('elegir_tema',codigo_asignatura=codigo_asignatura))
@app.route('/features')
def features():
    return render_template('features.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)