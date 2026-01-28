# Roadmap (portafolio) — Enfoque: Optimización de procesos

## Hito 1 — Baseline operacional (predictivo)
- Notebook EDA enfocado en operación:
  - cuándo ocurren eventos, duración, severidad
  - diferencias AUTO vs MANUAL
- Baseline (logistic / xgboost) con split temporal estricto
- Métricas “para operación”:
  - PR-AUC + Recall@Precision
  - tasa de falsas alarmas por día
  - matriz de confusión

## Hito 2 — Features temporales y explicabilidad
- Lags + rolling windows (tendencia, volatilidad, cambios)
- Importancias / SHAP para conectar modelo con lógica de proceso
- Ablation study: qué variables realmente aportan

## Hito 3 — Anticipación y costo operacional
- Lead time (minutos de anticipación útil)
- Curva costo: false alarms vs missed events
- Umbral de decisión calibrado para operación (no solo “accuracy”)

## Hito 4 — Sensor health (robustez industrial)
- Detector de fallas de medición (missing/stuck/spikes/drift)
- Estrategia: imputación/filtrado + degradación controlada del modelo
- Indicadores de confiabilidad del sensor para el usuario final

## Hito 5 — Prescriptivo (acción sugerida)
- Regla o modelo simple: “qué acción tomar” (ej. aumentar UF o ajustar floc)
- Métrica: reducción esperada de riesgo / tiempo en evento (simulado)
