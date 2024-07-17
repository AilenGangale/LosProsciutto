from flask_sqlalchemy import SQLAlchemy
import Datetime
db = SQLAlchemy()

def configure_database(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    plata = db.Column(db.Integer, nullable=False)
    
class Orden(db.Model):
    __tablename__ = 'ordenes'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'))
    costo_total = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.String(50), nullable=False)
    #Agrego los campos de fechas
    fecha_creacion = db.Column(db.DateTime, default= datetime.datetime.now)
    fecha_entrega = db.Column(db.DateTime, nullable=False)
    

class Pizza(db.Model):
    __tablename__ = 'pizzas'
    id = db.Column(db.Integer, primary_key=True)
    #Cambio el tipo de pizza por el sabor
    sabor = db.Column(db.String(255), nullable=False)
    costo_pizza = db.Column(db.Integer, nullable=False)
    #Agrego tiempo de coccion comentado
    tiempo_coccion = db.Column(db.Integer, nullable=False)
    

