# Bitácora — Dataset sintético y calibración (espesador)

## Objetivo del dataset
Crear un dataset sintético realista para:
- entrenar un clasificador de riesgo/evento,
- probar detección temprana (horizonte 30 min),
- simular modo manual y acciones operacionales,
- incluir fallas típicas de instrumentación.

## Umbrales
- **Spec (referencia):** 80 NTU
- **Warning (evento ML):** 70 NTU sostenido (label)

Motivo: con un evento sostenido sobre 80, el P95 tiende a subir demasiado. Separar warning vs spec permite:
- mantener **prevalencia objetivo (4–6%)**,
- mantener distribución realista (P95 ~70–95),
- seguir reportando “sobre 80” como KPI.

## Señal CLEAN vs MEDIDA
- `Overflow_Turb_NTU_clean`: proceso (sin fallas), usada para labels.
- `Overflow_Turb_NTU`: sensor (con fallas), usada para features/demos de data quality.

Motivo: evita que spikes/drift distorsionen la definición del evento (ground truth).

## Requisitos alcanzados (target)
- Prevalencia de eventos (label): 4–6%
- Modo MANUAL: 15–30%
- P95 turbidez CLEAN: 70–95 NTU
- P99 turbidez CLEAN: 120–180 NTU (cap ajustado a 160 para evitar saturación)

## Componentes modelados
- Campañas:
  - **CLAY:** aumento de finos (PSD fines index).
  - **UF:** degradación intermitente de capacidad underflow.
  - **FLOC:** subdosificación (déficit de floculante).
- Control:
  - `ControlMode` AUTO/MANUAL.
  - `OperatorAction` (aumentar UF, aumentar floc, etc).
- Instrumentación:
  - missing/stuck/spikes/drift en tags seleccionados.

## Próximos pasos (modelado)
- Features temporales (lags, rolling mean/std, ratios).
- Validación temporal (split por tiempo).
- Métricas: PR-AUC, Recall@precision, lead time efectivo.