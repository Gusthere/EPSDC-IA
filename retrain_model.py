# retrain_model.py
import pandas as pd
from sqlalchemy import create_engine, text
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, f1_score
import joblib
import os
from datetime import datetime
from config import DB_URI, MODEL_DIR, MODEL_PATH, ENCODER_PATH
import json
import shutil
import os

def retrain_model():
    print("🚀 Iniciando reentrenamiento del modelo CART...")

    engine = create_engine(DB_URI)
    df = pd.read_sql("SELECT * FROM dataset_entrenamiento", engine)

    # --- Preparación de datos ---
    # aceptar tanto 'etiqueta' como 'clase' como nombre de columna objetivo
    if 'etiqueta' in df.columns:
        target_col = 'etiqueta'
    elif 'clase' in df.columns:
        target_col = 'clase'
    else:
        raise RuntimeError("Columna objetivo no encontrada (esperada 'etiqueta' o 'clase').")

    X = df.drop(columns=[target_col])
    y = df[target_col]

    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42
    )

    # --- Entrenamiento ---
    model = DecisionTreeClassifier(
        criterion="gini",
        max_depth=6,
        class_weight="balanced",
        random_state=42
    )
    model.fit(X_train, y_train)

    # --- Evaluación ---
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")

    # --- Guardar nueva versión ---
    version_name = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    model_path = f"modelo_cart_{version_name}.joblib"
    encoder_path = f"encoder_etiquetas_{version_name}.joblib"

    joblib.dump(model, model_path)
    joblib.dump(encoder, encoder_path)

    # Copiar los artefactos versionados a la ruta 'activa' configurada
    try:
        active_model_path = os.path.join(MODEL_DIR, MODEL_PATH)
        active_encoder_path = os.path.join(MODEL_DIR, ENCODER_PATH)
        shutil.copyfile(model_path, active_model_path)
        shutil.copyfile(encoder_path, active_encoder_path)
    except Exception as e:
        print(f"⚠️ No se pudo copiar artefactos a ruta activa: {e}")

    # --- Registrar en base de datos ---
    # Insertar metadatos de la nueva versión en la BD usando parámetros nombrados
    with engine.begin() as conn:
        insert_sql = text("""
            INSERT INTO ai_model_versions
            (version_name, fecha_entrenamiento, accuracy, f1, clases, dataset_size, ruta_modelo, comentario)
            VALUES (:version_name, :fecha_entrenamiento, :accuracy, :f1, :clases, :dataset_size, :ruta_modelo, :comentario)
        """)
        conn.execute(insert_sql, {
            'version_name': version_name,
            'fecha_entrenamiento': datetime.now(),
            'accuracy': acc,
            'f1': f1,
            'clases': json.dumps(list(encoder.classes_)),
            'dataset_size': len(df),
            'ruta_modelo': model_path,
            'comentario': 'Reentrenamiento automático'
        })

    summary = {
        "version": version_name,
        "accuracy": acc,
        "f1": f1,
        "dataset_size": len(df)
    }

    print(f"✅ Reentrenamiento completado ({version_name})")
    print(f"Accuracy: {acc:.4f} | F1: {f1:.4f}")
    # Imprimir JSON con resumen para que scripts llamantes lo consuman
    print(json.dumps(summary))
    return summary

if __name__ == "__main__":
    retrain_model()
