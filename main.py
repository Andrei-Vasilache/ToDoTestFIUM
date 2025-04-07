from flask import Flask,render_template,request
from asignaturas.models import db, Tema, Pregunta, Respuesta,Asignatura

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todotest.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/test')
def tests():
    return render_template('rutaTest.html')

@app.route('/test/<codigo_asignatura>')
def showISO(codigo_asignatura):
    with app.app_context():
        asignatura = Asignatura.query.filter_by(codigo=codigo_asignatura).first_or_404()
    print(asignatura)
    return render_template('test.html',asignatura=asignatura)
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