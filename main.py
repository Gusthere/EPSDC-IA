# main.py
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from auth import verificar_jwt
from model_loader import load_model, predict_from_dict
import logging
from datetime import datetime
import subprocess
import json
from sqlalchemy import create_engine, text
from config import DB_URI
import os

from config import LOG_FILE

app = FastAPI(title="IA EPSDC - Servicio de Inferencia")

# Configuración de log
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")

# Cargar modelo al iniciar
@app.on_event("startup")
def startup_event():
    load_model()

# --- MODELOS DE DATOS ---
class FeaturesInput(BaseModel):
    consumo_7d: float
    consumo_30d: float
    promedio_12m: float
    dias_desde_ultima_entrega: int
    stock_actual: float
    stock_capacidad: float
    solicitudes_pendientes: int
    proyeccion_72h: float
    indicador_riesgo: float

# --- ENDPOINTS ---
@app.get("/api/v1/status")
def status(user=Depends(verificar_jwt)):
    return {"status": "ok", "message": "IA operativa", "user": user.get("username")}

@app.post("/api/v1/recommendations")
def predict(data: FeaturesInput, user=Depends(verificar_jwt)):
    try:
        result = predict_from_dict(data.dict())
        # Registrar en bitácora
        logging.info(f"Usuario:{user.get('username','?')} "
                     f"Predicción:{result.get('prediction')} "
                     f"Confianza:{result.get('confidence')}")

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "model_version": "cart_v1",
            "prediction": result["prediction"],
            "confidence": result["confidence"],
            "probabilities": result["probabilities"]
        }
    except Exception as e:
        # Log the full exception for debugging and return the message in the response
        logging.exception("Error en /api/v1/recommendations")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/retrain")
def retrain(user=Depends(verificar_jwt)):
    # Por ahora, desactivamos validación de rol (ya que no usas Laravel)
    try:
        result = subprocess.run(
            ["python", "retrain_model.py"],
            capture_output=True, text=True, check=True
        )

        # Extraer resumen del JSON (si el script lo devuelve)
        print(result.stdout)
        return {"status": "ok", "message": "Reentrenamiento completado", "output": result.stdout}

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error al reentrenar: {e.stderr}")

@app.get("/api/v1/metrics")
def get_metrics(user=Depends(verificar_jwt)):
    """
    Devuelve información de la versión actual del modelo,
    sus métricas y estado general.
    """
    try:
        engine = create_engine(DB_URI)
        with engine.connect() as conn:
            # Obtener última versión registrada
            result = conn.execute(text("""
                SELECT version_name, fecha_entrenamiento, accuracy, f1,
                       dataset_size, comentario
                FROM ai_model_versions
                ORDER BY fecha_entrenamiento DESC
                LIMIT 1
            """)).fetchone()

        if result:
            return {
                "version": result.version_name,
                "fecha_entrenamiento": str(result.fecha_entrenamiento),
                "accuracy": float(result.accuracy),
                "f1_score": float(result.f1),
                "dataset_size": int(result.dataset_size),
                "comentario": result.comentario,
                "modelo_existe": os.path.exists(f"modelo_cart_{result.version_name}.joblib")
            }
        else:
            return {"status": "empty", "message": "No hay modelos registrados aún."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener métricas: {e}")

@app.get("/api/v1/metrics/history")
def get_metrics_history(user=Depends(verificar_jwt)):
    engine = create_engine(DB_URI)
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT version_name, fecha_entrenamiento, accuracy, f1, dataset_size
            FROM ai_model_versions
            ORDER BY fecha_entrenamiento DESC
        """)).mappings().all()
    return {"history": list(result)}

