# model_loader.py
import joblib
from sklearn.tree import DecisionTreeClassifier
import pandas as pd
import os

from config import MODEL_DIR, MODEL_PATH, ENCODER_PATH

MODEL_FULLPATH = os.path.join(MODEL_DIR, MODEL_PATH)
ENCODER_FULLPATH = os.path.join(MODEL_DIR, ENCODER_PATH)

model: DecisionTreeClassifier = None
encoder = None

def load_model():
    global model, encoder
    model = joblib.load(MODEL_FULLPATH)
    encoder = joblib.load(ENCODER_FULLPATH)
    print("✅ Modelo cargado correctamente.")

def predict_from_dict(data: dict):
    if model is None:
        load_model()

    features = [
        'consumo_7d', 'consumo_30d', 'promedio_12m',
        'dias_desde_ultima_entrega', 'stock_actual',
        'stock_capacidad', 'solicitudes_pendientes',
        'proyeccion_72h', 'indicador_riesgo'
    ]
    df = pd.DataFrame([data], columns=features)
    pred = model.predict(df)[0]
    probs = model.predict_proba(df)[0]
    etiqueta = encoder.inverse_transform([pred])[0]
    confidence = round(float(max(probs)), 2)

    return {
        "prediction": etiqueta,
        "confidence": confidence,
        "probabilities": dict(zip(encoder.classes_, probs.round(3)))
    }
