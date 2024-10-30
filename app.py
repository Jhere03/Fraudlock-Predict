from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tensorflow as tf
import numpy as np
from ssl_check import check_ssl
from url_similarity import check_url_similarity
from domain_security import check_domain_security
from populary_domain import check_domain_popularity
from metadata_check import check_metadata
from conect_bd import get_db_connection
from report_manager import ReportManager
from urllib.parse import urlparse
from datetime import datetime
import requests

app = Flask(__name__)
CORS(app)

# Probar conexión a la base de datos
connection = get_db_connection()
if connection:
    print("Conexión a la base de datos exitosa")
    connection.close()  # Cierra la conexión después de la prueba
else:
    print("Error al conectar a la base de datos")

# Cargar el modelo entrenado
model = tf.keras.models.load_model('modelo_fraude_v2.h5')
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

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

# Funciones para el módulo de predicción
def is_url_or_domain_in_blacklist(url, connection):
    cursor = connection.cursor()
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    if domain.startswith('www.'):
        domain = domain[4:]
    query = "SELECT EXISTS(SELECT 1 FROM blacklist WHERE url = %s OR url = %s)"
    cursor.execute(query, (domain, url))
    result = cursor.fetchone()
    cursor.close()
    return result[0] == 1

def get_url_or_domain(url, api_endpoint):
    if "check_ssl" in api_endpoint or "check_metadata" in api_endpoint:
        return url 
    else:
        return urlparse(url).netloc

def call_api(url, api_endpoint):
    try:
        formatted_url = get_url_or_domain(url, api_endpoint)
        response = requests.post(api_endpoint, json={"url": formatted_url}, timeout=15)
        response.raise_for_status()
        response_data = response.json()
        return response_data.get("ESTADO", "fraud")
    except:
        return "fraud"

def get_feature_vector(url, connection):
    if is_url_or_domain_in_blacklist(url, connection):
        return np.array([0, 0, 0, 0, 0]).reshape(1, -1), 1.0
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

def predict_url(url, connection):
    features, manual_prob = get_feature_vector(url, connection)
    if manual_prob is not None:
        return manual_prob
    else:
        prediction = model.predict(features)
        return prediction[0][0]

# Ruta principal para la página de inicio
@app.route('/')
def home():
    return "Bienvenido a Fraudlock Backend API. Para predecir una URL, usa /predict con un método POST."

# Ruta para la predicción de URLs
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    start_time = datetime.now()
    connection = get_db_connection()
    result = predict_url(url, connection)
    end_time = datetime.now()
    time_taken = round((end_time - start_time).total_seconds(), 3)
    features, _ = get_feature_vector(url, connection)
    features_list = features.flatten().tolist()
    report_manager = ReportManager(connection)
    report_manager.save_report(result, time_taken)
    connection.close()
    return jsonify({"probability": float(result), "features": features_list}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
