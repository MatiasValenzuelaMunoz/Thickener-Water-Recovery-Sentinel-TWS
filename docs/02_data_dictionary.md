# Diccionario de datos (fuente única)

Dataset sintético de espesador. CLEAN vs MEDIDA y labels definidos sobre CLEAN.

## Variables

### Tiempo
| Columna | Tipo | Descripción |
|---|---|---|
| `timestamp` | datetime | Marca temporal. |

### Alimentación y mineralogía (proxy)
| Columna | Tipo | Unidad | Descripción |
|---|---:|---:|---|
| `Qf_m3h` | float | m³/h | Caudal de alimentación. Puede tener fallas (spikes/stuck/drift/missing). |
| `Solids_f_pct` | float | % | % sólidos en alimentación (antes de dilución). |
| `PSD_fines_idx` | float | adim. | Índice de finos/arcillas (driver CLAY). |

### Dilución de alimentación (variable explícita — para prescriptivo)
| Columna | Tipo | Unidad | Descripción |
|---|---:|---:|---|
| `FeedDilution_On` | int | - | 1 si dilución está activa. |
| `DilutionWater_m3h` | float | m³/h | Caudal agua de dilución. 0 si OFF. |
| `Solids_f_pct_diluted` | float | % | % sólidos efectivo después de dilución. Def: `Solids_f_pct * Qf_m3h / (Qf_m3h + DilutionWater_m3h)` |

> Nota: estas columnas se incorporarán al simulador para habilitar reglas prescriptivas (CLAY).

### Floculante
| Columna | Tipo | Unidad | Descripción |
|---|---:|---:|---|
| `Floc_gpt` | float | g/t (proxy) | Dosificación de floculante. En `Regime=FLOC` se simula subdosificación. |

### Underflow / descarga
| Columna | Tipo | Unidad | Descripción |
|---|---:|---:|---|
| `UF_capacity_factor` | float | adim. | Capacidad UF (cae por segmentos en `Regime=UF`). |
| `Qu_m3h` | float | m³/h | Caudal UF. |
| `Solids_u_pct` | float | % | % sólidos UF. Puede tener fallas (spikes/stuck/drift/missing). |

### Inventario/mecánica
| Columna | Tipo | Unidad | Descripción |
|---|---:|---:|---|
| `BedLevel_m` | float | m | Nivel de cama. |
| `RakeTorque_pct` | float | % | Torque rastrillos. |

### Turbidez
| Columna | Tipo | Unidad | Descripción |
|---|---:|---:|---|
| `Overflow_Turb_NTU_clean` | float | NTU | Ground truth del proceso. |
| `Overflow_Turb_NTU` | float | NTU | Medición corrompida por fallas. |

### Operación/Control
| Columna | Tipo | Valores | Descripción |
|---|---|---|---|
| `ControlMode` | category | `AUTO`, `MANUAL` | Modo de control. |
| `OperatorAction` | category | `NONE`, `INCREASE_UF`, `DECREASE_UF`, `INCREASE_FLOC`, `DECREASE_FLOC` | Acción en MANUAL. |

### Parámetros/umbral por fila
| Columna | Tipo | Descripción |
|---|---:|---|
| `spec_limit_NTU` | float | Umbral spec (80). |
| `event_limit_NTU` | float | Umbral warning para labels (70). |

### Labels y campañas
| Columna | Tipo | Descripción |
|---|---:|---|
| `event_now` | int | Evento sostenido (CLEAN > 70 por 20 min). |
| `target_event_30m` | int | Evento a +30 min. |
| `event_type` | category | Tipo dominante durante evento: `CLAY`, `UF`, `FLOC`, o `NONE`. |
| `Regime` | category | `NORMAL`, `CLAY`, `UF`, `FLOC`. |
