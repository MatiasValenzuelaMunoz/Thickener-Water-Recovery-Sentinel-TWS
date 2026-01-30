# Bitácora del proyecto (Engineering Log) — TWS

Esta bitácora registra decisiones de diseño y calibración del dataset sintético, con énfasis en realismo operacional y alineamiento con rangos sugeridos por metalurgia (espesador convencional Cu/Mo).

> Convención: cuando se habla de turbidez para evaluación de proceso se usa `Overflow_Turb_NTU_clean` (ground truth). La variable `Overflow_Turb_NTU` representa medición con fallas instrumentales y se usa como feature realista.

---

## 2026-01-30 — Alineamiento con rangos metalurgista (turbidez 50/100/200)
### Objetivo
Alinear el dataset a un esquema operacional tipo:
- **Zona verde:** turbidez CLEAN < 50 NTU
- **Degradación:** 50–100 NTU (meta ~15% del tiempo)
- **Crítico:** >100 NTU
- **Spec (severidad alta):** >200 NTU
- **Evento (crisis sostenida):** >100 NTU por ≥20 min (meta 3–6% para ML)

### Cambios conceptuales adoptados
- Se interpreta la recomendación “85% normal / 15% eventos” como:
  - **~85% en zona verde de clarificación** y
  - **~15% degradado** (turbidez en 50–100),
  - **no** como “15% de crisis sostenidas” (`event_now`), ya que eso suele ser excesivo para operación real.

### Evidencia y resultados (corridas)
#### Corrida A — Umbral actualizado (100 NTU) con calibración limitada por `scale_search_hi`
- `event_limit_NTU = 100`, `spec_limit_NTU = 200`
- Resultado:
  - Eventos sostenidos (>100 por 20 min): ~2.73% (bajo vs objetivo 3–6%)
  - Verde (<50): ~80%
  - Degradado (50–100): ~13.5% (cercano a meta)
  - Crítico (>100): ~6.5%

**Diagnóstico:** el calibrador llegó al techo de búsqueda (`scale ≈ scale_search_hi`), impidiendo llegar a la prevalencia objetivo de eventos.

#### Corrida B — Aumento de capacidad de calibración (permitir `scale` mayor)
- Ajuste: aumentar rango de búsqueda de escala (permitió `scale=4500`)
- Resultado:
  - Eventos sostenidos: ~4.53% ✓
  - Degradado (50–100): ~11.6% (bajó)
  - Crítico (>100): ~9.2% (subió)
  - Spec >200: ~2.6% (subió)
  - Turbidez alcanzó el cap (`turb_max`), lo que puede saturar extremos.

**Interpretación:** al empujar escala, parte de la masa del degradado migra a crítico y aparecen más puntos >200.

#### Corrida C (seleccionada) — Ajuste de forma vía `deadband` para equilibrar degradado/crítico sin saturación
- Archivo generado: `data/processed/thickener_timeseries_deadband0p3_sp4.parquet`
- Parámetro clave: `deadband = 0.30`
- Resultado (CLEAN):
  - Verde (<50): **77.78%**
  - Degradado (50–100): **12.78%** (cerca de ~15%; aceptable)
  - Crítico (>100): **9.44%**
  - Spec >200: **0.69%**
  - Eventos sostenidos (>100 por ≥20 min): **5.10%** ✓
  - Mediana: **36.5 NTU** (verde realista)
  - Máximo: **344.6 NTU** (severo pero sin saturación a cap)

### Decisión
Se adopta `deadband=0.30` como configuración preferida del escenario, porque:
- mantiene prevalencia de eventos útil para modelado (3–6%),
- mantiene degradación cercana al ~15% objetivo,
- mantiene cola severa realista sin saturación artificial.

### Notas pendientes
- Las bandas mecánicas/UF (bed/torque/UF density) deben evaluarse con criterio **de alerta/crítico y persistencia**, no como “todo simultáneamente verde”, porque eso es demasiado estricto punto a punto.
- Futuro: agregar métricas de persistencia (ej. bed > 3.0 m sostenido 30 min; torque trend %/h).
