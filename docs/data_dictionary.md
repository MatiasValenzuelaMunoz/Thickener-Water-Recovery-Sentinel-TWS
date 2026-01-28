# Diccionario de datos — Thickener Water Recovery Sentinel (TWS)

Dataset sintético de series temporales (espesador) para anticipar eventos de turbidez alta.
Frecuencia típica: **5 min**. Horizonte de predicción: **30 min**.

## Convenciones clave
- **CLEAN vs MEDIDA**:
  - `Overflow_Turb_NTU_clean`: turbidez "ground truth" del proceso (sin fallas).
  - `Overflow_Turb_NTU`: turbidez medida, **corrompida** por fallas (spikes/stuck/drift/missing).
- Umbrales:
  - `event_limit_NTU = 70` → warning (base de etiquetas)
  - `spec_limit_NTU = 80` → spec (KPI)
- Etiquetas:
  - `event_now`: evento sostenido sobre el umbral en CLEAN
  - `target_event_30m`: evento a 30 minutos (shift)

## Tabla de variables

### A) Tiempo
| Columna | Tipo | Ejemplo | Descripción |
|---|---|---|---|
| `timestamp` | datetime | `2026-01-01 00:00:00` | Marca temporal. |

### B) Alimentación (feed) y mineralogía (proxy)
| Columna | Tipo | Unidad | Descripción |
|---|---:|---:|---|
| `Qf_m3h` | float | m³/h | Caudal de alimentación. **Puede incluir fallas** (spikes/stuck/drift/missing). |
| `Solids_f_pct` | float | % | % sólidos en alimentación. Señal de densidad/carga. |
| `PSD_fines_idx` | float | adim. [0–1] | Índice de finos/arcillas. Driver principal en campaña CLAY. |

### C) Floculante / química (proxy)
| Columna | Tipo | Unidad | Descripción |
|---|---:|---:|---|
| `Floc_gpt` | float | g/t (proxy) | Dosificación de floculante. En régimen `FLOC` se simula subdosificación (factor 0.55–0.75). |

### D) Descarga / underflow
| Columna | Tipo | Unidad | Descripción |
|---|---:|---:|---|
| `UF_capacity_factor` | float | adim. [0–1] | Factor de capacidad de UF. En régimen `UF` baja intermitentemente (0.70–0.92). |
| `Qu_m3h` | float | m³/h | Caudal de underflow. Depende de `Qf_m3h` y `UF_capacity_factor`. |
| `Solids_u_pct` | float | % | % sólidos en underflow. **Puede incluir fallas** (spikes/stuck/drift/missing). |

### E) Estado del espesador (inventario y mecánica)
| Columna | Tipo | Unidad | Descripción |
|---|---:|---:|---|
| `BedLevel_m` | float | m | Nivel de cama (bed). Responde a carga, finos y restricción UF. |
| `RakeTorque_pct` | float | % (proxy) | Torque de rastrillos. Subirá con bed alto y finos. |

### F) Turbidez (variable objetivo de negocio)
| Columna | Tipo | Unidad | Descripción |
|---|---:|---:|---|
| `Overflow_Turb_NTU_clean` | float | NTU | Turbidez CLEAN (proceso/ground truth). Se calcula con estrés + deadband + ruido + efecto de acciones. |
| `Overflow_Turb_NTU` | float | NTU | Turbidez medida: parte igual a CLEAN y luego **se corrompe** por fallas. |

### G) Control y operación
| Columna | Tipo | Valores | Descripción |
|---|---|---|---|
| `ControlMode` | category | `AUTO`, `MANUAL` | Modo de control. Probabilidad de MANUAL aumenta con bed/torque altos y durante regímenes UF/FLOC. |
| `OperatorAction` | category | `NONE`, `INCREASE_UF`, `DECREASE_UF`, `INCREASE_FLOC`, `DECREASE_FLOC` | Acciones solo cuando `ControlMode=MANUAL`. Afectan levemente la turbidez vía `action_penalty`. |

### H) Parámetros (constantes por fila, para trazabilidad)
| Columna | Tipo | Descripción |
|---|---:|---|
| `spec_limit_NTU` | float | Umbral spec (80). |
| `event_limit_NTU` | float | Umbral warning para labels (70). |

### I) Etiquetas y contexto de campaña
| Columna | Tipo | Descripción |
|---|---:|---|
| `event_now` | int (0/1) | Evento sostenido: CLEAN > 70 por `sustain_points` (4 puntos = 20 min). |
| `target_event_30m` | int (0/1) | `event_now` desplazado -6 puntos (30 min). |
| `event_type` | category | Tipo dominante durante evento (`CLAY`, `UF`, `FLOC`) o `NONE` si no hay evento. |
| `Regime` | category | Régimen programado: `NORMAL`, `CLAY`, `UF`, `FLOC`. |

## Notas para modelado (portafolio)
- **No usar** `Overflow_Turb_NTU_clean` como feature (es ground truth).
- Para robustez industrial, entrenar con features que incluyan `Overflow_Turb_NTU` (con fallas) y variables de proceso.
- Split temporal estricto; métricas sugeridas: PR-AUC, Recall@Precision, falsas alarmas/día, lead time.
