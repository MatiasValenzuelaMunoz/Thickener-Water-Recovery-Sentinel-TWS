# Campañas sintéticas — CLAY / UF / FLOC (y acciones operacionales)

Este documento define las campañas (mecanismos causales sintéticos) y cómo se reflejan en variables del dataset.
Enfocado en uso operacional: **firma → diagnóstico → acción**.

## Cómo se usan las campañas en el simulador
- `Regime` programa períodos consecutivos: `NORMAL` → `CLAY` → `UF` → `FLOC`.
- `event_now` se etiqueta desde `Overflow_Turb_NTU_clean`:
  - CLEAN > `event_limit_NTU` (70) sostenido `sustain_points=4` (20 min).
- `event_type` se asigna durante evento según driver dominante (fines / UF / floc).

## Acción explícita: dilución de alimentación (feed dilution)
La dilución se modela como **más agua al feed**:
- `Qf_total_m3h = Qf_pulp_m3h + Qf_dilution_m3h`
- `Solids_f_pct` baja por mezcla (proxy)
- `Qf_m3h` es alias SCADA de `Qf_total_m3h`

Esto permite evaluar prescriptivo simple: “activar dilución” y observar su efecto en riesgo de evento.

---

## Escenario 1 — CLAY (Ataque de finos/arcillas)

### Firma esperada (síntomas)
- `Overflow_Turb_NTU_clean` ↑↑ (overflow “lechoso”)
- `PSD_fines_idx` ↑↑ (driver)
- `BedLevel_m` variable (puede bajar al inicio y luego subir si se acumula)
- `RakeTorque_pct` ↔/↑ (secundario)

### Acción inmediata (modo “bombero”)
- Activar dilución de alimentación:
  - `FeedDilution_On=1`
  - `Qf_dilution_m3h > 0`
  - `Qf_total_m3h` ↑
  - `Solids_f_pct` ↓

### Objetivos de modelado (CLAY)
- Predecir `target_event_30m`.
- Explicar drivers (sensibilidad a `PSD_fines_idx`, carga efectiva, etc.).
- Evaluar impacto de dilución sobre riesgo (prescriptivo).

---

## Escenario 2 — UF (Degradación de capacidad del underflow)

### Firma esperada (síntomas)
- `UF_capacity_factor` ↓ (restricción)
- `BedLevel_m` ↑↑
- `RakeTorque_pct` ↑↑
- `Qu_m3h` restringido (no evacua inventario)
- `Solids_u_pct` tiende a ↓/inestable (proxy)

### Acción inmediata (modo “bombero”, conceptual)
- Aumentar capacidad de descarga / aliviar UF (p.ej. dilución UF, aumento de bombeo, reducción temporal de feed).

### Objetivos de modelado (UF)
- Anticipar eventos UF y minimizar falsas alarmas por subidas transitorias de torque/bed.

---

## Escenario 3 — FLOC (Subdosificación de floculante)

### Firma esperada (síntomas)
- `Floc_gpt` bajo vs necesidad
- `Overflow_Turb_*` ↑↑
- `BedLevel_m` baja/estable
- `RakeTorque_pct` ↔ (sin firma mecánica fuerte)

### Acción inmediata (modo “bombero”, conceptual)
- Aumentar `Floc_gpt` y verificar preparación/calibración.

### Objetivos de modelado (FLOC)
- Distinguir déficit real de floc vs ruido instrumental en turbidez medida.

---

## Tabla de impacto (dirección esperada)
Leyenda: ↑ aumenta, ↓ disminuye, ↔ neutro/variable

| Variable | CLAY | UF | FLOC |
|---|---:|---:|---:|
| `PSD_fines_idx` | ↑�� | ↔ | ↔ |
| `UF_capacity_factor` | ↔ | ↓↓ | ↔ |
| `BedLevel_m` | ↔/variable | ↑↑ | ↔/↓ |
| `RakeTorque_pct` | ↔/↑ | ↑↑ | ↔ |
| `Floc_gpt` | ↑ (acción cautelosa) | ↔ | ↓↓ (causa) |
| `FeedDilution_On` | ↑ (acción) | ↔ | ↔ |
| `Qf_total_m3h` | ↑ (dilución) | ↔ | ↔ |
| `Solids_f_pct` | ↓ (dilución) | ↔ | ↔ |
| `Overflow_Turb_NTU_clean` | ↑↑ | ↑ | ↑↑ |
| `Overflow_Turb_NTU` | ↑↑ (+ fallas) | ↑ (+ fallas) | ↑↑ (+ fallas) |
