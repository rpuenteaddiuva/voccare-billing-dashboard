# Análisis de Nueva Política de Facturación (Caso México)

## Resumen Ejecutivo

Se ha implementado el modelo de la **Política de Facturación Global Voccare 2025** que incentiva la migración hacia canales digitales (App, Web, API). El análisis inicial para México muestra el impacto de esta nueva estructura.

**Hallazgos Clave (México Ene-Oct 2025):**
1.  **Costo Total Estimado:** Bajo el nuevo modelo, la facturación total para México (Ene-Oct 2025) asciende a **$216,004.25 USD**.
2.  **Distribución de Costos:**
    *   Servicios Concluidos (SC): $175,306.80 USD
    *   Llamadas Válidas (LV): $9,173.60 USD
    *   Transacciones Digitales (APP): $23.85 USD
    *   Fee Mensual (10 meses): $31,500.00 USD
3.  **Bajo Uso de APP:** Actualmente, la cantidad de transacciones digitales facturables en México es muy baja (53 en 10 meses), lo que resulta en un costo mínimo por este rubro.
4.  **Potencial de Ahorro:** Aunque la nueva política introduce un costo por transacción APP, está diseñada para ser más eficiente que las llamadas. Un aumento significativo en la adopción de la APP podría reducir la dependencia de las llamadas válidas (LV), llevando a ahorros operativos para la filial.

## Conciliación de "Servicios Concluidos" para México (Ene-Sep 2025)
-   **Conteo de la Calculadora (Basado en `CLAUDE.md`):** 2,065 Servicios Concluidos.
-   **Objetivo del Reporte Excel:** 2,165 Servicios Concluidos.
-   **Discrepancia Conocida:** La diferencia de 100 servicios (-4.62% de error) está documentada en `CLAUDE.md` y es el resultado de la aplicación de la lógica de filtrado y agrupamiento descrita allí. Nuestro script replica con precisión esta lógica y, por lo tanto, esta discrepancia conocida.

## Política de Facturación Global Voccare 2025 (Resumen)

### 1. Fee Mensual
-   Costo base de disponibilidad y soporte ($3,150.00 USD).
-   Incluye los primeros 50 Servicios Concluidos (SC) de forma gratuita.

### 2. Servicios Concluidos (SC) - Precios por Volumen
-   Tabla de precios escalonada por volumen (Rangos 1 al 10).
-   Los servicios originados por App SÍ suman al volumen total para alcanzar mejores rangos de precio, pero solo los servicios NO originados por App (voz) generan costo en este rubro (después de los primeros 50 SC totales).

### 3. Llamadas Válidas (LV) - Intervención Humana
-   Definición: Interacción de voz humana >15 segundos.
-   Tarifas escalonadas ($0.80, $0.37, $0.19 por unidad).
-   Este costo se ELIMINA para todos los servicios gestionados exitosamente a través del ecosistema digital que NO requieran intervención humana.

### 4. Servicios Cancelados Posterior (SCP)
-   Precio único de $2.47 USD por evento (no incluido en esta simulación debido a datos no disponibles en el CSV).

### 5. Servicios de Infraestructura (SIOD)
-   Costos pass-through de proveedores externos (Geolocalización, WhatsApp). No incluidos en esta simulación.

### 6. Transacciones Digitales (APP) - NUEVO RUBRO
-   Definición: Solicitud de servicio generada exitosamente vía App Móvil, Portal Web, Bot o API sin intervención telefónica inicial.
-   Tarifas preferenciales escalonadas:
    -   0 - 5,000: $0.45 / unidad
    -   5,001 - 20,000: $0.35 / unidad
    -   + 20,001: $0.20 / unidad

## Simulación de Facturación (México Ene-Oct 2025)

| Mes        | SC    | APP Tx  | LV    | Costo SC (USD) | Costo LV (USD) | Costo APP (USD) | Fee Mensual (USD) | Total Factura (USD) |
| :--------- | :---- | :------ | :---- | :------------- | :------------- | :-------------- | :---------------- | :------------------ |
| 2025-01    | 289   | 5       | 1997  | $24,593.40     | $1,597.60      | $2.25           | $3,150.00         | $29,343.25          |
| 2025-02    | 204   | 11      | 687   | $15,239.50     | $549.60        | $4.95           | $3,150.00         | $18,944.05          |
| 2025-03    | 253   | 2       | 1586  | $21,125.10     | $1,268.80      | $0.90           | $3,150.00         | $25,544.80          |
| 2025-04    | 193   | 7       | 1197  | $14,398.70     | $957.60        | $3.15           | $3,150.00         | $18,509.45          |
| 2025-05    | 202   | 6       | 1107  | $15,449.70     | $885.60        | $2.70           | $3,150.00         | $19,488.00          |
| 2025-06    | 225   | 3       | 1021  | $18,077.20     | $816.80        | $1.35           | $3,150.00         | $22,045.35          |
| 2025-07    | 233   | 6       | 849   | $18,707.80     | $679.20        | $2.70           | $3,150.00         | $22,539.70          |
| 2025-08    | 224   | 4       | 992   | $17,867.00     | $793.60        | $1.80           | $3,150.00         | $21,812.40          |
| 2025-09    | 242   | 5       | 1364  | $19,758.80     | $1,091.20      | $2.25           | $3,150.00         | $24,002.25          |
| 2025-10    | 149   | 4       | 667   | $10,089.60     | $533.60        | $1.80           | $3,150.00         | $13,775.00          |
| **TOTAL**  | **2214**| **53**    | **11467**| **$175,306.80**| **$9,173.60**  | **$23.85**      | **$31,500.00**    | **$216,004.25**     |

## Próximos Pasos
-   Considerar la implementación de simulaciones de escenarios de adopción de APP para proyectar ahorros potenciales de manera más estratégica.
-   Validar los factores de llamadas válidas (`valid_call_factor`) con datos más precisos de cada país, ya que la ausencia de `duracion_llamada` sigue siendo una limitación.
-   Integrar el cálculo de Servicios Cancelados Posterior (SCP) una vez que se disponga de datos o un criterio claro para identificarlos.
