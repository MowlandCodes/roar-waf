import logging
import re

from flask import Flask, Response, request

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ROAR-WAF")

RULES = [
    r"(?i)(union|select|insert|update|delete|drop|alter).*?",
    r"(?i)<script.*?>",
    r"\.\./",
    r"(?i)(;|\||`|\$)" 
]

@app.route('/inspect', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def inspect():
    original_uri = request.headers.get('X-Original-URI', '')
    original_method = request.headers.get('X-Original-Method', '')
    client_ip = request.headers.get('X-Real-IP', 'Unknown')
    
    payload = request.get_data(as_text=True) 

    logger.info(f"Inspecting Request: {original_method} {original_uri} from {client_ip}")

    data_to_check = f"{original_uri} {payload}"

    for rule in RULES:
        if re.search(rule, data_to_check):
            logger.warning(f"!!! ATTACK BLOCKED !!! IP: {client_ip} | Pattern: {rule}")
            return Response("Blocked", status=403)

    return Response("OK", status=200)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
