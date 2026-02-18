# Bitácora 06 — Descarte del mecanismo FLOC

**Fecha:** 2026-02-18
**Autor:** Decisión de diseño ML

---

## Motivo

El mecanismo de falla de preparación de floculante (FLOC) representaba apenas **0.2% de los eventos** (~3 puntos en 25920 filas). Esta fracción es completamente inviable para entrenar un clasificador de diagnóstico: cualquier modelo que reciba tan pocos ejemplos positivos simplemente ignorará la clase FLOC.

Distribución de event_type antes del cambio:
- NONE: ~94.9%
- CLAY: ~3.4%
- UF: ~1.5%
- FLOC: ~0.2% ← insuficiente

---

## Decisión

**Eliminar completamente el mecanismo FLOC del simulador.** El diagnóstico queda simplificado a un problema binario: **CLAY vs UF**.

El floculante sigue existiendo como **variable de proceso** (`Floc_gpt`), calculado a partir de las necesidades de PSD, carga de sólidos y contenido de arcilla. Lo que se elimina es la lógica de "incidentes de actividad degradada de floculante".

---

## Variables eliminadas del dataset

| Variable | Descripción |
|----------|-------------|
| `FlocActivity_factor` | Factor de actividad 0–1 del floculante preparado |
| `FlocPrepFail_On` | Indicador binario de incidente activo de preparación |
| `FlocEffective_gpt` | Dosis efectiva = Floc_gpt × FlocActivity_factor |
| `Floc_sp_delta_gpt` | Delta de setpoint de floculante por acción del operador |

---

## Variables mantenidas

| Variable | Descripción |
|----------|-------------|
| `Floc_gpt` | Dosis de floculante como variable de proceso (gpt), calculada según necesidades del proceso |

---

## Cambios en SimConfig

Parámetros eliminados:
- `floc_prep_fail_events_per_30d`
- `floc_prep_fail_duration_min`
- `floc_activity_normal_range`
- `floc_activity_fail_range`
- `floc_max_effect_gpt`
- `overfloc_ys_gain`
- `floc_setpoint_step` / `floc_setpoint_clip`
- `event_type_override_th_floc`

---

## Renormalización de pesos de stress

El componente `floc_c` (peso 0.26) fue eliminado del índice de stress. Los pesos restantes se renormalizaron para mantener coherencia:

```python
# Antes: w = [0.18, 0.20, 0.12, 0.26, 0.24]  (fines, load, var, floc, uf)
# Después: w = [0.24, 0.26, 0.15, 0.35]        (fines, load, var, uf)
```

El binary search sobre `scale` recalibra automáticamente la tasa de eventos al target 5% ± 0.6%.

---

## Simplificación del operador

- Eliminada acción `INCREASE_FLOC`
- Eliminado `Floc_sp_delta` como setpoint manipulable
- Solo queda `INCREASE_UF` como acción manual
- `manual_prob` ya no incluye el término `FlocPrepFail_On`

---

## Simplificación del playbook

- Eliminada rama `CHECK_FLOC_PREP_INCREASE_FLOC`
- Playbook simplificado: UF → `INCREASE_UF_WATCH_CARRYOVER`, CLAY → `START_DILUTION_AND_OPTIMIZE_FLOC`, resto → `MONITOR_AND_TUNE`

---

## Diagnóstico final: CLAY vs UF

`event_type` solo toma valores: `"CLAY"`, `"UF"`, `"NONE"`.

- **CLAY**: dominado por `fines_c` (Clay_idx alto, PSD alto). Reforzado por `regime == "CLAY"`.
- **UF**: dominado por `uf_c` (UF_capacity_factor bajo, Qu insuficiente). Reforzado con override si `regime == "UF"`.

---

## Impacto esperado en KPIs

El event_rate se recalibrará automáticamente vía binary search al target 5% ± 0.6%. Los KPIs de distribución de turbidez (verde/degradado) deberían mantenerse similares dado que la contribución de `floc_c` era la más baja del vector de stress antes de renormalización.
