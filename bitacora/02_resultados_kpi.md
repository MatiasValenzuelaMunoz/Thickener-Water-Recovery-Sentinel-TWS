# Resultados — KPIs del dataset (evidencia)

Fecha: 2026-01-28

## Dataset
- Filas: 25920
- Columnas: 20

## KPIs
- Prevalencia de eventos (label sobre CLEAN @70): **4.95%**
- Fracción modo MANUAL: **25.94%**

### Turbidez CLEAN (proceso)
- Min: 5.0 NTU
- Mediana: 22.2 NTU
- P95: 89.4 NTU
- P99: 138.5 NTU
- Max: 160.0 NTU

### Turbidez MEDIDA (con fallas)
- Min: 0.0 NTU
- Mediana: 21.7 NTU
- P95: 88.2 NTU
- P99: 135.2 NTU
- Max: 160.0 NTU

### Puntos sobre umbrales
- MEDIDA > 70: **8.67%**
- MEDIDA > 80: **6.37%**
- CLEAN  > 70: **9.42%**
- CLEAN  > 80: **6.75%**

### Tipos de evento
- CLAY: 919 (71.6%)
- UF: 365 (28.4%)

## Interpretación breve
El dataset cumple targets de prevalencia, presencia de MANUAL y rangos P95/P99, y separa correctamente warning (70) vs spec (80) como KPI.
