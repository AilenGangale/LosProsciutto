
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


@app.route('/clientes/borrar_cliente/<int:id_cliente>', methods=['DELETE'])
def delete_cliente(id_cliente):
    try:
        # Obtén el cliente
        cliente = Cliente.query.get(id_cliente)
        if cliente:
            # Elimina las órdenes asociadas al cliente
            Orden.query.filter_by(cliente_id=id_cliente).delete()

            # Elimina el cliente
            db.session.delete(cliente)
            db.session.commit()
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Cliente no encontrado"}), 404
    except Exception as e:
        print(f"Error al eliminar el cliente: {e}")
        db.session.rollback()  # Deshaz cualquier cambio en caso de error
        return jsonify({"success": False, "error": "Error al eliminar el cliente"}), 500


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

#Devolver todos las ordenes
@app.route('/clientes/<id_cliente>/ordenes', methods=['GET'])
def all_ordenes(id_cliente):
    try:
         # Recupera las órdenes del cliente
        ordenes = Orden.query.filter_by(cliente_id=id_cliente).all()
        # Recupera el cliente específico
        cliente = Cliente.query.filter_by(id=id_cliente).first()  # Usa `first()` para obtener un solo objeto
        return render_template('ordenes.html', ordenes=ordenes, cliente=cliente)
    except:
        return jsonify({"error": "No se pudieron recuperar los datos"})

@app.route('/clientes/<cliente_id>/nueva_orden/<int:sabor_id>', methods=['POST'])
def nueva_orden(cliente_id, sabor_id):
    try:
        print(f"Recibiendo solicitud para cliente_id: {cliente_id} y sabor_id: {sabor_id}")

        # Verifica que el cliente exista
        cliente = Cliente.query.get(cliente_id)
        if not cliente:
            return jsonify({"mensaje": "Cliente no encontrado."}), 404

        # Asignar sabor basado en el número
        sabores = {1: "Muzzarella", 2: "Fugazzeta", 3: "Jamón y Morrón"}
        sabor = sabores.get(sabor_id)
        if not sabor:
            return jsonify({"mensaje": "Sabor no válido."}), 400

        # Crear una nueva pizza con el sabor proporcionado
        nueva_pizza = Pizza(sabor=sabor, costo_pizza=120)  # Asegúrate de que `costo_pizza` esté definido
        db.session.add(nueva_pizza)
        db.session.commit()

        # Crear una nueva orden con la nueva pizza
        nueva_orden = Orden(
            cliente_id=cliente_id,
            pizza_id=nueva_pizza.id,
            costo_total=120,
            estado="Pendiente"
        )
        db.session.add(nueva_orden)
        db.session.commit()

        return jsonify({"orden": {
            "id": nueva_orden.id,
            "pizza_id": nueva_orden.pizza_id,
            "costo_total": nueva_orden.costo_total,
            "estado": nueva_orden.estado
        }}), 200

    except Exception as e:
        print(f"Error interno del servidor: {e}")
        return jsonify({"mensaje": "Error interno del servidor."}), 500
	
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