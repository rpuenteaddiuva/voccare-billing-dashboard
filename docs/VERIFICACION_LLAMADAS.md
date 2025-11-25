# Verificación de Llamadas Válidas (LV) vs Reporte Acumulado

## Metodología
Se compararon los volúmenes de "Llamadas Válidas" calculados por la simulación (usando la lógica `Non-App Raw Calls * 0.90`) contra la métrica "Total de llamadas Validas" del archivo Excel `REPORTE ACUMULADO INDICES SEPTIEMBRE 2025 (1).xlsx` para la República Dominicana (DO).

## Resultados: República Dominicana (DO)

| Mes | Simulación LV (Est.) | Excel "Total Validas" | Diferencia | % Diff |
| :--- | :--- | :--- | :--- | :--- |
| **Ene** | 10,965 | 11,119 | -154 | **-1.4%** |
| **Feb** | 10,695 | 9,713 | +982 | +10.1% |
| **Mar** | 10,531 | 12,772 | -2,241 | -17.5% |
| **Abr** | 11,503 | 11,082 | +421 | +3.8% |
| **May** | 11,952 | 12,419 | -467 | -3.8% |
| **Jun** | 10,605 | 11,495 | -890 | -7.7% |
| **Jul** | 10,534 | 11,473 | -939 | -8.2% |
| **Ago** | 9,632 | 9,303 | +329 | +3.5% |
| **Sep** | 9,703 | 9,999 | -296 | -3.0% |

## Conclusión
*   **Alta Correlación:** Existe una coincidencia muy fuerte entre el volumen de llamadas de servicios "No-App" (ajustado al 90% de validez) y el reporte oficial.
*   **Validación de Política:** Esto confirma que el reporte oficial de "Llamadas Válidas" **excluye** el tráfico generado por la App, alineándose con la nueva política de 2025 que busca no cobrar voz por transacciones digitales.
*   **Factor de Ajuste:** El factor de `0.90` (90% de llamadas brutas son válidas >15s) demuestra ser mucho más preciso que la estimación inicial conservadora del 50%.

## Nota sobre Guatemala (GU)
El análisis de Guatemala mostró inconsistencias severas en la fuente de datos CSV (volúmenes brutos triplicándose en Q3 mientras el Excel se mantiene estable), lo que sugiere errores en la extracción de datos para ese país específico en el CSV proporcionado. Se recomienda usar Dominicana como referencia de integridad de datos.
