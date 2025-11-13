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

# --- 1. Conexión y carga del dataset ---
DB_URI = "mysql+pymysql://root:tu_contraseña@localhost/epsdc_principal"
engine = create_engine(DB_URI)
df = pd.read_sql("SELECT * FROM dataset_entrenamiento", engine)

print("✅ Datos cargados:", df.shape)
print(df.head())

# --- 2. Preparar variables ---
features = [
    'consumo_7d', 'consumo_30d', 'promedio_12m',
    'dias_desde_ultima_entrega', 'stock_actual',
    'stock_capacidad', 'solicitudes_pendientes',
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
model.fit(X_train, y_train)

# --- 5. Evaluar modelo ---
y_pred = model.predict(X_test)
print("\n📊 MATRIZ DE CONFUSIÓN:")
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d',
            xticklabels=encoder.classes_,
            yticklabels=encoder.classes_)
plt.xlabel("Predicción")
plt.ylabel("Real")
plt.show()

print("\n📈 REPORTE DE CLASIFICACIÓN:")
print(classification_report(y_test, y_pred, target_names=encoder.classes_))

# --- 6. Guardar modelo y metadatos ---
joblib.dump(model, "modelo_cart.joblib")
joblib.dump(encoder, "encoder_etiquetas.joblib")
print("💾 Modelo y codificador guardados.")

# --- 7. Visualización opcional del árbol ---
plt.figure(figsize=(16,8))
plot_tree(model,
          feature_names=features,
          class_names=encoder.classes_,
          filled=True,
          rounded=True,
          fontsize=8)
plt.show()

# --- 8. Importancia de variables ---
importances = pd.Series(model.feature_importances_, index=features)
importances.sort_values(ascending=False).plot(kind='barh', figsize=(8,5), title='Importancia de variables')
plt.show()
print("✅ Entrenamiento completado")