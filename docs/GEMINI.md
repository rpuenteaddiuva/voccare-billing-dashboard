# GEMINI.md

This file serves as the context and knowledge base for Gemini in the "Calculadora SOA" project, focusing on the implementation of the new billing policy rewarding App usage.

## Project Objective
Create a new billing policy that incentivizes the use of the Voccare App. App usage has been proven to reduce call volume by ~23.8%.

## Key Resources
- **Legacy Context**: `CLAUDE.md` (contains critical data cleaning rules and historical bug fixes).
- **Data Source**: `Client05_Mexico.csv` (and others).
- **Validation Target**: `REPORTE ACUMULADO INDICES SEPTIEMBRE 2025 (1).xlsx`.
- **Policy Document**: `Politica de Facturacioìn Voccare 2024 Firmada (1).pdf`.

## Current Analysis Status (Mexico)
- **Data Logic**:
  - Group by `creacion_asistencia` month (not `fecha_cierre`).
  - Filter: `creacion_asistencia.year >= 2023`.
  - **Deduplication**: SKIP for Mexico (per `CLAUDE.md`).
  - **App Usage (EKUS)**: `tipo_asignacion` IN ['APP', 'ANCLAJE_APP_SOA', 'ANCLAJE', 'ANCLAJE_APP'].
  - **No App (GLOBAL)**: `tipo_asignacion` IN ['MANUAL', 'ANCLAJE_BASE'].

## Known Challenges
1.  **Call Duration**: The CSV lacks call duration, leading to overcounting of "Valid Calls" (>15s). We must rely on "Concluded Services" for accurate reconciliation or find a proxy/workaround.
2.  **Missing Dates**: High percentage of missing `fecha_finalizacion_asistencia`.
3.  **Inconsistent Naming**: 'EKUS' = App, 'GLOBAL' = Manual/Phone.

## Implementation Roadmap
1.  **Baseline**: Match "Concluded Services" counts for Mexico against the Excel report.
2.  **Policy Logic**: Define the new pricing rules based on the "reward" system (needs clarification from user or PDF).

## Billing Policy 2024 (Current Rules)

### 1. Fee Mensual
- Includes first **50** Concluded Services (SC).
- Price: **$3,150.00** (Base Fee).

### 2. Servicios Concluidos (SC) - Tiered Pricing
*Cumulative progressive calculation (Marginal Tax Rate style)*
- **0 - 50**: Included in Fee.
- **51 - 500**: $10.51 / unit
- **501 - 1,000**: $9.28 / unit
- **1,001 - 2,000**: $8.04 / unit
- **2,001 - 3,000**: $6.80 / unit
- **3,001 - 6,000**: $5.57 / unit
- **6,001 - 9,000**: $5.26 / unit
- **9,001 - 12,000**: $4.95 / unit
- **12,001 - 15,000**: $4.64 / unit
- **> 15,000**: $4.33 / unit

### 3. Llamadas Válidas (LV)
*Definition: Interaction > 15 seconds (Note: CSV lacks duration, currently estimated/filtered)*
- **0 - 4,000**: $0.80 / unit
- **4,001 - 20,000**: $0.37 / unit
- **> 20,000**: $0.19 / unit

### 4. Servicios Cancelados Posterior (SCP)
- Fixed price: **$2.47** / unit.
- Definition: Service cancelled after provider assignment.

### 5. Other Costs (Pass-through)
- **Geolocalización (Maplink)**: Per coordinate.
- **WhatsApp**: Per conversation (country dependent).

## Global Impact Analysis (Projected 2025)
*Based on Jan-Oct 2025 Data using proposed 10% App Discount Policy*

| Country | Total Services | App Adoption | Current Bill (Est.) | New Bill (Est.) | Direct Savings (Client) | Notes |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Mexico** | 2,214 | ~2% | $58,861 | $58,818 | **$42** | Low adoption; negligible impact. Potential for growth. |
| **Dominicana** | 23,700 | ~68% | $292,533 | $278,692 | **$13,841** | High adoption; significant savings for client immediately. |
| **Puerto Rico** | 368,591 | ~30% | $1,964,881 | $1,907,921 | **$56,959** | High volume; 10% discount is a major financial value. |
| **Argentina** | 17,234 | ~12% | $213,816 | $211,801 | **$2,014** | Moderate adoption; room for optimization. |
| **Costa Rica** | 42,613 | ~36% | $393,947 | $382,214 | **$11,733** | Healthy adoption; consistent savings. |

### Strategic Recommendation
1.  **High Adoption Countries (DO, PR, CR)**: The 10% discount is a *reward* for existing behavior. Ensure the **call reduction savings** (internal cost) > **discount given** (revenue loss).
    *   *Check*: Does 30-70% App usage actually reduce calls by ~23% in these countries? Validation needed.
2.  **Low Adoption Countries (MX, AR)**: The 10% discount is a *loss leader / incentive* to drive change. The financial risk is low because current usage is low. Aggressive promotion recommended.

## Data Integrity & Limitations
**Current Gap:**
- **Mexico Data:** Analyzed ~220 records/month vs 75K/month expected reality.
- **Missing Fields:** `duracion_llamada` is missing in CSVs, forcing estimation of "Valid Calls".
- **Solution:** A SQL extraction query has been prepared (`scripts/QUERY_EXTRACCION_BD.sql`) to run against the production database (`SOAANG_CLIENT_1`) once access is granted. This will provide the granular data needed for precise margin calculation.
