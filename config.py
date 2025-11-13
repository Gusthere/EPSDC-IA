# config.py
from dotenv import load_dotenv
import os

# Cargar variables desde .env
load_dotenv()

# --- BASE DE DATOS ---
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "epsdc_principal")

DB_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# --- JWT ---
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# --- LOGS ---
LOG_FILE = os.getenv("LOG_FILE", "ia_audit.log")
