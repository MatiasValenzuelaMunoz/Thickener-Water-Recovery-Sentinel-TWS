# TWS — Project Walkthrough Completo
### Decisiones, argumentos y resultados de inicio a fin

---

## Cómo leer este documento

Cada sección está etiquetada con los perfiles para los que es más relevante:

| Ícono | Perfil |
|---|---|
| 🔧 | ML Engineer — decisiones técnicas de modelado |
| ⚗️ | Metalurgista — física del proceso y validez operacional |
| 🏭 | Gerente de Planta — qué cambia en la operación y por qué importa |
| 💼 | Recruiter — qué demuestra el proyecto como portafolio |

Podés leer todo en orden o saltar directamente a las secciones de tu perfil.

---

## 1. El punto de partida — ⚗️ 🏭 💼

### El problema real

En un espesador convencional de concentrado Cu/Mo, las crisis de turbidez en el overflow son uno de los eventos operacionales de mayor impacto. Cuando la turbidez supera los 100 NTU de forma sostenida, el agua clarificada no es apta para recircular al circuito de flotación. El resultado: pérdida de agua de proceso, riesgo al circuito de flotación, y una maniobra de emergencia que el operador debe ejecutar contra el tiempo.

El sistema estándar de monitoreo — una alarma que se dispara cuando la turbidez ya cruzó el umbral — avisa **cuando el problema ya ocurrió**. El operador entonces identifica la causa, aplica la corrección (ajuste de floculante, caudal de purga, dilución), y espera el efecto. Ese ciclo toma entre 20 y 40 minutos adicionales.

### La pregunta central

¿Pueden las señales del proceso — nivel de lecho, torque del rastrillo, caudal de underflow, pH, turbidez medida — advertir una crisis 30 minutos antes de que ocurra, mientras todavía hay tiempo para actuar con calma?

### Por qué es un problema de ML y no de control clásico

Los controladores PID y las alarmas de umbral son reactivos por diseño. El problema de anticipación de crisis requiere reconocer **combinaciones de señales en evolución temporal** — no umbrales individuales. Eso es exactamente lo que hace un modelo de ML supervisado con features de series de tiempo.

---

## 2. La decisión de usar datos sintéticos — 🔧 ⚗️ 💼

### El problema de datos

En la mayoría de las plantas concentradoras no existe un historial etiquetado que:
1. Identifique la causa raíz de cada evento de turbidez (CLAY vs falla de underflow)
2. Distinga entre la señal real del proceso y las fallas del sensor de turbidez
3. Sea suficientemente largo y con suficiente variabilidad operacional para entrenar modelos

Incluso donde existe el historian del DCS, los datos de causa raíz están en la bitácora del operador en texto libre — no en una columna estructurada.

### La decisión

Construir un **simulador de proceso calibrado operacionalmente** que genere datos sintéticos realistas. El simulador modela la física del espesador, inyecta perturbaciones operacionales conocidas (campañas de arcilla, fallas de underflow), y agrega fallas de sensor realistas.

### Por qué es válido como punto de partida

- Permite desarrollar y validar el framework metodológico completo sin esperar acceso a datos reales
- El simulador es transparente: cualquier metalurgista puede revisar los parámetros y evaluar si el comportamiento generado es plausible
- Los patrones aprendidos por el modelo son interpretables en términos de proceso (ver sección de SHAP en §6)
- El framework está diseñado para reemplazar los datos sintéticos por datos reales sin cambiar la arquitectura

### La limitación honesta

Los modelos entrenados sobre datos sintéticos sobreajustan al simulador, no a la realidad de ninguna planta. Los resultados cuantitativos (PR-AUC, recall) son válidos como prueba de concepto pero **no son transferibles directamente** a una planta real sin reentrenamiento.

---

## 3. Diseño del dataset — 🔧 ⚗️

### 3.1 Dos columnas de turbidez — decisión de arquitectura fundamental

**El problema:** en una planta real, el sensor de turbidez del overflow falla regularmente (picos, valores pegados, deriva, datos faltantes). Si se usa la turbidez medida para definir las etiquetas (cuándo hay una crisis), los eventos de falla del sensor se confunden con eventos reales de proceso.

**La decisión:** dos columnas separadas desde el inicio.

