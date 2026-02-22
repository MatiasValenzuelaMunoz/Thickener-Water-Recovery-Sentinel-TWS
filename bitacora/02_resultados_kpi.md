# Resultados — KPIs del dataset (evidencia)

> 📋 **Registro histórico — etapa temprana (2026-01-28).** Corresponde a deadband=0.33 y event_limit=70 NTU. Los KPIs actuales del proyecto usan deadband=0.27, event_limit=100 NTU. Ver `05_bitacora.md` para la calibración final.

Fecha: 2026-01-28

## Dataset
- Filas: 25920
- Columnas: 23
- Archivo: `data/processed/thickener_timeseries_deadband0p33_sp4.parquet`

## KPIs
- Prevalencia de eventos (label CLEAN @70 sostenido): **5.48%**
- Fracción modo MANUAL: **27.14%**

### Turbidez CLEAN (proceso)
- Min: 5.0 NTU
- Mediana: 22.7 NTU
- P95: 94.6 NTU
- P99: 151.4 NTU
- Max: 160.0 NTU

### Turbidez MEDIDA (con fallas)
- Min: 0.0 NTU
- Mediana: 22.3 NTU
- P95: 93.1 NTU
- P99: 148.6 NTU
- Max: 160.0 NTU

### Puntos sobre umbrales
- MEDIDA > 70: **9.61%**
- MEDIDA > 80: **7.08%**
- CLEAN  > 70: **10.47%**
- CLEAN  > 80: **7.60%**

### Tipos de evento (`event_type`)
- CLAY: 1005 (70.7%)
- UF: 413 (29.1%)
- FLOC: 3 (0.2%)

### Calidad de datos
- Missing en `Qf_m3h`: **1.00%**
