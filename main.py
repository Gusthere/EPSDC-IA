# main.py
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from auth import verificar_jwt
from model_loader import load_model, predict_from_dict
import logging
from datetime import datetime

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
    result = predict_from_dict(data.dict())

    # Registrar en bitácora
    logging.info(f"Usuario:{user.get('username','?')} "
                 f"Predicción:{result['prediction']} "
                 f"Confianza:{result['confidence']}")

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "model_version": "cart_v1",
        "prediction": result["prediction"],
        "confidence": result["confidence"],
        "probabilities": result["probabilities"]
    }

@app.post("/api/v1/retrain")
def retrain(user=Depends(verificar_jwt)):
    # aquí puedes ejecutar tu script de reentrenamiento
    # por seguridad, solo permitir si el usuario tiene rol admin
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede reentrenar el modelo.")
    # ... ejecutar script de retrain (pendiente)
    logging.info(f"Reentrenamiento solicitado por {user.get('username')}")
    return {"status": "ok", "message": "Reentrenamiento en cola."}
