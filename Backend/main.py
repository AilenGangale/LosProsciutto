
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

# @app.route("/cliente/<id_cliente>")
# def data(id_cliente):
#   cliente= Cliente.query.where(Cliente.id = id_cliente).all()
#   print('Cliente:', cliente)
  
#   return id_cliente

@app.route("/clientes/<id_cliente>") 
def data(id_cliente):
  cliente= Cliente.query.get(id_cliente)
  cliente_data ={
    "id" : cliente.id,
    "nombre": cliente.nombre,
    "plata ": cliente.plata
  }
  return cliente_data


#/clientes --> POST 
@app.route('/clientes', methods=['POST'])
def nuevo_cliente():
    try:
        data = request.json
        nuevo_nombre = data.get("nombre")
        nueva_plata = data.get("plata")
        
        nuevo_cliente = Cliente(nombre=nuevo_nombre, plata=nueva_plata)
        
        db.session.add(nuevo_cliente)
        db.session.commit()
        
        return jsonify({
            'cliente': {
                'id': nuevo_cliente.id,
                'nombre': nuevo_cliente.nombre,
                'plata': nuevo_cliente.plata
            }
        })
    
    except:
        return jsonify({
            'message': 'No se pudo crear el cliente'
        }), 500
    


if __name__ == '__main__':
    print("Starting server...")
    with app.app_context():
        db.create_all()  # Crear todas las tablas definidas en los modelos
    app.run(host='0.0.0.0', debug=True, port=8000)
    print("Server started")