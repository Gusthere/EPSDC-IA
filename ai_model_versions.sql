CREATE TABLE ai_model_versions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    version_name VARCHAR(50),
    fecha_entrenamiento DATETIME,
    accuracy DECIMAL(5,4),
    f1 DECIMAL(5,4),
    clases JSON,
    dataset_size INT,
    ruta_modelo VARCHAR(200),
    comentario VARCHAR(255)
);
