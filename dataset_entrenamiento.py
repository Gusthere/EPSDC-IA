# V1.0

# dataset_entrenamiento.py
import pandas as pd
from sqlalchemy import create_engine

from config import DB_URI

def cargar_dataset():
    engine = create_engine(DB_URI)
    query = "SELECT * FROM dataset_entrenamiento"
    df = pd.read_sql(query, engine)
    return df

if __name__ == "__main__":
    df = cargar_dataset()
    print(df.head())

    # Conteo de clases
    print("\nDistribución de etiquetas:")
    print(df['etiqueta'].value_counts())

    # Limpieza básica (opcional)
    df = df.dropna(subset=[
        'consumo_7d','consumo_30d','promedio_12m',
        'stock_actual','stock_minimo'
    ])

    # Guardar CSV para entrenamiento
    df.to_csv("dataset_entrenamiento.csv", index=False)
    print("✅ Dataset exportado a dataset_entrenamiento.csv")