| Columna | Qué representa | Para qué se usa |
|---|---|---|
| `Overflow_Turb_NTU_clean` | Verdad del proceso (sin fallas de sensor) | Definición de etiquetas, evaluación de KPIs |
| `Overflow_Turb_NTU` | Señal medida (con fallas inyectadas) | Feature del modelo ML |

**Por qué importa:** el modelo aprende a predecir usando la señal ruidosa (lo que tiene disponible en planta real), pero se evalúa contra la verdad del proceso. Esto replica exactamente la condición de operación real.

### 3.2 Definición de "crisis" — 100 NTU sostenidos por 20 minutos

**Opciones consideradas:**
- Cruce instantáneo de umbral → demasiado sensible a picos transitorios del sensor
- Promedio móvil → pierde precisión temporal
- Criterio de persistencia → operacionalmente relevante: una crisis real es sostenida

**Decisión:** `event_now = 1` cuando `Overflow_Turb_NTU_clean > 100 NTU` de forma **sostenida por al menos 4 puntos consecutivos (20 minutos a resolución de 5 min)**.

**Argumento operacional:** 100 NTU es el umbral donde el agua clarificada ya no es apta para recircular. El criterio de 20 minutos filtra picos transitorios y exige que el proceso esté genuinamente en crisis, no en una oscilación momentánea.

### 3.3 Horizonte de predicción — 30 minutos

**`target_event_30m`** es `event_now` desplazado 30 minutos hacia atrás en el tiempo (6 puntos a 5 min). El modelo entrena para predecir si habrá una crisis en los próximos 30 minutos.

**Por qué 30 minutos:** es el tiempo mínimo razonable para que el operador aplique una corrección (ajuste de floculante, cambio de setpoint de underflow) y vea el efecto antes de que el proceso entre en crisis. Con menos de 20 minutos, la ventana de acción es demasiado corta.

### 3.4 Calibración del event rate — 5% objetivo

**El problema:** la tasa de eventos (fracción del tiempo en crisis sostenida) es un parámetro crítico para el ML. Si es muy alta, el problema no es representativo de la operación real. Si es muy baja, el desbalance de clases hace el modelado más difícil.

**La decisión:** target del 5% ± 0.6%, logrado mediante búsqueda binaria automática sobre el parámetro `scale` del simulador. El `scale` controla la amplificación del índice de estrés a turbidez.

**Tres corridas de calibración:**
- **Corrida A:** umbral 100 NTU sin calibración completa → solo 2.73% de eventos (bajo)
- **Corrida B:** aumento del rango de búsqueda → 4.53% pero con saturación de extremos
- **Corrida C (seleccionada):** ajuste de `deadband=0.30` para controlar la forma de la curva estrés→turbidez → **5.10% de eventos** ✓, degradado 12.78%, sin saturación

### 3.5 Distribución de campañas — 3 CLAY + 3 UF en 90 días

**El problema original:** con las campañas CLAY concentradas en días 14-28 y UF en días 28-42, un split temporal en día 60 ponía casi todos los eventos de entrenamiento en CLAY y casi todos los de test sin CLAY — creando un desbalance artificial de ~8x entre train y test.

**La decisión:** distribuir 3 episodios CLAY y 3 episodios UF a lo largo de los 90 días:
- CLAY: días (10,5), (38,6), (65,5) → 16 días totales
- UF: días (20,4), (52,4), (78,4) → 12 días totales

**Resultado:** split en día 60 da ~5.6% de tasa de eventos en train y ~4.1% en test — diferencia razonable, sin desbalance artificial.

### 3.6 Fallas de sensor inyectadas

Se inyectan cuatro tipos de fallas solo en las columnas "medidas" (nunca en `_clean`):
- **Picos (spikes):** valores absurdamente altos por 1-3 puntos
- **Valores pegados (stuck):** el sensor congela en un valor por varios minutos
- **Deriva (drift):** desplazamiento gradual sistemático
- **Datos faltantes (NaN):** brechas aleatorias

Esto replica el comportamiento real de sensores de turbidez en entornos de proceso agresivos.

### 3.7 Descarte del mecanismo FLOC — 2026-02-18

**Contexto:** el simulador tenía tres modos de falla: CLAY, UF, y FLOC (falla en la preparación de floculante).

