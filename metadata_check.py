from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import argparse
import os


app = Flask(__name__)

def extract_domain(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc or parsed_url.path  # netloc para URLs con protocolo, path para las que no tienen
    if domain.startswith("www."):
        domain = domain[4:]  # Remover 'www.' si está presente
    
    # Si el dominio aún tiene un '/' al final, removerlo
    domain = domain.rstrip('/')
    
    return domain

def fetch_metadata(domain):
    try:
        if not domain:  # Verifica si el dominio está vacío
            raise ValueError("Invalid domain")

        # Intentar primero con HTTPS
        url = f"https://{domain}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()  # Lanza una excepción si el estado HTTP es 4xx/5xx
        
        # Si HTTPS falla, intenta con HTTP
        if response.status_code != 200:
            url = f"http://{domain}"
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        description = soup.find('meta', attrs={'name': 'description'})
        keywords = soup.find('meta', attrs={'name': 'keywords'})
        title = soup.title.string if soup.title else "No title found"

        metadata = {
            'description': description['content'] if description else "No description found",
            'keywords': keywords['content'] if keywords else "No keywords found",
            'title': title,
            'url': domain
        }

        return metadata, "Valid"

    except requests.exceptions.Timeout:
        print(f"Timeout for domain {domain}: Assuming fraud")
        return {
            'description': "No description found",
            'keywords': "No keywords found",
            'title': "Request timed out",
            'url': domain
        }, "Invalid"

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print(f"Access forbidden for domain {domain}: Assuming fraud")
            return {
                'description': "No description found",
                'keywords': "No keywords found",
                'title': "Access forbidden",
                'url': domain
            }, "Invalid"
        else:
            print(f"HTTP error occurred: {e} for domain {domain}")
            return {
                'description': "No description found",
                'keywords': "No keywords found",
                'title': "HTTP error occurred",
                'url': domain
            }, "Invalid"

    except Exception as e:
        print(f"Unhandled exception: {e} for domain {domain}")
        return {
            'description': "No description found",
            'keywords': "No keywords found",
            'title': "Unhandled exception occurred",
            'url': domain
        }, "Invalid"

@app.route('/api/check_metadata', methods=['POST'])
def check_metadata():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    domain = extract_domain(url)
    metadata, status = fetch_metadata(domain)
    
    response = {
        "metadata": metadata,
        "status": status,
        "ESTADO": "legal" if status == "Valid" else "fraud"
    }
    
    return jsonify(response)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Usa el puerto asignado por el entorno
    app.run(debug=True, host='0.0.0.0', port=port)  # Asegúrate de escuchar en todas las interfaces

