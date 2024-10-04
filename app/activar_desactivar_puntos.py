from flask import Blueprint, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Conectar a MongoDB
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client.reciclaje_db

# Crear Blueprint
activar_desactivar_bp = Blueprint('activar_desactivar', __name__)

# Paso 1: Mostrar lista de empresas
@activar_desactivar_bp.route('/activar_desactivar', methods=['GET', 'POST'])
def seleccionar_empresa():
    if request.method == 'GET':
        # Obtener todas las empresas registradas
        empresas = db.puntos_activos.distinct('empresa')
        return render_template('activar_desactivar.html', empresas=empresas)

    elif request.method == 'POST':
        # Obtener la empresa seleccionada
        empresa = request.form.get('empresa')
        accion = request.form.get('accion')  # Activar o desactivar
        return redirect(url_for('activar_desactivar.confirmar_accion', empresa=empresa, accion=accion))

# Paso 2: Confirmar acción de activación/desactivación
@activar_desactivar_bp.route('/activar_desactivar/confirmar/<empresa>/<accion>', methods=['GET', 'POST'])
def confirmar_accion(empresa, accion):
    if request.method == 'POST':
        if accion == 'activar':
            nuevo_estado = True
        elif accion == 'desactivar':
            nuevo_estado = False

        # Actualizar todos los puntos de la empresa
        db.puntos_activos.update_many({'empresa': empresa}, {"$set": {'punto_activo': nuevo_estado}})


        flash(f'Todos los puntos de la empresa {empresa} han sido {"activados" if nuevo_estado else "desactivados"}.')
        return redirect(url_for('activar_desactivar.seleccionar_empresa'))

    return render_template('confirmar_accion.html', empresa=empresa, accion=accion)
