# Thickener Water Recovery Sentinel (TWS)

Proyecto personal de portafolio para **detección temprana de deterioro de clarificación** en un espesador, usando un **dataset sintético reproducible** (sin datos sensibles) que incorpora campañas operacionales, modo manual y fallas de instrumentación.

## Problema
Aumentos sostenidos de **turbidez de overflow** reducen recuperación de agua y afectan estabilidad operacional.  
Objetivo: habilitar un entorno end-to-end para **anticipar eventos** y comparar estrategias de modelado/evaluación.

## Idea clave (diferenciador)
Separación explícita entre:
- `Overflow_Turb_NTU_clean`: “ground truth” del proceso (sin fallas), usada para **labels**
- `Overflow_Turb_NTU`: medición con fallas (missing/stuck/spikes/drift), usada para **features**

Esto permite entrenar y evaluar modelos robustos con sensores imperfectos sin contaminar el etiquetado.

## Umbrales
- `event_limit_NTU = 70` → **warning** (base de labels y calibración)
- `spec_limit_NTU = 80` → **spec** (KPI operacional/reporting)

## Qué incluye
- Simulador de series temporales multivariables (≈90 días @ 5 min).
- Campañas / causas sintéticas (ej. **CLAY**, **UF**, opcional **FLOC**).
- Control **AUTO vs MANUAL** y acciones de operador.
- Etiquetas:
  - `event_now`: evento sostenido sobre `event_limit_NTU` en CLEAN
  - `target_event_30m`: evento a 30 minutos

## KPIs logrados (dataset típico)
- Prevalencia de eventos (label, CLEAN @70): ~5%
- Fracción modo MANUAL: ~26%
- Turbidez CLEAN: P95 ~89 NTU / P99 ~139 NTU

## Estructura del repo
- `src/`: simulación + validación rápida
- `bitacora/`: decisiones y evolución del proyecto (narrativa)
- `docs/`: arquitectura y decisiones técnicas
- `notebooks/`: EDA, features, modelos (por completar)
- `outputs/`: figuras y métricas (no versionar artefactos pesados)

## Roadmap corto
1) Baseline model + evaluación temporal (PR-AUC, Recall@Precision).
2) Features temporales (lags/rolling) sin leakage.
3) Métrica de “lead time” y trade-off falsas alarmas vs misses.
4) Monitoreo de salud de sensores (clasificación de fallas).

