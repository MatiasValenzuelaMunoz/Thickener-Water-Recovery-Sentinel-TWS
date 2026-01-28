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

## Salidas esperadas del proyecto (portafolio)
1) Modelo baseline con validación temporal (PR-AUC, falsas alarmas/día).
2) Explicabilidad operacional (drivers coherentes con proceso).
3) Extensión prescriptiva: “qué hacer” según firma (incluye dilución de feed).
