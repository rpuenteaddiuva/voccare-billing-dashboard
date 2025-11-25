# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Calculadora SOA** - Billing calculation system for Voccare that analyzes service and call data across multiple countries to support invoicing based on:
- Concluded services (tiered pricing)
- Valid calls (tiered pricing)
- Post-cancelled services (fixed price $2.47)
- Infrastructure services (geolocation, WhatsApp)

**Key Goal**: Incorporate APP usage (EKUS vs GLOBAL) as a pricing differentiator, as APP usage reduces calls by 23.8%.

## Running the Analysis

### Main Analysis Script
```bash
python scripts/analisis_calculadora_CORREGIDO.py
```
Processes Mexico, Dominicana, and Puerto Rico. Generates 7 CSVs per country in `resultados/{Country}/`.

### Generate Visualizations
```bash
python scripts/generar_graficas.py
```
Creates 8 PNG charts (300dpi) in `graficas/`.

### APP vs Calls Correlation Analysis
```bash
python scripts/analisis_correlacion_app_llamadas.py
```
Statistical analysis proving APP reduces calls by 23.8% (p < 0.001).

## Critical Business Logic

### **IMPORTANT: Different Rules for Services vs Calls**

#### For CONCLUDED SERVICES:
- ❌ **DO NOT** filter test records (all work is billable)
- ✅ Deduplicate by `id_asistencia` only
- ❌ **DO NOT** deduplicate by expediente
- ✅ Group by closing month (`fecha_finalizacion_asistencia`)

