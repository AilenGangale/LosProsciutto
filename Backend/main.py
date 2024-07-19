
from flask import Flask, render_template, request, jsonify
#pip install psycopg2
#pip install flask-cors
from flask_cors import CORS
from models import db, configure_database, Cliente, Pizza, Orden
import datetime

app = Flask(__name__, template_folder="../Frontend/templates", static_folder="../Frontend/static")
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:111276@localhost:5432/papaspizza'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

configure_database(app)
CORS(app) 

@app.route('/')
def home():
    return render_template('home.html')

#Devolver todos los clientes
@app.route('/clientes/', methods=['GET'])
def all_clientes():
    try:
        # Recupera los registros de una tabla
        clientes = Cliente.query.all()
        return render_template('clientes_existentes.html', clientes=clientes)
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
    cliente_data = {
    "id" : cliente.id,
    "nombre": cliente.nombre,
    "plata ": cliente.plata
    }
    return jsonify(cliente_data)


#/clientes --> POST 
@app.route('/cliente_nuevo', methods=['POST'])
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

@app.route('/nuevo_cliente')
def nuevo_cliente_page():
    return render_template('clientes_nuevos.html')


@app.route('/ordenes')
def orden_cliente():
    return render_template('ordenes.html')

#Devolver todos los clientes
@app.route('/clientes/<id_cliente>/ordenes', methods=['GET'])
def all_ordenes(id_cliente):
    try:
        # Recupera los registros de una tabla
        ordenes = Orden.query.filter_by(cliente_id=id_cliente).all()
        return render_template('ordenes.html', ordenes=ordenes)
    except:
        return jsonify({"error": "No se pudieron recuperar los datos"})



# @app.route("/clientes/<id_cliente>/ordenes", methods=['GET'])
# def ordenes_de_un_cliente(id_cliente):
# 	try:
# 		ordenes = db.session.query(Orden, Pizza
# 		).filter(Orden.pizza_id == Pizza.id
# 		).filter(Orden.cliente_id == id_cliente).all()
		
# 		ordenes_data = []
# 		for (orden, pizza) in ordenes:
# 			orden_data = {
# 				'id': orden.id,
#                 #NO es necesario proque hay un fil
#                 'cliente_id':id_cliente,
# 				'pizza_id': pizza.id,
# 				'costo_total': orden.costo_total,
#                 'estado': orden.estado
# 				#'fecha_cosecha': orden.fecha_cosecha.isoformat()
# 			}
# 			ordenes_data.append(orden_data)
# 		return jsonify(ordenes_data)
# 	except:
# 		return jsonify({"mensaje": "No hay ordenes."})
     
# @app.route("/clientes/<id_cliente>/ordenes", methods=['GET'])
# def ordenes_de_un_cliente(id_cliente):
#     try:
#         ordenes = db.session.query(Orden, Pizza
#         ).filter(Orden.pizza_id == Pizza.id
#         ).filter(Orden.cliente_id == id_cliente).all()
        
#         print("Órdenes recuperadas:", ordenes)  # Imprime para verificar
        
#         ordenes_data = []
#         for (orden, pizza) in ordenes:
#             orden_data = {
#                 'id': orden.id,
#                 'pizza_id': pizza.id,
#                 'costo_total': orden.costo_total,
#                 'estado': orden.estado
#             }
#             ordenes_data.append(orden_data)
            
        
#         print("Órdenes en formato de datos:",ordenes_data)  # Imprime para verificar

#         # Renderizar la plantilla con los datos de las órdenes
#         return render_template('ordenes.html', ordenes= jsonify(ordenes_data))
#     except Exception as e:
#         print(f"Error: {e}")  # Imprime el error para depuración
#         return render_template('ordenes.html', mensaje="No hay órdenes.")

# @app.route("/clientes/<int:id_cliente>/ordenes", methods=['GET'])
# def ordenes_de_un_cliente(id_cliente):
#     try:
#         # Consulta las órdenes para el cliente dado
#         ordenes = db.session.query(Orden).filter_by(cliente_id=id_cliente).all()
        
#         # Prepara los datos para la respuesta
#         ordenes_data = []
#         for orden in ordenes:
#             orden_data = {
#                 'id': orden.id,
#                 'costo': orden.costo_total,
#                 'estado': orden.estado,
#                 'id_cliente': orden.cliente_id
#             }
#             ordenes_data.append(orden_data)

#         # Retorna los datos en formato JSON
#         return jsonify({'ordenes': ordenes_data})
#     except Exception as e:
#         print(f"Error: {e}")  # Imprime el error para depuración
#         return jsonify({'mensaje': "No se pudieron recuperar las órdenes."}), 500

    
		
@app.route("/clientes/id/nueva_orden/<id_tipo_orden>", methods=['POST'])
def nueva_orden(id_cliente, id_pizza):
    try:
        pizza = Pizza.query.get(id_pizza)
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
	
#dado el id de la orden que le llega por parámetro busca la orden en la base de datos, busca el cliente en la base de datos y busca la pizza en la base de datos. Tiene 3 variables, hace los cambios necesarios (si recibió la orden le resto plata y pongo que la pizza está entregada). Luego se añaden esas cosas a la sesión y commiteamos. Devolvemos como retorno del post la nueva plata del cliente para poder actualizar dinámicamente la página
@app.route("/retirar/<id_orden>", methods=['POST'])
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

#Permite modificar una orden. Primero la busca por su id, luego obtiene los datos de la solicitud. Actualiza los campos si se proporcionaron nuevos datos, guarda los cambios y devuelve la información actualizada de la orden.
@app.route('/ordenes/<id_orden>', methods=['PUT'])
def actualizar_orden(id_orden):
    try:
        orden = Orden.query.get(id_orden)
        if not orden:
            return jsonify({"error": "Orden no encontrada"}), 404

        data = request.json
        nuevo_estado = data.get("estado")
        nuevo_costo_total = data.get("costo_total")
        nueva_pizza_id = data.get("pizza_id")

        if nuevo_estado:
            orden.estado = nuevo_estado
        if nuevo_costo_total is not None:
            orden.costo_total = nuevo_costo_total
        if nueva_pizza_id:
            nueva_pizza = Pizza.query.get(nueva_pizza_id)
            if nueva_pizza:
                orden.pizza_id = nueva_pizza_id
            else:
                return jsonify({"error": "Pizza no encontrada"}), 404

        db.session.commit()

        orden_data = {
            "id": orden.id,
            "pizza_id": orden.pizza_id,
            "costo_total": orden.costo_total,
            "estado": orden.estado
        }
        return jsonify(orden_data), 200
    except Exception as error:
        print(error)
        return jsonify({"error": "No se pudo actualizar la orden"}), 500

if __name__ == '__main__':
    print("Starting server...")
    with app.app_context():
        db.create_all()  # Crear todas las tablas definidas en los modelos
    app.run(host='0.0.0.0', debug=True, port=8000)
    print("Server started")