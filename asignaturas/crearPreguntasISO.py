from models import db, Tema, Pregunta,Asignatura
from flask import Flask
import pandas as pd
import os
import json

def crear_pregunta_opcion_simple(texto_pregunta,tema,asignatura_id, 
                                 opciones, indice_correcto,dificultad, explicacion=None):
    """
    Crea una pregunta de opción simple con sus respuestas
    
    Args:
        texto_pregunta: Texto de la pregunta
        tema_id: ID del tema al que pertenece
        opciones: Lista de textos de opciones
        indice_correcto: Índice (empezando por 0) de la opción correcta
        explicacion: Explicación opcional de la respuesta correcta
    """
    opciones = str(json.loads(opciones))
    # Crear la pregunta
    pregunta = Pregunta(
        texto=texto_pregunta,
        tema_num=tema,
        asignatura_id=asignatura_id,
        tipo='simple',
        dificultad=dificultad,
        indice_correcto=indice_correcto,
        explicacion=explicacion,
        opciones=opciones
    )
    db.session.add(pregunta)
    db.session.flush()  # Para obtener el ID asignado
    
    db.session.commit()
    return pregunta

def cargar_datos_ejemplo(asignatura_nombre,tema_param):
    asignatura = Asignatura.query.filter(Asignatura.codigo == asignatura_nombre).first()

    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    directorio_raiz = os.path.dirname(directorio_actual)
    ruta_archivo = os.path.join(directorio_raiz ,f'preguntas{asignatura_nombre}',f'preguntas{asignatura_nombre}_T{tema_param}.csv')
    preguntasISO = pd.read_csv(ruta_archivo)
    for indice, fila in preguntasISO.iterrows():
        # Cada fila es una Serie de pandas

        crear_pregunta_opcion_simple(
            texto_pregunta=fila.texto_pregunta,
            tema=tema_param,
            asignatura_id=asignatura.id,
            opciones=fila.opciones,
            indice_correcto=fila.indices_correctos,
            explicacion=fila.explicacion,
            dificultad=fila.dificultad
        )
    # Crear preguntas para el tema de Programación
    #crear_pregunta_opcion_simple(
    #    "En el concepto de sistema operativo como controlador de recursos:",
    #    tema_ISO.id,
    #    ["El SO asigna recursos solo cuando un programa lo solicita explícitamente",
    #     "El SO mantiene un registro continuo de la utilización de recursos y media en conflictos"],
    #    1,  # char es la respuesta correcta (índice 1)
    #    # Explicacion
    #    'El SO como controlador de recursos mantiene registro continuo de la utilización de los mismos, da paso ' \
    #    'a las solicitudes de uso, lleva cuenta de ese uso y media en los conflictos producidos por ' \
    #    'las solicitudes de distintos programas y usuarios, no solo cuando se solicitan explícitamente.'
    #)
    
    print("Datos de ejemplo cargados correctamente.")

# Función para inicializar la base de datos desde un script de Flask
def inicializar_db(app):
    with app.app_context():
        db.create_all()
        cargar_datos_ejemplo()

# Si ejecutamos este archivo directamente, creamos una pequeña aplicación Flask
# para poder inicializar la base de datos
if __name__ == "__main__":
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todotest.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        cargar_datos_ejemplo(asignatura_nombre="ISO",tema_param=1)
        cargar_datos_ejemplo(asignatura_nombre="ISO",tema_param=2)
        cargar_datos_ejemplo(asignatura_nombre="ISO",tema_param=3)
        cargar_datos_ejemplo(asignatura_nombre="ISO",tema_param=4)
        cargar_datos_ejemplo(asignatura_nombre="ISO",tema_param=5)
        cargar_datos_ejemplo(asignatura_nombre="ISO",tema_param=6)
        cargar_datos_ejemplo(asignatura_nombre="AEC",tema_param=1)
        cargar_datos_ejemplo(asignatura_nombre="AEC",tema_param=2)
        cargar_datos_ejemplo(asignatura_nombre="AEC",tema_param=3)
        cargar_datos_ejemplo(asignatura_nombre="AEC",tema_param=4)
with app.app_context():
    todas_preguntas = Pregunta.query.all()
    print(f"Total de preguntas en la base de datos: {len(todas_preguntas)}")
    for p in todas_preguntas:
        print(f"ID: {p.id}, Texto: {p.texto[:30]}..., Tema ID: {p.tema_num}")
