-- QUERY PARA EXTRACCIÓN DE DATOS HISTÓRICOS (SOLICITUD IT)
-- Objetivo: Alimentar calculadora de pricing diferenciado (App vs Voz)
-- Tablas estimadas: Assistances, Services, CallDetails (Nombres hipotéticos basados en esquema común)

SELECT 
    a.id_asistencia,
    a.id_expediente,
    a.fecha_creacion AS creacion_asistencia, -- Vital para agrupar por mes
    a.fecha_cierre AS fecha_finalizacion_asistencia,
    
    -- Estado del servicio (Vital para filtrar CONCLUIDA)
    s.estado AS estado_asistencia, 
    
    -- Identificador de Canal (CRÍTICO para pricing App vs Tel)
    -- Se necesita saber si fue asignado por App, Web, o Manualmente
    a.origen_asignacion AS tipo_asignacion, 
    
    -- Métricas de Voz
    -- Necesitamos saber si hubo llamadas y su duración
    (SELECT COUNT(*) FROM calls c WHERE c.id_asistencia = a.id_asistencia) AS cantidad_llamadas,
    (SELECT SUM(duration_sec) FROM calls c WHERE c.id_asistencia = a.id_asistencia) AS duracion_total_llamadas,
    
    -- Costos (Opcional, para comparar margen)
    ac.costo_total AS costo_proveedor

FROM Assistances a
LEFT JOIN Services s ON a.id_servicio = s.id
LEFT JOIN AssistancesCost ac ON a.id_asistencia = ac.id_asistencia
WHERE 
    a.fecha_creacion >= '2024-01-01' -- Histórico relevante
    -- AND a.pais IN ('Mexico', 'Puerto Rico', 'Dominicana', ...)
;
