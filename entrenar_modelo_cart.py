# V1.0

# entrenar_modelo_cart.py
import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import os
from config import MODEL_DIR, MODEL_PATH, ENCODER_PATH

# --- 1. Conexión y carga del dataset ---
from config import DB_URI

engine = create_engine(DB_URI)
df = pd.read_sql("SELECT * FROM dataset_entrenamiento", engine)

print("Datos cargados:", df.shape)
print(df.head())

# --- 2. Preparar variables ---
features = [
    'consumo_7d', 'consumo_30d', 'promedio_12m',
    'dias_desde_ultima_entrega', 'stock_actual',
    'stock_minimo', 'entregas_pendientes',
    'proyeccion_72h', 'indicador_riesgo'
]

X = df[features]
y = df['etiqueta']

# Codificar etiquetas (multiclase)
encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)
print("Clases:", dict(zip(encoder.classes_, encoder.transform(encoder.classes_))))

# --- 3. División de datos ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.25, random_state=42, stratify=y_encoded
)

# --- 4. Entrenar modelo CART ---
model = DecisionTreeClassifier(
    criterion='gini',
    max_depth=6,
    min_samples_split=4,
    class_weight='balanced',
    random_state=42
)
# Simple missing value handling
X_train = X_train.fillna(0)
X_test = X_test.fillna(0)

model.fit(X_train, y_train)

# --- 5. Evaluar modelo ---
y_pred = model.predict(X_test)
print("\nMATRIZ DE CONFUSIÓN:")
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d',
            xticklabels=encoder.classes_,
            yticklabels=encoder.classes_)
plt.xlabel("Predicción")
plt.ylabel("Real")
plt.savefig('confusion_matrix.png', bbox_inches='tight')
print('Matriz de confusión guardada en confusion_matrix.png')

print("\nREPORTE DE CLASIFICACIÓN:")
print(classification_report(y_test, y_pred, target_names=encoder.classes_))

# --- 6. Guardar modelo y metadatos ---
joblib.dump(model, os.path.join(MODEL_DIR, MODEL_PATH))
joblib.dump(encoder, os.path.join(MODEL_DIR, ENCODER_PATH))
print("Modelo y codificador guardados.")

# Save textual report to a log file
try:
    with open('training.log', 'w', encoding='utf-8') as fh:
        fh.write('Reporte de clasificación:\n')
        fh.write(classification_report(y_test, y_pred, target_names=encoder.classes_))
        fh.write('\nMatriz de confusión:\n')
        fh.write(str(cm))
    print('Registro de entrenamiento guardado en training.log')
except Exception as e:
    print('No se pudo escribir training.log:', e)

# --- 7. Visualización opcional del árbol ---
plt.figure(figsize=(16,8))
plot_tree(model,
          feature_names=features,
          class_names=encoder.classes_,
          filled=True,
          rounded=True,
          fontsize=8)
plt.savefig('tree.png', bbox_inches='tight')
print('Visualización del árbol guardada en tree.png')

# --- 8. Importancia de variables ---
importances = pd.Series(model.feature_importances_, index=features)
importances.sort_values(ascending=False).plot(kind='barh', figsize=(8,5), title='Importancia de variables')
plt.savefig('importances.png', bbox_inches='tight')
print('Importancias de variables guardadas en importances.png')
print("Entrenamiento completado")