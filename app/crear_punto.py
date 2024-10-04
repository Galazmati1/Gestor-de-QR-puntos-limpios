from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from pymongo import MongoClient
import os
import qrcode
from io import BytesIO
import base64
from dotenv import load_dotenv
from bson.objectid import ObjectId
from PIL import Image

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Conectar a MongoDB
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client.reciclaje_db

# Crear un Blueprint
crear_punto_bp = Blueprint('crear_punto', __name__)

# Paso 1: Seleccionar o crear empresa
@crear_punto_bp.route('/crear_punto', methods=['GET', 'POST'])
def crear_punto():
    if request.method == 'GET':
        # Obtener todas las empresas registradas en la colección puntos_activos
        empresas = db.puntos_activos.distinct('empresa')
        return render_template('crear_punto.html', empresas=empresas)

    elif request.method == 'POST':
        # Obtener la empresa seleccionada o la nueva ingresada
        empresa = request.form.get('empresa')
        nueva_empresa = request.form.get('nueva_empresa')
        
        if nueva_empresa:
            empresa = nueva_empresa
        
        # Redirigir al siguiente paso con la empresa seleccionada
        return redirect(url_for('crear_punto.crear_punto_numero', empresa=empresa))

# Paso 2: Generar y validar número de punto
@crear_punto_bp.route('/crear_punto/numero/<empresa>', methods=['GET', 'POST'])
def crear_punto_numero(empresa):
    if request.method == 'GET':
        # Buscar el número más alto de punto para la empresa seleccionada
        puntos = db.puntos_activos.find({'empresa': empresa}).sort('punto_limpio', -1).limit(1)
        ultimo_punto = 0
        
        for punto in puntos:
            ultimo_punto = punto['punto_limpio']

        nuevo_punto = int(ultimo_punto) + 1
        
        return render_template('crear_punto_numero.html', empresa=empresa, nuevo_punto=nuevo_punto)

    elif request.method == 'POST':
        punto_limpio = request.form.get('punto_limpio')
        empresa = request.form.get('empresa')  # Asegúrate de que también pasamos la empresa
        return redirect(url_for('crear_punto.crear_punto_ubicacion', punto_limpio=punto_limpio, empresa=empresa))

# Paso 3: Ingresar ubicación y coordenadas
@crear_punto_bp.route('/crear_punto/ubicacion/<punto_limpio>/<empresa>', methods=['GET', 'POST'])
def crear_punto_ubicacion(punto_limpio, empresa):
    if request.method == 'GET':
        return render_template('crear_punto_ubicacion.html', punto_limpio=punto_limpio, empresa=empresa)

    elif request.method == 'POST':
        descripcion = request.form.get('descripcion')
        latitud = request.form.get('latitud')
        longitud = request.form.get('longitud')
        return redirect(url_for('crear_punto.generar_qr', punto_limpio=punto_limpio, empresa=empresa, descripcion=descripcion, latitud=latitud, longitud=longitud))

# Paso 4: Generar URL y código QR
@crear_punto_bp.route('/crear_punto/generar_qr/<punto_limpio>/<empresa>/<descripcion>/<latitud>/<longitud>', methods=['GET', 'POST'])
def generar_qr(punto_limpio, empresa, descripcion, latitud, longitud):
    # Generar la URL
    url = f"http://plataforma.teleportero.cl/upload?punto_limpio={punto_limpio}&empresa={empresa}"

    # Crear el código QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Generar la imagen QR con PIL
    img = qr.make_image(fill="black", back_color="white").convert('RGB')
    buffer = BytesIO()

    # Guardar la imagen en formato JPEG en el buffer
    img.save(buffer, format="JPEG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # Guardar en la base de datos
    nuevo_punto = {
        "punto_limpio": punto_limpio,
        "empresa": empresa,
        "latitud": float(latitud),
        "longitud": float(longitud),
        "ubicacion": descripcion,
        "url_qr": url,
        "qr_image_base64": img_str,
        "punto_activo": True
    }
    resultado = db.puntos_activos.insert_one(nuevo_punto)
    punto_id = str(resultado.inserted_id)

    # Redirigir al paso final para mostrar el QR
    return redirect(url_for('crear_punto.punto_creado', punto_id=punto_id))


# Paso 5: Mostrar el resultado y descargar el QR
@crear_punto_bp.route('/crear_punto/punto_creado/<punto_id>', methods=['GET'])
def punto_creado(punto_id):
    # Recuperar el punto limpio desde MongoDB
    punto = db.puntos_activos.find_one({"_id": ObjectId(punto_id)})

    if not punto or "qr_image_base64" not in punto:
        return "No QR code available", 404

    img_str = punto['qr_image_base64']
    empresa = punto['empresa']
    punto_limpio = punto['punto_limpio']

    # Renderizar la página con la imagen en base64 y las variables empresa y punto_limpio
    return render_template('punto_creado.html', img_str=img_str, empresa=empresa, punto_limpio=punto_limpio)
