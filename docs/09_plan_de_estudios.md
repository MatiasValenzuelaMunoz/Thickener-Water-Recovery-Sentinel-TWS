# Plan de Estudios — Ingeniero en Minas + Data Scientist
## Proyecto: TWS_ESPESADOR — Sistema Predictivo de Turbiedad

> **Para quién es este documento**: Ingeniero en minas con experiencia en metalurgia, con conocimientos básicos de Python, construyendo un portafolio profesional de Data Science aplicado a procesos mineros.
>
> **Filosofía**: Aprender *justo a tiempo*. Cada concepto aparece cuando el proyecto lo necesita. La IA es tu tutor, no tu teclado.
>
> **Regla de oro**: Si llevas menos de 15 minutos atascado, sigue intentando. Después de 15 minutos, pide ayuda para *entender*, no para que te escriban el código.

---

## Mapa de Etapas

```
Etapa 0: Fundamentos Python para Datos          [COMPLETADA]
    │
    ▼
Etapa 1: EDA y Diagnóstico Inicial              ← Aquí empiezas
    │
    ▼
Etapa 2: Salud de Sensores (Sensor Health)
    │
    ▼
Etapa 3: Visualización Operacional (Power BI)
    │
    ▼
Etapa 4: Feature Engineering Minero
    │
    ▼
Etapa 5: Modelado Predictivo Base
    │
    ▼
Etapa 6: Interpretabilidad y Análisis de Errores
    │
    ▼
Etapa 7: Despliegue y Portafolio Final
    │
    ▼
[Entregable]: Repositorio GitHub publicable +
              Informe estilo memoria de título
```

---

## Estado del Proyecto al Inicio

```
✅ HECHO
  ├── Dataset sintético generado (90 días, 5 min)
  ├── simulate_fixed.py funcionando y calibrado
  ├── EDA inicial (notebook 01_eda.ipynb)
  ├── Feature engineering preliminar
  └── Estructura de carpetas src/ data/ docs/ notebooks/

🔲 PENDIENTE
  ├── Sensor health module (detección de fallas)
  ├── Dashboard Power BI
  ├── Modelos ML entrenados y evaluados
  ├── Interpretabilidad (SHAP)
  ├── API de predicción (opcional)
  └── Documentación final tipo memoria
```

---

## ETAPA 1 — Exploración Profunda y Diagnóstico de Datos

> **Analogía minera**: Antes de diseñar un circuito de flotación, el metalurgista hace pruebas de laboratorio para entender el mineral. El EDA es exactamente eso: entender tu "mineral" (los datos) antes de procesar.

### Objetivo de Aprendizaje
- Dominar pandas para manipulación de series de tiempo.
- Identificar patrones, correlaciones y anomalías en datos de proceso.
- Producir visualizaciones interpretables para ingenieros y operadores.
- Entender qué variables "mueven la aguja" en turbiedad del espesador.

### Entregable Concreto
- `notebooks/01_eda.ipynb` completado con las **5 figuras definitorias** del proyecto:
  - Fig 1: Timeline turbiedad limpia vs medida + bandas + eventos + régimen manual.
  - Fig 2: Episodios de eventos (duración vs severidad, coloreados por CLAY/UF).
  - Fig 3: Torque vs Yield Stress y Torque vs Cp (diagnóstico de reología).
  - Fig 4: Error del sensor de turbiedad (medida − limpia) — distribución y series.
  - Fig 5: Vista de trade-off de eficiencia (recuperación de agua vs calidad).
- `reports/EDA_summary.md` con hallazgos clave en lenguaje de operador.

---

### Módulo 1.1 — pandas y Series de Tiempo

**¿Por qué lo necesitas ahora?**
Tu dataset tiene 25.920 filas (90 días × 288 puntos/día). Sin pandas fluido, cualquier análisis será doloroso.

**Concepto clave**: Un DataFrame de pandas es como una hoja de cálculo inteligente que entiende fechas. El índice temporal es tu "eje X" natural para datos de proceso.

