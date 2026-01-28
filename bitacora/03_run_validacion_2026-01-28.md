# Bitácora — Run de validación del simulador (v4)

- Fecha: 2026-01-28
- Título: Dataset sintético generado + validación rápida OK (90 días @ 5 min)

## Cambios
- Generación y validación ejecutadas sobre `simulate_fixed.py` y `quick_checks.py`.
- Export del dataset a parquet versionado + archivo “latest”.

## Evidencia (métricas/logs)
- Archivo: `data/processed/thickener_timeseries_deadband0p33_sp4.parquet`
- Dimensiones: **25920 filas × 23 columnas**
- DEBUG SUMMARY:
  - deadband: 0.33
  - sustain_points: 4
  - scale: 1875.0
  - event_rate: **0.0548**

KPIs (quick_checks):
- Prevalencia eventos (label CLEAN > 70 sostenido): **5.48%**
- Fracción modo MANUAL: **27.14%**
- Turbidez CLEAN: P95 **94.6** / P99 **151.4** / Max 160.0
- Turbidez MEDIDA: P95 **93.1** / P99 **148.6** / Max 160.0
- Puntos MEDIDA > 70: **9.61%**, > 80: **7.08%**
- Puntos CLEAN  > 70: **10.47%**, > 80: **7.60%**
- Distribución `event_type`:
  - CLAY: 1005 (70.7%)
  - UF: 413 (29.1%)
  - FLOC: 3 (0.2%)
- Calidad de datos: faltantes en `Qf_m3h` **1.00%**

## Decisión
- El dataset cumple targets de prevalencia de eventos, %MANUAL y cuantiles P95/P99.
- Se detecta que el escenario FLOC no está representado en eventos de forma significativa → ajustar en próxima iteración si se quiere clasificación por campaña.

## Riesgos/Notas
- Si se incorpora “Feed Dilution” explícita, puede reducir el event_rate y requerir recalibración del `scale`.
- Mantener CLEAN como base de etiquetas para evitar sesgo por fallas.

## Próximo paso
1) Incorporar variable explícita `FeedDilution_On` (acción “bombero” en CLAY) y cuantificar su efecto en event_rate y P95/P99.
2) (Opcional) aumentar contribución del déficit de floc para que `event_type=FLOC` sea más representativo.
