from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Asignatura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    
    # Relación con temas
    temas = db.relationship('Tema', backref='asignatura', lazy=True)
    # Relación con las preguntas
    preguntas = db.relationship('Pregunta', backref='asignatura', lazy=True)

class Tema(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tema = db.Column(db.Integer, nullable=True)
    asignatura_id = db.Column(db.Integer, db.ForeignKey('asignatura.id'), nullable=False)
# Modelo para las preguntas
class Pregunta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    tema_num = db.Column(db.Integer,nullable=False)
    asignatura_id = db.Column(db.Integer, db.ForeignKey('asignatura.id'),nullable=False)
    explicacion = db.Column(db.Text, nullable=True)
    opciones = db.Column(db.Text, nullable=False)
    dificultad = db.Column(db.Text,nullable=False)
    indice_correcto = db.Column(db.Integer,nullable=False)
    # Tipo de pregunta: multiple, simple, verdadero_falso, texto_libre
    tipo = db.Column(db.String(20), default='simple')
    
    # Fecha de creación
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    
    def __repr__(self):
        return f'<Pregunta {self.id}: {self.texto[:30]}...>'
