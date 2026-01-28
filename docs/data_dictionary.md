# Diccionario de datos — Thickener Water Recovery Sentinel (TWS)

Este proyecto usa un **dataset sintético** de series temporales para simular operación de un espesador y eventos de turbidez alta.

## Convenciones generales
- Frecuencia típica: **5 min**
- Dos señales de turbidez:
  - `Overflow_Turb_NTU_clean`: estado del proceso (ground truth, sin fallas)
  - `Overflow_Turb_NTU`: medición del sensor con fallas (spikes/drift/missing/stuck)
- Umbrales:
  - `event_limit_NTU = 70` (warning, para labels)
  - `spec_limit_NTU = 80` (spec, KPI)
- Labels:
  - `event_now`: evento sostenido (CLEAN > 70)
  - `target_event_30m`: evento a 30 min

> Nota: Los nombres de columnas pueden evolucionar. Si cambias un nombre en `src/`, actualiza este documento.

---

## Esquema (alto nivel)

### A) Índices y tiempo
| Columna | Tipo | Unidad | Ejemplo | Descripción |
|---|---:|---|---|---|
| `timestamp` | datetime | - | `2026-01-01 00:00:00` | Marca temporal de cada observación. |

---

### B) Variables de proceso (operacionales)
| Columna | Tipo | Unidad | Descripción |
|---|---:|---|---|
| `Qf_m3h` | float | m³/h | Caudal de alimentación (feed). Puede contener faltantes. |
| `Solids_Load` | float | t/h (o adim.) | Carga de sólidos (puede derivarse de caudal y %sol). |
| `PSD_fines_index` | float | adim. [0–1] | Índice de finos (proxy de variabilidad mineralógica). |
| `UF_m3h` | float | m³/h | Caudal de underflow. Variable manipulada/objetivo de acciones. |
| `UF_density` | float | % o adim. | Densidad underflow (proxy de capacidad/operación). |
| `Floc_dose` | float | g/t o adim. | Dosificación de floculante. Variable manipulada. |
| `Rake_torque` | float | % o adim. | Torque / esfuerzo mecánico (proxy de bed / carga). |
| `Bed_level` | float | m o adim. | Nivel de cama (bed). Proxy de inventario/estabilidad. |

> Ajusta unidades según tu simulador (en portafolio basta consistencia interna).

---

### C) Calidad del dato / Instrumentación
| Columna | Tipo | Descripción |
|---|---:|---|
| `sensor_fault` | bool/int | Bandera general de falla de medición (si existe). |
| `fault_type` | category | Tipo de falla: `missing`, `stuck`, `spike`, `drift` (si existe). |

Si tu simulador no exporta estas banderas, puedes:
- mantenerlas como “internas” del simulador, o
- agregarlas para análisis de robustez (recomendado para hito “Sensor health”).

---

### D) Turbidez (variable principal)
| Columna | Tipo | Unidad | Descripción |
|---|---:|---:|---|
| `Overflow_Turb_NTU_clean` | float | NTU | Turbidez de overflow “ideal” del proceso (sin fallas). Usada para etiquetar. |
| `Overflow_Turb_NTU` | float | NTU | Turbidez medida con fallas de instrumentación (lo que vería operación/SCADA). |

---

### E) Control y contexto operacional
| Columna | Tipo | Descripción |
|---|---:|---|
| `ControlMode` | category | `AUTO` / `MANUAL`. |
| `OperatorAction` | category | Acción aplicada (p.ej. `INCREASE_UF`, `DECREASE_UF`, `INCREASE_FLOC`, `DECREASE_FLOC`, `NONE`). |

---

### F) Campañas / eventos (causas sintéticas)
| Columna | Tipo | Descripción |
|---|---:|---|
| `campaign_type` | category | `CLAY`, `UF` (y opcional `FLOC`). Representa la “causa dominante” en el período. |
| `campaign_active` | bool/int | 1 si hay campaña activa. (si existe) |

---

### G) Targets (ML)
| Columna | Tipo | Definición |
|---|---:|---|
| `event_now` | int (0/1) | 1 si existe evento sostenido con `Overflow_Turb_NTU_clean > event_limit_NTU`. |
| `target_event_30m` | int (0/1) | 1 si se observa `event_now` en +30 min (shift temporal). |

---

## Notas de uso (para modelado)
- **Features**: usar `Overflow_Turb_NTU` + variables de proceso/control; evitar usar CLEAN como feature.
- **Validación**: split temporal (walk-forward o train/val/test por bloques) para evitar leakage.
- **Métricas recomendadas**: PR-AUC, Recall@Precision y “false alarms/día”.
