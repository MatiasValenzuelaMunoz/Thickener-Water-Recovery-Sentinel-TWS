# Diccionario de datos — Thickener Water Recovery Sentinel (TWS)

Dataset sintético de series temporales (espesador) para anticipar eventos de turbidez alta.
Frecuencia típica: **5 min**. Horizonte de predicción: **30 min**.

## Columnas (orden real del parquet)
`timestamp`, `Qf_pulp_m3h`, `Qf_dilution_m3h`, `Qf_total_m3h`, `Qf_m3h`, `Solids_f_pct`, `FeedDilution_On`, `FeedDilution_factor`, `PSD_fines_idx`, `Floc_gpt`, `UF_capacity_factor`, `Qu_m3h`, `Solids_u_pct`, `BedLevel_m`, `RakeTorque_pct`, `Overflow_Turb_NTU_clean`, `Overflow_Turb_NTU`, `ControlMode`, `OperatorAction`, `spec_limit_NTU`, `event_limit_NTU`, `event_now`, `event_type`, `Regime`, `target_event_30m`

## Convenciones clave
- **CLEAN vs MEDIDA**:
  - `Overflow_Turb_NTU_clean`: turbidez "ground truth" del proceso (sin fallas).
  - `Overflow_Turb_NTU`: turbidez medida, **corrompida** por fallas (spikes/stuck/drift/missing).
- Umbrales:
  - `event_limit_NTU = 70` → warning (base de etiquetas)
  - `spec_limit_NTU = 80` → spec (KPI)
- Etiquetas:
  - `event_now`: evento sostenido (CLEAN > 70 por 20 min)
  - `target_event_30m`: evento a 30 min

## Convención importante (caudales y dilución)
- `Qf_pulp_m3h`: caudal de pulpa “base” (sin agua de dilución).
- `Qf_dilution_m3h`: agua agregada para dilución (acción “bombero”).
- `Qf_total_m3h = Qf_pulp_m3h + Qf_dilution_m3h`: caudal total al espesador.
- `Qf_m3h`: **alias SCADA** de `Qf_total_m3h` (se mantiene por compatibilidad) y es el tag que se corrompe con fallas.

Cuando `FeedDilution_On=1` se espera:
- `Qf_total_m3h` ↑
- `Solids_f_pct` ↓

---

## Tabla de variables

### A) Tiempo
| Columna | Tipo | Descripción |
|---|---|---|
| `timestamp` | datetime | Marca temporal. |

### B) Alimentación (feed)
| Columna | Tipo | Unidad | Descripción |
|---|---:|---:|---|
| `Qf_pulp_m3h` | float | m³/h | Caudal de pulpa base (sin agua añadida). |
| `Qf_dilution_m3h` | float | m³/h | Agua de dilución añadida. 0 si no aplica. |
| `Qf_total_m3h` | float | m³/h | Caudal total a espesador (pulp + dilución). |
| `Qf_m3h` | float | m³/h | Tag compatible/SCADA = `Qf_total_m3h`. **Puede incluir fallas** (spikes/stuck/drift/missing). |
| `Solids_f_pct` | float | % | % sólidos en alimentación luego de mezclar con agua de dilución. |

### C) Acción explícita: dilución de alimentación
| Columna | Tipo | Unidad | Descripción |
|---|---:|---:|---|
| `FeedDilution_On` | int (0/1) | - | 1 si está activa la dilución de alimentación. |
| `FeedDilution_factor` | float | adim. | Factor objetivo aplicado por mezcla (ej. 0.80 ≈ -20% %sol). |

### D) Mineralogía (proxy)
| Columna | Tipo | Descripción |
|---|---:|---|
| `PSD_fines_idx` | float | Índice de finos/arcillas. Driver principal en CLAY. |

### E) Floculante
| Columna | Tipo | Descripción |
|---|---:|---|
| `Floc_gpt` | float | Dosificación de floculante (proxy). En `Regime=FLOC` se simula subdosificación. |

### F) Underflow / descarga
| Columna | Tipo | Descripción |
|---|---:|---|
| `UF_capacity_factor` | float | Factor [0–1] de capacidad de descarga UF. |
| `Qu_m3h` | float | Caudal UF (depende de `Qf_total_m3h` y `UF_capacity_factor`). |
| `Solids_u_pct` | float | % sólidos UF. **Puede incluir fallas** (spikes/stuck/drift/missing). |

### G) Estado del espesador
| Columna | Tipo | Descripción |
|---|---:|---|
| `BedLevel_m` | float | Nivel de cama. |
| `RakeTorque_pct` | float | Torque rastrillos (proxy). |

### H) Turbidez
| Columna | Tipo | Unidad | Descripción |
|---|---:|---:|---|
| `Overflow_Turb_NTU_clean` | float | NTU | Turbidez CLEAN (ground truth). Base para labels. |
| `Overflow_Turb_NTU` | float | NTU | Turbidez medida, corrompida por fallas. |

### I) Operación
| Columna | Tipo | Valores | Descripción |
|---|---|---|---|
| `ControlMode` | category | `AUTO`, `MANUAL` | Modo de control. |
| `OperatorAction` | category | `NONE`, `INCREASE_UF`, `DECREASE_UF`, `INCREASE_FLOC`, `DECREASE_FLOC` | Acción cuando `MANUAL`. |

### J) Umbrales (constantes)
| Columna | Tipo | Descripción |
|---|---:|---|
| `spec_limit_NTU` | float | 80 NTU (spec). |
| `event_limit_NTU` | float | 70 NTU (warning para labels). |

### K) Targets + contexto de campaña
| Columna | Tipo | Descripción |
|---|---:|---|
| `event_now` | int | 1 si CLEAN > 70 sostenido (20 min). |
| `target_event_30m` | int | 1 si habrá evento en 30 min. |
| `event_type` | category | Tipo dominante durante evento (`CLAY`,`UF`,`FLOC`) o `NONE`. |
| `Regime` | category | Régimen programado (`NORMAL`,`CLAY`,`UF`,`FLOC`). |

## Notas para modelado
- Features: usar `Overflow_Turb_NTU` + variables de proceso + `FeedDilution_*` + caudales.
- No usar CLEAN como feature.
- Split temporal estricto; reportar PR-AUC, Recall@Precision, falsas alarmas/día y lead time.
