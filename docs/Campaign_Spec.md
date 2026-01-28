# Campaign Spec — Campañas sintéticas y objetivos de modelado

Este documento describe las **campañas** (mecanismos causales sintéticos) modeladas en el simulador para inducir deterioro de turbidez en overflow.

## Propósito
1) Generar variabilidad realista (no ruido aleatorio).
2) Crear **patrones distintos** por campaña para:
   - entrenar detección temprana (predictivo)
   - evaluar robustez ante diferentes “modos de falla” del proceso
   - habilitar análisis prescriptivo (qué acción conviene)

## Definiciones rápidas
- **CLAY**: incremento de finos/arcillas → peor clarificación, más turbidez, suele requerir ajuste de floc y/o estrategia operativa.
- **UF**: degradación de capacidad/eficiencia de underflow (restricción mecánica/proceso) → sube bed/torque, empeora overflow.
- **FLOC (opcional)**: subdosificación de floculante → turbidez aumenta; respuesta típica es aumentar dosis.

---

## Tabla de impacto (dirección esperada por campaña)

Leyenda:
- ↑ aumenta
- ↓ disminuye
- ↔ neutro/variable
- (sec.) efecto secundario frecuente

| Variable / Señal | CLAY | UF | FLOC |
|---|---:|---:|---:|
| `Overflow_Turb_NTU_clean` | ↑↑ | ↑ | ↑↑ |
| `Overflow_Turb_NTU` (medida) | ↑↑ (+ fallas posibles) | ↑ (+ fallas posibles) | ↑↑ (+ fallas posibles) |
| `PSD_fines_index` | ↑↑ (driver) | ↔ | ↔ |
| `Floc_dose` | ↑ (acción esperada) | ↔ / ↑ (sec.) | ↑↑ (acción directa) |
| `UF_m3h` | ↔ / ↑ (acción compensatoria) | ↓ (capacidad efectiva) / ↑ (acción) | ↔ |
| `Bed_level` | ↑ (sec.) | ↑↑ (driver) | ↑ (sec.) |
| `Rake_torque` | ↑ (sec.) | ↑↑ (driver) | ↑ (sec.) |
| `ControlMode` MANUAL | ↑ probabilidad | ↑ probabilidad | ↑ probabilidad |

> Ajusta la tabla si tus nombres/variables difieren. La idea es documentar “mecanismo → señales → acción”.

---

## Objetivos de modelado por campaña

### Objetivo común (todas)
- **Predictivo**: estimar `P(evento en 30 min)` (`target_event_30m`)
- Restricciones:
  - validación temporal
  - métricas operacionales (false alarms/día, lead time)

### CLAY — Objetivo específico
- Detectar deterioro causado por aumento de finos antes de cruzar 70 NTU sostenido.
- Señales esperadas:
  - subida de `PSD_fines_index`
  - aumento gradual en turbidez clean
  - respuesta vía `Floc_dose` y/o ajustes operacionales
- Evaluación recomendada:
  - recall para eventos CLAY
  - lead time promedio en CLAY
  - sensibilidad a cambios de finos (robustez)

### UF — Objetivo específico
- Anticipar eventos ligados a limitación de underflow (capacidad/estabilidad).
- Señales esperadas:
  - incremento de `Bed_level` y `Rake_torque`
  - degradación dinámica (más “inercial”)
  - acciones: aumentar UF (si posible) o cambios de estrategia
- Evaluación recomendada:
  - recall para eventos UF
  - tasa de falsas alarmas cuando torque/bed suben pero no hay evento
  - interpretación: drivers mecánicos/proceso

### FLOC (opcional) — Objetivo específico
- Detectar subdosificación vs ruido instrumental.
- Señales esperadas:
  - caída o insuficiencia en `Floc_dose`
  - aumento rápido en turbidez clean
- Evaluación recomendada:
  - precisión en detección (evitar alarmas por spikes de sensor)
  - robustez ante fallas tipo `spike`

---

## Prescriptivo (extensión futura)
Una vez entrenado el modelo predictivo:
- reglas simples o recomendador:
  - si riesgo alto + patrón CLAY → sugerir aumentar floc (o revisar feed fines)
  - si riesgo alto + patrón UF → sugerir revisar UF/bed/torque y acción sobre UF
- métrica: reducción esperada de tiempo en evento (simulado) vs falsas alarmas
