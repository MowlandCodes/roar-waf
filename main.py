import os

import requests
from dotenv import load_dotenv
from flask import Flask, Response, request

from libs import db
from libs.helper import inspect_head_and_tail
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

with app.app_context():
    # Create all databases if it doesn't exist
    db.create_all()


@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PATCH", "PUT", "DELETE"])
@app.route("/<path>", methods=["GET", "POST", "PATCH", "PUT", "DELETE"])
def inspect_traffic(path):
    hostname = request.headers.get("Host", "unknown")

    target_app: str | None = App.query.filter_by(domain_name=hostname, is_active=True).first()

    if not target_app:
        logger.error(f"App {hostname} not found")
    
        return Response(f"ROAR-WAF: Domain not found {hostname}", status=404)

    active_rules = Rule.query.filter_by(is_active=True).all()

    try:
        upstream_response = requests.request(
            method=request.method,
            url=f"{target_app.upstream_url}/{path}",
            headers={k: v for k,v in request.headers.items() if k != "Host"},
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
            return Response(f"Connection blocked by Security Policy", status=403)

        return Response(f"Upstream Error", status=502)
