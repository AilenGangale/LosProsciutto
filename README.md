# Papas Pizza - Grupo: Los Prosciutto
Tp/final de introduccion al software

## Descripción

Es una aplicación web desarrollada con Flask para gestionar clientes y órdenes de pizza. Se pueden crear nuevos clientes, realizar pedidos de pizzas y gestionar las órdenes existentes. Utiliza una base de datos PostgreSQL para almacenar la información de clientes, pizzas y órdenes.

## Características

- Gestión de Clientes
  - Crear, editar y eliminar clientes.
- Gestión de Órdenes
  - Crear, ver, cancelar y retirar órdenes de pizza.

# Instalar python utltima version
sudo apt install python3

# Instalar Postgres
sudo apt install postgresql postgresql-contrib

# Instalar entorno virtual
sudo apt install python3.12-venv

# Activar Entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar Flask
pip install flask

# Instalar sqlalchemy
pip install Flask Flask-SQLAlchemy
pip install flask-cors
pip install psycopg2
