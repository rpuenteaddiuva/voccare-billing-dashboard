# Verificación de Servicios Concluidos (SC) vs Reporte Acumulado

## Metodología
Se compararon los volúmenes de "Servicios Concluidos" (SC) calculados por la simulación (filtro: `estado_asistencia == 'CONCLUIDA'`) contra la métrica "Total Servicios Concluidos (C)" del archivo Excel `REPORTE ACUMULADO INDICES SEPTIEMBRE 2025 (1).xlsx` para la República Dominicana (DO).

## Resultados: República Dominicana (DO)

| Mes | Simulación (CSV) | Excel "Servicios (C)" | Diferencia | % Diff |
| :--- | :--- | :--- | :--- | :--- |
| **Ene** | 2,537 | 2,533 | +4 | **+0.16%** |
| **Feb** | 2,319 | 2,310 | +9 | +0.39% |
| **Mar** | 2,631 | 2,625 | +6 | +0.23% |
| **Abr** | 2,239 | 2,237 | +2 | +0.09% |
| **May** | 2,486 | 2,460 | +26 | +1.06% |
| **Jun** | 2,246 | 2,218 | +28 | +1.26% |
| **Jul** | 2,401 | 2,351 | +50 | +2.13% |
| **Ago** | 2,368 | 2,328 | +40 | +1.72% |
| **Sep** | 2,518 | 2,472 | +46 | +1.86% |

## Conclusión
*   **Precisión Casi Perfecta:** La coincidencia es extremadamente alta, con una variación menor al **0.5%** en el primer trimestre y manteniéndose por debajo del **2.2%** en el peor de los casos.
*   **Integridad de Datos:** Esto confirma que el archivo CSV `Client03_Dominicana_20251027.csv` contiene prácticamente la totalidad de los registros reportados oficialmente como concluidos.
*   **Validación de Lógica:** La lógica de filtrado `estado_asistencia == 'CONCLUIDA'` es correcta y consistente con los reportes financieros oficiales.
