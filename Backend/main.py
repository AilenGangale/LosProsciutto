from flask import Flask, render_template, request, jsonify
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

@app.route('/nuevo_cliente')
def nuevo_cliente_page():
    return render_template('clientes_nuevos.html')


@app.route('/ordenes')
def orden_cliente():
    return render_template('ordenes.html')

#Endpoints de CLIENTES

#Devolver todos los clientes GET
@app.route('/clientes/', methods=['GET'])
def all_clientes():
    try:
        
        # Recupera los registros de una tabla
        clientes = Cliente.query.all()
        return render_template('clientes_existentes.html', clientes=clientes) #Renderiza la pagina y devuelve la informacion de clientes
    except:
        return jsonify({"error": "No se pudieron recuperar los datos"})

#Devuelve la informacion de un solo cliente GET
@app.route("/clientes/<id_cliente>") 
def data(id_cliente):
    cliente= Cliente.query.get(id_cliente) #Obtiene el cliente que tenga el id que se le pasa por parametro
    #Se guradan los datos en diccionario
    cliente_data = {
    "id" : cliente.id,
    "nombre": cliente.nombre,
    "plata ": cliente.plata
    }
    return jsonify(cliente_data)

#Sube un nuevo cliente a la base de datos POST
@app.route('/cliente_nuevo', methods=['POST'])
def nuevo_cliente():
    try:
        #Obtenemos la informacion del rquest y se interppreta en json
        data = request.json

        #se extraen los valores para los cmapos del nuevo_cliente
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
#Deja actuaszlizar el nombre del cliente
@app.route('/clientes/<int:cliente_id>/editar_nombre', methods=['PUT'])
def editar_nombre_cliente(cliente_id):
    data = request.get_json()
    nuevo_nombre = data.get('nombre')

    cliente = Cliente.query.get(cliente_id)
    if cliente:
        cliente.nombre = nuevo_nombre
        db.session.commit()
        return jsonify(success=True, message="Nombre del cliente actualizado exitosamente.")
    else:
        return jsonify(success=False, message="Cliente no encontrado."), 404

#Borra un cliente cons todas sus oordens y pizzas de la base de datos DELETE
@app.route('/clientes/borrar_cliente/<int:id_cliente>', methods=['DELETE'])
def delete_cliente(id_cliente):
    try:
        # Obtener el cliente
        cliente = Cliente.query.get(id_cliente)
        if cliente:
            # Elimina las órdenes asociadas al cliente
            Orden.query.filter_by(cliente_id=id_cliente).delete()
            db.session.delete(cliente)
            db.session.commit()
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Cliente no encontrado"}), 404
    except Exception as e:
        print(f"Error al eliminar el cliente: {e}")
        db.session.rollback() #Si algun error sucede se deshace todo
        return jsonify({"success": False, "error": "Error al eliminar el cliente"}), 500

#Endpoints de ORDENES
#Obtenemos todas las ordenes de un solo cliente GET
@app.route('/clientes/<int:id_cliente>/ordenes', methods=['GET'])
def all_ordenes(id_cliente):
    try:
        # Obtiene el cliente
        cliente = Cliente.query.filter_by(id=id_cliente).first()
        if not cliente:
            return jsonify({"error": "Cliente no encontrado"}), 404

        # Obtiene todas las órdenes del cliente
        ordenes = Orden.query.filter_by(cliente_id=id_cliente).all()
        
        # GUarda la información de las pizzas asocwiadas a las órdenes
        ordenes_info = []
        for orden in ordenes:
            pizza = Pizza.query.get(orden.pizza_id)
            if pizza:
                ordenes_info.append({
                    'orden_id': orden.id,
                    'pizza_id': pizza.id,
                    'pizza_sabor': pizza.sabor,
                    'pizza_costo': pizza.costo_pizza,
                    'costo_total': orden.costo_total,
                    'estado': orden.estado,
                    'fecha_creacion': orden.fecha_creacion.isoformat(),
                    'fecha_entrega': orden.fecha_entrega.isoformat()
                })

        return render_template('ordenes.html', ordenes=ordenes_info, cliente=cliente)
    except Exception as e:
        print(f"Error al recuperar las órdenes: {e}")
        return jsonify({"error": "No se pudieron recuperar los datos"}), 500

