import logging
import re

import requests
from flask import Flask, Response, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ROAR-WAF")

BACKEND_URL = "http://backend-app:80"

RULES = [
    r"(?i)(union|select|insert|update|delete|drop|alter).*?",
    r"(?i)<script.*?>",
    r"(?i)(;|\||`|'|\$)" 
]

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', "PATCH", 'DELETE'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def proxy(path):
    body_payload = request.get_data(as_text=True) # Aman, karena Nginx udah push semua ke sini
    
    for rule in RULES:
        if re.search(rule, body_payload) or re.search(rule, request.url):
            logger.warning(f"!!! BLOCKED !!! IP: {request.remote_addr} | Payload: {body_payload}")
            return Response("Forbidden by ROAR-WAF", status=403)

    # 2. KALAU AMAN, TERUSIN KE BACKEND (Forwarding)
    logger.info(f"Forwarding to Backend: {path}")
    
    try:
        # Kirim request persis kayak yang user kirim (Method, Header, Body sama)
        resp = requests.request(
            method=request.method,
            url=f"{BACKEND_URL}/{path}",
            headers={key: value for (key, value) in request.headers if key != 'Host'},
            data=request.get_data(),
            params=request.args,
            allow_redirects=True
        )
        
        # 3. BALIKIN JAWABAN BACKEND KE USER
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]
        
        return Response(resp.content, resp.status_code, headers)
        
    except Exception as e:
        logger.error(f"Backend Error: {e}")
        return Response("Backend Down", status=502)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
