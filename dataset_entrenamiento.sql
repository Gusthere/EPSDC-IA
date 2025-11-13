-- V1.0

-- dataset_entrenamiento.sql
CREATE OR REPLACE VIEW dataset_entrenamiento AS
SELECT 
    f.parroquia,
    f.fecha,
    f.consumo_7d,
    f.consumo_30d,
    f.promedio_12m,
    f.dias_desde_ultima_entrega,
    f.stock_actual,
    f.stock_capacidad,
    f.solicitudes_pendientes,
    f.proyeccion_72h,
    f.indicador_riesgo,

    CASE
        WHEN f.stock_actual < (f.stock_capacidad * 0.25)
             AND f.solicitudes_pendientes > 0
             THEN 'riesgo'
        WHEN f.fecha IN (SELECT fecha_inicio FROM periodo)
             THEN 'abrir'
        WHEN f.fecha IN (SELECT fecha_fin FROM periodo)
             THEN 'cerrar'
        ELSE 'normal'
    END AS etiqueta

FROM features_parroquia_daily f;
