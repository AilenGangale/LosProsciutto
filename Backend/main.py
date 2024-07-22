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
# @app.route('/clientes/<cliente_id>/nueva_orden/<int:sabor_id>', methods=['POST'])
# def nueva_orden(cliente_id, sabor_id):
#     try:

#         cliente = Cliente.query.get(cliente_id)
#         if not cliente:
#             return jsonify({"mensaje": "Cliente no encontrado."}), 404

#         # Asignar sabor segun el numero
#         sabores = {1: "Muzzarella", 2: "Fugazzeta", 3: "Jamón y Morrón"}
#         sabor = sabores.get(sabor_id)
#         if not sabor:
#             return jsonify({"mensaje": "Sabor no válido."}), 400

#         # Crear una nueva pizza
#         nueva_pizza = Pizza(sabor=sabor, costo_pizza=120)  # Asegúrate de que `costo_pizza` esté definido
#         db.session.add(nueva_pizza)
#         db.session.commit()

#         # Crear una nueva orden con la nueva pizza
#         nueva_orden = Orden(
#             cliente_id=cliente_id,
#             pizza_id=nueva_pizza.id,
#             costo_total=120,
#             estado="Pendiente"
#         )
#         db.session.add(nueva_orden)
#         db.session.commit()

#         return jsonify({"orden": {
#             "id": nueva_orden.id,
#             "pizza_id": nueva_orden.pizza_id,
#             "costo_total": nueva_orden.costo_total,
#             "estado": nueva_orden.estado
#         }}), 200

#     except Exception as e:
#         print(f"Error interno del servidor: {e}")
#         return jsonify({"mensaje": "Error interno del servidor."}), 500
# @app.route('/clientes/<int:cliente_id>/nueva_orden/<int:sabor_id>', methods=['POST'])
# def nueva_orden(cliente_id, sabor_id):
#     try:
#         cliente = Cliente.query.get(cliente_id)
#         if not cliente:
#             return jsonify({"mensaje": "Cliente no encontrado."}), 404

#         # Asignar sabor según el número
#         sabores = {1: "Muzzarella", 2: "Fugazzeta", 3: "Jamón y Morrón"}
#         sabor = sabores.get(sabor_id)
#         if not sabor:
#             return jsonify({"mensaje": "Sabor no válido."}), 400

#         # Crear una nueva pizza
#         tiempo_coccion = 1  # Tiempo de cocción en minutos
#         nueva_pizza = Pizza(sabor=sabor, costo_pizza=120, tiempo_coccion=tiempo_coccion)
        
#         # Chequear si el cliente tiene suficiente dinero
#         if cliente.plata < nueva_pizza.costo_pizza:
#             return jsonify({"mensaje": "No hay suficiente dinero."}), 400
        
#         # Agregar la pizza a la base de datos
#         db.session.add(nueva_pizza)
#         db.session.commit()

#         # Calcular la fecha de entrega
#         fecha_creacion = datetime.datetime.now()
#         fecha_entrega = fecha_creacion + datetime.timedelta(minutes=tiempo_coccion)

#         # Crear una nueva orden con la nueva pizza
#         nueva_orden = Orden(
#             cliente_id=cliente_id,
#             pizza_id=nueva_pizza.id,
#             costo_total=nueva_pizza.costo_pizza,
#             estado="Pendiente",
#             fecha_creacion=fecha_creacion,
#             fecha_entrega=fecha_entrega
#         )

#         # Reducir el dinero del cliente
#         cliente.plata -= nueva_pizza.costo_pizza
#         db.session.add(cliente)
        
#         db.session.add(nueva_orden)
#         db.session.commit()

#         return jsonify({"orden": {
#             "id": nueva_orden.id,
#             "pizza_id": nueva_orden.pizza_id,
#             "costo_total": nueva_orden.costo_total,
#             "estado": nueva_orden.estado,
#             "fecha_creacion": nueva_orden.fecha_creacion,
#             "fecha_entrega": nueva_orden.fecha_entrega,
#             "tiempo_coccion": nueva_pizza.tiempo_coccion  # Añadido tiempo de cocción
#         }}), 200

#     except Exception as e:
#         print(f"Error interno del servidor: {e}")
#         return jsonify({"mensaje": "Error interno del servidor."}), 500
@app.route('/clientes/<int:cliente_id>/nueva_orden/<int:sabor_id>', methods=['POST'])
def nueva_orden(cliente_id, sabor_id):
    try:
        cliente = Cliente.query.get(cliente_id)
        if not cliente:
            return jsonify({"mensaje": "Cliente no encontrado."}), 404

        sabores = {1: "Muzzarella", 2: "Fugazzeta", 3: "Jamón y Morrón"}
        sabor = sabores.get(sabor_id)
        if not sabor:
            return jsonify({"mensaje": "Sabor no válido."}), 400

        tiempo_coccion = 1
        nueva_pizza = Pizza(sabor=sabor, costo_pizza=120, tiempo_coccion=1)
        
        if cliente.plata < nueva_pizza.costo_pizza:
            return jsonify({"mensaje": "No hay suficiente dinero."}), 400
        
        db.session.add(nueva_pizza)
        db.session.commit()

        print(f"Tiempo de cocción: {nueva_pizza.tiempo_coccion}")

        fecha_creacion = datetime.datetime.now()
        fecha_entrega = fecha_creacion + datetime.timedelta(minutes=tiempo_coccion)

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

