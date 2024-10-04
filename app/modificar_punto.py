from flask import Blueprint, request, render_template, redirect, url_for, jsonify, send_file
from pymongo import MongoClient
import os
from bson.objectid import ObjectId
from dotenv import load_dotenv
import qrcode
from io import BytesIO
import base64

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Conectar a MongoDB
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client.reciclaje_db

# Crear un Blueprint
modificar_punto_bp = Blueprint('modificar_punto', __name__)

# Paso 1: Seleccionar empresa para buscar puntos limpios
@modificar_punto_bp.route('/modificar_punto', methods=['GET', 'POST'])
def seleccionar_empresa():
    if request.method == 'GET':
        # Obtener todas las empresas registradas
        empresas = db.puntos_activos.distinct('empresa')
        return render_template('modificar_punto.html', empresas=empresas)

    elif request.method == 'POST':
        empresa = request.form.get('empresa')
        # Redirigir al paso de selección del punto limpio
        return redirect(url_for('modificar_punto.seleccionar_punto', empresa=empresa))

# Paso 2: Seleccionar punto limpio para editar
@modificar_punto_bp.route('/modificar_punto/seleccionar_punto/<empresa>', methods=['GET', 'POST'])
def seleccionar_punto(empresa):
    if request.method == 'GET':
        # Buscar todos los puntos limpios de la empresa
        puntos = db.puntos_activos.find({'empresa': empresa})
        return render_template('seleccionar_punto.html', empresa=empresa, puntos=puntos)

    elif request.method == 'POST':
        punto_id = request.form.get('punto_id')
        # Redirigir al formulario para modificar el punto limpio
        return redirect(url_for('modificar_punto.modificar_punto_form', punto_id=punto_id))

# Paso 3: Modificar la información del punto limpio
@modificar_punto_bp.route('/modificar_punto/formulario/<punto_id>', methods=['GET', 'POST'])
def modificar_punto_form(punto_id):
    # Recuperar el punto limpio desde la base de datos
    punto = db.puntos_activos.find_one({"_id": ObjectId(punto_id)})

    if request.method == 'GET':
        if not punto:
            return "Punto no encontrado", 404
        # Renderizar formulario con los detalles del punto limpio
        return render_template('modificar_punto_form.html', punto=punto)

    elif request.method == 'POST':
        # Obtener los datos del formulario
        ubicacion = request.form.get('ubicacion')  # Cambiado de 'descripcion' a 'ubicacion'
        latitud = request.form.get('latitud')
        longitud = request.form.get('longitud')

        # Actualizar el punto en la base de datos
        db.puntos_activos.update_one(
            {"_id": ObjectId(punto_id)},
            {"$set": {"ubicacion": ubicacion, "latitud": float(latitud), "longitud": float(longitud)}}
        )

        # Redirigir al último paso
        return redirect(url_for('modificar_punto.confirmar_cambios', punto_id=punto_id))


# Paso 4: Confirmar cambios
@modificar_punto_bp.route('/modificar_punto/confirmar/<punto_id>', methods=['GET', 'POST'])
def confirmar_cambios(punto_id):
    # Obtener el punto actualizado para mostrarlo al usuario
    punto = db.puntos_activos.find_one({"_id": ObjectId(punto_id)})

    if not punto:
        return "Punto no encontrado", 404

    if request.method == 'GET':
        return render_template('confirmar_cambios.html', punto=punto)

    elif request.method == 'POST':
        # Confirmar que los cambios fueron guardados
        return "Cambios guardados exitosamente."

# Descargar QR sin modificar
@modificar_punto_bp.route('/modificar_punto/descargar_qr/<punto_id>', methods=['GET'])
def descargar_qr(punto_id):
    # Recuperar el punto limpio y su QR
    punto = db.puntos_activos.find_one({"_id": ObjectId(punto_id)})

    if not punto or "qr_image_base64" not in punto:
        return "QR no disponible", 404

    # Decodificar el QR de la base de datos
    try:
        img_data = base64.b64decode(punto['qr_image_base64'])
    except Exception as e:
        return f"Error al decodificar la imagen QR: {str(e)}", 500

    # Guardar la imagen en un buffer
    buffer = BytesIO(img_data)
    buffer.seek(0)

    # Enviar el archivo al usuario con el nombre apropiado
    nombre_archivo = f"{punto['empresa']}_{punto['punto_limpio']}_QR.jpeg"
    return send_file(buffer, mimetype='image/jpeg', as_attachment=True, download_name=nombre_archivo)

# Eliminar un punto limpio
@modificar_punto_bp.route('/modificar_punto/eliminar/<punto_id>', methods=['GET'])
def eliminar_punto(punto_id):
    # Eliminar el punto limpio de la base de datos
    db.puntos_activos.delete_one({"_id": ObjectId(punto_id)})
    return redirect(url_for('index'))
