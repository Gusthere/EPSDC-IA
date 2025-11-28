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
    print("Modelo cargado correctamente.")

def predict_from_dict(data: dict):
    if model is None:
        load_model()
    # Build feature vector matching what the model was trained with.
    # scikit-learn estimators created from pandas keep `feature_names_in_`.
    try:
        expected = list(model.feature_names_in_)
    except Exception:
        # Fallback to a sensible default if metadata isn't available
        expected = [
            'consumo_7d', 'consumo_30d', 'promedio_12m',
            'dias_desde_ultima_entrega', 'stock_actual',
            'stock_capacidad', 'solicitudes_pendientes',
            'proyeccion_72h', 'indicador_riesgo'
        ]

    # Common aliases mapping (UI/ETL differences)
    aliases = {
        'solicitudes_pendientes': 'entregas_pendientes',
        'entregas_pendientes': 'entregas_pendientes',
        'stock_capacidad': 'stock_minimo',
        'stock_minimo': 'stock_minimo',
        'parroquia': 'parroquia'
    }

    # build ordered dict of features matching expected names
    feature_values = {}
    for name in expected:
        # if the incoming data contains the expected name, use it
        if name in data:
            feature_values[name] = data[name]
            continue

        # else try to find an alias in incoming data
        found = False
        for incoming_key, mapped in aliases.items():
            if mapped == name and incoming_key in data:
                feature_values[name] = data[incoming_key]
                found = True
                break

        if found:
            continue

        # try the reverse: if an incoming key maps to some expected name
        for incoming_key in data.keys():
            if incoming_key in aliases and aliases[incoming_key] == name:
                feature_values[name] = data[incoming_key]
                found = True
                break

        if found:
            continue

        # As a last resort, if incoming data has similar names, try simple replacements
        if incoming_key := name.replace('entregas_pendientes', 'solicitudes_pendientes'):
            if incoming_key in data:
                feature_values[name] = data[incoming_key]
                continue

        # If nothing found, default to 0
        feature_values[name] = 0

    # create DataFrame with expected column order
    df = pd.DataFrame([feature_values], columns=expected)

    # ensure numeric types
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0)

    pred = model.predict(df)[0]
    probs = model.predict_proba(df)[0]
    etiqueta = encoder.inverse_transform([pred])[0]
    confidence = round(float(max(probs)), 2)

    return {
        "prediction": etiqueta,
        "confidence": confidence,
        "probabilities": dict(zip(encoder.classes_, probs.round(3)))
    }
