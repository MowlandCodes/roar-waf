import os

from dotenv import load_dotenv
from flask import Flask

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv("APP_SECRET_KEY", "")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