#Permite modificar una orden. Primero la busca por su id, luego obtiene los datos de la solicitud. Actualiza los campos si se proporcionaron nuevos datos, guarda los cambios y devuelve la información actualizada de la orden.
# @app.route('/ordenes/<id_orden>', methods=['PUT'])
# def actualizar_orden(id_orden):
#     try:
#         orden = Orden.query.get(id_orden)
#         if not orden:
#             return jsonify({"error": "Orden no encontrada"}), 404

#         data = request.json
#         nuevo_estado = data.get("estado")
#         nuevo_costo_total = data.get("costo_total")
#         nueva_pizza_id = data.get("pizza_id")

#         if nuevo_estado:
#             orden.estado = nuevo_estado
#         if nuevo_costo_total is not None:
#             orden.costo_total = nuevo_costo_total
#         if nueva_pizza_id:
#             nueva_pizza = Pizza.query.get(nueva_pizza_id)
#             if nueva_pizza:
#                 orden.pizza_id = nueva_pizza_id
#             else:
#                 return jsonify({"error": "Pizza no encontrada"}), 404

#         db.session.commit()

#         orden_data = {
#             "id": orden.id,
#             "pizza_id": orden.pizza_id,
#             "costo_total": orden.costo_total,
#             "estado": orden.estado
#         }
#         return jsonify(orden_data), 200
#     except Exception as error:
#         print(error)
#         return jsonify({"error": "No se pudo actualizar la orden"}), 500

@app.route('/ordenes/<id_orden>', methods=['PUT'])
def actualizar_orden(id_orden):
    try:
        orden = Orden.query.get(id_orden)
        if not orden:
            return jsonify({"error": "Orden no encontrada"}), 404
        data = request.json
        nueva_pizza_id = data.get("pizza_id")

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

# Primero busca la orden por su ID y luego la elimina
@app.route('/ordenes/<id_orden>', methods=['DELETE'])
def eliminar_orden(id_orden):
    try:
        # Buscar la orden por ID
        orden = Orden.query.get(id_orden)
        if not orden:
            return jsonify({"error": "Orden no encontrada"}), 404

        # Eliminar la orden
        db.session.delete(orden)
        db.session.commit()

        return jsonify({"success": True, "message": "Orden eliminada con éxito"}), 200

    except Exception as e:
        print(f"Error al eliminar la orden: {e}")
        db.session.rollback()  # Deshacer cualquier cambio en caso de error
        return jsonify({"success": False, "error": "Error al eliminar la orden"}), 500



#dado el id de la orden que le llega por parámetro busca la orden en la base de datos, busca el cliente en la base de datos y busca la pizza en la base de datos. Tiene 3 variables, hace los cambios necesarios (si recibió la orden le resto plata y pongo que la pizza está entregada). Luego se añaden esas cosas a la sesión y commiteamos. Devolvemos como retorno del post la nueva plata del cliente para poder actualizar dinámicamente la página
@app.route("/retirar/<id_orden>", methods=['POST'])
def retirar_orden(id_orden):
    try:
        # orden = Orden.query.get(id_orden)
        # cliente = Cliente.query.get(orden.cliente_id)
        # pizza = Pizza.query.get(orden.pizza_id)
        
        orden = Orden.query.get(id_orden)
        if not orden:
            return jsonify({"mensaje": "Orden no encontrada."}), 404

        cliente = Cliente.query.get(orden.cliente_id)
        if not cliente:
            return jsonify({"mensaje": "Cliente no encontrado."}), 404

        pizza = Pizza.query.get(orden.pizza_id)
        if not pizza:
            return jsonify({"mensaje": "Pizza no encontrada."}), 404
        
        orden.estado = "Entregada"

        db.session.add(orden)
        db.session.add(cliente)
        db.session.commit()

        return jsonify({'mensaje': 'Orden marcada como entregada'}), 201
    except Exception as error:
        print(error)
        return jsonify({"mensaje": "No se pudo retirar la orden."}),500

@app.route('/nuevo_cliente')
def nuevo_cliente_page():
    return render_template('clientes_nuevos.html')


@app.route('/ordenes')
def orden_cliente():
    return render_template('ordenes.html')

if __name__ == '__main__':
    print("Starting server...")
    with app.app_context():
        db.create_all()  # Crear todas las tablas definidas en los modelos
    app.run(host='0.0.0.0', debug=True, port=8000)
    print("Server started")