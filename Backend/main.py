
from flask import Flask, render_template, request, jsonify
from models import db, configure_database, Cliente, Pizza, Orden

app = Flask(__name__, template_folder="Frontend/templates", static_folder="Frontend")
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:111276@localhost:5432/papaspizza'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

configure_database(app)

@app.route('/')
def hello_world():
    return 'Hello world'

#Devolver todos los clientes
@app.route('/clientes/', methods=['GET'])
def all_clientes():
    try:
        # Recupera los registros de una tabla
        clientes = Cliente.query.all()
        
        clientes_data = []
        #Guarda la informacion de clientes en la lista como diccionario de cada cliente
        for cliente in clientes:
            cliente_data = {
                "id_cliente": cliente.id,
                "nombre": cliente.nombre,
                "plata": cliente.plata
            }
            clientes_data.append(cliente_data)
        #Lo pone en formato de json (usa base de datos)
        return jsonify(clientes_data)
    except:
        return jsonify({"error": "No se pudieron recuperar los datos"})
    
def data(id_conejo):
  conejo= Conejo.query.get(id_conejo)
  conejo_data ={
    "id" : conejo.id,
    "nombre": comejo.nombre,
    "plata ": conejo.plata
  }
  return conejo_data
  

      

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8000)
