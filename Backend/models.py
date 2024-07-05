import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def configure_database(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer,primary_key =True)
    nombre = db.Column(db.String(255), nullable=False)
    plata = db.Column(db.Integer, nullable=False)
    #fecha_creacion = db. Column(db.DateTime, default=datetime.datetime.now())
  
class Pizza(db.Model):
    __tablename__ = 'pizzas'
    id = db.Column(db.Integer, primary_key =True)
    tipo_pizza = db.Column(db.String(255), nullable=False)
    costo_pizza = db.Column(db.Integer, nullable=False)
    #tiempo_coccion = db.Column(db.Integer, nullable=False)
    #fecha_creacion = db. Column(db.DateTime, default=datetime.datetime.now())

class Orden(db.Model):
    __tablename__ = 'ordenes'
    id = db.Column(db.Integer,primary_key =True)
    cliente_id= db.Column(db.Integer, db.ForeignKey('clientes.id'))
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'))
    costo_total = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.String(50), nullable=False)
    #fecha_entrega = db.Column(db.Datetime ,nullable=False)
    #fecha_creacion = db. Column(db.DateTime, default=datetime.datetime.now())
  
# tabla: pizzas
# - id
# - tipo pizza
# - costo de pizza
# 
# 
# tabla: clientes
#  - id
#  - nombre
# 
# 
# tabla: ordenes
# - id
# - id_cliente (clave foránea)
# - id_pizza
# - estado (si esta entregada o no (y no se si agregar en preparación))
# - costo total