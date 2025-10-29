from flask import Flask
import logging
import os
from config import Config
from routes.teller_routes import teller_bp
import google.generativeai as genai

# Logging config
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(LOG_DIR, "app.log"), encoding="utf-8"),
    ],
)

# Initialize Flask
app = Flask(__name__)
app.config.from_object(Config)

# Initialize Gemma
genai.configure(api_key=Config.GEMMA_API_KEY)

# Register Blueprints
app.register_blueprint(teller_bp, url_prefix='/api')

if __name__ == "__main__":
    logging.info(f"Starting Flask app on port {Config.PORT}")
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)
