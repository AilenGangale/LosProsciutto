# Papas Pizza - Grupo: Los Prosciutto

Tp/final de introduccion al software

## Descripción

Es una aplicación web desarrollada con Flask para gestionar clientes y órdenes de pizza. Se pueden crear nuevos clientes, realizar pedidos de pizzas y gestionar las órdenes existentes. Utiliza una base de datos PostgreSQL para almacenar la información de clientes, pizzas y órdenes.

## Características

- Gestión de Clientes
  - Crear, editar y eliminar clientes.
- Gestión de Órdenes
  - Crear, ver, cancelar y retirar órdenes de pizza.

## Tecnologías

- Backend: Flask (Python)
- Base de Datos: PostgreSQL
- Frontend: HTML, CSS, JavaScript
- ORM: SQLAlchemy

## Instalación

### Instalar python utltima version
sudo apt install python3

### Clonación del Repositorio

git clone https://github.com/AilenGangale/LosProsciutto.git
cd LosProsciutto

### Configuración del entorno virtual

#### Crear Entorno virtual

python3 -m venv venv

#### Activar Entorno virtual

source venv/bin/activate

### Instalar Flask y demás dependencias

pip install flask
pip install Flask-SQLAlchemy
pip install flask-cors
pip install psycopg2

### Instalar Postgres

sudo apt install postgresql postgresql-contrib

## Uso

### Iniciar el servidor

python3 main.py

La aplicación estará disponible en http://localhost:8000.