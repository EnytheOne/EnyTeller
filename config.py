import os
from dotenv import load_dotenv

# Load the .env file in project root
load_dotenv()

class Config:
    DEBUG = os.getenv("DEBUG", True)
    PORT = int(os.getenv("PORT", 5000))

    # Database
    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")

    # Gemma API
    GEMMA_API_KEY = os.getenv("GEMMA_API_KEY")

    # Input validation & security
    MAX_QUESTION_LENGTH = int(os.getenv("MAX_QUESTION_LENGTH", 1024))
    MAX_CUSTOMER_INFO_LENGTH = int(os.getenv("MAX_CUSTOMER_INFO_LENGTH", 512))
    MAX_PDF_SIZE_MB = float(os.getenv("MAX_PDF_SIZE_MB", 5))
    ALLOWED_PDF_DIRECTORY = os.getenv("ALLOWED_PDF_DIRECTORY", "assets/pdfs")
    ALLOWED_LANGUAGES = [lang.strip() for lang in os.getenv("ALLOWED_LANGUAGES", "").split(",") if lang.strip()]

    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", 60))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", 60))

    MAX_MEMORY_ENTRIES = int(os.getenv("MAX_MEMORY_ENTRIES", 500))