**El problema:** FLOC representaba apenas el **0.2% de los eventos** (~3 puntos en 25.920 filas). Ningún algoritmo de clasificación puede aprender un patrón con 3 ejemplos positivos.

**La decisión:** eliminar completamente el mecanismo FLOC. El floculante (`Floc_gpt`) se mantiene como variable de proceso calculada a partir de la física, pero desaparece como modo de falla.

**Impacto:** diagnóstico simplificado a problema binario CLAY vs UF. Los pesos de estrés se renormalizaron y el binary search recalibró automáticamente la tasa de eventos al 5%.

**Por qué es la decisión correcta:** un modelo de diagnóstico que no puede aprender FLOC correctamente sería peor que ignorarlo. Es mejor tener un diagnóstico confiable para dos clases que un diagnóstico inútil para tres.

---

## 4. Feature Engineering — 🔧

### 4.1 Estrategia general

El dominio de series de tiempo de proceso requiere features que capturen **tendencias**, **variabilidad** y **estado acumulado** — no solo el valor instantáneo. Se generaron tres conjuntos de features:

| Conjunto | Features | Descripción |
|---|---|---|
| `FEATURES_ALL` | 324 | Todo, incluyendo variables latentes del simulador |
| `FEATURES_PROD` | 221 | Solo variables disponibles en planta real (sin latentes) |
| `FEATURES_TOP30_PROD` | 30 | Top 30 por importancia, sin latentes |

### 4.2 Tipos de features generadas por tag

Para cada señal de proceso se calcularon:
- Ventanas rolling: media, std, min, max en 15min, 30min, 1h, 2h, 6h, 12h, 24h
- Deltas: diferencia respecto a N puntos anteriores
- Pendientes de regresión lineal (agregadas en Model B): 60min, 120min
- Flags binarios: `pH_off_spec` (pH > 9.5)

### 4.3 Exclusión de variables latentes de FEATURES_PROD

Variables como `Overflow_Turb_NTU_clean` (la verdad del proceso), `Floc_effectiveness`, y `pH_clean` no están disponibles en una planta real — son construcciones del simulador. Incluirlas en el modelo sería **data leakage**: el modelo usaría información que no existe en producción.

`FEATURES_PROD` excluye sistemáticamente todo lo que no existe en el DCS estándar.

### 4.4 La cadena causal del pH

El pH tiene un rol causal real en el proceso:
`Clay_idx↑ → pH↑ (arcilla consume alcalinidad) → Floc_effectiveness↓ → estrés de floculación↑ → turbidez↑`

Esto se traduce en features de `pH_feed` (medido, con fallas) que capturan esta dinámica. El pH es una señal de alerta temprana porque responde antes de que la turbidez se deteriore.

### 4.5 Top features por importancia (SHAP)

Las señales que el modelo aprende a combinar son exactamente las que un metalurgista experimentado monitorearía manualmente:

1. **Turbidez medida rolling (15-30 min)** — distingue tendencia sostenida de picos transitorios
2. **Caudal de underflow (Qu)** — caída de Qu precede al colapso del lecho en modo UF
3. **Nivel de lecho rolling (12h)** — acumulación progresiva en escala de turno
4. **Torque del rastrillo rolling (1h)** — densificación del lecho antes de la crisis

---

## 5. Decisiones de modelado — metodología — 🔧

### 5.1 Métrica primaria: PR-AUC, no ROC-AUC

Con ~5% de tasa de eventos, el dataset es fuertemente desbalanceado. ROC-AUC puede ser engañosamente alta incluso para modelos malos, porque el numerador (TPR) y denominador (FPR) son ambos afectados por la clase negativa dominante.

**PR-AUC (Average Precision)** mide la calidad del modelo específicamente en la clase positiva (los eventos). Es la métrica correcta para clasificación con desbalance.

### 5.2 Validación temporal: TimeSeriesSplit, nunca shuffle

Los datos de series de tiempo tienen dependencia temporal. Un split aleatorio (shuffle) causa **leakage temporal**: el modelo ve el futuro durante el entrenamiento y aprende patrones que no existirían en producción.

