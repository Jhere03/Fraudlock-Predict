import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
import requests
from urllib.parse import urlparse
from datetime import datetime
from conect_bd import get_db_connection
from report_manager import ReportManager
from ssl_check import check_ssl
from url_similarity import check_url_similarity
from domain_security import check_domain_security
from populary_domain import check_domain_popularity
from metadata_check import check_metadata

app = Flask(__name__)
CORS(app)

# Forzar uso de CPU en lugar de GPU
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

# Cargar el modelo entrenado
model = tf.keras.models.load_model('modelo_fraude_v2.h5')
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Función para verificar si la URL o su dominio base está en la lista negra de la base de datos
def is_url_or_domain_in_blacklist(url, connection):
    cursor = connection.cursor()
    
    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    # Normalizar el dominio eliminando 'www.'
    if domain.startswith('www.'):
        domain = domain[4:]
    
    # Consultar la base de datos para verificar si el dominio o la URL está en la lista negra
    query = "SELECT EXISTS(SELECT 1 FROM blacklist WHERE url = %s OR url = %s)"
    cursor.execute(query, (domain, url))
    result = cursor.fetchone()
    
    cursor.close()

    return result[0] == 1

# Función para normalizar el dominio de una URL
def normalize_url(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc or parsed_url.path  # Si no hay netloc, usa path
    if domain.startswith('www.'):
        domain = domain[4:]  # Eliminar 'www.' si está presente
    domain = domain.rstrip('/')  # Eliminar cualquier barra final '/'
    return domain

# Función para determinar si se debe usar la URL completa o solo el dominio
def get_url_or_domain(url, api_endpoint):
    if "check_ssl" in api_endpoint or "check_metadata" in api_endpoint:
        return url 
    else:
        return normalize_url(url)

# Función para llamar a las APIs
def call_api(url, api_endpoint):
    try:
        formatted_url = get_url_or_domain(url, api_endpoint)
        response = requests.post(api_endpoint, json={"url": formatted_url}, timeout=500)
        response.raise_for_status()  # Verifica si la respuesta es exitosa (status 200)
        response_data = response.json()
        return response_data.get("ESTADO", "fraud")  # Devuelve 'legal' o 'fraud'
    except requests.exceptions.Timeout:
        return "fraud"
    except requests.exceptions.RequestException as e:
        return "fraud"

# Función para obtener el vector de características
def get_feature_vector(url, connection):
    # Verificar si la URL o dominio está en la lista negra de la base de datos
    if is_url_or_domain_in_blacklist(url, connection):
        return np.array([0, 0, 0, 0, 0]).reshape(1, -1), 1.0000  # Características fraudulentas y probabilidad de 1.0
    
    apis = [
        "https://fraudlock-backend-production.up.railway.app/api/check_ssl",
        "https://fraudlock-backend-production.up.railway.app/api/check_url_similarity",
        "https://fraudlock-backend-production.up.railway.app/api/check_domain_security",
        "https://fraudlock-backend-production.up.railway.app/api/check_domain_popularity",
        "https://fraudlock-backend-production.up.railway.app/api/check_metadata"
    ]
    
    features = []
    for api in apis:
        status = call_api(url, api)
        features.append(1 if status == "legal" else 0)
    
    return np.array(features).reshape(1, -1), None

# Función para predecir la probabilidad de que una URL sea fraudulenta
def predict_url(url, connection):
    features, manual_prob = get_feature_vector(url, connection)
 
    if manual_prob is not None:
        return manual_prob
    else:
        prediction = model.predict(features)
        return prediction[0][0]
    
# Ruta de bienvenida para la URL base
@app.route('/', methods=['GET'])
def welcome():
    return "Bienvenido al back de FRAUDLOCK", 200

# Registrar las rutas de todas las APIs
@app.route('/api/check_ssl', methods=['POST'])
def check_ssl_route():
    return check_ssl()

@app.route('/api/check_url_similarity', methods=['POST'])
def check_url_similarity_route():
    return check_url_similarity()

@app.route('/api/check_domain_security', methods=['POST'])
def check_domain_security_route():
    return check_domain_security()

@app.route('/api/check_domain_popularity', methods=['POST'])
def check_domain_popularity_route():
    return check_domain_popularity()

@app.route('/api/check_metadata', methods=['POST'])
def check_metadata_route():
    return check_metadata()

# Ruta para la predicción de URLs
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    url = data.get('url')
    
    if not url or url == "":
        return jsonify({"error": "No URL provided"}), 400

    # Iniciar el contador de tiempo
    start_time = datetime.now()
    
    # Crear conexión a la base de datos
    connection = get_db_connection()
    
    # Realizar la predicción
    result = predict_url(url, connection)
    
    # Terminar el contador de tiempo
    end_time = datetime.now()
    time_taken = (end_time - start_time).total_seconds()
    time_taken = round(time_taken, 3)

    features, _ = get_feature_vector(url, connection)
    features_list = features.flatten().tolist()  # Convertir a lista simple para JSON

    # Guardar en la base de datos usando report_manager
    report_manager = ReportManager(connection)
    report_manager.save_report(result, time_taken)
    
    connection.close()

    return jsonify({"probability": float(result), "features": features_list}), 200

# Ejecutar la aplicación Flask
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