#### Recursos de Estudio (30–45 min)
| Recurso | Capítulo/Sección | Enfoque |
|---------|-----------------|---------|
| [Pandas Getting Started](https://pandas.pydata.org/docs/getting_started/intro_tutorials/) | Tutoriales 1–4 | Leer y ejecutar |
| *Python for Data Analysis*, Wes McKinney (O'Reilly) | Cap. 5 y 10 | Series temporales |
| [Real Python — Pandas DataFrames](https://realpython.com/pandas-dataframe/) | Secciones 1–3 | Referencia práctica |
| YouTube: [Corey Schafer — Pandas Series](https://www.youtube.com/watch?v=zmdjNSmRXF4) | Video completo | Visual y claro |

#### Práctica (2h)

**Ejercicio 1.1.1 — Carga y exploración básica** (30 min)
```python
# Sin copiar este código: escríbelo tú mismo en el notebook.
# Objetivos:
# 1. Carga el parquet con pd.read_parquet()
# 2. Imprime shape, dtypes, primeras 10 filas
# 3. Verifica que el índice es datetime
# 4. Reporta: ¿cuántos NaN hay por columna? (usa .isnull().sum())
# 5. ¿Cuál es el rango temporal exacto del dataset?
```

**Ejercicio 1.1.2 — Resample y estadísticas horarias** (45 min)
```python
# Sin copiar este código: escríbelo tú mismo.
# 1. Crea df_hourly = df.resample('1h').mean()
# 2. Calcula media, std, min, max de Overflow_Turb_NTU_clean por hora del día
# 3. ¿A qué hora del día hay más eventos de turbiedad alta?
# Analogía: es como calcular la ley de cabeza promedio por turno de 8h
```

**Ejercicio 1.1.3 — Filtrado por régimen** (45 min)
```python
# Sin copiar: impleméntalo tú.
# 1. Separa los datos en tres DataFrames: df_normal, df_clay, df_uf
# 2. Para cada uno calcula: turbiedad promedio, tasa de eventos, torque promedio
# 3. Crea una tabla comparativa con pd.concat() o un dict
# Pregunta guía: ¿Los eventos CLAY y UF son distinguibles solo con turbiedad?
```

**Desafío sin IA** (opcional, si terminas antes):
- ¿Existe correlación entre el día de la semana y la frecuencia de eventos?
  Pista: `df.index.dayofweek`

#### Verificación de Aprendizaje
1. ¿Cómo filtras filas de un DataFrame donde `Overflow_Turb_NTU_clean > 100`?
2. ¿Qué diferencia hay entre `.loc[]` y `.iloc[]`?
3. ¿Por qué hacer `resample('1h').mean()` en lugar de simplemente `.groupby()`?

**Lo logré si...**
- [ ] Puedo cargar, explorar y describir el dataset sin consultar notas.
- [ ] Entiendo qué columna es "ground truth" y cuál tiene fallas instrumentales.
- [ ] Produje al menos una tabla de estadísticas por régimen (NORMAL/CLAY/UF).

---

### Módulo 1.2 — Visualización con matplotlib y seaborn

**Analogía minera**: Un buen gráfico de proceso es como un diagrama de flujo: comunica en segundos lo que una tabla tarda minutos en revelar. Un operador no lee tablas de números durante una guardia.

#### Recursos de Estudio (30–45 min)
| Recurso | Sección | Enfoque |
|---------|---------|---------|
| [Matplotlib Tutorials](https://matplotlib.org/stable/tutorials/index.html) | Introductory | Subplots, ejes duales |
| [Seaborn Gallery](https://seaborn.pydata.org/examples/index.html) | Distribuciones, heatmaps | Ver y replicar |
| *Storytelling with Data*, Cole Nussbaumer Knaflic | Cap. 2–3 | Principios de visualización |
| YouTube: [Keith Galli — Matplotlib](https://www.youtube.com/watch?v=DAQNHzOcXBU) | Completo | Práctica |

#### Práctica (2h) — Figura 1 y Figura 4

**Figura 1: Timeline completo** (1h)
```
Objetivo visual:
- Eje superior: Overflow_Turb_NTU_clean (línea azul) y Overflow_Turb_NTU (gris, semitransparente)
- Banda roja horizontal en 100 NTU (límite de evento)
- Sombras de fondo: verde=NORMAL, naranja=CLAY, rojo=UF
- Sombras grises verticales: periodos de control MANUAL
- Marcadores: puntos donde target_event_30m = 1
Pista: usa ax.axhspan() para las bandas y ax.fill_between() para regímenes
```

**Figura 4: Error del sensor** (1h)
```
Objetivo:
- Calcula error = Overflow_Turb_NTU - Overflow_Turb_NTU_clean
- Subplot 1: histograma del error (seaborn.histplot con kde=True)
- Subplot 2: error en el tiempo, coloreado por tipo de falla (spike, stuck, drift)
- ¿Cuándo el sensor subestima? ¿Cuándo sobreestima?
```

#### Verificación de Aprendizaje
1. ¿Cómo crear dos ejes Y en el mismo gráfico (eje dual)?
2. ¿Qué hace `ax.fill_between()` y para qué sirve en datos de proceso?
3. ¿Cuál es la diferencia entre un gráfico de dispersión y uno de línea para datos de tiempo?

**Lo logré si...**
- [ ] Produje la Figura 1 con todas las capas (turbiedad, bandas, regímenes, eventos).
- [ ] Produje la Figura 4 con distribución e interpretación del error del sensor.
- [ ] Mis gráficos tienen títulos, etiquetas de ejes y leyenda.

---

### Módulo 1.3 — Análisis de Correlación y Patrones

**Analogía minera**: La correlación entre variables de proceso es como el metalurgista que sabe que cuando sube el pH, baja la recuperación de Cu. No es causalidad, pero es una señal de alarma.

#### Recursos de Estudio (30 min)
| Recurso | Sección |
|---------|---------|
| [Pandas Correlation](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.corr.html) | Documentación oficial |
| Seaborn `heatmap` + `pairplot` | [Gallery](https://seaborn.pydata.org/examples/index.html) |
| *Hands-On ML*, Aurélien Géron | Cap. 2 (EDA section) | Análisis de correlación |

#### Práctica (1h30min)

**Figura 3: Torque vs Reología** (45 min)
```
Objetivo:
- Scatter: Torque_kNm vs UF_YieldStress_Pa, coloreado por Regime
- Línea de tendencia (np.polyfit o seaborn.regplot por régimen)
- Anotación: "¿El torque es un proxy válido del Yield Stress?"
- Segundo scatter: Torque_kNm vs Cp_pct
```

**Heatmap de correlaciones** (45 min)
```
Objetivo:
- Calcula matriz de correlación de las variables numéricas clave
- Visualiza con seaborn.heatmap (annot=True, cmap='coolwarm')
- Identifica: ¿qué variables están más correlacionadas con Overflow_Turb_NTU_clean?
- Reporta top 5 correlaciones en EDA_summary.md
```

**Lo logré si...**
- [ ] Identifiqué las 5 variables más correlacionadas con la turbiedad limpia.
- [ ] Produje la Figura 3 con interpretación escrita.
- [ ] Puedo explicar por qué correlación alta no implica que una variable cause la otra.

---

### Rúbrica de Autoevaluación — Etapa 1

| Hito | Criterio de Éxito | Básico | Intermedio | Avanzado |
|------|-----------------|--------|------------|----------|
| Carga y exploración | DataFrame cargado, tipos correctos | Cargué el archivo | Identifiqué NaN y outliers | Automaticé el reporte con función |
| Figura 1 | Timeline completo con capas | Una línea de turbiedad | Bandas y regímenes | Interactivo con plotly |
| Figura 3 | Torque vs reología | Scatter básico | Líneas de tendencia por régimen | Modelo lineal y R² reportado |
| Figura 4 | Error del sensor | Histograma simple | Distribución + serie temporal | Cuantifiqué fallas por tipo |
| EDA Summary | Hallazgos escritos | 3 observaciones | 5 con implicaciones operativas | Draft de narrativa tipo informe |

---

## ETAPA 2 — Salud de Sensores (Sensor Health Module)

> **Analogía minera**: Un operador experimentado sabe cuándo el pH-metro está "loco" sin necesidad de un algoritmo. Tu objetivo es *codificar ese conocimiento* para que el sistema lo detecte automáticamente.

### Objetivo de Aprendizaje
- Implementar detección de fallas instrumentales con reglas basadas en dominio.
- Generar flags de confianza (`conf_turbidity`, etc.) por tag.
- Comparar alertas con y sin el módulo de salud para demostrar su valor.

### Entregable Concreto
- `src/sensor_health.py` — módulo independiente con funciones de detección.
- `notebooks/02_sensor_health.ipynb` — análisis y validación del módulo.
- Columna `turb_fault_flag` en el dataset procesado.

---

### Módulo 2.1 — Tipos de Fallas Instrumentales

**Teoría (30 min)**

Las fallas de sensores en plantas mineras siguen patrones reconocibles:

| Tipo de Falla | Descripción | Señal en Datos | Ejemplo en Espesador |
|--------------|-------------|---------------|---------------------|
| **Spike** | Valor aberrante aislado | Pico puntual muy alejado de vecinos | Turbiedad salta a 9999 NTU por 5 min |
| **Stuck/Flatline** | Sensor congelado | Varianza cero en ventana temporal | pH = 7.43 exacto por 2 horas |
| **Drift** | Desviación gradual | Tendencia sin respuesta al proceso | Turbiedad sube 0.5 NTU/hora sin causa |
| **Missing** | Dato ausente | NaN | Pérdida de comunicación SCADA |
| **Intermitente** | Alterna entre bueno y malo | Saltos entre valor real y cero/constante | Sensor de nivel con falla de conexión |

**Recursos de Estudio**
| Recurso | Enfoque |
|---------|---------|
| [Pandas Rolling Window](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rolling.html) | Para cálculos en ventana |
| Artículo: *"Sensor Fault Detection in Industrial Processes"* — buscar en Google Scholar | Fundamentos |
| Documentación de `Overflow_Turb_NTU` en `docs/02_data_dictionary.md` | Qué fallas están simuladas |

---

### Módulo 2.2 — Detección Basada en Reglas

#### Práctica (2h30min)

**Ejercicio 2.2.1 — Detección de spikes** (45 min)
```python
# Implementar tú mismo en src/sensor_health.py:
# Un spike es un punto donde |valor - mediana_móvil| > k * mad_móvil
# donde MAD = Median Absolute Deviation (más robusto que std)
# Parámetros sugeridos: ventana=12 puntos (1h), k=5
# Devuelve: Serie booleana con True donde hay spike

def detect_spikes(series, window=12, k=5):
    """
    Detecta spikes por distancia a mediana móvil normalizada por MAD.
    Analogía: es como el operador que descarta lecturas "que no tienen sentido"
    porque el valor anterior/siguiente son normales.
    """
    # Tu implementación aquí
    pass
```

**Ejercicio 2.2.2 — Detección de flatlines** (45 min)
```python
# Un flatline es una ventana donde la std es prácticamente cero
# Parámetros: ventana=6 puntos (30 min), umbral_std=0.01
# Cuidado: en el espesador, turbiedad PUEDE ser estable en condición normal.
# El criterio debe ser: std muy baja Y la variable debería tener variación natural.

def detect_flatline(series, window=6, std_threshold=0.01):
    """
    Detecta periodos donde el sensor reporta variación nula.
    Trampa común: no confundir proceso estable con sensor congelado.
    Solución: comparar con otra variable que debería co-variar.
    """
    pass
```

**Ejercicio 2.2.3 — Score de confianza compuesto** (1h)
```python
# Combina los detectores anteriores en un score:
# conf = 1.0  -> sensor confiable
# conf = 0.5  -> sospechoso (revisar)
# conf = 0.0  -> falla confirmada

def compute_confidence(df, tag='Overflow_Turb_NTU'):
    """
    Devuelve Serie con conf en [0, 1] para el tag especificado.
    Usar reglas AND/OR para combinar detectores.
    """
    pass
```

**Desafío sin IA**:
- El dataset tiene `Overflow_Turb_NTU_clean` como ground truth.
- Evalúa tu detector calculando: ¿cuántas fallas reales detecta? ¿cuántas falsas alarmas genera?
- Esto te anticipa el concepto de Precision/Recall de la Etapa 5.

#### Verificación de Aprendizaje
1. ¿Por qué usar la mediana en lugar de la media para detectar outliers?
2. ¿Qué problema tiene un umbral de `std < 0.01` para detectar flatlines en todas las variables por igual?
3. ¿Cómo afecta un spike no detectado a un modelo ML entrenado con esa variable?

**Lo logré si...**
- [ ] `sensor_health.py` tiene al menos 3 funciones de detección independientes.
- [ ] Puedo aplicar el módulo al dataset real y obtener flags por columna.
- [ ] Cuantifiqué precision y recall de mi detector contra el ground truth del simulador.

---

### Módulo 2.3 — Para Profundizar (Opcional)

> **Si tienes tiempo**: Los métodos estadísticos de detección de anomalías en series temporales son un campo activo. Aquí hay un nivel más:

- **Isolation Forest para anomalías multivariadas**: cuando la falla no es visible en una sola variable sino en la combinación de varias.
  - Recurso: `sklearn.ensemble.IsolationForest` — [documentación](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)
- **Control Charts (SPC)**: el método industrial estándar. Los gráficos de control EWMA (Exponentially Weighted Moving Average) son usados en plantas mineras.
  - Recurso: *Statistical Process Control*, Montgomery — Cap. 9.
- **Prophet para detección de drift**: el modelo de Meta para series de tiempo puede modelar la tendencia esperada y detectar desvíos.

---

### Rúbrica de Autoevaluación — Etapa 2

| Hito | Básico | Intermedio | Avanzado |
|------|--------|------------|----------|
| Detección de spikes | Umbral simple (> 3σ) | MAD robusto con ventana móvil | Comparación cruzada entre sensores |
| Detección de flatlines | std < umbral | std < umbral + verificación de co-varianza | Longitud mínima del evento |
| Score de confianza | Flag binario | Score 0–1 continuo | Score con nivel de confianza estadístico |
| Validación | Inspección visual | Precision/Recall vs ground truth | Curva ROC del detector |
| Módulo `sensor_health.py` | Funciones sueltas | Módulo importable y testeado | Con docstrings y tests unitarios |

---

## ETAPA 3 — Visualización Operacional (Power BI)

> **Analogía minera**: El dashboard de Power BI es el "sala de control" digital. Si el panel del operador no muestra la información correcta, el mejor modelo del mundo es inútil.

### Objetivo de Aprendizaje
- Construir un dashboard operacional en Power BI Desktop.
- Conectar Power BI con datos exportados desde Python.
- Crear KPIs visuales alineados con los objetivos del espesador.

### Entregable Concreto
- `dashboards/TWS_operacional.pbix` — archivo Power BI Desktop.
- `data/processed/for_powerbi/` — carpeta con CSVs exportados desde Python.
- `reports/dashboard_guide.md` — guía de uso del dashboard.

---

### Módulo 3.1 — Exportar Datos desde Python para Power BI

**Por qué hacerlo bien desde el principio**: Power BI tiene un límite de actualización de datos. Si exportas CSVs con estructura limpia (una fila = un punto en el tiempo, columnas bien nombradas), el dashboard se actualiza sin problemas.

#### Práctica (1h30min)

**Ejercicio 3.1.1 — Preparar tablas para BI**
```python
# En un script src/export_for_bi.py (escríbelo tú):
# 1. Cargar dataset procesado
# 2. Exportar tabla_operacion.csv:
#    Columnas: Timestamp, Regime, Turb_clean, Turb_measured, conf_turbidity,
#              event_now, target_event_30m, Torque_kNm, Underflow_Density_gpl
# 3. Exportar tabla_eventos.csv:
#    Una fila por evento de turbiedad (inicio, fin, duración, máx_NTU, regime)
# 4. Exportar tabla_kpis_diarios.csv:
#    Una fila por día con: fracción_verde, fracción_degradado, fracción_evento,
#    fracción_manual, agua_recuperada_proxy
```

---

### Módulo 3.2 — Construcción del Dashboard

**Recursos de Estudio**
| Recurso | Enfoque |
|---------|---------|
| [Power BI Desktop — Getting Started](https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-getting-started) | Tutorial oficial |
| YouTube: [Guy in a Cube](https://www.youtube.com/@GuyInACube) | Canal referencia en Power BI |
| YouTube: [Avi Singh Power BI](https://www.youtube.com/@LearnPowerBI) | Visualizaciones avanzadas |

#### Práctica (3h — distribuir en varios días)

**Vista 1 — Panel de Estado Actual**
```
Diseño sugerido (dibuja en papel antes de abrir Power BI):
┌─────────────────────────────────────────────────────┐
│  ESTADO ACTUAL DEL ESPESADOR                       │
├──────────┬──────────┬──────────┬───────────────────┤
│ Turbiedad│ Régimen  │ Alarma   │ Conf. Sensor      │
│ 47 NTU   │ CLAY     │ 🟡 PREV │ 0.82              │
├──────────┴──────────┴──────────┴───────────────────┤
│  Timeline últimas 24h (turbiedad + límites)        │
├─────────────────────────────────────────────────────┤
│  KPIs diarios: % Verde | % Degradado | % Evento    │
└─────────────────────────────────────────────────────┘
```

**Vista 2 — Salud de Sensores**
- Tabla de tags con semáforo (verde/amarillo/rojo) según `conf_xxx`.
- Gráfico de últimas lecturas por sensor con banda de operación normal.

**Vista 3 — Histórico de Eventos**
- Tabla de eventos: inicio, fin, duración, máximo NTU, régimen.
- Gráfico de barras: eventos por semana y por régimen.

#### Verificación de Aprendizaje
1. ¿Cómo crear una medida DAX que calcule el porcentaje de tiempo en estado VERDE?
2. ¿Qué diferencia hay entre un visual de "Tarjeta" y uno de "KPI" en Power BI?
3. ¿Cómo configurar una actualización automática cuando cambia el CSV de origen?

**Lo logré si...**
- [ ] El dashboard tiene al menos 3 vistas navegables.
- [ ] Los KPIs operacionales son visibles sin scroll en la vista principal.
- [ ] Puedo actualizar el dashboard exportando nuevos CSVs desde Python.

---

## ETAPA 4 — Feature Engineering Minero

> **Analogía minera**: El feature engineering es como la preparación de muestra antes del análisis. Si molieras mal la muestra, aunque tengas el mejor ICP-MS del mundo, los resultados serán malos. Los features son la preparación de tu "muestra" para el modelo.

### Objetivo de Aprendizaje
- Crear features basadas en conocimiento del proceso (lag features, rolling stats, derivadas).
- Transformar variables de dominio en señales útiles para el modelo.
- Documentar cada feature con su justificación metalúrgica.

### Entregable Concreto
- `src/feature_engineering.py` — módulo con función `build_features(df)`.
- `notebooks/03_feature_engineering.ipynb` — análisis de importancia de features.
- `docs/feature_catalog.md` — catálogo con cada feature, su fórmula y justificación.

---

### Módulo 4.1 — Features Temporales (Lag y Rolling)

**Teoría (30 min)**

El horizonte de predicción es 30 minutos (6 puntos a 5 min). Eso significa:
- El modelo ve datos hasta el momento `t`.
- Predice si habrá evento en `[t+6, t+6+4]` (ventana de evento sostenido).
- Los features más útiles son los que capturan la *tendencia reciente*.

**Tipos de features temporales:**

| Feature | Fórmula | Justificación Minera |
|---------|---------|---------------------|
| Lag-N | `x(t-N)` | "¿Cómo estaba la turbiedad hace 30 min?" |
| Rolling Mean | `mean(x[t-N:t])` | "Tendencia de la última hora" |
| Rolling Std | `std(x[t-N:t])` | "¿Está el proceso inestable?" |
| Diferencia | `x(t) - x(t-1)` | "¿Está subiendo o bajando?" |
| Aceleración | `Δx(t) - Δx(t-1)` | "¿Está acelerando el cambio?" |
| Rolling Max | `max(x[t-N:t])` | "¿Hubo un pico reciente?" |

#### Recursos de Estudio
| Recurso | Enfoque |
|---------|---------|
| [Pandas shift()](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.shift.html) | Para lags |
| [Pandas rolling()](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rolling.html) | Para ventanas |
| Artículo: *"Feature Engineering for Time Series Classification"* | Google Scholar |

#### Práctica (2h)

**Ejercicio 4.1.1 — Implementar build_features()** (1h30min)
```python
# En src/feature_engineering.py, implementa:
# Cada feature debe tener un comentario con su justificación de proceso

FEATURE_CONFIG = {
    # Variables base para crear features
    'rolling_vars': [
        'Overflow_Turb_NTU',       # Turbiedad medida (con fallas)
        'FeedFlowrate_m3h',        # Caudal de alimentación
        'Torque_kNm',              # Torque del rastrillos
        'Floc_gpt',                # Dosis de floculante
        'Underflow_Density_gpl',   # Densidad de underflow
    ],
    'windows': [2, 6, 12, 24],    # 10min, 30min, 1h, 2h
    'lags': [1, 2, 6, 12],        # 5min, 10min, 30min, 1h
}

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construye features para el modelo de predicción de turbiedad.
    Returns: DataFrame con features nuevas + columnas originales.
    """
    pass
```

**Ejercicio 4.1.2 — Features derivadas de dominio** (30 min)
```python
# Features que requieren conocimiento metalúrgico:
# 1. Stress_Index: combinación de fines, carga, variabilidad, UF (ya en simulador)
# 2. Turb_trend: pendiente de regresión lineal en últimos 6 puntos
#    Pista: usa np.polyfit(range(6), valores, deg=1)[0]
# 3. Time_above_50NTU: minutos consecutivos sobre 50 NTU
# 4. Floc_efficiency: turbiedad / dosis_floculante (ratio inverso de eficiencia)
# 5. Torque_normalized: Torque_kNm / FeedFlowrate_m3h (torque por unidad de caudal)
```

**Desafío sin IA**:
- ¿Cuántas features terminas creando? ¿Cuáles son las 10 más correlacionadas con `target_event_30m`?
- Pista: Calcula la correlación y ordena de mayor a menor.

#### Verificación de Aprendizaje
1. ¿Por qué es importante que los features de lag/rolling se calculen **sin incluir el futuro** (sin data leakage)?
2. ¿Qué pasa si entrenas un modelo con un feature que incluye la variable target en su cálculo?
3. ¿Cómo se detecta el "data leakage" en un pipeline de ML?

**Lo logré si...**
- [ ] `build_features()` genera al menos 30 features documentadas.
- [ ] Ningún feature incluye información del futuro respecto a `t`.
- [ ] El catálogo de features tiene justificación de proceso para cada grupo.

---

### Módulo 4.2 — Selección de Features y Visualización de Importancia

**Teoría (30 min)**

Con 30+ features, no todas son útiles. Dos problemas comunes:
1. **Multicolinealidad**: features muy correlacionadas entre sí confunden al modelo.
2. **Ruido**: features con poca señal aumentan el tiempo de entrenamiento sin mejorar el modelo.

**Recursos de Estudio**
| Recurso | Enfoque |
|---------|---------|
| [Sklearn Feature Selection](https://scikit-learn.org/stable/modules/feature_selection.html) | Métodos estadísticos |
| *Hands-On ML*, Géron | Cap. 4: regularización y selección |

#### Práctica (1h30min)
```python
# 1. Calcula matriz de correlación de los features (no del target)
# 2. Identifica pares con correlación > 0.95 (candidatos a eliminar uno)
# 3. Usa SelectKBest con f_classif para ranking estadístico de features
# 4. Visualiza un heatmap de las top-20 features vs target
# Entregable: lista de features_finales.txt con las features seleccionadas
```

**Lo logré si...**
- [ ] Identifiqué y eliminé features redundantes (correlación > 0.95 entre sí).
- [ ] Tengo una lista priorizada de los top-20 features para el modelo.
- [ ] Entiendo por qué "más features" no siempre es mejor.

---

### Rúbrica de Autoevaluación — Etapa 4

| Hito | Básico | Intermedio | Avanzado |
|------|--------|------------|----------|
| Features temporales | Lags simples | Rolling + diferencias | Regresión local (tendencia) |
| Features de dominio | 2–3 ratios simples | 5+ con justificación | Validadas con experto o literatura |
| Catálogo | Lista de nombres | Descripción + fórmula | Justificación operativa + ejemplo |
| Selección | Sin selección | Correlación con target | SelectKBest + visualización |
| Módulo `feature_engineering.py` | Script secuencial | Función reutilizable | Pipeline sklearn compatible |

---

## ETAPA 5 — Modelado Predictivo Base

> **Analogía minera**: El modelo de ML es como el ensayo metalúrgico a escala piloto. Antes de instalar equipos nuevos en la planta, pruebas en laboratorio. Aquí tu "laboratorio" es el conjunto de datos históricos.

### Objetivo de Aprendizaje
- Implementar clasificadores para `target_event_30m` con división temporal correcta.
- Evaluar con métricas operacionales (no solo accuracy).
- Comparar al menos 2 modelos y seleccionar el mejor justificadamente.

### Entregable Concreto
- `notebooks/04_modeling.ipynb` — entrenamiento, evaluación y comparación.
- `models/baseline_lgbm.pkl` — modelo serializado.
- `reports/model_card.md` — ficha técnica del modelo seleccionado.

---

### Módulo 5.1 — División Temporal y Métricas Operacionales

**ADVERTENCIA CRÍTICA — La trampa más común en ML con series de tiempo**

> Si usas `train_test_split` aleatorio en datos temporales, estás "mirando el futuro" durante el entrenamiento. Esto da métricas falsas y un modelo que falla en producción.
>
> **La regla**: en datos de proceso, el conjunto de entrenamiento siempre precede al de prueba en el tiempo.

```
Correcto:    |---Train (60 días)---|--Val (15 días)--|--Test (15 días)--|
Incorrecto:  Mezcla aleatoria de todos los puntos del tiempo
```

**Métricas operacionales para este proyecto**

| Métrica | Fórmula | Interpretación Minera |
|---------|---------|----------------------|
| **Recall** | TP/(TP+FN) | % de crisis que el modelo detectó. Una crisis no detectada puede contaminar el proceso. |
| **Precision** | TP/(TP+FP) | % de alarmas que fueron reales. Muchas falsas alarmas = operadores ignoran el sistema. |
| **F1-Score** | 2·P·R/(P+R) | Balance entre los dos anteriores. |
| **Lead Time** | media(t_alarma − t_inicio_evento) | ¿Con cuántos minutos de anticipación avisa? Meta: ≥ 20 min. |
| **False Alarms/Day** | FP / días_totales | Tolerancia del operador: máximo 2–3 por turno. |

**Recursos de Estudio**
| Recurso | Enfoque |
|---------|---------|
| *Hands-On ML*, Géron | Cap. 3: clasificación y métricas |
| [Sklearn metrics](https://scikit-learn.org/stable/modules/model_evaluation.html) | classification_report, confusion_matrix |
| LightGBM: [documentación oficial](https://lightgbm.readthedocs.io/) | Instalación y parámetros |
| YouTube: [StatQuest — ROC Curves](https://www.youtube.com/watch?v=4jRBRDbJemM) | Visual y claro |

#### Práctica (3h — distribuir en varios días)

**Ejercicio 5.1.1 — División temporal** (30 min)
```python
# En notebooks/04_modeling.ipynb, implementa:
# Estrategia: 60 días train, 15 días val, 15 días test
# SIN usar train_test_split aleatoriamente

def temporal_split(df, train_days=60, val_days=15):
    """
    Divide el DataFrame por fechas, no aleatoriamente.
    Verifica que no hay solapamiento entre conjuntos.
    """
    pass

# Después de dividir:
# Imprime la distribución de target_event_30m en cada conjunto
# ¿Es similar en train, val y test? ¿Por qué o por qué no?
```

**Ejercicio 5.1.2 — Modelo baseline: Logistic Regression** (45 min)
```python
# 1. Entrena LogisticRegression con los top-20 features de la Etapa 4
# 2. Imprime classification_report en val y test
# 3. Grafica la matriz de confusión (usa seaborn.heatmap)
# 4. Calcula: ¿cuántas falsas alarmas por día? ¿cuántos eventos no detectados?
# 5. Registra resultados en una tabla de comparación
```

**Ejercicio 5.1.3 — Modelo mejorado: LightGBM** (1h30min)
```python
# 1. Instala lightgbm si no está: pip install lightgbm
# 2. Entrena LGBMClassifier con parámetros por defecto
# 3. Ajusta scale_pos_weight para compensar el desbalance de clases
#    (los eventos son ~5% de los datos; sin compensar, el modelo ignorará los eventos)
#    scale_pos_weight = n_negatives / n_positives
# 4. Compara métricas con logistic regression
# 5. Grafica curva ROC para ambos modelos en el mismo gráfico
```

**Desafío sin IA**:
- ¿Qué umbral de probabilidad usarías para la clasificación final?
- El umbral por defecto es 0.5, pero para este problema, ¿debería ser mayor o menor?
- Pista: piensa en qué es peor, una alarma falsa o una crisis no detectada.

#### Verificación de Aprendizaje
1. ¿Por qué `accuracy` es una métrica engañosa cuando el 95% de los datos son negativos?
2. ¿Qué es la curva ROC y cómo se interpreta el área bajo la curva (AUC)?
3. ¿Por qué necesitas un conjunto de validación además del de test?

**Lo logré si...**
- [ ] Implementé división temporal (sin mezcla aleatoria) y lo entiendo.
- [ ] Tengo al menos 2 modelos comparados con las mismas métricas operacionales.
- [ ] Puedo justificar la elección del umbral de clasificación en términos operativos.

---

### Módulo 5.2 — Para Profundizar (Opcional)

> **Si tienes tiempo**: el modelo base puede mejorarse de varias formas.

- **Cross-validation temporal (TimeSeriesSplit)**: en lugar de una sola división, usa 5 divisiones temporales para estimaciones más robustas.
  - Recurso: `sklearn.model_selection.TimeSeriesSplit`
- **Optuna para optimización de hiperparámetros**: búsqueda automática de los mejores parámetros de LightGBM.
  - Recurso: [Optuna documentation](https://optuna.org/)
- **Calibración de probabilidades**: los modelos de árbol suelen estar mal calibrados. `CalibratedClassifierCV` mejora las probabilidades predichas.
- **Modelos de secuencia**: si los resultados del modelo base son buenos, considera LSTM o Temporal Fusion Transformer para capturar dependencias temporales más largas.

---

## ETAPA 6 — Interpretabilidad y Análisis de Errores

> **Analogía minera**: Si el modelo dice "el espesador va a tener una crisis", el operador pregunta "¿por qué?". Si no tienes respuesta, no confiará en el sistema. SHAP es la respuesta a ese "¿por qué?".

### Objetivo de Aprendizaje
- Implementar análisis SHAP para el modelo seleccionado.
- Identificar cuáles features son más importantes para cada predicción.
- Analizar los errores del modelo (falsos positivos y falsos negativos) para mejorar o documentar limitaciones.

### Entregable Concreto
- `notebooks/05_interpretability.ipynb` — análisis SHAP completo.
- `reports/model_errors.md` — casos representativos de errores con explicación.

---

### Módulo 6.1 — SHAP Values

**Teoría (45 min)**

SHAP (SHapley Additive exPlanations) responde: "¿Cuánto contribuyó cada feature a esta predicción específica?"

**Analogía minera**: Es como la auditoría de una planta. Al final del mes, calculas cuánto aportó cada etapa del proceso (chancado, molienda, flotación) a la pérdida de Cu. SHAP hace lo mismo con el modelo.

- **SHAP global**: importancia promedio de cada feature en todas las predicciones.
- **SHAP local**: explicación de una predicción individual.
- **SHAP summary plot**: visualiza la distribución de importancias para todas las features.

**Recursos de Estudio**
| Recurso | Enfoque |
|---------|---------|
| [SHAP Documentation](https://shap.readthedocs.io/) | Tutorial oficial |
| *Interpretable Machine Learning*, Christoph Molnar | Cap. 9 (gratis en línea) |
| YouTube: [Weights & Biases — SHAP](https://www.youtube.com/watch?v=ngOBhhINWb8) | Visual y práctico |

#### Práctica (2h)

**Ejercicio 6.1.1 — Summary Plot** (45 min)
```python
# import shap
# explainer = shap.TreeExplainer(modelo_lgbm)
# shap_values = explainer(X_test)
# shap.summary_plot(shap_values, X_test, max_display=20)
# Interpreta: ¿qué feature tiene mayor impacto promedio?
# ¿Los valores altos de turbiedad_rolling_mean_12 aumentan o disminuyen el riesgo?
```

**Ejercicio 6.1.2 — Waterfall Plot para un Evento Real** (45 min)
```python
# Selecciona un verdadero positivo (TP): el modelo predijo evento y ocurrió
# Muestra el waterfall plot de SHAP para ese punto
# Interpreta: "En este punto, la turbiedad media de la última hora (47 NTU)
# aumentó la probabilidad de evento en +0.23"
# Repite para un falso negativo (FN): ¿por qué el modelo no lo detectó?
```

**Ejercicio 6.1.3 — Análisis de Errores** (30 min)
```python
# Clasifica los errores del modelo:
# FP: ¿tienden a ocurrir en régimen CLAY o UF?
# FN: ¿el proceso tenía alguna señal inusual que el modelo ignoró?
# Documenta 2 casos representativos en reports/model_errors.md
```

**Lo logré si...**
- [ ] Puedo explicar por qué el modelo predijo "evento" en un punto específico usando SHAP.
- [ ] Identifiqué las 3 features más importantes globalmente y tienen sentido operativo.
- [ ] Documenté al menos un caso de FP y uno de FN con contexto del proceso.

---

### Módulo 6.2 — Para Profundizar (Opcional)
- **LIME (Local Interpretable Model-agnostic Explanations)**: alternativa a SHAP para explicaciones locales.
- **Partial Dependence Plots (PDP)**: visualiza el efecto marginal de una feature manteniendo las demás constantes.
  - Recurso: `sklearn.inspection.PartialDependenceDisplay`
- **Monitoring del drift en producción**: ¿cómo detectar cuando la distribución de features cambia respecto a los datos de entrenamiento? `evidently` library.

---

## ETAPA 7 — Despliegue y Portafolio Final

> **Analogía minera**: No basta con demostrar que el proceso funciona en laboratorio (notebook). Necesitas demostrar que puede operar en planta (API + dashboard). Un portafolio sin código desplegable es un informe de tesis, no un producto.

### Objetivo de Aprendizaje
- Empaquetar el modelo como API simple con FastAPI.
- Completar la documentación del repositorio.
- Preparar la "memoria de título" como README y reporte técnico.

### Entregable Concreto
- `api/main.py` — API con endpoint `/predict` (opcional pero recomendado).
- `README.md` — principal del repositorio, con badges, descripción y ejemplos.
- `reports/memoria_titulo.md` — informe técnico completo.
- Repositorio GitHub público con commits limpios.

---

### Módulo 7.1 — API con FastAPI (Opcional, Alta Prioridad)

**¿Por qué FastAPI?**
- Más rápido de aprender que Flask para principiantes.
- Genera documentación automática (Swagger UI).
- Un endpoint `/predict` que acepta JSON y devuelve predicción + SHAP top-3 es lo que diferencia un portafolio de "notebook" de uno de "producto".

#### Recursos de Estudio
| Recurso | Enfoque |
|---------|---------|
| [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/) | Primeros 5 capítulos |
| `joblib.dump` / `joblib.load` | Para serializar el modelo |

#### Práctica (2h)
```python
# api/main.py — escríbelo tú:
# Endpoints:
#   GET  /health  -> {"status": "ok"}
#   POST /predict -> acepta JSON con últimas N lecturas del sensor
#                    devuelve {"prob_evento": 0.73, "alarma": true,
#                              "top_features": [{"name": "turb_roll_12", "shap": 0.31}]}

# Paso 1: Carga el modelo serializado con joblib
# Paso 2: Define el schema de entrada con Pydantic (FastAPI lo usa automáticamente)
# Paso 3: Implementa la función de predicción que:
#    - Recibe datos raw
#    - Aplica build_features()
#    - Predice con el modelo
#    - Calcula SHAP para los top-3 features
# Paso 4: Prueba con uvicorn y visita /docs para ver Swagger
```

**Lo logré si...**
- [ ] La API devuelve una predicción real cuando le envío datos del dataset de test.
- [ ] La documentación Swagger describe el endpoint correctamente.
- [ ] Puedo conectar Power BI a la API (o al menos describir cómo hacerlo).

---

### Módulo 7.2 — Repositorio GitHub y Documentación

**Estructura final del repositorio**
```
TWS_ESPESADOR/
├── .github/
│   └── workflows/         # CI básico (opcional)
├── api/
│   ├── main.py            # FastAPI app
│   └── schemas.py         # Pydantic models
├── bitacora/              # Decisiones de ingeniería (ya existe)
├── dashboards/
│   └── TWS_operacional.pbix
├── data/
│   ├── processed/         # Gitignored (generado)
│   └── for_powerbi/       # CSVs exportados
├── docs/
│   ├── 00_overview.md     # Ya existe
│   ├── feature_catalog.md # Nuevo
│   └── model_card.md      # Nuevo
├── models/
│   └── baseline_lgbm.pkl  # Gitignored (generado)
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_sensor_health.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_modeling.ipynb
│   └── 05_interpretability.ipynb
├── reports/
│   ├── EDA_summary.md
│   ├── model_errors.md
│   └── memoria_titulo.md  # Informe final
├── src/
│   ├── simulate_fixed.py
│   ├── quick_checks.py
│   ├── sensor_health.py   # Nuevo
│   ├── feature_engineering.py # Nuevo
│   └── export_for_bi.py   # Nuevo
├── tests/
│   ├── test_sensor_health.py
│   └── test_features.py
├── .gitignore
├── CLAUDE.md
├── README.md              # Renovar completamente
└── requirements.txt
```

**Checklist del README.md**
- [ ] Badge de Python version y licencia.
- [ ] Descripción del problema en 2 párrafos (contexto minero + solución ML).
- [ ] Diagrama de arquitectura del sistema (ASCII o imagen).
- [ ] Instrucciones de instalación y generación de datos.
- [ ] Tabla de resultados del modelo con métricas operacionales.
- [ ] Screenshot del dashboard de Power BI.
- [ ] Sección "Próximos pasos" con mejoras identificadas.

---

### Módulo 7.3 — Informe Técnico (Memoria de Título)

**Estructura de `reports/memoria_titulo.md`**

```markdown
# Sistema de Monitoreo Predictivo para Espesador de Relaves
## Detección Temprana de Crisis de Turbiedad — Proyecto TWS_ESPESADOR

### 1. Resumen Ejecutivo (1 página)
### 2. Introducción
   - Contexto: recuperación de agua en minería del cobre
   - Problema: crisis de turbiedad y sus consecuencias
   - Objetivo y alcance del proyecto
### 3. Dataset Sintético
   - Diseño del simulador
   - Validación KPI contra literatura
   - Limitaciones y supuestos
### 4. Metodología
   - Pipeline de datos (sensor health → features → modelo)
   - Criterio de división temporal
   - Métricas operacionales seleccionadas
### 5. Resultados
   - Modelo seleccionado y métricas
   - Análisis SHAP e interpretabilidad
   - Casos de estudio (un CLAY, un UF)
### 6. Dashboard y Despliegue
   - Power BI y lógica de actualización
   - API de predicción (si aplica)
### 7. Discusión y Conclusiones
   - Aportes del proyecto
   - Limitaciones
   - Trabajo futuro
### Apéndices
   - Catálogo de features
   - Parámetros del modelo
   - Guía de uso del dashboard
```

**Lo logré si...**
- [ ] El repositorio es cloneable y reproducible por otra persona siguiendo el README.
- [ ] La memoria tiene introducción, metodología y resultados coherentes.
- [ ] El dashboard muestra datos reales del dataset generado.

---

## ENTREGABLES FINALES DEL PROYECTO

| Entregable | Archivo/Ubicación | Estado |
|-----------|------------------|--------|
| Pipeline ETL con detección de fallas | `src/sensor_health.py` + `src/feature_engineering.py` | 🔲 |
| Dashboard Power BI | `dashboards/TWS_operacional.pbix` | 🔲 |
| Modelo predictivo interpretable | `models/baseline_lgbm.pkl` + `notebooks/05_interpretability.ipynb` | 🔲 |
| API de predicción | `api/main.py` | 🔲 (opcional) |
| Repositorio GitHub documentado | Público, con README completo | 🔲 |
| Informe tipo memoria de título | `reports/memoria_titulo.md` | 🔲 |

---

## BUENAS PRÁCTICAS DE GIT (recordatorio permanente)

```bash
# Flujo de trabajo diario recomendado:
git status                           # Ver qué cambió
git add src/sensor_health.py         # Agregar archivos específicos (no git add .)
git commit -m "feat: add flatline detector with std threshold"
# Formato de commit: tipo: descripción breve
# Tipos: feat, fix, docs, refactor, test, chore
```

**Reglas básicas**
- Un commit = un cambio conceptual. No acumules una semana de trabajo en un commit.
- Nunca subas a GitHub: datos (`.parquet`), modelos (`.pkl`), credenciales (`.env`), o notebooks con output de celdas sensibles.
- El `.gitignore` ya existe: revísalo y actualizalo cuando agregues nuevos tipos de archivos.

---

## TRAMPAS MENTALES — Errores Comunes de Principiantes

> Estos son los errores más frecuentes. Léelos **ahora** y vuelve a leerlos cuando algo no funcione.

### Data Science

| Trampa | Consecuencia | Solución |
|--------|-------------|---------|
| Usar `train_test_split` aleatorio en series de tiempo | Métricas infladas, modelo inútil en producción | Siempre dividir por fecha |
| Escalar datos antes de dividir train/test | Data leakage: el scaler "vio" el test | Siempre fit en train, transform en train y test |
| Evaluar solo con accuracy en clases desbalanceadas | El modelo parece bueno prediciendo siempre "sin evento" | Usar recall, precision y F1 |
| Incluir la variable target en los features | El modelo "hace trampa" | Verificar que ningún feature deriva del label |
| No documentar decisiones de modelado | Olvidar por qué se tomaron decisiones | Usar `bitacora/` para cada experimento relevante |

### Python / Programación

| Trampa | Consecuencia | Solución |
|--------|-------------|---------|
| Hardcodear rutas absolutas (`C:/Matias/...`) | El código no funciona en otro computador | Usar `pathlib.Path` relativo al proyecto |
| Variables globales en notebooks | Estado imposible de reproducir | Usar funciones con parámetros explícitos |
| No crear entorno virtual | Conflictos de dependencias | Siempre trabajar en `.venv` |
| Hacer `git add .` sin revisar | Subir archivos de datos, claves, basura | Hacer `git status` antes de cada commit |

### Power BI

| Trampa | Consecuencia | Solución |
|--------|-------------|---------|
| Conectar directamente al parquet | Difícil de actualizar con nuevos datos | Exportar CSVs desde Python con script |
| No documentar las medidas DAX | Dashboard no mantenible | Comentar cada medida DAX |
| Crear demasiadas páginas | Dashboard confuso para el operador | Máximo 3 vistas bien diseñadas |

---

## RECURSOS PERMANENTES

### Libros Clave (buscar versiones PDF o en biblioteca)
| Libro | Autor | Uso en este proyecto |
|-------|-------|---------------------|
| *Python for Data Analysis* (3rd ed.) | Wes McKinney | pandas, numpy, matplotlib |
| *Hands-On Machine Learning* (3rd ed.) | Aurélien Géron | sklearn, xgboost, métricas |
| *Interpretable Machine Learning* | Christoph Molnar | SHAP, PDP, LIME (gratis en línea) |
| *The Kaggle Book* | Banachewicz & Massaron | Feature engineering, competencias |

### Canales de YouTube Recomendados
| Canal | Enfoque |
|-------|---------|
| [StatQuest with Josh Starmer](https://www.youtube.com/@statquest) | Estadística y ML visual, sin matemáticas densas |
| [Corey Schafer](https://www.youtube.com/@coreyms) | Python intermedio, pandas, matplotlib |
| [Krish Naik](https://www.youtube.com/@krishnaik06) | ML aplicado, SHAP, deployment |
| [Guy in a Cube](https://www.youtube.com/@GuyInACube) | Power BI profesional |

### Documentación Oficial (marcar como favoritos)
- [pandas](https://pandas.pydata.org/docs/) — especialmente User Guide > Time Series
- [scikit-learn](https://scikit-learn.org/stable/user_guide.html) — User Guide completo
- [LightGBM](https://lightgbm.readthedocs.io/)
- [SHAP](https://shap.readthedocs.io/)
- [FastAPI](https://fastapi.tiangolo.com/)

---

*Última actualización: 2026-02-18 | Versión: 1.0*
*Para actualizar este plan, editarlo directamente y hacer commit con mensaje `docs: update study plan`*
