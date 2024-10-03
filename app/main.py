import os
import logging
from flask import Flask, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
from crear_punto import crear_punto_bp
from modificar_punto import modificar_punto_bp

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configurar Flask
app = Flask(__name__)

# Agregar clave secreta para sesiones
app.secret_key = os.getenv('SECRET_KEY')  # Asegúrate de que esta variable esté en tu archivo .env

# Habilitar CORS para todas las rutas
CORS(app)

# Conectar a MongoDB
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client.reciclaje_db

# Registrar los Blueprints
app.register_blueprint(crear_punto_bp)
app.register_blueprint(modificar_punto_bp)

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# No necesitas el bloque 'if __name__ == "__main__"' porque vas a usar gunicorn en producción