#Crear la pizza con el sabor correspondiente y la orden con cliente que corresponda POST
@app.route('/clientes/<int:cliente_id>/nueva_orden/<int:sabor_id>', methods=['POST'])
def nueva_orden(cliente_id, sabor_id):
    try:
        cliente = Cliente.query.get(cliente_id)
        if not cliente:
            return jsonify({"mensaje": "Cliente no encontrado."}), 404
        # Asignar sabor segun el numero
        sabores = {1: "Muzzarella", 2: "Fugazzeta", 3: "Jamón y Morrón"}
        sabor = sabores.get(sabor_id)
        if not sabor:
            return jsonify({"mensaje": "Sabor no válido."}), 400
        
        if sabor == "Muzzarella":
            costo_pizza= 200
            tiempo_coccion= 0.5
        elif sabor == "Fugazzeta":
            costo_pizza= 400
            tiempo_coccion= 0.6
        else:
            costo_pizza= 300
            tiempo_coccion= 1

        nueva_pizza = Pizza(sabor=sabor, costo_pizza=costo_pizza, tiempo_coccion=tiempo_coccion)
        
        if cliente.plata < nueva_pizza.costo_pizza:
            return jsonify({"mensaje": "No hay suficiente dinero."}), 400
        
        db.session.add(nueva_pizza)
        db.session.commit()

        print(f"Tiempo de cocción: {nueva_pizza.tiempo_coccion}")

        fecha_creacion = datetime.datetime.now()
        fecha_entrega = fecha_creacion + datetime.timedelta(minutes=tiempo_coccion)

        # Crear una nueva orden con la nueva pizza
        nueva_orden = Orden(
            cliente_id=cliente_id,
            pizza_id=nueva_pizza.id,
            costo_total=nueva_pizza.costo_pizza,
            estado="Pendiente",
            fecha_creacion=fecha_creacion,
            fecha_entrega=fecha_entrega
        )

        cliente.plata -= nueva_pizza.costo_pizza
        db.session.add(cliente)
        db.session.add(nueva_orden)
        db.session.commit()

        return jsonify({"orden": {
            "id": nueva_orden.id,
            "pizza_id": nueva_orden.pizza_id,
            "costo_total": nueva_orden.costo_total,
            "estado": nueva_orden.estado,
            "fecha_creacion": nueva_orden.fecha_creacion.isoformat(),
            "fecha_entrega": nueva_orden.fecha_entrega.isoformat(),
            "tiempo_coccion": nueva_pizza.tiempo_coccion
        }}), 200

    except Exception as e:
        print(f"Error interno del servidor: {e}")
        return jsonify({"mensaje": "Error interno del servidor."}), 500


# Primero busca la orden por su ID y luego la elimina, le devuelve la plata al cliente.
@app.route('/ordenes/<id_orden>', methods=['DELETE'])
def eliminar_orden(id_orden):
    try:
        # Buscar la orden por ID
        orden = Orden.query.get(id_orden)
        if not orden:
            return jsonify({"error": "Orden no encontrada"}), 404

        # Obtener el cliente y la pizza correspondientes
        cliente = Cliente.query.get(orden.cliente_id)
        pizza = Pizza.query.get(orden.pizza_id)
        
        if not cliente:
            return jsonify({"error": "Cliente no encontrado"}), 404

        if not pizza:
            return jsonify({"error": "Pizza no encontrada"}), 404

        # Devolver el dinero al cliente
        cliente.plata += pizza.costo_pizza

        # Eliminar la orden
        db.session.delete(orden)
        db.session.commit()

        return jsonify({"success": True, "message": "Orden eliminada con éxito", "nueva_plata": cliente.plata}), 200

    except Exception as e:
        print(f"Error al eliminar la orden: {e}")
        db.session.rollback()  # Deshacer cualquier cambio en caso de error
        return jsonify({"success": False, "error": "Error al eliminar la orden"}), 500



@app.route("/retirar/<id_orden>", methods=['DELETE'])
def retirar_orden(id_orden):
    try:
        orden = Orden.query.get(id_orden)
        if not orden:
            return jsonify({"mensaje": "Orden no encontrada."}), 404

        cliente = Cliente.query.get(orden.cliente_id)
        if not cliente:
            return jsonify({"mensaje": "Cliente no encontrado."}), 404

        pizza = Pizza.query.get(orden.pizza_id)
        if not pizza:
            return jsonify({"mensaje": "Pizza no encontrada."}), 404

        # Eliminar la orden y la pizza
        db.session.delete(orden)
        db.session.delete(pizza)
        db.session.commit()

        return jsonify({
            'mensaje': f'Tu pizza de ID {orden.pizza_id} fue retirada y eliminada.',
        }), 200

    except Exception as error:
        print(error)
        return jsonify({"mensaje": "No se pudo retirar la orden."}), 500

if __name__ == '__main__':
    print("Starting server...")
    with app.app_context():
        db.create_all()  # Crear todas las tablas definidas en los modelos
    app.run(host='0.0.0.0', debug=True, port=8000)
    print("Server started")