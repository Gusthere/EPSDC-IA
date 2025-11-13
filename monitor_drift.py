# monitor_drift.py
import pandas as pd
from sqlalchemy import create_engine
import joblib
from scipy.stats import ks_2samp
from config import DB_URI

THRESHOLD_DRIFT = 0.2  # Si más de 20% de las variables presentan drift → alerta

def check_drift():
    engine = create_engine(DB_URI)
    df_actual = pd.read_sql("SELECT * FROM dataset_entrenamiento", engine)
    import os
    prev_csv = "dataset_entrenamiento.csv"
    if not os.path.exists(prev_csv):
        print(f"⚠️ Archivo previo '{prev_csv}' no encontrado. Ejecuta dataset_entrenamiento.py para generarlo antes de monitorizar drift.")
        return

    df_prev = pd.read_csv(prev_csv)  # dataset previo guardado

    numeric_cols = df_actual.select_dtypes(include="number").columns
    drift_count = 0
    total = len(numeric_cols)

    for col in numeric_cols:
        stat, p_value = ks_2samp(df_prev[col], df_actual[col])
        if p_value < 0.05:  # diferencia significativa
            drift_count += 1

    ratio = drift_count / total
    print(f"Variables con drift: {drift_count}/{total} ({ratio:.1%})")

    if ratio > THRESHOLD_DRIFT:
        print("⚠️ ALERTA: Posible drift detectado, considera reentrenar.")
    else:
        print("✅ Sin drift significativo.")

if __name__ == "__main__":
    check_drift()
