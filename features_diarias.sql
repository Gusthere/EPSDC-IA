-- V1.0
-- -- features_diarias.sql
-- INSERT INTO features_parroquia_daily (
--     parroquia_id,
--     fecha,
--     consumo_7d,
--     consumo_30d,
--     promedio_12m,
--     dias_desde_ultima_entrega,
--     stock_actual,
--     stock_minimo,
--     entregas_pendientes,
--     proyeccion_72h,
--     indicador_riesgo,
--     calidad_datos
-- )
-- SELECT 
--     p.id AS parroquia_id,
--     CURDATE() AS fecha,

--     -- Total entregado últimos 7 días
--     COALESCE((
--         SELECT SUM(e.cantidad_entregada)
--         FROM entrega e
--         WHERE e.parroquia_id = p.id
--           AND e.fecha_entrega BETWEEN CURDATE() - INTERVAL 7 DAY AND CURDATE()
--     ), 0) AS consumo_7d,

--     -- Total entregado últimos 30 días
--     COALESCE((
--         SELECT SUM(e.cantidad_entregada)
--         FROM entrega e
--         WHERE e.parroquia_id = p.id
--           AND e.fecha_entrega BETWEEN CURDATE() - INTERVAL 30 DAY AND CURDATE()
--     ), 0) AS consumo_30d,

--     -- Promedio mensual de los últimos 12 meses
--     COALESCE((
--         SELECT SUM(e.cantidad_entregada) / 12
--         FROM entrega e
--         WHERE e.parroquia_id = p.id
--           AND e.fecha_entrega BETWEEN CURDATE() - INTERVAL 12 MONTH AND CURDATE()
--     ), 0) AS promedio_12m,

--     -- Días desde la última entrega
--     DATEDIFF(
--         CURDATE(),
--         COALESCE(
--             (SELECT MAX(e.fecha_entrega)
--              FROM entrega e
--              WHERE e.parroquia_id = p.id),
--             CURDATE()
--         )
--     ) AS dias_desde_ultima_entrega,

--     -- Stock actual y mínimo
--     COALESCE(a.stock_actual, 0) AS stock_actual,
--     COALESCE(a.stock_minimo, 0) AS stock_minimo,

--     -- Solicitudes pendientes
--     (
--         SELECT COUNT(*)
--         FROM solicitud s
--         WHERE s.parroquia_id = p.id
--           AND s.estado IN ('pendiente', 'en_proceso')
--     ) AS entregas_pendientes,

--     -- Proyección simple de consumo a 3 días
--     ROUND(
--         (COALESCE((
--             SELECT SUM(e.cantidad_entregada)
--             FROM entrega e
--             WHERE e.parroquia_id = p.id
--               AND e.fecha_entrega BETWEEN CURDATE() - INTERVAL 7 DAY AND CURDATE()
--         ), 0) / 7) * 3,
--         2
--     ) AS proyeccion_72h,

--     -- Indicador de riesgo: stock / consumo semanal
--     CASE 
--         WHEN COALESCE((
--             SELECT SUM(e.cantidad_entregada)
--             FROM entrega e
--             WHERE e.parroquia_id = p.id
--               AND e.fecha_entrega BETWEEN CURDATE() - INTERVAL 7 DAY AND CURDATE()
--         ), 0) = 0 THEN 0
--         ELSE ROUND(
--             a.stock_actual / (
--                 COALESCE((
--                     SELECT SUM(e.cantidad_entregada)
--                     FROM entrega e
--                     WHERE e.parroquia_id = p.id
--                       AND e.fecha_entrega BETWEEN CURDATE() - INTERVAL 7 DAY AND CURDATE()
--                 ), 1)
--             ), 2)
--     END AS indicador_riesgo,

--     -- Calidad de datos básica
--     CASE 
--         WHEN a.stock_actual IS NULL THEN 'MISSING_STOCK'
--         WHEN p.id IS NULL THEN 'NO_PARROQUIA'
--         ELSE 'OK'
--     END AS calidad_datos

-- FROM parroquia p
-- LEFT JOIN almacen a ON a.parroquia_id = p.id
-- ON DUPLICATE KEY UPDATE
--     consumo_7d = VALUES(consumo_7d),
--     consumo_30d = VALUES(consumo_30d),
--     promedio_12m = VALUES(promedio_12m),
--     dias_desde_ultima_entrega = VALUES(dias_desde_ultima_entrega),
--     stock_actual = VALUES(stock_actual),
--     stock_minimo = VALUES(stock_minimo),
--     entregas_pendientes = VALUES(entregas_pendientes),
--     proyeccion_72h = VALUES(proyeccion_72h),
--     indicador_riesgo = VALUES(indicador_riesgo),
--     calidad_datos = VALUES(calidad_datos),
--     updated_at = CURRENT_TIMESTAMP;
-- -- features_diarias.sql

