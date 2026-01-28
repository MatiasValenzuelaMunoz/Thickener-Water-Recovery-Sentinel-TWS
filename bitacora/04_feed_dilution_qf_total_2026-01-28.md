# Bitácora — Feed dilution físicamente consistente (Qf_total)

- Fecha: 2026-01-28
- Título: Se incorpora dilución explícita con caudal total a espesador (Qf_total)

## Cambios
- Se redefinió la dilución de alimentación para que represente **más agua** en vez de “menos sólidos”.
- Se agregaron tags explícitos:
  - `Qf_pulp_m3h`, `Qf_dilution_m3h`, `Qf_total_m3h`
- `Qf_m3h` se mantiene como tag compatible y ahora representa el **caudal total al espesador** (`Qf_total_m3h`).
- `Solids_f_pct` se recalcula por mezcla conservando la masa de sólidos del stream de pulpa (proxy).

## Evidencia (métricas/logs)
DEBUG SUMMARY:
- event_rate: **0.0488**
- dilution_on_rate: **0.0102**
- qf_total_q95: **776.36 m³/h**

Validación rápida:
- Dimensiones: **25920 × 25**
- Prevalencia eventos: **4.88%**
- Modo MANUAL: **25.04%**
- Turbidez CLEAN: P95 **90.6**, P99 **147.1**
- Missing en `Qf_m3h`: **1.00%**

## Decisión
- Mantener este enfoque (Qf_total) como base porque hace la acción prescriptiva “diluir feed” interpretable y realista.

## Riesgos/Notas
- `event_type` reportado solo CLAY/UF: FLOC puede estar subrepresentado como evento sostenido.

## Próximo paso
- Definir si FLOC debe ser un escenario evaluable (más eventos) y ajustar pesos/implementación para que aparezca en `event_type` con frecuencia útil.
