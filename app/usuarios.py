from flask import Blueprint, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
import os
import bcrypt
from bson.objectid import ObjectId
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Conectar a MongoDB
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client.reciclaje_db
usuarios_collection = db.usuarios
puntos_activos_collection = db.puntos_activos  # Para obtener las empresas desde puntos_activos

# Crear un Blueprint
usuarios_bp = Blueprint('usuarios', __name__)

# Paso 1: Mostrar lista de usuarios
@usuarios_bp.route('/usuarios', methods=['GET', 'POST'])
def seleccionar_usuario():
    if request.method == 'GET':
        # Obtener todos los nombres de usuario registrados desde la colección de usuarios
        usuarios = list(usuarios_collection.find({}, {"usuario": 1, "Empresa": 1}))
        return render_template('seleccionar_usuario.html', usuarios=usuarios)

    elif request.method == 'POST':
        usuario_id = request.form.get('usuario_id')
        if usuario_id == "crear":
            return redirect(url_for('usuarios.crear_modificar_usuario', usuario_id='nuevo'))
        else:
            return redirect(url_for('usuarios.crear_modificar_usuario', usuario_id=usuario_id))

# Paso 2: Crear o modificar usuario
@usuarios_bp.route('/usuarios/formulario/<usuario_id>', methods=['GET', 'POST'])
def crear_modificar_usuario(usuario_id):
    # Obtener las empresas desde la colección puntos_activos para mostrarlas en el formulario
    empresas = db.puntos_activos.distinct('empresa')

    if request.method == 'GET':
        if usuario_id == 'nuevo':
            usuario = None  # Formulario vacío para nuevo usuario
        else:
            usuario = usuarios_collection.find_one({"_id": ObjectId(usuario_id)})

        return render_template('formulario_usuario.html', usuario=usuario, empresas=empresas)

    elif request.method == 'POST':
        usuario = request.form.get('usuario')
        empresa = request.form.get('empresa')
        contraseña = request.form.get('contraseña')

        if not contraseña:
            contraseña = 'Contraseña123'  # Contraseña por defecto si no se ingresa una

        # Encriptar la contraseña
        contraseña_encriptada = bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt())

        if usuario_id == 'nuevo':
            # Crear nuevo usuario
            nuevo_usuario = {
                "usuario": usuario,
                "psw": contraseña_encriptada.decode('utf-8'),
                "Empresa": empresa
            }
            usuarios_collection.insert_one(nuevo_usuario)
            flash(f'Usuario "{usuario}" creado exitosamente.')
        else:
            # Actualizar usuario existente
            usuarios_collection.update_one(
                {"_id": ObjectId(usuario_id)},
                {"$set": {
                    "usuario": usuario,
                    "psw": contraseña_encriptada.decode('utf-8'),
                    "Empresa": empresa
                }}
            )
            flash(f'Usuario "{usuario}" actualizado exitosamente.')

        return redirect(url_for('usuarios.seleccionar_usuario'))
