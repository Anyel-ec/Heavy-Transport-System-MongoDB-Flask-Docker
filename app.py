from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os
from bson import ObjectId
from data_manager import DataManager

#Cargar variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)

# Cargar variables de entorno desde el archivo .env

app.secret_key = os.getenv('SECRET_KEY')

# Configuración de la base de datos MongoDB desde la variable de entorno
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
mongo = PyMongo(app)

data_manager = DataManager(mongo)


@app.route('/')
def index():
    trailers_con_colores = data_manager.get_trailers_with_colors()
    return render_template('index.html', trailers=trailers_con_colores)


@app.route('/agregar_trailer', methods=['POST'])
def agregar_trailer():
    if request.method == 'POST':
        matricula = request.form.get('matricula')
        Ejes = int(request.form.get('Ejes'))
        marca_id = int(request.form.get('marca'))
        modelo = request.form.get('modelo')
        color_id = int(request.form.get('color'))
        capacidad_carga = int(request.form.get('capacidadCarga'))

        data_manager.add_trailer(matricula, Ejes, marca_id, modelo, color_id, capacidad_carga)

        flash('Trailer agregado correctamente', 'success')
        return redirect(url_for('index'))

@app.route('/editar_trailer/<string:matricula>', methods=['GET', 'POST'])
def editar_trailer(matricula):
    trailer = mongo.db.trailer.find_one({'matricula': matricula})

    if request.method == 'POST':
        nuevo_modelo = request.form.get('modelo')
        nuevo_color_id = int(request.form.get('color'))
        nueva_capacidad_carga = int(request.form.get('capacidadCarga'))

        data_manager.edit_trailer(matricula, nuevo_modelo, nuevo_color_id, nueva_capacidad_carga)

        flash('Trailer actualizado correctamente', 'success')
        return redirect(url_for('index'))

    colores = mongo.db.colores.find()
    marcas = mongo.db.marcas.find()

    return render_template('actualizarTrailer.html', trailer=trailer, colores=colores, marcas=marcas)


@app.route('/eliminar_trailer/<string:matricula>', methods=['GET', 'POST'])
def eliminar_trailer(matricula):
    trailer, marca, color = data_manager.delete_trailer(matricula)

    if request.method == 'POST':
        flash('Trailer eliminado correctamente', 'danger')
        return redirect(url_for('index'))

    return render_template('eliminarTrailer.html', trailer=trailer, marca=marca, color=color)

# Nueva ruta para renderizar la plantilla agregarTrailer.html
@app.route('/formulario_agregar_trailer')
def formulario_agregar_trailer():
    # Obtener los colores desde la colección "colores"
    colores = mongo.db.colores.find()
    marcas = mongo.db.marcas.find()

    # Pasar la lista de colores a la plantilla
    return render_template('agregarTrailer.html', colores=colores, marcas=marcas)


# Ruta de ejemplo para probar la conexión
@app.route('/test_mongo_connection')
def test_mongo_connection():
    try:
        # Intenta realizar una consulta simple para verificar la conexión
        result = mongo.db.test_collection.find_one()
        return jsonify({'message': 'Conexión exitosa a MongoDB', 'data': result})
    except Exception as e:
        return jsonify({'message': 'Error en la conexión a MongoDB', 'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


