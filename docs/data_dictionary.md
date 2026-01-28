# Diccionario de Datos - Espesador de Relaves
## Versión 1.0 (Contrato Estable)

---

## 📊 ESPECIFICACIONES DEL DATASET

| Parámetro | Valor | Notas |
|-----------|-------|-------|
| **Nombre archivo** | `thickener_timeseries.parquet` | |
| **Formato alternativo** | `thickener_timeseries.csv` | Para verificación |
| **Frecuencia** | 5 minutos | |
| **Duración** | 90 días | 1 Ene 2026 - 31 Mar 2026 |
| **Total registros** | 25,920 | (90 días × 288 puntos/día) |
| **Prevalencia objetivo eventos** | ~5% | Ajustable automáticamente |
| **Límite especificación** | 80 NTU | `spec_limit_NTU` |

---

## 🕐 COLUMNAS - TIEMPO

| Columna | Tipo | Descripción | Ejemplo |
|---------|------|-------------|---------|
| `timestamp` | datetime | Marca de tiempo | 2026-01-01 00:00:00 |

---

## ⚙️ COLUMNAS - PROCESO (SIMULADO)

| Columna | Unidad | Rango Normal | Descripción |
|---------|--------|--------------|-------------|
| `Qf_m3h` | m³/h | 250-900 | Caudal de alimentación |
| `Solids_f_pct` | % | 8-22 | Porcentaje de sólidos en alimentación |
| `PSD_fines_idx` | 0-1 | 0.05-0.85 | Índice de finos/arcillas (0=bajo, 1=alto) |
| `Floc_gpt` | g/t | 5-40 | Dosificación de floculante |
| `UF_capacity_factor` | adim | 0.7-1.0 | Factor de capacidad del underflow |
| `Qu_m3h` | m³/h | 80-450 | Caudal underflow |
| `Solids_u_pct` | % | 45-68 | Porcentaje de sólidos en underflow |
| `BedLevel_m` | m | 0.5-3.5 | Nivel de cama del espesador |
| `RakeTorque_pct` | % | 10-95 | Torque del mecanismo de rastrillo |
| `Overflow_Turb_NTU` | NTU | 5-250 | Turbiedad del overflow |

---

## 🎮 COLUMNA - MODO OPERACIÓN

| Columna | Valores | Descripción |
|---------|---------|-------------|
| `ControlMode` | AUTO / MANUAL | Modo de control operacional |

---

## 📏 COLUMNA - ESPECIFICACIÓN

| Columna | Valor | Descripción |
|---------|-------|-------------|
| `spec_limit_NTU` | 80 NTU | Límite de especificación para turbiedad |

---

## 🏷️ COLUMNAS - ETIQUETAS

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `event_now` | 0/1 | Evento actual (turbiedad > 80 NTU por ≥ 15 min) |
| `target_event_30m` | 0/1 | Evento a predecir (30 minutos adelante) |
| `event_type` | NONE/CLAY/UF/FLOC | Tipo de evento (solo diagnóstico) |

---

## 🔧 FALLAS INSTRUMENTALES SIMULADAS

| Tipo de falla | Tasa | Afecta a | Descripción |
|---------------|------|----------|-------------|
| **Valores faltantes** | 1% por tag | Qf_m3h, Solids_u_pct, Overflow_Turb_NTU | Datos ausentes aleatorios |
| **Spikes** | 2 por día por tag | Qf_m3h, Solids_u_pct, Overflow_Turb_NTU | Valores extremos puntuales |
| **Sensor pegado** | 2 cada 30 días por tag | Qf_m3h, Solids_u_pct, Overflow_Turb_NTU | Valor constante por 2-6 horas |
| **Drift** | 1 cada 90 días por tag | Qf_m3h, Solids_u_pct, Overflow_Turb_NTU | Deriva lenta del sensor |

---

## 📈 RANGOS DE TURBIEDAD ESPERADOS

| Estadístico | Valor NTU | Interpretación |
|-------------|-----------|----------------|
| **Mediana** | 20-40 | Operación normal |
| **P90** | 40-60 | Atención |
| **P95** | 70-90 | Cerca del límite |
| **P99** | 100-150 | Eventos severos |
| **Máximo** | 180-250 | Crisis operacional |

---

## 🔗 ARCHIVOS RELACIONADOS

- `src/simulate.py` - Generador del dataset
- `src/quick_checks.py` - Validaciones rápidas
- `docs/event_definition.md` - Lógica de eventos
- `docs/campaign_specs.md` - Especificación de campañas