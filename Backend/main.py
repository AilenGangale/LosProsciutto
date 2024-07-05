
from flask import Flask, render_template
from models import db, Cliente, Pizza, Orden

configure_database(app)

app = Flask(__name__)
# Configurar la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:111276@localhost:5432/papaspizza'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


@app.route('/')
def hello_world():
    return 'Hello world'

@app.route('/hello')
def otro_hello():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8000)