#### For VALID CALLS:
- ✅ **DO** filter test records (test calls aren't real)
- ✅ Deduplicate by `id_asistencia`
- ✅ Deduplicate by `id_expediente` (keep='last' - last assistance per file)
- ✅ Group by closing month

**Test Filter Pattern** (7 columns): `prueba|PRUEBA|test|TEST|QA|qa`
- Columns: nombre_titular, nombre_contacto, usuario_que_apertura, plan, cuenta, justificacion_cancelacion, usuario_que_asigna

### EKUS vs GLOBAL Classification

**EKUS (CON_APP)** - Mobile app usage:
- APP
- ANCLAJE_APP_SOA
- ANCLAJE (deprecated)
- ANCLAJE_APP (deprecated)

**GLOBAL (SIN_APP)** - No app:
- MANUAL
- ANCLAJE_BASE

**OTHER:**
- BASE_AUTOMATICO
- APIROUTE1
- SIN_ASIGNAR

## Country-Specific Configurations

### Mexico (`Client05_Mexico.csv`)
- **Date format**: `%d/%m/%Y %H:%M`
- **CSV separator**: `,`
- **CRITICAL**: Use `creacion_asistencia` for month grouping (not `fecha_cierre`)
- **CRITICAL**: Skip deduplication (`skip_deduplication: True`)
- **CRITICAL BUG FIX**: When using `creacion_asistencia` for grouping, MUST also filter by `creacion_asistencia.year >= 2023` (NOT `fecha_cierre.year >= 2023`)
- **Data characteristics**:
  - 1,326 CONCLUDED services (26.9%) missing `fecha_finalizacion_asistencia`
  - 71 duplicate records (20 unique IDs) in 2025 data → DO NOT deduplicate
- **Accuracy after fix**: -4.62% error ✅ (2,065 vs 2,165 expected)
- **Previous errors**:
  - Before bug fix: -16.1% error (1,817 services - lost 248 due to filtering bug)
  - Before using creacion_asistencia: -18.11% error

### Dominicana (`Client03_Dominicana.csv`)
- **Date format**: `%d/%m/%Y %H:%M`
- **CSV separator**: `,`
- **CRITICAL**: Use `creacion_asistencia` for month grouping
- **CRITICAL**: Skip deduplication (`skip_deduplication: True`)
- **Reason**: 28.9% of CONCLUDED services missing `fecha_finalizacion_asistencia`
- **Accuracy**: -0.40% error (improved from -1.91%) ✅

### Puerto Rico (`Client01_Puerto_Rico_20251027.csv`)
- **Date format**: `%Y-%m-%d %H:%M:%S` (different!)
- **CSV separator**: `;` (different!)
- **Filter**: `cuenta = 'MCS CLASSICARE'`
- **Use standard logic**: `fecha_cierre` for grouping, with deduplication
- **Accuracy**: +2.6% error ✅
- **Status**: MCS working, INC identification pending

### Argentina (`Client06_Argentina_20251027.csv`)
- **Date format**: `%Y-%m-%d %H:%M:%S`
- **CSV separator**: `;`
- **CRITICAL**: Process in 3 segments:
  1. **Argentina** (total): No filter
  2. **Argentina_AON**: Filter `*AON*` (captures AON + AON FORD)
  3. **Argentina_SIN_AON**: Filter `!*AON*` (excludes all AON accounts)
- **Use standard logic**: `fecha_cierre` for grouping, with deduplication
- **Data quality**: Only 0.01% missing `fecha_finalizacion_asistencia` (excellent!)
- **Accuracy** (Ene-Sep 2025):
  - Total: -0.03% error (15,302 vs 15,306) ✅ Almost perfect
  - AON: -0.26% error (4,189 vs 4,200) ✅ Excellent
  - SIN_AON: +0.06% error (11,113 vs 11,106) ✅ Excellent
- **Key accounts**: AON (5,507), AON FORD (1,293) = 6,800 total AON records
- **Services**: 99.33% VEHICULAR (mostly remolque)

**IMPORTANT**: Use wildcard filters (`*AON*`) to capture all variants of account names.

### Costa Rica (`Client08_Costa_Rica_20251027.csv`)
- **Date format**: `%Y-%m-%d %H:%M:%S`
- **CSV separator**: `;`
- **Total records**: 186,525
- **Excel shows TWO segments**:
  - **CR-CR**: 29,406 concluidos (88.9%)
  - **CR**: 3,688 concluidos (11.1%)
  - **Total expected**: 33,094
- **Current analysis** (combined):
  - Total concluidos: 34,266
  - **Accuracy**: +3.54% error ✅ (very close)
- **Status**: ⚠️ **SEGMENTATION PENDING** - Similar to Puerto Rico MCS/INC issue
- **Problem**: Cannot identify criteria to separate CR-CR from CR
  - No dominant account pattern (~18% MNK ASISTENCIA is largest)
  - No clear plan or condicion_servicio separation
  - Monthly values don't match when summed separately
- **Top accounts**: MNK ASISTENCIA (18.8%), SEGUROS LAFISE (12.1%), CAJA DE ANDE (11.0%)
- **Action Required**: Consult with Costa Rica team about CR-CR vs CR separation criteria

## Key Architectural Decisions

### Discovery: Month Grouping Logic
The official calculator uses **creation month**, not **closing month**, for services that lack `fecha_finalizacion_asistencia`. This discovery reduced Mexico error from -19.7% to -4.6%.

**Implementation in `analisis_calculadora_CORREGIDO.py:125-173`:**
```python
def convertir_fechas(df, use_fecha_creacion_para_mes=False):
    # use_fecha_creacion_para_mes: Use creation month instead of closing month
    # Required for Mexico and Dominicana to match calculator
```

### Discovery: Deduplication Inconsistency
The official calculator appears to NOT deduplicate certain duplicate `id_asistencia` records. Setting `skip_deduplication: True` for Mexico and Dominicana significantly improves accuracy.

**Configuration in lines 52-80:**
```python
PAISES_CONFIG = [
    {
        'nombre': 'Mexico',
        'use_fecha_creacion_para_mes': True,
        'skip_deduplication': True  # Improves from -19.7% to -4.62%
    },
    ...
]
```

### CRITICAL BUG FIX (October 31, 2025)

**Problem**: Filtering inconsistency causing -16.1% error in Mexico

The script was grouping by `creacion_asistencia` but filtering by `fecha_cierre.year >= 2023`:

```python
# INCORRECT (line 393, 399):
df_unico['anio_mes_cierre'] = df_unico['creacion_asistencia'].dt.to_period('M')  # Groups by creation
df_concluidos = df_unico[df_unico['fecha_cierre'].dt.year >= 2023].copy()  # ❌ Filters by closing
```

This lost 248 services (1,326 CONCLUDED services have no `fecha_cierre`).

**Solution implemented (lines 391-400)**:
```python
if use_fecha_creacion_para_mes:
    df_unico['anio_mes_cierre'] = df_unico['creacion_asistencia'].dt.to_period('M')
    df_concluidos = df_unico[df_unico['creacion_asistencia'].dt.year >= 2023].copy()  # ✅ Consistent
else:
    df_unico['anio_mes_cierre'] = df_unico['fecha_cierre'].dt.to_period('M')
    df_concluidos = df_unico[df_unico['fecha_cierre'].dt.year >= 2023].copy()
```

**Impact**:
- Mexico: -16.1% error → **-4.62% error** ✅ (recovered 248 services)
- Root cause: 1,326 services (26.9%) have no `fecha_finalizacion_asistencia`

### Wildcard Account Filters (October 31, 2025)

**Feature**: Support for pattern matching in account filters using `*` wildcard

**Implementation (lines 381-411)**:
```python
if cuenta_filter:
    if cuenta_filter.startswith('!'):
        # Exclude accounts
        if '*' in cuenta_filter:
            df = df[~df['cuenta'].str.contains(pattern, case=False, na=False)]
        else:
            df = df[df['cuenta'] != cuenta_filter]
    else:
        # Include accounts
        if '*' in cuenta_filter:
            df = df[df['cuenta'].str.contains(pattern, case=False, na=False)]
        else:
            df = df[df['cuenta'] == cuenta_filter]
```

**Examples**:
- `'MCS CLASSICARE'` - Exact match (Puerto Rico)
- `'*AON*'` - Contains "AON" (captures AON + AON FORD in Argentina)
- `'!*AON*'` - Excludes any account containing "AON"

**Use case**: Argentina has 2 AON accounts (AON + AON FORD). Using `*AON*` captures both:
- Before: Filter `'AON'` captured 5,507 records (error -19.76%)
- After: Filter `'*AON*'` captures 6,800 records (error -0.26%) ✅

## Data Structure

### Input Files
- `datos_originales/Client05_Mexico.csv` - Mexico source data
- `datos_originales/Client03_Dominicana.csv` - Dominicana source data
- `datos_originales/Client01_Puerto_Rico_20251027.csv` - Puerto Rico source data
- `datos_originales/Client06_Argentina_20251027.csv` - Argentina source data (processed in 3 segments)

### Output Structure (per country)
```
resultados/{Country}/
├── base_concluidos_{country}.csv - Concluded services (no test filter)
├── base_llamadas_{country}.csv - Calls (with test filter)
├── evolucion_mensual_{country}.csv - Monthly evolution
├── evolucion_tipo_anclaje_{country}.csv - By assignment type
├── evolucion_categoria_servicio_{country}.csv - VEHICULAR vs HOGAR
├── evolucion_top5_servicios_{country}.csv - Top 5 services
└── resumen_estadistico_{country}.csv - Statistical summary
```

### Reference Document
- `Politica de Facturación Voccare 2024 Firmada (1).pdf` - Official billing policy
- `REPORTE ACUMULADO INDICES SEPTIEMBRE 2025 (1).xlsx` - Calculator validation data

## Known Issues & Status

### 1. Puerto Rico INC Separation ⚠️ BLOCKED
**Problem**: Cannot identify INC (Incentivo) services in data. Only found MCS CLASSICARE (257,084 services). Calculator expects 37,125 INC services.

**Attempts**:
- Searching "INC" literal → Only 15 records
- Filtering by `condicion_servicio` → Doesn't match
- Searching in `plan` field → Only "MCS CLASSICARE" exists

**Action Required**: Consult with Joana's team about MCS vs INC separation criteria.

**Files**: See `CLAUDE.md` lines 125-140, `COMPARACION_CALCULADORA.md` lines 99-126

### 2. Valid Calls - Systematic Over-counting ⚠️ CRITICAL

**Problem**: All countries show significant over-counting of calls:
- Mexico: +175.8% error (15,204 vs 5,512)
- Argentina: +74.6% error (74,398 vs 42,611)
- Dominicana: +112% error (similar pattern)

**Investigation (November 4, 2025)**:

Tested multiple hypotheses:

1. ✅ **Filter test records** - Already implemented
2. ✅ **Deduplicate by expediente** - Already implemented (keep='last')
3. ✅ **Only count calls with fecha_finalizacion** - Improved but not enough
   - Mexico: +117.9% error (12,009 vs 5,512)
4. ✅ **Filter period by finalization date (not creation)** - Still not enough
   - Mexico: +114.4% error (11,817 vs 5,512)
5. ❌ **Remove deduplication by expediente** - Made it worse (+138.7%)
6. ⚠️ **Divide by 2** - Works for Mexico but not Argentina
   - Mexico /2: +7.2% error ✅ (5,908 vs 5,512)
   - Argentina /2: -12.7% error ❌ (37,199 vs 42,611)

**Root Cause CONFIRMED** (November 4, 2025):

According to **Política de Facturación Voccare 2024**:
> "Llamada válida = interacción superior a 15 segundos"

**The CSVs do NOT contain call duration field:**

Verified all country CSVs - only field present:
- `cantidad_llamadas` - Total call count (includes ALL calls, regardless of duration)

**Missing field needed:**
- `duracion_llamada` or similar - Duration in seconds to filter >15 seconds

**Why we over-count:**
```
CSV field:         cantidad_llamadas = ALL calls (includes <15s, lost, abandoned)
Calculator uses:   Valid calls = cantidad_llamadas WHERE duracion > 15 seconds
```

**Excel breakdown** (Mexico sheet):
```
Total de llamadas Validas: 5,512
  ├─ Llamadas válidas Proveedores: 175
  └─ Llamadas válidas Clientes CAT: 5,337
```

This confirms calculator has access to call detail records (CDR) with duration that we don't have in CSV.

**Action Required - CRITICAL**:

Request from technical team **ONE** of these options:

1. **New CSV with call details** (preferred):
   - Columns: id_llamada, id_asistencia, duracion_segundos, tipo_llamada, timestamp
   - This allows us to filter >15 seconds ourselves

2. **Additional field in current CSV**:
   - `cantidad_llamadas_validas` - Pre-filtered count (>15 seconds only)

3. **Access to call center logs/database**:
   - Direct access to CDR (Call Detail Records) system

**Without call duration data, we CANNOT accurately calculate billable valid calls.**

**Files**: `CLAUDE.md` line 314-320

### 3. EKUS vs GLOBAL Classification - 7-14% Error 🟡 MODERATE
**Problem**:
- Dominicana EKUS: 7.70% error (we're missing services)
- Dominicana GLOBAL: 13.77% error (we're counting extra)

**Hypothesis**: Calculator uses additional criteria not available in CSV exports or field definitions changed over time.

**Action Required**: Validate classification with local teams.

**Files**: `CLAUDE.md` lines 322-329

## Key Findings

### Financial Impact of APP Usage
- **CON_APP (EKUS)**: 4.39 calls/file average
- **SIN_APP (GLOBAL)**: 5.76 calls/file average
- **Reduction**: 23.8% fewer calls with APP (p < 0.001)
- **Implication**: APP reduces call center costs and improves customer experience

**Source**: `scripts/analisis_correlacion_app_llamadas.py`, documented in `README.md` lines 147-150

### Data Quality Issues
~27% of CONCLUDED services lack `fecha_finalizacion_asistencia` across countries. This impacts:
- Performance tracking
- Resolution time metrics
- Report accuracy

**Recommendation**: Implement mandatory validation on service closure.

## Dependencies

```bash
pip install pandas numpy matplotlib seaborn scipy openpyxl
```

## Additional Documentation

- `README.md` - User-facing documentation
- `COMPARACION_CALCULADORA.md` - Detailed accuracy comparison
- `HALLAZGOS_MEXICO.md` - Mexico discrepancy investigation
- `REPORTE_HALLAZGOS_CRITICOS.md` - Critical findings report
- `scripts/analisis_codigo_zombie.md` - Code analysis notes

## Analysis Period

**January - September 2025** (9 months)

---

**Last Updated**: October 30, 2025
