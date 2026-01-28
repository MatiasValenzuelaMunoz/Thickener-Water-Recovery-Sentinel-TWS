# Campaign Spec — Campañas sintéticas (CLAY / UF / FLOC)

Este simulador incluye campañas que representan mecanismos típicos de deterioro en clarificación y descarga de un espesador.  
Objetivo: habilitar modelado **predictivo** (riesgo de evento) y, a futuro, **prescriptivo** (acción sugerida).

## Cómo se implementan en el simulador
- `Regime` programa períodos consecutivos:
  - `NORMAL` → `CLAY` → `UF` → `FLOC`
- El evento (`event_now`) se etiqueta desde `Overflow_Turb_NTU_clean` con condición sostenida:
  - CLEAN > `event_limit_NTU` (70) por `sustain_points` (4 puntos = 20 min)
- `event_type` se asigna cuando hay evento, según el **driver dominante**:
  - argmax entre contribuciones normalizadas de finos (CLAY), restricción UF (UF), déficit floc (FLOC)

---

## Resumen ejecutivo: firma e intervención

### CLAY — Ataque de finos/arcillas
**Qué representa:** incremento de finos coloidales (arcillas) que sobrepasa el mecanismo de sedimentación.  
**Implementación:** `PSD_fines_idx` tiende a valores altos en CLAY; esto sube el estrés y la turbidez.

- **Firma esperada (tags):**
  - `Overflow_Turb_*` ↑↑ (overflow “lechoso”)
  - `PSD_fines_idx` ↑↑
  - `BedLevel_m` puede ↓ inicialmente y luego ↑ si se acumula
  - `RakeTorque_pct` ↔/↑ (secundario)
- **Acción típica:**
  - ajustar `Floc_gpt` (cauteloso) + considerar dilución/menor carga (conceptual)

### UF — Degradación de capacidad de underflow
**Qué representa:** cuello de botella en descarga (bomba/válvula/reología), inventario se acumula.  
**Implementación:** `UF_capacity_factor` cae por segmentos durante UF → limita `Qu_m3h` y eleva bed/torque.

- **Firma esperada (tags):**
  - `BedLevel_m` ↑↑
  - `RakeTorque_pct` ↑↑
  - `UF_capacity_factor` ↓ y/o `Qu_m3h` restringido
  - `Solids_u_pct` tiende a bajar (descarga más “diluida” o inestable)
- **Acción típica:**
  - aliviar descarga (conceptual): aumentar capacidad/flujo, dilución UF, reducir feed temporalmente

### FLOC — Subdosificación de floculante
**Qué representa:** déficit de floc (bomba/preparación/dosis) → flóculos débiles y mala clarificación.  
**Implementación:** durante `Regime=FLOC`, `Floc_gpt` se reduce multiplicando por 0.55–0.75, elevando `floc_deficit` y turbidez.

- **Firma esperada (tags):**
  - `Overflow_Turb_*` ↑↑
  - `Floc_gpt` ↓ (relativo a necesidad)
  - `BedLevel_m` ↔ / baja-estable
  - `RakeTorque_pct` ↔ (sin firma mecánica fuerte)
- **Acción típica:**
  - subir `Floc_gpt` (más directo que en CLAY) y verificar preparación/calibración (conceptual)

---

## Tabla de impacto en variables clave (dirección)
Leyenda: ↑ aumenta, ↓ disminuye, ↔ neutro/variable

| Variable | CLAY | UF | FLOC |
|---|---:|---:|---:|
| `PSD_fines_idx` | ↑↑ | ↔ | ↔ |
| `UF_capacity_factor` | ↔ | ↓↓ | ↔ |
| `Qu_m3h` | ↔ | ↓ / restringido | ↔ |
| `BedLevel_m` | ↓ luego ↑ | ↑↑ | ↔ / ↓ |
| `RakeTorque_pct` | ↔ / ↑ | ↑↑ | ↔ |
| `Floc_gpt` | ↑ (acción) | ↔ | ↓↓ (causa) |
| `Overflow_Turb_NTU_clean` | ↑↑ | ↑ | ↑↑ |
| `Overflow_Turb_NTU` | ↑↑ (+ fallas) | ↑ (+ fallas) | ↑↑ (+ fallas) |

---

## Objetivos de modelado por campaña

### Objetivo global (binario)
Predecir `target_event_30m` (evento en 30 min) con split temporal estricto.

### Objetivo adicional (explicabilidad para operación)
- Importancias/SHAP para “traducir” el riesgo a drivers:
  - finos (`PSD_fines_idx`), descarga (`UF_capacity_factor`, `BedLevel_m`, `RakeTorque_pct`), déficit de floc (`Floc_gpt`)

### Objetivo avanzado (multi-tarea)
- **Clasificar `event_type`** durante evento (CLAY/UF/FLOC) para habilitar recomendación de acción.
