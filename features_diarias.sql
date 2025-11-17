-- features_diarias.sql (adapted)
-- Compute features for each parroquia using existing schema:
--  - consumption derived from solicitud + solicitud_cilindro via vocero->consejo->comunidad->parroquia
--  - stock attempted from almacen.litraje_total snapshot if present

INSERT INTO features_parroquia_daily (
    parroquia_id,
    fecha,
    consumo_7d,
    consumo_30d,
    promedio_12m,
    dias_desde_ultima_entrega,
    stock_actual,
    stock_minimo,
    entregas_pendientes,
    proyeccion_72h,
    indicador_riesgo,
    calidad_datos
)
SELECT
    p.id AS parroquia_id,
    CURDATE() AS fecha,

    -- consumo últimos 7 días (suma de cilindros solicitados en solicitudes finalizadas/entregadas)
    COALESCE((
        SELECT SUM(sc.cantidad)
        FROM solicitud s
        JOIN solicitud_cilindro sc ON sc.solicitud_id = s.id
        JOIN vocero_comunal v ON v.cedula = s.vocero_comunal
        JOIN consejo_comunal cc ON cc.rif = v.consejo_comunal_rif
        JOIN comunidad com ON com.id = cc.comunidad_id
        WHERE com.parroquia_id = p.id
          AND s.fecha BETWEEN CURDATE() - INTERVAL 7 DAY AND CURDATE()
          AND s.estado IN ('FINALIZADA','EN ENTREGA')
    ), 0) AS consumo_7d,

    -- consumo últimos 30 días
    COALESCE((
        SELECT SUM(sc.cantidad)
        FROM solicitud s
        JOIN solicitud_cilindro sc ON sc.solicitud_id = s.id
        JOIN vocero_comunal v ON v.cedula = s.vocero_comunal
        JOIN consejo_comunal cc ON cc.rif = v.consejo_comunal_rif
        JOIN comunidad com ON com.id = cc.comunidad_id
        WHERE com.parroquia_id = p.id
          AND s.fecha BETWEEN CURDATE() - INTERVAL 30 DAY AND CURDATE()
          AND s.estado IN ('FINALIZADA','EN ENTREGA')
    ), 0) AS consumo_30d,

    -- promedio 12 meses (simple promedio de total cilindros / 12)
    COALESCE((
        SELECT SUM(sc.cantidad) / 12
        FROM solicitud s
        JOIN solicitud_cilindro sc ON sc.solicitud_id = s.id
        JOIN vocero_comunal v ON v.cedula = s.vocero_comunal
        JOIN consejo_comunal cc ON cc.rif = v.consejo_comunal_rif
        JOIN comunidad com ON com.id = cc.comunidad_id
        WHERE com.parroquia_id = p.id
          AND s.fecha BETWEEN CURDATE() - INTERVAL 12 MONTH AND CURDATE()
          AND s.estado IN ('FINALIZADA','EN ENTREGA')
    ), 0) AS promedio_12m,

    -- Días desde la última solicitud finalizada (proxy de última entrega)
    DATEDIFF(
        CURDATE(),
        COALESCE((
            SELECT MAX(s.fecha)
            FROM solicitud s
            JOIN vocero_comunal v ON v.cedula = s.vocero_comunal
            JOIN consejo_comunal cc ON cc.rif = v.consejo_comunal_rif
            JOIN comunidad com ON com.id = cc.comunidad_id
            WHERE com.parroquia_id = p.id
              AND s.estado IN ('FINALIZADA','EN ENTREGA')
        ), CURDATE())
    ) AS dias_desde_ultima_entrega,

    -- Stock: try to use almacen.litraje_total if present (may be global snapshot), else NULL
    (
        SELECT COALESCE(MAX(a.litraje_total), NULL)
        FROM almacen a
    ) AS stock_actual,
    NULL AS stock_minimo,

    -- solicitudes pendientes (estados predefinidos)
    (
        SELECT COUNT(*)
        FROM solicitud s
        JOIN vocero_comunal v ON v.cedula = s.vocero_comunal
        JOIN consejo_comunal cc ON cc.rif = v.consejo_comunal_rif
        JOIN comunidad com ON com.id = cc.comunidad_id
        WHERE com.parroquia_id = p.id
          AND s.estado IN ('PENDIENTE','EN PROCESO','POR PAGAR','VALIDANDO')
    ) AS entregas_pendientes,

    -- proyección 72h (basada en promedio semanal de cilindros)
    ROUND((COALESCE((
        SELECT SUM(sc.cantidad)
        FROM solicitud s
        JOIN solicitud_cilindro sc ON sc.solicitud_id = s.id
        JOIN vocero_comunal v ON v.cedula = s.vocero_comunal
        JOIN consejo_comunal cc ON cc.rif = v.consejo_comunal_rif
        JOIN comunidad com ON com.id = cc.comunidad_id
        WHERE com.parroquia_id = p.id
          AND s.fecha BETWEEN CURDATE() - INTERVAL 7 DAY AND CURDATE()
          AND s.estado IN ('FINALIZADA','EN ENTREGA')
    ), 0) / 7) * 3, 2) AS proyeccion_72h,

    -- indicador riesgo: si no hay consumo en 7d -> 0, else NULL (no stock reliable)
    CASE WHEN (
        COALESCE((
            SELECT SUM(sc.cantidad)
            FROM solicitud s
            JOIN solicitud_cilindro sc ON sc.solicitud_id = s.id
            JOIN vocero_comunal v ON v.cedula = s.vocero_comunal
            JOIN consejo_comunal cc ON cc.rif = v.consejo_comunal_rif
            JOIN comunidad com ON com.id = cc.comunidad_id
            WHERE com.parroquia_id = p.id
              AND s.fecha BETWEEN CURDATE() - INTERVAL 7 DAY AND CURDATE()
              AND s.estado IN ('FINALIZADA','EN ENTREGA')
        ), 0) = 0) THEN 0 ELSE NULL END AS indicador_riesgo,

    -- calidad de datos básica
    CASE WHEN p.id IS NULL THEN 'SIN_PARROQUIA' ELSE 'OK' END AS calidad_datos

FROM parroquia p

ON DUPLICATE KEY UPDATE
    consumo_7d = VALUES(consumo_7d),
    consumo_30d = VALUES(consumo_30d),
    promedio_12m = VALUES(promedio_12m),
    dias_desde_ultima_entrega = VALUES(dias_desde_ultima_entrega),
    stock_actual = VALUES(stock_actual),
    stock_minimo = VALUES(stock_minimo),
    entregas_pendientes = VALUES(entregas_pendientes),
    proyeccion_72h = VALUES(proyeccion_72h),
    indicador_riesgo = VALUES(indicador_riesgo),
    calidad_datos = VALUES(calidad_datos),
    updated_at = CURRENT_TIMESTAMP;
