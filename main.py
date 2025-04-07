from flask import Flask,render_template
from asignaturas.models import db, Tema, Pregunta, Respuesta,Asignatura

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todotest.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/test')
def showTest():
    return render_template('rutaTest.html')

@app.route('/test/<codigo_asignatura>')
def showISO(codigo_asignatura):
    with app.app_context():
        asignatura = Asignatura.query.filter_by(codigo=codigo_asignatura).first_or_404()
    print(asignatura)
    return render_template('test.html',asignatura=asignatura)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)