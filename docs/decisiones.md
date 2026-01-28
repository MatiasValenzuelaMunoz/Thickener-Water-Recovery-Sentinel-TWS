# Decisiones técnicas (registro)

## D1 — Umbrales separados: warning vs spec
- `event_limit_NTU = 70` para labels y calibración
- `spec_limit_NTU = 80` como KPI operacional
Motivo: controlar prevalencia de eventos y mantener P95/P99 realistas.

## D2 — Labels sobre CLEAN
Motivo: evitar que fallas de instrumento alteren la verdad del proceso.

## D3 — Dataset sintético como estrategia de portafolio
Motivo: demostrar capacidades end-to-end sin exponer información sensible.
