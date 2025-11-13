-- V1.0
-- CREATE TABLE IF NOT EXISTS features_parroquia_daily (
--     id BIGINT AUTO_INCREMENT PRIMARY KEY,
--     parroquia_id INT NOT NULL,
--     fecha DATE NOT NULL,

--     -- Variables de consumo
--     consumo_7d DECIMAL(10,2) DEFAULT NULL,
--     consumo_30d DECIMAL(10,2) DEFAULT NULL,
--     promedio_12m DECIMAL(10,2) DEFAULT NULL,

--     -- Variables operativas
--     dias_desde_ultima_entrega INT DEFAULT NULL,
--     stock_actual DECIMAL(10,2) DEFAULT NULL,
--     stock_minimo DECIMAL(10,2) DEFAULT NULL,
--     entregas_pendientes INT DEFAULT NULL,

--     -- Indicadores derivados
--     proyeccion_72h DECIMAL(10,2) DEFAULT NULL,
--     indicador_riesgo DECIMAL(5,2) DEFAULT NULL,
--     calidad_datos VARCHAR(20) DEFAULT 'OK',

--     -- Metadatos
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

--     CONSTRAINT uq_features UNIQUE (fecha, parroquia_id)
-- );
-- V2.0
CREATE TABLE IF NOT EXISTS features_parroquia_daily (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    parroquia INT NOT NULL,
    fecha DATE NOT NULL,

    consumo_7d DECIMAL(10,2) DEFAULT NULL,
    consumo_30d DECIMAL(10,2) DEFAULT NULL,
    promedio_12m DECIMAL(10,2) DEFAULT NULL,

    dias_desde_ultima_entrega INT DEFAULT NULL,
    stock_actual DECIMAL(10,2) DEFAULT NULL,
    stock_capacidad DECIMAL(10,2) DEFAULT NULL,
    solicitudes_pendientes INT DEFAULT NULL,

    proyeccion_72h DECIMAL(10,2) DEFAULT NULL,
    indicador_riesgo DECIMAL(5,2) DEFAULT NULL,
    calidad_datos VARCHAR(20) DEFAULT 'OK',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_features UNIQUE (fecha, parroquia)
);