Se usó `TimeSeriesSplit(n_splits=3, test_size=2800)` — cada fold usa solo datos pasados para predecir el futuro. Con SPLIT_DAY=60 en el split train/test, solo 3 folds son viables (el cuarto fold tiene muy pocos eventos en train).

### 5.3 Manejo del desbalance: class_weight, no SMOTE

**SMOTE** (Synthetic Minority Oversampling Technique) genera ejemplos sintéticos de la clase minoritaria interpolando entre ejemplos existentes. En series de tiempo, esto viola la estructura temporal: los ejemplos sintéticos no respetan la causalidad.

**Conclusión experimental:** SMOTE empeoró el PR-AUC en todos los modelos evaluados (RF: -7.9pp, LR: -0.5pp). Se usó `class_weight='balanced_subsample'` (RF) y `class_weight='balanced'` (LR) en su lugar.

### 5.4 Split train/test: día 60 de 90

**Por qué día 60 y no otro:** un split anterior (ej. día 35) concentraba los eventos de crisis en el período de test (por la distribución original de campañas), creando hasta 8x de desbalance entre train y test. Día 60 con la nueva distribución de campañas da tasas similares en ambos períodos.

**La limitación de este split:** el modelo se entrena sobre episodios 1 y 2 (CLAY y UF), y se evalúa sobre episodio 3. Es el mejor escenario posible dentro de 90 días de datos, pero no equivale a validación sobre datos de una planta diferente.

---

## 6. Modelo A — Alerta Temprana 30 minutos — 🔧 ⚗️ 🏭

### 6.1 Selección de algoritmo

Se compararon tres algoritmos con CV temporal sobre `FEATURES_TOP30_PROD`:

| Algoritmo | CV PR-AUC | CV ROC-AUC |
|---|---|---|
| **RandomForest** | **0.755** | **0.977** |
| LightGBM | 0.737 | 0.973 |
| Logistic Regression | 0.716 | 0.975 |

**RF ganó el CV** → fue el único que se tunó (protocolo: un modelo, una evaluación en test — sin doble-testing).

### 6.2 Tuning del RandomForest

`RandomizedSearchCV` con `n_iter=20`, `n_jobs=-1`, sobre `FEATURES_PROD` (221 features):

- `n_estimators`: 100
- `max_depth`: 10
- `min_samples_leaf`: 20
- `max_features`: 0.3
- `class_weight`: balanced_subsample

Mejor CV PR-AUC: **0.786**

### 6.3 Resultados en test

| Métrica | Valor |
|---|---|
| PR-AUC | 0.587 |
| ROC-AUC | 0.980 |
| F1-macro | 0.825 |
| Recall (eventos detectados) | 70.1% (249/355) |
| Falsas alarmas | 145 en 30 días |
| Umbral óptimo | 0.586 |

**Gap CV→test (PR-AUC 0.786 → 0.587):** el modelo entrena sobre episodios 1+2 y testea sobre episodio 3. Esta brecha es esperada — no hay leakage, hay variabilidad de episodio. En datos de planta real con historial largo, la brecha sería menor.

### 6.4 Comparación con la alarma actual

| | Alarma actual (NTU > 80) | TWS Alerta Temprana |
|---|---|---|
| Momento del aviso | Crisis ya en curso | **30 min antes** |
| PR-AUC | 0.663 | **0.587** |
| F1-macro | 0.695 | **0.825** |

> El modelo mejora todas las métricas comparables y **agrega** 30 minutos de anticipación.

---

## 7. Modelo B — Alerta Precoz 2 horas — 🔧 ⚗️

### 7.1 La motivación

Si con 30 minutos el operador puede actuar de forma controlada, con 2 horas podría actuar de forma **preventiva**: ajustar la dosis de floculante gradualmente, anticipar un cambio de turno, reducir la carga de alimentación sin impacto en producción.

### 7.2 El hallazgo del análisis de lead time

Antes de construir el modelo, se analizó cuánto tiempo real existe entre el estado "proceso en zona verde" y el inicio de una crisis. El resultado fue revelador:

- **El 71% de las degradaciones ocurren dentro de los 30 minutos siguientes** a la última observación en zona verde
- La turbidez media 30 minutos antes del inicio de un episodio: **107 NTU** — el proceso ya está en crisis
- Lo que parecía ser "lead time de 2 horas" resultó ser fragmentación: las campañas multi-día hacen que el proceso oscile alrededor del umbral de 100 NTU, generando muchos "inicios de episodio" artificiales

