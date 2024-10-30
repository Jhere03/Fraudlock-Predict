from flask import Flask, request, jsonify
import ssl
import socket
from urllib.parse import urlparse
import argparse
import os


app = Flask(__name__)

class SiteValidator:
    def __init__(self, url):
        # Asegurarse de usar el dominio correcto, sin importar el protocolo
        self.url = urlparse(url).hostname

    def has_ssl_certificate(self):
        context = ssl.create_default_context()
        try:
            with socket.create_connection((self.url, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=self.url) as ssock:
                    cert = ssock.getpeercert()
                    return True if cert else False
        except Exception as e:
            # Si no se puede establecer una conexión SSL o la URL no es accesible, lo consideramos fraudulento
            return False

@app.route('/api/check_ssl', methods=['POST'])
def check_ssl():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    # Forzar siempre https:// en la verificación
    if not url.startswith("https://"):
        url = "https://" + url.lstrip("http://")

    validator = SiteValidator(url)
    has_ssl = validator.has_ssl_certificate()
    
    response = {
        'url': url,
        'has_ssl': has_ssl,
        'ESTADO': 'legal' if has_ssl else 'fraud'
    }
    
    return jsonify(response)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Usa el puerto asignado por el entorno
    app.run(debug=True, host='0.0.0.0', port=port)  # Asegúrate de escuchar en todas las interfaces

