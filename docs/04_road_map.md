# Roadmap Completo — Sistema de Soporte para Optimización de Espesadores (TWS)

## Objetivo del proyecto
Construir un sistema end-to-end que combine experiencia operativa en gestión de relaves con analítica avanzada para:

- **Predecir** eventos de turbidez alta con **30 min** de anticipación (`target_event_30m`).
- **Diagnosticar** causas raíz (CLAY / UF / FLOC) con explicabilidad alineada a física de procesos.
- **Prescribir** acciones jerárquicas mediante un **playbook de tres niveles** (Operador / Supervisor / Superintendencia).
- **Cuantificar** el impacto económico de decisiones (agua, floculante, estabilidad, riesgo de parada).

---

## Hitos del proyecto (versión mejorada)

### Hito 1 — Dataset industrial-grade con realismo operacional
**Objetivo:** generar un dataset sintético que capture retardos operacionales, estados de equipos y comportamiento humano.

| Componente | Descripción | Entregables | Criterios de éxito |
|---|---|---|---|
| Variables base | Feed rate, bed height, torque, turbidez, UF flow/density | `data/processed/thickener_timeseries.parquet` | Dataset reproducible (misma semilla → mismo resultado), rangos coherentes |
| Retardos operacionales | Lag medición turbidez (5–15 min), retardo acción→efecto (20–40 min) | `src/simulate_fixed.py` (o módulo dedicado a delays) | Correlación cruzada realista entre acción y efecto |
| Estados de equipos | Estado bomba UF (Off/On/Alarm/Maint), posiciones válvula (si se modela) | `data/processed/equipment_states.parquet` (si aplica) | Estados coherentes con restricciones mecánicas |
| Intervenciones humanas | Switch AUTO/MANUAL, ajustes dosis, **dilución feed** | `ControlMode`, `OperatorAction`, `FeedDilution_On`, `Qf_total_m3h` | 15–30% del tiempo en MANUAL |
| Validación | KPIs operacionales (P95/P99), campañas diferenciadas | Notebook/Script de validación | Eventos 4–6%, reproducibilidad total |

> Nota (estado actual en TWS): ya existe **dilución de feed explícita** (más agua), modelada con `Qf_pulp_m3h`, `Qf_dilution_m3h`, `Qf_total_m3h` y `Solids_f_pct`.

---

### Hito 2 — EDA operacional con enfoque en turnos
**Objetivo:** entender patrones desde la perspectiva del supervisor de turno.

| Análisis | Métricas | Visualización | Insights esperados |
|---|---|---|---|
| Episodios de crisis | duración, severidad (NTU-max), tiempo a recuperación | Timeline con overlays (Regime, eventos, acciones) | Patrones por campaña (CLAY vs UF vs FLOC) |
| Efectividad por turno | `%_time_in_alarm`, `intervention_count`, `floculant_ton` (proxy) | Dashboard comparativo A/B/C (si se simula turno) | Turnos con “mejores prácticas” |
| Costo de eventos | agua fresca extra, floc extra, tonelaje “perdido” (proxy) | heatmap costo vs duración | Estimar costo mínimo por evento (escala) |
| Análisis de intervenciones | efecto de `FeedDilution_On`, cambios de floc | before/after | Lead time efectivo de acciones correctivas |

**Entregable principal:** `notebooks/02_operational_eda.ipynb` con ≥3 figuras listas para presentación.

---

### Hito 3 — Baseline predictivo con features de proceso
**Objetivo:** modelo que prediga `target_event_30m` con validación temporal estricta.

| Componente | Implementación | Validación | Métricas objetivo |
|---|---|---|---|
| Split temporal | Bloques semanales (5 días train, 2 días test) | Walk-forward (8+ bloques) | Sin leakage temporal |
| Features base | Lags (5,10,15,30,60 min) de variables MEDIDAS | `src/feature_engineering.py` (o notebook) | 50+ features iniciales |
| Features de proceso | índices derivados (ej. floc deficit proxy, stress proxies) | fórmulas derivadas | +10% PR-AUC vs baseline simple |
| Modelo baseline | LightGBM o XGBoost con class_weight | tuning (Optuna/Hyperopt) | PR-AUC > 0.65 (objetivo inicial) |
| Calibración | threshold operacional | curva cost-benefit | Recall@Precision=0.70 > 0.60 |
| Validación por escenario | métricas separadas CLAY/UF/FLOC | matriz confusión por tipo | Recall CLAY > 0.75 (meta) |

**Entregables:**
- `models/baseline_lgbm.pkl`
- `notebooks/03_model_training_evaluation.ipynb`
- `reports/baseline_metrics.json`

---

### Hito 4 — Explicabilidad + diagnóstico asistido
**Objetivo:** conectar predicciones con lógica de proceso mediante diagnóstico interpretable.

