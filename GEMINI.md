# Contexto del Proyecto: Calculadora de Facturación Voccare 2025

## 1. Objetivo Principal
Implementar, simular y comparar la "Política de Facturación Global Voccare 2025 v2.1" frente al modelo 2024, asegurando la viabilidad financiera mediante incentivos a la adopción digital.

## 2. Definición de Políticas

### Política 2024 (Actual)
*   **Fee Mensual:** $3,150 USD (incluye primeros 50 SC).
*   **Servicios Concluidos (SC):** Tiers de volumen total. Costo unitario alto (~$10.51 - $4.33).
*   **Llamadas Válidas (LV):** Costo por tiers ($0.80, $0.37, $0.19). Se cobran todas las llamadas > 15s.

### Política 2025 v2.1 (Propuesta Final)
*   **Fee Mensual:** $3,150 USD.
*   **Servicios Concluidos (SC):** Se cobra por volumen TOTAL (App + Voz).
    *   **Incentivo Comercial:** **10% de Descuento** aplicado específicamente a la porción del costo correspondiente a SC originados por App.
*   **Transacción App:** $0.45 USD por servicio digital exitoso.
*   **Llamadas Válidas (LV):** Se siguen cobrando si ocurren.
    *   *Hallazgo:* Los usuarios App siguen generando llamadas (coordinación, dudas), pero en menor medida.

## 3. Calibración de Datos ("Triple Check")

Para asegurar que la simulación financiera coincida con la facturación real del Excel oficial (`REPORTE ACUMULADO INDICES SEPTIEMBRE 2025.xlsx`), se ajustaron los factores técnicos.

### Definición de "Llamada Válida" para Simulación
Se determinó que la forma más precisa de alinear el CSV operativo con el Excel financiero es contar **solo las llamadas asociadas a Servicios Concluidos (SC)** y aplicar un factor de eficiencia por país.

| País | Factor de Ajuste (Valid Call Factor) | Razón |
| :--- | :--- | :--- |
| **Dominicana** | **0.57** | Alta eficiencia, volumen masivo. |
| **Puerto Rico** | **0.50** | Volumen alto, mucha llamada de coordinación. |
| **México** | **0.29** | Muchas llamadas cortas/no facturables. |
| **Costa Rica** | **0.30** | Similar a México. |
| **Guatemala** | **1.00** (Tope) | Datos del CSV menores al Excel (posible subregistro). |
| **Otros** | **0.40** | Promedio conservador por defecto. |

## 4. Resultados Clave (Enero - Octubre 2025)

*   **Impacto Global:** La nueva política es neutral o genera ligeros ahorros para el cliente (~0.5% - 2.2%), incentivando la migración digital sin penalización financiera.
*   **Adopción App:**
    *   Alta: Dominicana (~70%), Uruguay (~43%).
    *   Media: Puerto Rico (~25%).
    *   Baja: Colombia, Ecuador, Perú (<2%).
*   **Conclusión:** El descuento del 10% en SC App es el mecanismo clave que hace viable la propuesta, absorbiendo el costo de la transacción digital ($0.45) y el remanente de llamadas de voz.