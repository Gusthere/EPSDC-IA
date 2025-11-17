-- V1.0

-- dataset_entrenamiento.sql
CREATE OR REPLACE VIEW dataset_entrenamiento AS
SELECT 
     f.parroquia_id AS parroquia,
     f.fecha,
    f.consumo_7d,
    f.consumo_30d,
    f.promedio_12m,
    f.dias_desde_ultima_entrega,
    f.stock_actual,
     f.stock_minimo,
     f.entregas_pendientes,
    f.proyeccion_72h,
    f.indicador_riesgo,

    CASE
        WHEN f.stock_actual < (COALESCE(f.stock_minimo, 0) * 0.25)
             AND f.entregas_pendientes > 0
             THEN 'riesgo'
        WHEN EXISTS (
             SELECT 1 FROM periodo p
             WHERE p.parroquia_id = f.parroquia_id
               AND p.fecha_inicio = f.fecha
        ) THEN 'abrir'
        WHEN EXISTS (
             SELECT 1 FROM periodo p
             WHERE p.parroquia_id = f.parroquia_id
               AND p.fecha_final = f.fecha
        ) THEN 'cerrar'
        ELSE 'normal'
    END AS etiqueta

FROM features_parroquia_daily f;