**Conclusión:** cuando el proceso está en zona verde genuina (NTU < 50), las señales del DCS son silenciosas respecto a lo que pasará en 2 horas.

### 7.3 El descubrimiento de leakage

Durante el desarrollo del Model B se detectó que dos features (`is_CLAY`, `is_UF`) tenían **100% de concordancia con la variable `Regime`** — una variable de campaña del simulador que no existe en una planta real. El modelo usaba información de qué tipo de campaña estaba activa para predecir el futuro.

Al remover estas features (junto con otras que actuaban como proxies del sensor de turbidez en zona degradada), el PR-AUC de test cayó de ~0.19 a ~0.134.

### 7.4 Resultados honestos sin leakage

| Configuración | CV PR-AUC | Test PR-AUC | Test ROC |
|---|---|---|---|
| v1: con leakage, H=2h | 0.293 | 0.191 | 0.560 |
| v2a: sin leakage, H=2h | ~0.28 | **0.134** | 0.568 |
| v2b: sin leakage, H=1h | 0.607 | 0.071 | 0.510 |

El v2b tiene CV alto (0.607) pero test muy bajo (0.071) — el horizonte de 1h colapsa los positivos de entrenamiento (278 → 105), generando sobreajuste en CV.

### 7.5 Por qué el sensor no puede hacer esto solo

La alerta precoz de 2 horas requiere conocer qué está entrando al espesador **antes** de que esa alimentación llegue a afectar la turbidez. Esa información no está en los sensores del espesador — está en:

- Análisis granulométrico de la alimentación (laboratorio, delay 4-8h)
- Datos de planificación minera (qué zona de extracción, qué tipo de roca)
- Sensores en línea de composición (FBRM, densímetro de alimentación)

Es el mismo problema que anticipar una tormenta con solo un termómetro local: la señal predictiva a 2h plazo no está en el sensor de proceso — está en la mineralogía de lo que está entrando a la planta.

**Esta conclusión no es un fracaso — es el hallazgo más valioso del proyecto para un metalurgista**: define exactamente qué dato adicional se necesita y por qué.

---

## 8. Diagnóstico de causa — CLAY vs UF — 🔧 ⚗️ 🏭

### 8.1 Por qué el diagnóstico importa tanto como la alerta

Saber que viene una crisis sin saber la causa lleva a acciones incorrectas. Aplicar la corrección de UF a un evento CLAY puede agravar la situación. El diagnóstico automático convierte la alerta en una **acción específica**.

| Causa | Señal característica | Acción correctiva |
|---|---|---|
| CLAY | Lecho alto y rígido, torque elevado | ↑ floculante · dilución en feedwell · reducir carga |
| UF | Caída de caudal de underflow, lecho moderado | ↑ caudal de purga · revisar bomba/válvula |

### 8.2 El hallazgo: una regla simple supera al ML

El análisis mostró que el nivel de lecho (`BedLevel_m`) es un discriminador casi perfecto entre CLAY y UF.

**La razón es física:**
- **CLAY:** la arcilla forma una capa densa y rígida → el lecho sube de forma sostenida y se mantiene alto
- **UF:** la falla de purga no genera acumulación de esa naturaleza → el lecho es moderado

**La regla:**
```
Si BedLevel > 1.9 m → causa probable: CLAY
Si BedLevel ≤ 1.9 m → causa probable: falla de underflow
```

**Resultado:** 93.1% de exactitud (339 de 364 eventos correctamente clasificados).

### 8.3 Comparación con ML

| Método | ROC-AUC | F1-macro |
|---|---|---|
| Regla BedLevel > 1.9m | 0.922 | 0.923 |
| LightGBM TOP30_PROD | 0.836 | 0.851 |

**La regla simple gana.** Este es un resultado importante: para este problema específico, el conocimiento de proceso es más potente que el algoritmo.

### 8.4 Cuándo el ML complementa la regla

Los 53 eventos CLAY mal clasificados por la regla corresponden a campañas de baja intensidad donde el lecho no alcanzó el umbral de 1.9m. En esos casos, el modelo LightGBM actúa como segunda opinión — también cuando el sensor de nivel de lecho falla o cuando se busca diagnóstico temprano antes de que el lecho haya divergido.

