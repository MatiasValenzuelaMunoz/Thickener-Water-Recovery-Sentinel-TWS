# Propuesta de valor 

## Qué problema ataco
La operación necesita decisiones “hoy”, no reportes “de ayer”.
En procesos minero-metalúrgicos, la variabilidad y las restricciones operacionales hacen que las soluciones genéricas fallen.

## Cómo lo resuelvo
Combino conocimiento de planta + analítica para construir:
- indicadores operacionales accionables
- modelos predictivos con evaluación temporal (sin leakage)
- componentes prescriptivos (recomendación de acción) cuando corresponde

## Evidencia en este repo (TWS)
- Dataset sintético realista de espesador con:
  - campañas (CLAY/UF)
  - AUTO/MANUAL y acciones de operador
  - fallas de instrumentación (sensor health)
- Etiquetas definidas sobre “ground truth” (CLEAN) para evitar sesgos por fallas de sensor
- Validación con KPIs objetivos (prevalencia, P95/P99, manual rate)

## Qué entregable imagino en producción
- alerta temprana de riesgo (horizonte 30 min)
- explicación de drivers (features + SHAP / importancias)
- recomendación simple: acción sugerida y confianza
