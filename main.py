import os
import uuid

import requests
from dotenv import load_dotenv
from flask import Flask, Response, render_template, request

from libs import db
from libs.helper import inspect_head_and_tail, inspect_url
from libs.logger import logger
from models import App, Rule

load_dotenv()

app = Flask(__name__)

db_url = os.getenv("DATABASE_URL", "sqlite:///roar-waf.db") # Fallback to SQLite if DATABASE_URL is not set

if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
db.init_app(app)

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_details=str(e)), 500

@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PATCH", "PUT", "DELETE"])
@app.route("/<path:path>", methods=["GET", "POST", "PATCH", "PUT", "DELETE"])
def inspect_traffic(path):
    hostname = request.headers.get("Host", "unknown")

    target_app: str | None = App.query.filter_by(domain_name=hostname, is_active=True).first()

    if not target_app:
        logger.error(f"App {hostname} not found")
    
        return Response(f"ROAR-WAF: Domain not found {hostname}", status=404)

    active_rules = Rule.query.filter_by(is_active=True).all()

    try:
        # Check if the url contains any of the active rules
        inspect_url(request.url, active_rules, hostname, request.remote_addr)


        excluded_proxy_headers = ["host", "content-length"]
        proxy_headers = {
            k: v for k,v in request.headers.items()
            if k.lower() not in excluded_proxy_headers
        }

        upstream_response = requests.request(
            method=request.method,
            url=f"{target_app.upstream_url}/{path}",
            headers=proxy_headers,
            data=inspect_head_and_tail(request.stream, active_rules, hostname, remote_addr=request.remote_addr),
            params=request.args.to_dict(),
            stream=True,
            allow_redirects=False
        )

        excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]

        # Catch all response headers except for the excluded headers
        headers = [(name, value) for (name, value) in upstream_response.raw.headers.items() if name.lower() not in excluded_headers]


        return Response(
            upstream_response.iter_content(chunk_size=4096), # Send the response in chunks of 4kb to avoid memory issues
            status=upstream_response.status_code,
            headers=headers
        )

    except Exception as e:
        if "BLOCKED" in str(e):
            req_id = str(uuid.uuid4()).split('-')[0].upper()
            
            reason = str(e).replace("BLOCKED :", "").replace("rule triggered", "").strip()

            return render_template(
                '403.html', 
                client_ip=request.remote_addr,
                request_id=req_id,
                reason=reason
            ), 403

        logger.error(f"Error inspecting traffic: {str(e)}")
        return render_template('error.html', error_details=f"Upstream error: {str(e)}"), 502
