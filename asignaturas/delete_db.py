from flask import Flask
from models import db, Asignatura, Tema, Pregunta, Respuesta

def vaciar_base_datos(app):
    """Elimina todos los datos de las tablas pero mantiene la estructura"""
    with app.app_context():
        # Eliminar en orden inverso para respetar las restricciones de clave foránea
        print("Eliminando respuestas...")
        Respuesta.query.delete()
        
        print("Eliminando preguntas...")
        Pregunta.query.delete()
        
        print("Eliminando temas...")
        Tema.query.delete()
        
        print("Eliminando asignaturas...")
        Asignatura.query.delete()
        
        # Guardar los cambios
        db.session.commit()
        print("Base de datos vaciada correctamente.")

# Si ejecutas este archivo directamente, se conectará y vaciará la base de datos
if __name__ == "__main__":
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todotest.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    # Pedir confirmación antes de vaciar
    confirmacion = input("¿Estás seguro de que quieres vaciar la base de datos? Esta acción no se puede deshacer. (s/n): ")
    
    if confirmacion.lower() == 's':
        vaciar_base_datos(app)
    else:
        print("Operación cancelada.")