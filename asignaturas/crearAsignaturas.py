from models import db, Tema, Pregunta,Asignatura
from flask import Flask
app = Flask(__name__)
def crear_asignatura(nombre,codigo):
    asignatura = Asignatura(
        nombre=nombre,
        codigo=codigo
    )
    db.session.add(asignatura)
    db.session.commit()
    return asignatura

def crear_tema(asignatura_id, nombre, tema=None):
    """Crea un nuevo tema en la base de datos"""
    tema = Tema(
        nombre=nombre, 
        tema=tema,
        asignatura_id=asignatura_id
    )
    db.session.add(tema)
    db.session.commit()
    return tema
def cargar_asignaturas():
    #ISO
    asignatura_ISO = crear_asignatura("Introduccion a los Sistemas Operativos","ISO")
    tema1_ISO = crear_tema(asignatura_id=asignatura_ISO.id,nombre="ISO",tema="1")
    tema2_ISO = crear_tema(asignatura_id=asignatura_ISO.id,nombre="ISO",tema="2")
    tema3_ISO = crear_tema(asignatura_id=asignatura_ISO.id,nombre="ISO",tema="3")
    tema4_ISO = crear_tema(asignatura_id=asignatura_ISO.id,nombre="ISO",tema="4")
    tema5_ISO = crear_tema(asignatura_id=asignatura_ISO.id,nombre="ISO",tema="5")
    tema6_ISO = crear_tema(asignatura_id=asignatura_ISO.id,nombre="ISO",tema="6")

    #AEC
    asignatura_AEC = crear_asignatura("Ampliacion de Estructura de Computadores","AEC")
    tema1_AEC = crear_tema(asignatura_id=asignatura_AEC.id,nombre="AEC",tema="1")
    tema2_AEC = crear_tema(asignatura_id=asignatura_AEC.id,nombre="AEC",tema="2")
    tema3_AEC = crear_tema(asignatura_id=asignatura_AEC.id,nombre="AEC",tema="3")
    tema4_AEC = crear_tema(asignatura_id=asignatura_AEC.id,nombre="AEC",tema="4")

if __name__ == "__main__":
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todotest.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        cargar_asignaturas()