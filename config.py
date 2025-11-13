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

# --- RUTAS DE ARTEFACTOS ML ---
# Directorio donde se guardan los modelos (por defecto la raíz del proyecto)
MODEL_DIR = os.getenv("MODEL_DIR", "./")
# Nombre del archivo del modelo 'activo' (sin versión). El reentrenamiento puede generar archivos versionados
MODEL_PATH = os.getenv("MODEL_PATH", "modelo_cart.joblib")
# Nombre del archivo del codificador de etiquetas
ENCODER_PATH = os.getenv("ENCODER_PATH", "encoder_etiquetas.joblib")