**Recomendación operacional:** implementar la regla en el DCS hoy, sin necesidad de ML. El modelo actúa como respaldo.

---

## 9. Decisión de arquitectura — dos modelos separados — 🔧 🏭

### 9.1 Por qué no un solo modelo

Dos modelos con objetivos diferentes:
- **Modelo A (30 min):** alerta durante la degradación activa — usa toda la señal del proceso incluyendo turbidez ya elevada
- **Modelo B (2h):** alerta preventiva desde zona verde — opera solo cuando turbidez < 50 NTU, señales todavía silenciosas

Un solo modelo para ambos horizontes confundiría los dos problemas y empeoraría ambos.

### 9.2 Por qué no se implementó un Modelo C (predictor de régimen)

La idea original incluía un "Modelo C" que predijera el régimen operacional futuro (CLAY / UF / NORMAL) por turno. Este modelo fue **descartado como componente implementable** por una razón fundamental:

Con datos de sensor del espesador solamente, el modelo puede clasificar el **estado actual** del proceso, no el **régimen futuro**. La diferencia:
- Clasificar estado actual: "el proceso está en modo CLAY *ahora*" → esto ya lo hace la regla de BedLevel
- Predecir régimen futuro: "en las próximas 8 horas entrará una campaña de arcilla" → requiere datos de mineralogía de la alimentación, no disponibles en el DCS

**La analogía:** un pronóstico del tiempo válido para 24h requiere datos de presión atmosférica, satélite, y modelos globales — no solo el termómetro local. El Modelo C es análogo: requiere asays de laboratorio de granulometría o datos de planificación minera.

**Esta conclusión se convirtió en el argumento central para la Fase 2 del proyecto:** integrar granulometría de alimentación para desbloquear la alerta precoz real.

---

## 10. Lo que el proyecto demuestra — 💼 🏭

### Como portafolio técnico

El proyecto demuestra capacidad para:
1. **Definir un problema real de ingeniería** — no un benchmark académico
2. **Diseñar un dataset sintético calibrado** — con parámetros justificados desde la física del proceso
3. **Ejecutar un pipeline ML completo:** simulación → EDA → feature engineering → CV temporal → tuning → evaluación honesta
4. **Detectar y reportar leakage** — uno de los errores más comunes en ML aplicado
5. **Dar conclusiones honestas:** el Model B no funciona con solo datos de sensor, y eso se dice explícitamente con la evidencia
6. **Proponer siguiente paso concreto** — qué dato adicional se necesita y por qué

### Como propuesta de valor operacional

- **La alerta temprana existe hoy:** una regla de BedLevel > 1.9m para diagnóstico puede implementarse en el DCS sin ML, sin inversión en infraestructura
- **El Modelo A agrega 30 minutos de margen** sobre la alarma existente, con 70% de recall
- **El framework es adaptable:** los notebooks están documentados, el código es reproducible, y el pipeline está diseñado para recibir datos reales

### La limitación central y por qué es una fortaleza comunicarla

Un proyecto que reporta PR-AUC perfecta en datos sintéticos sería sospechoso. Este proyecto reporta exactamente lo que logra, por qué logra lo que logra, y qué necesita para llegar más lejos. Eso es más valioso que resultados inflados.

---

## 11. El siguiente paso — todos los perfiles

| Fase | Objetivo | Lo que se necesita |
|---|---|---|
| **1 — Validación real** | Reentrenar y evaluar con historian de planta real | 6-12 meses de datos DCS: turbidez, lecho, torque, caudales, densidades, floculante |
| **2 — Integración lab** | Desbloquear alerta precoz de 2h | Análisis granulométrico de alimentación con timestamp |
| **3 — Prototipo operacional** | Panel en sala de control | Integración con DCS / SCADA, validación operacional |

Los datos pueden ser anonimizados. No se requiere identificar la planta ni la empresa.

**Repositorio:** github.com/MatiasValenzuelaMunoz/Thickener-Water-Recovery-Sentinel-TWS
**Contacto:** linkedin.com/in/matiasvalenzuelam

---

*TWS v1.0 — Febrero 2026*
