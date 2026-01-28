# Arquitectura y flujo

## Flujo principal
1) `src/simulate_fixed.py`
- genera series temporales sintéticas
- crea `Overflow_Turb_NTU_clean` (proceso) y etiquetas
- crea `Overflow_Turb_NTU` (medida) e inyecta fallas instrumentales
- exporta parquet en `data/processed/`

2) `src/quick_checks.py`
- valida KPIs del dataset (prevalencia, percentiles, etc.)

## Contrato de datos (principios)
- Labels **solo** desde `Overflow_Turb_NTU_clean`
- Features desde mediciones realistas: `Overflow_Turb_NTU` + variables de proceso
- Validación temporal estricta (sin leakage)

## Convenciones
- Frecuencia típica: 5 min
- Etiqueta sostenida: 20 min (`sustain_points=4`)
- Horizonte: 30 min (`horizon_points=6`)
