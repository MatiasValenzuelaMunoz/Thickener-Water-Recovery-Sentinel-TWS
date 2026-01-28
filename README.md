# Thickener Water Recovery Sentinel (TWS)

Proyecto personal (portfolio) orientado a **monitoreo y predicción de deterioro de clarificación** en un espesador, usando un **dataset sintético realista** (sin datos sensibles) y un pipeline reproducible.

## Problema
En espesadores, aumentos sostenidos de **turbidez de overflow** reducen recuperación de agua y afectan estabilidad operacional.

- **Spec (referencia):** 80 NTU  
- **Warning (evento para ML):** 70 NTU sostenido  
- **Objetivo ML:** anticipar un evento con **horizonte 30 min** (clasificación binaria).

## Qué incluye este repo
- Generación de dataset sintético multivariable con:
  - campañas (CLAY / UF / FLOC),
  - modos de control (AUTO / MANUAL),
  - acciones de operador (OperatorAction),
  - fallas de instrumentación (missing/stuck/spikes/drift),
  - turbidez **CLEAN** (proceso) vs turbidez **MEDIDA** (sensor).
- Script de validación rápida (sanity checks).
- Bitácora técnica (decisiones y calibración del dataset).
- Espacio para notebooks de EDA, features y modelado.

## Dataset y etiquetas
Columnas clave:
- `Overflow_Turb_NTU_clean`: “ground truth” del proceso (sin fallas).
- `Overflow_Turb_NTU`: medición con fallas (lo que vería el sistema).
- `event_now`: evento sostenido basado en `Overflow_Turb_NTU_clean > event_limit_NTU` (70 NTU).
- `target_event_30m`: etiqueta a 30 minutos (shift de `event_now`).

## Cómo ejecutar
### 1) Generar dataset sintético
```bash
python src/simulate_fixed.py
```

### 2) Validar distribución y KPIs
```bash
python src/quick_checks.py
```

## Bitácora
Ver carpeta [`bitacora/`](bitacora/) para decisiones de diseño, iteraciones y resultados.

## Notas
Este repo usa **datos sintéticos** para evitar exposición de información sensible.
