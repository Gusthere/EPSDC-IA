CREATE TABLE ai_audit_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(100),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accion VARCHAR(50),
    input JSON,
    output JSON,
    confianza DECIMAL(5,2)
);