-- V2.0
-- features_diarias.sql
INSERT INTO features_parroquia_daily (
    parroquia,
    fecha,
    consumo_7d,
    consumo_30d,
    promedio_12m,
    dias_desde_ultima_entrega,
    stock_actual,
    stock_capacidad,
    solicitudes_pendientes,
    proyeccion_72h,
    indicador_riesgo,
    calidad_datos
)
SELECT 
    p.id_parroquia AS parroquia,
    CURDATE() AS fecha,

    -- Total entregado últimos 7 días
    COALESCE((
        SELECT SUM(e.cantidad)
        FROM entrega e
        WHERE e.parroquia = p.id_parroquia
          AND e.fecha_entrega BETWEEN CURDATE() - INTERVAL 7 DAY AND CURDATE()
    ), 0) AS consumo_7d,

    -- Total entregado últimos 30 días
    COALESCE((
        SELECT SUM(e.cantidad)
        FROM entrega e
        WHERE e.parroquia = p.id_parroquia
          AND e.fecha_entrega BETWEEN CURDATE() - INTERVAL 30 DAY AND CURDATE()
    ), 0) AS consumo_30d,

    -- Promedio mensual de los últimos 12 meses
    COALESCE((
        SELECT SUM(e.cantidad) / 12
        FROM entrega e
        WHERE e.parroquia = p.id_parroquia
          AND e.fecha_entrega BETWEEN CURDATE() - INTERVAL 12 MONTH AND CURDATE()
    ), 0) AS promedio_12m,

    -- Días desde la última entrega
    DATEDIFF(
        CURDATE(),
        COALESCE(
            (SELECT MAX(e.fecha_entrega)
             FROM entrega e
             WHERE e.parroquia = p.id_parroquia),
            CURDATE()
        )
    ) AS dias_desde_ultima_entrega,

    -- Stock actual y capacidad
    COALESCE(a.existencia, 0) AS stock_actual,
    COALESCE(a.capacidad, 0) AS stock_capacidad,

    -- Solicitudes pendientes
    (
        SELECT COUNT(*)
        FROM solicitud s
        WHERE s.parroquia = p.id_parroquia
          AND s.estado IN ('pendiente', 'en_proceso')
    ) AS solicitudes_pendientes,

    -- Proyección de consumo a 3 días (basada en promedio semanal)
    ROUND(
        (COALESCE((
            SELECT SUM(e.cantidad)
            FROM entrega e
            WHERE e.parroquia = p.id_parroquia
              AND e.fecha_entrega BETWEEN CURDATE() - INTERVAL 7 DAY AND CURDATE()
        ), 0) / 7) * 3,
        2
    ) AS proyeccion_72h,

    -- Indicador de riesgo (stock_actual / consumo semanal)
    CASE 
        WHEN COALESCE((
            SELECT SUM(e.cantidad)
            FROM entrega e
            WHERE e.parroquia = p.id_parroquia
              AND e.fecha_entrega BETWEEN CURDATE() - INTERVAL 7 DAY AND CURDATE()
        ), 0) = 0 THEN 0
        ELSE ROUND(
            a.existencia / (
                COALESCE((
                    SELECT SUM(e.cantidad)
                    FROM entrega e
                    WHERE e.parroquia = p.id_parroquia
                      AND e.fecha_entrega BETWEEN CURDATE() - INTERVAL 7 DAY AND CURDATE()
                ), 1)
            ), 2)
    END AS indicador_riesgo,

    -- Verificación básica de datos
    CASE 
        WHEN a.existencia IS NULL THEN 'SIN_STOCK'
        WHEN p.id_parroquia IS NULL THEN 'SIN_PARROQUIA'
        ELSE 'OK'
    END AS calidad_datos

FROM parroquia p
LEFT JOIN almacen a ON a.parroquia = p.id_parroquia

ON DUPLICATE KEY UPDATE
    consumo_7d = VALUES(consumo_7d),
    consumo_30d = VALUES(consumo_30d),
    promedio_12m = VALUES(promedio_12m),
    dias_desde_ultima_entrega = VALUES(dias_desde_ultima_entrega),
    stock_actual = VALUES(stock_actual),
    stock_capacidad = VALUES(stock_capacidad),
    solicitudes_pendientes = VALUES(solicitudes_pendientes),
    proyeccion_72h = VALUES(proyeccion_72h),
    indicador_riesgo = VALUES(indicador_riesgo),
    calidad_datos = VALUES(calidad_datos),
    updated_at = CURRENT_TIMESTAMP;
