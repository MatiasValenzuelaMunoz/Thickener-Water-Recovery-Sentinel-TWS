# TWS — Overview (portafolio)

## Qué es
**Thickener Water Recovery Sentinel (TWS)** es un proyecto personal para demostrar analítica aplicada a **procesos minero-metalúrgicos**, enfocado en **alerta temprana** de deterioro de clarificación (turbidez alta en overflow) usando un **dataset sintético reproducible** (sin datos sensibles).

## Por qué importa en planta
Eventos sostenidos de turbidez alta:
- reducen recuperación de agua
- aumentan variabilidad operacional
- incrementan intervención manual y riesgo de restricciones (bed/torque/descarga)

## Idea diferenciadora
Separación explícita entre:
- `Overflow_Turb_NTU_clean` (ground truth del proceso) → define labels
- `Overflow_Turb_NTU` (medición con fallas) → se usa como feature realista

Esto permite entrenar modelos robustos **sin contaminar el etiquetado** por drift/spikes/missing.

## Umbrales
- `event_limit_NTU = 70` (warning): base de etiquetas y calibración
- `spec_limit_NTU = 80` (spec): KPI operacional

## Campañas simuladas (causas)
- `CLAY`: ataque de finos/arcillas
- `UF`: degradación de capacidad de underflow (restricción de descarga)
- `FLOC`: subdosificación/problemas de preparación de floculante

## Escenario del dataset (contexto operacional)
Este dataset representa la operación de **un espesador de relaves** (una línea) en una planta concentradora, con variabilidad de mineral, restricciones de descarga y acciones de operador.

### Temporalidad y resolución
- Ventana simulada: **90 días continuos**
- Frecuencia de muestreo: **cada 5 minutos**
- Total típico: **25,920 registros**
- Horizonte de predicción objetivo: **30 min** (`target_event_30m`)
- Definición de evento: turbidez CLEAN > 70 NTU sostenido **20 min** (`sustain_points=4`)

### Dimensiones “operacionales” (caudales)
- **Caudal total a espesador** (tag SCADA): `Qf_m3h` (m³/h)  
  - En este proyecto, `Qf_m3h` es alias de `Qf_total_m3h` (caudal total real al espesador).
- Descomposición del caudal:
  - `Qf_pulp_m3h`: caudal de pulpa base (sin agua añadida)
  - `Qf_dilution_m3h`: agua de dilución (acción operacional)
  - `Qf_total_m3h = Qf_pulp_m3h + Qf_dilution_m3h`

> Interpretación: cuando `FeedDilution_On=1`, el operador agrega agua, sube `Qf_total_m3h` y baja `Solids_f_pct` por mezcla.

### Rangos típicos (del dataset actual)
- `Qf_total_m3h`:
  - media: **579.42 m³/h**
  - P50: **569.61 m³/h**
  - P95: **776.36 m³/h**
- `Solids_f_pct`:
  - media: **14.03%**
  - P50: **14.03%**
  - P95: **17.09%**
- `Overflow_Turb_NTU_clean`: 5–160 NTU (cap)
- Modo MANUAL: objetivo 15–30% del tiempo

### Capacidad equivalente de planta (balance rápido)
Para dar escala física, se estima capacidad equivalente usando:
- densidad de sólido: **ρ_s = 2.7 t/m³**
- recuperación en peso a concentrado (mass pull): **8%**
- supuesto: este dataset representa **1 espesador / 1 línea**; un escenario industrial realista considera **2 espesadores en paralelo**.

**Estimación por línea (1 espesador):**
- Sólidos a relaves: ~**219 t/h** (≈ **5.3 ktpd**)
- Alimentación equivalente a planta: relaves / 0.92 ≈ **239 t/h** (≈ **5.7 ktpd**)

**Estimación planta total (2 espesadores en paralelo):**
- Alimentación equivalente a planta: ~**477 t/h** (≈ **11.4 ktpd**)
- Concentrado (8%): ~**38 t/h** (≈ **0.9 ktpd**)

> Estas cifras son “orden de magnitud” (back-of-envelope) para contextualizar el dataset; no representan una planta específica.

### Qué significa “realista” aquí
No busca replicar una operación particular, sino capturar **patrones operacionales plausibles**:
- campañas causales (CLAY/UF/FLOC),
- retardos (lags) implícitos en el proceso,
- fallas instrumentales localizadas (missing/stuck/spikes/drift),
- acción prescriptiva explícita (dilución de feed).

## Acción operacional modelada explícitamente (prescriptivo)
El dataset incluye una acción “bombero” realista: **dilución de alimentación** para ganar tiempo ante mala clarificación.
Se refleja en:
- `FeedDilution_On` (0/1)
- `Qf_dilution_m3h` (agua añadida)
- `Qf_total_m3h` (caudal total al espesador)
- `Solids_f_pct` (baja por mezcla)

> Nota: `Qf_m3h` se mantiene como alias compatible y representa el caudal total (`Qf_total_m3h`).

## Salidas esperadas del proyecto (portafolio)
1) Modelo baseline con validación temporal (PR-AUC, falsas alarmas/día).
2) Explicabilidad operacional (drivers coherentes con proceso).
3) Extensión prescriptiva: “qué hacer” según firma (incluye dilución de feed).
