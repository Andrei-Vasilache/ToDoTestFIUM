from models import db, Tema, Pregunta, Respuesta,Asignatura
from flask import Flask
import pandas as pd
import os
import json
def crear_pregunta_opcion_multiple(texto_pregunta, tema_id,tema,opciones, indices_correctos, explicacion=None):
    """
    Crea una pregunta de opción múltiple con sus respuestas
    
    Args:
        texto_pregunta: Texto de la pregunta
        tema_id: ID del tema al que pertenece
        opciones: Lista de textos de opciones
        indices_correctos: Lista de índices (empezando por 0) de las opciones correctas
        explicacion: Explicación opcional de la respuesta correcta
    """
    # Crear la pregunta
    pregunta = Pregunta(
        texto=texto_pregunta,
        tema_id=tema_id,
        tema=tema,
        tipo='multiple',
        explicacion=explicacion
    )
    db.session.add(pregunta)
    db.session.flush()  # Para obtener el ID asignado
    
    # Crear las opciones de respuesta
    for i, opcion_texto in enumerate(opciones):
        es_correcta = i in indices_correctos
        respuesta = Respuesta(
            texto=opcion_texto,
            pregunta_id=pregunta.id,
            es_correcta=es_correcta
        )
        db.session.add(respuesta)
    
    db.session.commit()
    return pregunta
def crear_pregunta_opcion_simple(texto_pregunta, tema_id,tema,asignatura_id, opciones, indice_correcto, explicacion=None):
    """
    Crea una pregunta de opción simple con sus respuestas
    
    Args:
        texto_pregunta: Texto de la pregunta
        tema_id: ID del tema al que pertenece
        opciones: Lista de textos de opciones
        indice_correcto: Índice (empezando por 0) de la opción correcta
        explicacion: Explicación opcional de la respuesta correcta
    """
    opciones = json.loads(opciones)
    # Crear la pregunta
    pregunta = Pregunta(
        texto=texto_pregunta,
        tema_id=tema_id,
        tema_num=tema,
        asignatura_id=asignatura_id,
        tipo='simple',
        explicacion=explicacion,
        opcion1=opciones[0],
        opcion2=opciones[1]
    )
    db.session.add(pregunta)
    db.session.flush()  # Para obtener el ID asignado
    for i, opcion_texto in enumerate(opciones):
        es_correcta = (i == indice_correcto)
        print(f"Opción {i}: '{opcion_texto}' - ¿Es correcta? {es_correcta}")  # Depuración
        respuesta = Respuesta(
            texto=opcion_texto,
            pregunta_id=pregunta.id,
            es_correcta=es_correcta,
            indice_correcto=indice_correcto
        )
        db.session.add(respuesta)
    
    db.session.commit()
    return pregunta

def crear_pregunta_verdadero_falso(texto_pregunta, tema_id, es_verdadero, explicacion=None):
    """
    Crea una pregunta de verdadero/falso
    
    Args:
        texto_pregunta: Texto de la pregunta
        tema_id: ID del tema al que pertenece
        es_verdadero: True si la respuesta correcta es "Verdadero", False si es "Falso"
        explicacion: Explicación opcional de la respuesta correcta
    """
    # Crear la pregunta
    pregunta = Pregunta(
        texto=texto_pregunta,
        tema_id=tema_id,
        tipo='verdadero_falso',
        explicacion=explicacion
    )
    db.session.add(pregunta)
    db.session.flush()  # Para obtener el ID asignado
    
    # Crear las opciones de respuesta
    respuesta_verdadero = Respuesta(
        texto="Verdadero",
        pregunta_id=pregunta.id,
        es_correcta=es_verdadero
    )
    db.session.add(respuesta_verdadero)
    
    respuesta_falso = Respuesta(
        texto="Falso",
        pregunta_id=pregunta.id,
        es_correcta=not es_verdadero
    )
    db.session.add(respuesta_falso)
    
    db.session.commit()
    return pregunta

def crear_pregunta_texto_libre(texto_pregunta, tema_id, respuesta_correcta, explicacion=None):
    """
    Crea una pregunta de texto libre
    
    Args:
        texto_pregunta: Texto de la pregunta
        tema_id: ID del tema al que pertenece
        respuesta_correcta: Texto de la respuesta correcta
        explicacion: Explicación opcional de la respuesta correcta
    """
    # Crear la pregunta
    pregunta = Pregunta(
        texto=texto_pregunta,
        tema_id=tema_id,

        tipo='texto_libre',
        explicacion=explicacion
    )
    db.session.add(pregunta)
    db.session.flush()  # Para obtener el ID asignado
    
    # Crear la respuesta correcta
    respuesta = Respuesta(
        texto=respuesta_correcta,
        pregunta_id=pregunta.id,
        es_correcta=True
    )
    db.session.add(respuesta)
    
    db.session.commit()
    return pregunta

def cargar_datos_ejemplo(asignatura_nombre,tema_param):
    asignatura = Asignatura.query.filter(Asignatura.codigo == asignatura_nombre).first()
    tema = Tema.query.filter(
    Tema.nombre.like(f"%{asignatura_nombre}%"), 
    Tema.descripcion.like(f"%Tema {tema_param}%")
    ).first()
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    directorio_raiz = os.path.dirname(directorio_actual)
    ruta_archivo = os.path.join(directorio_raiz ,'preguntasISO','preguntasISO_T1.csv')
    preguntasT1ISO = pd.read_csv(ruta_archivo)
    for indice, fila in preguntasT1ISO.iterrows():
        # Cada fila es una Serie de pandas

        crear_pregunta_opcion_simple(
            texto_pregunta=fila.texto_pregunta,
            tema_id=tema.id,
            tema=tema_param,
            asignatura_id=asignatura.id,
            opciones=fila.opciones,
            indice_correcto=fila.indices_correctos,
            explicacion=fila.explicacion,
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
        cargar_datos_ejemplo(asignatura_nombre="ISO",tema_param=3)
        cargar_datos_ejemplo(asignatura_nombre="ISO",tema_param=1)

        cargar_datos_ejemplo(asignatura_nombre="ISO",tema_param=2)

with app.app_context():
    todas_preguntas = Pregunta.query.all()
    print(f"Total de preguntas en la base de datos: {len(todas_preguntas)}")
    for p in todas_preguntas:
        print(f"ID: {p.id}, Texto: {p.texto[:30]}..., Tema ID: {p.tema_id}")
