# Campaign Spec — Campañas sintéticas (CLAY / UF / FLOC)

Este simulador incluye campañas que representan mecanismos típicos de deterioro en clarificación y descarga de un espesador.
Objetivo: habilitar modelado **predictivo** (riesgo de evento) y, a futuro, **prescriptivo** (acción sugerida).

## Variables clave agregadas (acción explícita)
La dilución de alimentación se modela explícitamente como **más agua al feed** (no “menos sólidos”):
- `Qf_total_m3h = Qf_pulp_m3h + Qf_dilution_m3h`
- `Solids_f_pct` baja por mezcla manteniendo la masa de sólidos del stream de pulpa (proxy)
- `Qf_m3h` es alias SCADA de `Qf_total_m3h` (y es el tag que se corrompe con fallas)

Tags asociados:
- `FeedDilution_On` (0/1)
- `FeedDilution_factor` (objetivo de reducción de %sol)
- `Qf_dilution_m3h` (agua agregada)

---

## Cómo se implementan en el simulador
- `Regime` programa períodos consecutivos: `NORMAL` → `CLAY` → `UF` → `FLOC`
- Etiquetado:
  - `event_now` se define con `Overflow_Turb_NTU_clean > event_limit_NTU` (70) sostenido (`sustain_points` = 4 → 20 min)
  - `target_event_30m` es `event_now` desplazado 30 min
- `event_type` durante evento se asigna por driver dominante (fines/UF/floc).

---

## Resumen por campaña (firma + acción)

### CLAY — Ataque de finos/arcillas
**Drivers:** `PSD_fines_idx` alto.  
**Firma:** turbidez ↑↑, finos ↑↑, cama variable; puede aumentar MANUAL.  

**Acción inmediata representada en datos (dilución de alimentación):**
- `FeedDilution_On = 1`
- `Qf_dilution_m3h > 0`
- `Qf_total_m3h` ↑
- `Solids_f_pct` ↓

**Objetivo de modelado (CLAY):**
- anticipar evento y explicar sensibilidad a finos
- evaluar si la dilución reduce riesgo (base del componente prescriptivo)

### UF — Restricción en descarga (capacidad UF)
**Driver:** `UF_capacity_factor` bajo (segmentos).  
**Firma:** `BedLevel_m ↑` + `RakeTorque_pct ↑` + `Solids_u_pct` tiende a ↓/inestable, turbidez ↑.  
**Objetivo:** anticipar eventos UF y reducir falsas alarmas cuando sube torque/bed sin evento.

### FLOC — Subdosificación de floculante
**Driver:** `Floc_gpt` reducido en `Regime=FLOC`.  
**Firma:** turbidez ↑↑ con cama baja/estable y sin firma mecánica fuerte.  
**Objetivo:** distinguir déficit de floc vs ruido instrumental.

---

## Tabla de impacto (dirección esperada)
Leyenda: ↑ aumenta, ↓ disminuye, ↔ neutro/variable

| Variable | CLAY | UF | FLOC |
|---|---:|---:|---:|
| `PSD_fines_idx` | ↑↑ | ↔ | ↔ |
| `UF_capacity_factor` | ↔ | ↓↓ | ↔ |
| `BedLevel_m` | ↔ / variable | ↑↑ | ↔ / ↓ |
| `RakeTorque_pct` | ↔ / ↑ | ↑↑ | ↔ |
| `Floc_gpt` | ↑ (acción cautelosa) | ↔ | ↓↓ (causa) |
| `FeedDilution_On` | ↑ (acción) | ↔ | ↔ |
| `Qf_total_m3h` | ↑ (por dilución) | ↔ | ↔ |
| `Solids_f_pct` | ↓ (por dilución) | ↔ | ↔ |
| `Overflow_Turb_NTU_clean` | ↑↑ | ↑ | ↑↑ |
| `Overflow_Turb_NTU` | ↑↑ (+ fallas) | ↑ (+ fallas) | ↑↑ (+ fallas) |
