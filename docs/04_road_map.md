# Roadmap (portafolio) — Optimización de procesos

## Hito 1 — Baseline operacional
- EDA operativo: eventos (inicio/duración), AUTO vs MANUAL, campañas
- Baseline (logistic / xgboost) con validación temporal
- Métricas: PR-AUC, Recall@Precision, falsas alarmas/día

## Hito 2 — Features temporales + explicabilidad
- Lags/rolling (tendencia, volatilidad, cambios)
- SHAP/importancias con narrativa de proceso
- Ablations por familias de features

## Hito 3 — Métrica de anticipación
- Lead time (min) y estabilidad de alertas
- Curva costo (false alarms vs misses) y calibración de umbral

## Hito 4 — Robustez industrial
- Sensor health (missing/stuck/spikes/drift) y degradación controlada
- Estrategias de imputación/filtrado

## Hito 5 — Prescriptivo (acción sugerida)
- Reglas v1 basadas en firmas + variables manipulables
- Incluir `FeedDilution_On` como palanca explícita