| Técnica | Aplicación | Salida | Criterio de calidad |
|---|---|---|---|
| SHAP global | importancia por campaña | gráficos de importancia | variables “de proceso” en top 10 |
| SHAP local | explicación por alerta | waterfall plots | coherencia con física (UF: bed↑, torque↑) |
| Diagnóstico automático | clasificador causa probable (CLAY/UF/FLOC) | `src/diagnosis_engine.py` | F1 > 0.70 (tipos balanceados) |
| Reporte diagnóstico | plantilla por alerta con evidencia | generador markdown | 90% “creíbles” para operación |
| Análisis de errores | falsas alarmas vs misses por escenario | pattern analysis | <2 falsas alarmas/turno en operación estable |

**Ejemplo de reporte (formato):**
```markdown
ALERTA #457 — 14:30 2024-03-15
Riesgo: ALTO (92%) | ETA: 25 min
Diagnóstico: RESTRICCIÓN UF MECÁNICA (Confianza: 85%)

Evidencia:
1) BedLevel_m: P98 (▲ 0.8 m en 2 h) [SHAP +0.18]
2) RakeTorque_pct: +14% últimas 90 min (trend continuo) [SHAP +0.15]
3) Qu_m3h: constante a pesar de acción/condición [SHAP +0.12]
```

**Entregables:**
- `src/diagnosis_engine.py`
- `notebooks/04_explainability.ipynb`
- `templates/diagnosis_report.md`

---

### Hito 5 — Playbook de tres niveles (prescriptivo)
**Objetivo:** recomendaciones escaladas según severidad y rol operativo.

#### Nivel 1 — Acciones inmediatas (Operador, <5 min)
**Activación:** Score > 10 y confianza > 80%

| Escenario | Firma | Acción 1-click | Costo/beneficio (ejemplo) |
|---|---|---|---|
| UF restringido | bed>P90, torque↗, Solids_u_pct↓ | Activar dilución UF / aumentar stroke | evita parada ($/h) |
| CLAY agudo | finos↑, turbidez↑ | **Aumentar dilución feed** (`FeedDilution_On`) | gana tiempo diagnóstico |
| FLOC crítico | Floc_gpt bajo vs necesidad, turbidez↗ | +25% floc / verificar preparación | recupera control rápido |
| Sensor sucio | turbidez medida “plana” vs resto señales | marcar sensor no confiable | evita actuar con dato falso |

**Interfaz (conceptual):** dashboard operador con botones y confirmación.

#### Nivel 2 — Investigación guiada (Supervisor, 15–30 min)
**Activación:** Score 5–10 o confianza 60–80%

Checklist ejemplo (CLAY):
```yaml
INVESTIGACIÓN GUIADA — SOSPECHA ARCILLA
1) Confirmar fuente mineral:
   - Rajo actual: ________
   - Reporte geología arcillas: [Sí/No/No sé]

2) Verificar floculante:
   - Solución madre <24h: [Sí/No]
   - Agua preparación NTU<10: [Sí/No]
   - Prueba jarras último turno: [Sí/No]

3) Acciones:
   [ ] Tomar muestra alimentación P80 urgente
   [ ] Contactar lab para prueba polímero B
   [ ] Ajustar dilución feed +8% por 2h

TIEMPO: 25 min | CONFIANZA POST-CHECK: [CALCULAR]
```

#### Nivel 3 — Acciones estratégicas (Superintendencia, horas/días)
**Activación:** evento >2 h, múltiples unidades, impacto balance hídrico

Reporte ejemplo:
```markdown
INFORME ESTRATÉGICO — EVENTO EXTENDIDO
Espesador: S-101 | Duración: 2h 15min | Estado: ACTIVO

IMPACTO:
- Floculante: +35% vs normal (▲ $850 USD)
- Agua fresca: 320 m³ extra (▲ $640 USD)
- Tonelaje: -8% por restricción

ACCIONES ESTRATÉGICAS:
[ ] Revisar plan minero (evitar rajo arcilloso)
[ ] Evaluar coagulante primario (CAPEX)
[ ] Ajustar blend mineral próximas 72h
```

**Sistema de scoring (conceptual):**
```text
Score_Valor = (Beneficio_Evitado * Prob_Éxito) / (Costo_Acción * Riesgo_Colateral)

Umbrales:
- Score > 10: Nivel 1
- Score 5–10: Nivel 2
- Score 2–5: Nivel 3
- Score < 2: Solo monitoreo
```

**Entregables:**
- `src/playbook_engine.py`
- `templates/checklists/` (CLAY, UF, FLOC, SENSOR)
- `templates/strategic_reports/`
- Dashboards por rol (prototipos)

---

### Hito 6 — Sensor health + robustez industrial
**Objetivo:** distinguir problema de proceso vs falla instrumental.

