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

---

## **Actualizaciones Recientes del Dashboard (Noviembre 2025)**

### **Funcionalidades Añadidas y Mejoras de UX:**
*   **Despliegue en Streamlit Cloud:** La aplicación está ahora optimizada para despliegue en la nube, manejando archivos grandes (`.csv` convertidos a `.zip`).
*   **Filtro de Meses Mejorado:** Implementado un selector de meses tipo Excel con botones "Ver Todos" y "Limpiar", y selección individual dentro de un desplegable en la barra lateral.
*   **Gráfica de Volumen Total de Servicios:** Añadida una nueva gráfica en la pestaña Operativa que muestra la tendencia mensual consolidada de Servicios Concluidos.
*   **Toggle "Con Fee / Sin Fee":** Se añadió un selector en la barra lateral para incluir o excluir el Fee Mensual ($3,150 USD) de las estimaciones y de la Facturación Real, permitiendo análisis más flexibles.
*   **Etiquetas de Valor en Gráficas:** Las gráficas de barras ahora muestran los valores numéricos directamente sobre las barras para una mejor legibilidad.
*   **Rango de Descuento App Ampliado:** El slider de "Descuento por Uso de App" ahora permite seleccionar hasta un 50%.
*   **Tabla de Datos Detallados Colapsable:** La tabla de datos se oculta por defecto en un `st.expander` para mejorar la experiencia móvil.

### **Integración de Facturación Real:**
Se han integrado los datos de facturación real (Enero a Noviembre 2025) para los siguientes países, permitiendo una comparación directa con las políticas simuladas:
*   **Puerto Rico**
*   **Argentina** (datos históricos desde Julio 2023)
*   **Dominicana**
*   **Bolivia** (suma de cuentas Mercantil y Normal)
*   **Perú**
*   **Chile**
*   **Ecuador**
*   **México**

### **Correcciones y Refinamientos Técnicos:**
*   Se corrigieron múltiples `IndentationError` y `SyntaxError` a lo largo del código.
*   Se resolvió el `KeyError` en el Dashboard asegurando que la columna de facturación simulada se renombrara consistentemente a `Factura 2026` desde el origen (`run_simulation`).
*   Se ajustó el `streamlit_app.py` para leer directamente los archivos `.zip` comprimidos.
*   Se implementó una lógica robusta para el procesamiento de archivos Excel con estructuras complejas (e.g., Dominicana).

Este `GEMINI.md` actualizado proporciona una visión general completa del estado actual del proyecto.