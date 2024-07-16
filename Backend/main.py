
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from models import db, configure_database, Cliente, Pizza, Orden
import datetime

app = Flask(__name__, template_folder="../Frontend", static_folder="Frontend")
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:111276@localhost:5432/papaspizza'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

configure_database(app)
CORS(app) 

@app.route('/')
def home():
    return render_template('index.html')

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
    

@app.route("/clientes/<id_cliente>/ordenes", methods=["GET"])
def ordenes_de_un_cliente(id_cliente):
	try:
		ordenes = db.session.query(Orden, Pizza
		).filter(Orden.pizza_id == Pizza.id
		).filter(Orden.cliente_id == id_cliente).all()
		
		ordenes_data = []
		for (orden, pizza) in ordenes:
			orden_data = {
				'id': orden.id,
				'pizza_id': pizza.verdura,
				'costo_total': orden.costo_total,
                'estado': orden.estado
				#'fecha_cosecha': orden.fecha_cosecha.isoformat()
			}
			ordenes_data.append(orden_data)
		return jsonify(ordenes_data)
	except:
		return jsonify({"mensaje": "No hay ordenes."})
		
@app.route("/clientes/id/nueva_orden/<id_tipo_orden>", method=["POST"])
def nueva_orden(id_cliente, id_pizza):
    try:
        tipo_orden = Pizza.query.get(id_pizza)
        #fecha_cosecha = datetime.datetime.now() + datetime.timedelta(minutes = pizza.tiempo_cosecha) #le suma el tiempo de ese tipo de granja
        #nueva_orden = Orden(conejo_id = id_conejo, tipo_granja_id = id_pizza, fecha_cosecha = fecha_cosecha)
        nueva_orden = Orden(cliente_id = id_cliente, pizza_id = id_pizza)
        db.session.add(nueva_orden)
        db.session.commit()

        orden_data = {
				'id': nueva_orden.id,
				'pizza_id': pizza.tipo_pizza,
				'costo_total': nueva_orden.costo_total,
                'estado': nueva_orden.estado
				#'fecha_cosecha': orden.fecha_cosecha.isoformat()
			}
        return jsonify({'orden': orden_data}),201
    except Exception as error:
        print(error)
        return jsonify({"mensaje": "No se pudo crear la orden."}),500
	
#dado el id de la granja que le llega por parámetro busca la granja en la base de datos, busca el conejo en la base de datos y busca el tipo de granja en la base de datos. Tiene 3 variables, hace los cambios necesarios (si cosecho al conejo le sumo plata y pongo que la granja está cosechada). Luego se añaden esas cosas a la sesión y commiteamos. Devolvemos como retorno del post la nueva plata del conejo para poder actualizar dinámicamente la página
@app.route("/retirar/<id_orden>", method=["POST"])
def retirar_orden(id_orden):
	try:
		orden = Orden.query.get(id_orden)
		cliente = Cliente.query.get(orden.cliente_id)
		pizza = Pizza.query.get(orden.pizza_id)
		
		#FALTAN UN MONTÓN DE CHEQUEOS (la granja tiene que estar lista para cosechar, la granja no tiene que ya estar cosechada)
		cliente.plata -= pizza.costo_pizza
		#orden.cosechada = True
		
		db.session.add(orden)
		db.session.add(cliente)
		db.session.commit()
		
		return jsonify({'nueva_plata': cliente.plata}),201
	except Exception as error:
		print(error)
		return jsonify({"mensaje": "No se pudo retirar la orden."}),500

if __name__ == '__main__':
    print("Starting server...")
    with app.app_context():
        db.create_all()  # Crear todas las tablas definidas en los modelos
    app.run(host='0.0.0.0', debug=True, port=8000)
    print("Server started")


    