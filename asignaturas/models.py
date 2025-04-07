from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Asignatura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    
    # Relación con temas
    temas = db.relationship('Tema', backref='asignatura', lazy=True)

class Tema(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    asignatura_id = db.Column(db.Integer, db.ForeignKey('asignatura.id'), nullable=False)
    
    # Relación con las preguntas
    preguntas = db.relationship('Pregunta', backref='tema', lazy=True)
# Modelo para las preguntas
class Pregunta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    tema_id = db.Column(db.Integer, db.ForeignKey('tema.id'), nullable=False)
    explicacion = db.Column(db.Text, nullable=True)
    
    # Tipo de pregunta: multiple, simple, verdadero_falso, texto_libre
    tipo = db.Column(db.String(20), default='simple')
    
    # Fecha de creación
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con las respuestas
    respuestas = db.relationship('Respuesta', backref='pregunta', lazy=True)
    
    def __repr__(self):
        return f'<Pregunta {self.id}: {self.texto[:30]}...>'

# Modelo para las respuestas
class Respuesta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    pregunta_id = db.Column(db.Integer, db.ForeignKey('pregunta.id'), nullable=False)
    es_correcta = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Respuesta {self.id} para Pregunta {self.pregunta_id}>'