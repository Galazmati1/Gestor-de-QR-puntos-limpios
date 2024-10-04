import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
from crear_punto import crear_punto_bp
from modificar_punto import modificar_punto_bp
from PIL import Image  # Asegúrate de importar Pillow aquí

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configurar Flask
app = Flask(__name__)

# Agregar clave secreta para sesiones (usada para flash messages)
app.secret_key = os.getenv('SECRET_KEY')  # Asegúrate de que esta variable esté en tu archivo .env

# Habilitar CORS para todas las rutas
CORS(app)

# Conectar a MongoDB
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client.reciclaje_db

# Ruta para solicitar la clave
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        entered_password = request.form['password']
        correct_password = os.getenv('ACCESS_PASSWORD', 'Gamo1234')  # Clave en .env

        if entered_password == correct_password:
            # Si la clave es correcta, redirigir al usuario al menú principal
            return redirect(url_for('menu'))
        else:
            # Si la clave es incorrecta, mostrar un mensaje de error
            flash('Clave incorrecta. Inténtalo de nuevo.')
            return render_template('login.html')  # Modificado para apuntar a la nueva plantilla de login

    return render_template('login.html')  # Modificado para apuntar a la nueva plantilla de login

# Menú principal después de la autenticación
@app.route('/menu')
def menu():
    return render_template('menu.html')  # Crear un menú que redirija a los blueprints

# Registrar los Blueprints
app.register_blueprint(crear_punto_bp)
app.register_blueprint(modificar_punto_bp)

# No necesitas el bloque 'if __name__ == "__main__"' porque vas a usar gunicorn en producción
