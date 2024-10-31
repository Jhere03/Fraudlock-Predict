import os
import asyncio
import aiohttp
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from conect_bd import get_db_connection
from report_manager import ReportManager
from urllib.parse import urlparse
import tensorflow as tf

app = Flask(__name__)
CORS(app)

# Cargar el modelo entrenado solo una vez
model = tf.keras.models.load_model('modelo_fraude_v2.h5')

# Función para verificar si la URL o dominio está en la lista negra
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

# Función para determinar si se debe usar la URL completa o solo el dominio
def get_url_or_domain(url, api_endpoint):
    if "check_ssl" in api_endpoint or "check_metadata" in api_endpoint:
        return url
    else:
        return urlparse(url).netloc

# Función asíncrona para llamar a las APIs de forma paralela
async def call_api_async(session, url, api_endpoint):
    try:
        formatted_url = get_url_or_domain(url, api_endpoint)
        async with session.post(api_endpoint, json={"url": formatted_url}, timeout=60) as response:
            response_data = await response.json()
            # Convertir el estado devuelto a 0 (fraud) o 1 (legal)
            return 1 if response_data.get("ESTADO") == "legal" else 0
    except asyncio.TimeoutError:
        return 0  # Asumir "fraud" en caso de timeout
    except Exception as e:
        print(f"Error al llamar a {api_endpoint}: {str(e)}")
        return 0  # Asumir "fraud" en caso de error

# Función asíncrona para obtener el vector de características
async def get_feature_vector_async(url):
    apis = [
        "https://web-production-4432.up.railway.app/api/check_ssl",
        "https://web-production-4432.up.railway.app/api/check_url_similarity",
        "https://web-production-4432.up.railway.app/api/check_domain_security",
        "https://web-production-4432.up.railway.app/api/check_domain_popularity",
        "https://web-production-4432.up.railway.app/api/check_metadata"
    ]

    async with aiohttp.ClientSession() as session:
        tasks = [call_api_async(session, url, api) for api in apis]
        results = await asyncio.gather(*tasks)

    return np.array(results).reshape(1, -1)

# Función para realizar la predicción usando el modelo de TensorFlow
def predict_url(url):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    features = loop.run_until_complete(get_feature_vector_async(url))
    prediction = model.predict(features)
    return prediction[0][0]

# Ruta principal para la página de inicio
@app.route('/')
def home():
    return "Bienvenido a Fraudlock Prediction API. Usa /predict con un método POST para predecir."

# Ruta para la predicción de URLs
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    # Iniciar el contador de tiempo
    start_time = datetime.now()

    # Conectar a la base de datos
    connection = get_db_connection()

    # Verificar si la URL está en la lista negra
    if is_url_or_domain_in_blacklist(url, connection):
        result = 1.0  # Si está en la lista negra, marcarlo como fraude con probabilidad 1.0
        features = np.array([0, 0, 0, 0, 0]).reshape(1, -1)
    else:
        # Si no está en la lista negra, hacer la predicción
        result = predict_url(url)
        features = asyncio.run(get_feature_vector_async(url))

    # Calcular el tiempo de ejecución
    end_time = datetime.now()
    time_taken = round((end_time - start_time).total_seconds(), 3)

    # Convertir los resultados a listas simples para JSON
    features_list = features.flatten().tolist()

    # Guardar en la base de datos usando report_manager
    report_manager = ReportManager(connection)
    report_manager.save_report(result, time_taken)

    # Cerrar la conexión a la base de datos
    connection.close()

    return jsonify({"probability": float(result), "features": features_list, "time_taken": time_taken}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