| Detección | Método | Acción | Umbral (ejemplo) |
|---|---|---|---|
| Sensor stuck | varianza última hora ≈ 0 | marcar no confiable | var < 0.01% del rango |
| Drift gradual | comparación vs variables correlacionadas | generar OT mantenimiento | diff > 5% por 24 h |
| Spikes/ruido | filtro Hampel | suavizar + alertar | z-score > 3.5 |
| Missing data | patrón random vs bloque | imputación + flag | >10% missing en 1 h |
| Índice confianza | combinación métricas | ponderar predicción | score 0–100 |

Índice de confianza por predicción:
```python
confidence_score = 0.7 * sensor_health + 0.2 * model_confidence + 0.1 * data_completeness
if confidence_score < 60:
    recommendation = "Verificar instrumentación antes de actuar"
```

**Entregables:**
- `src/sensor_health_monitor.py`
- `notebooks/06_sensor_health.ipynb`
- `reports/sensor_performance.json`

---

### Hito 7 — Simulación de impacto económico (nuevo)
**Objetivo:** traducir mejoras operativas a impacto financiero (justificación gerencial).

| Métrica | Cálculo | Datos necesarios | Dashboard |
|---|---|---|---|
| Ahorro floculante | ΔEventos * consumo_evento * precio | consumo + precio polímero | ahorro mensual |
| Ahorro agua fresca | ΔUso_dilución_emergencia * costo_m³ | costo agua | comparativo mensual |
| Incremento producción | ΔTonelaje_no_perdido * margen | margen por tonelada | ROI acumulado |
| Reducción riesgo | Prob_parada * costo_parada | costo parada ($/h) | heatmap riesgo |
| ROI sistema | (ahorro - costo) / costo | costos + ahorros | resumen ejecutivo |

Reporte mensual ejemplo:
```markdown
IMPACTO ECONÓMICO — SISTEMA ALERTAS ESPESADORES
Período: Marzo 2024

AHORROS DIRECTOS:
- Floculante: $12,500 USD (▼18% vs febrero)
- Agua fresca: $8,200 USD (▼22% vs febrero)
- Producción: $45,000 USD (▲3% eficiencia)

REDUCCIÓN DE RIESGO:
- Eventos críticos: 3 vs 11 (▼73%)
- Horas en alarma: 42h vs 156h (▼73%)
- Probabilidad parada: 2% vs 8% (▼75%)

ROI ACUMULADO (3 meses):
- Inversión: $120,000 USD
- Ahorro: $198,000 USD
- ROI: 65% | Payback: 5.4 meses
```

**Entregables:**
- `src/economic_calculator.py`
- dashboard ejecutivo (prototipo)
- `reports/monthly_impact_*.md`

---

## Cronograma estimado (semanas)
| Semana | Hitos | Entregables clave |
|---|---|---|
| 1–2 | Hito 1 | Dataset completo + documentación |
| 3 | Hito 2 | EDA operacional + figuras |
| 4–5 | Hito 3 | Baseline entrenado + métricas |
| 6 | Hito 4 | Explicabilidad + diagnóstico |
| 7–8 | Hito 5 | Playbook + templates |
| 9 | Hito 6 | Sensor health + índice confianza |
| 10 | Hito 7 | Calculadora ROI + reporte |
| 11–12 | Integración + documentación | Demo final + docs completas |

---

## Métricas de éxito globales
| KPI | Objetivo | Métrica |
|---|---|---|
| Predictivo | PR-AUC > 0.70 | `metrics/pr_auc` |
| Lead time | mediana > 25 min | `metrics/lead_time_median` |
| Falsas alarmas | < 2 por turno operativo | `metrics/false_alarms_per_shift` |
| Tiempo respuesta | < 10 min (Nivel 1), < 30 min (Nivel 2) | `metrics/response_time_by_level` |
| ROI económico | > 50% en 6 meses | `economics/roi_6months` |
| Adopción operacional | > 80% alertas con acción confirmada | `operations/action_confirmation_rate` |

---

## Riesgos y mitigaciones
| Riesgo | Impacto | Probabilidad | Mitigación |
|---|---|---:|---|
| Dataset poco realista | modelo no generaliza | media | validación con expertos desde Hito 1 |
| Falsa alarma alta | fatiga operador / desuso | alta | umbral operacional + métricas falsas alarmas/turno |
| Complejidad playbook | difícil de implementar | media | prototipar primero CLAY y UF |
| Resistencia al cambio | baja adopción | media | involucrar usuarios, entrenamiento práctico |
| FLOC subrepresentado | diagnóstico incompleto | media | ajustar severidad/ponderaciones si se requiere |

---

## Stack tecnológico (solo referencia)
- Datos: Python (pandas/numpy), Parquet
- Modelado: LightGBM / scikit-learn, Optuna (tuning)
- Explicabilidad: SHAP
- Visualización: Plotly / Dash o Streamlit
- Producción (conceptual): FastAPI, Docker
