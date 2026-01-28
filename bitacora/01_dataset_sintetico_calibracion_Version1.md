# Bitácora — Dataset sintético y calibración

## Objetivo
Generar un dataset sintético realista para prototipar detección temprana de deterioro de clarificación, sin exponer datos sensibles.

## Umbrales y etiquetas
- `event_limit_NTU = 70` (warning): umbral para labels y calibración.
- `spec_limit_NTU = 80` (spec): KPI operacional para reporting.

Labels:
- `event_now`: evento sostenido sobre `event_limit_NTU` en señal CLEAN.
- `target_event_30m`: evento a 30 minutos (shift del `event_now`).

## CLEAN vs MEDIDA
- CLEAN: representa el estado del proceso sin fallas de instrumentación (ground truth).
- MEDIDA: incorpora fallas típicas (missing/stuck/spikes/drift).

Motivación: entrenar con condiciones realistas sin contaminar el “ground truth”.

## Componentes simulados
- Campañas: CLAY, UF (y opcional FLOC).
- Control: AUTO/MANUAL + acciones de operador (OperatorAction).
- Calidad de datos: faltantes y fallas controladas por tasa.

## Criterios de realismo (targets)
- Eventos: 4–6%
- MANUAL: 15–30%
- P95 CLEAN: 70–95 NTU
- P99 CLEAN: 120–180 NTU
