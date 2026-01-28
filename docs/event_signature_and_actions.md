# Firmas operacionales y acciones sugeridas (playbook)

Este documento traduce las campañas sintéticas del simulador a **síntomas observables** (tags) y **acciones recomendadas**.  
Objetivo: que el proyecto se venda como analítica “para operación” (predictivo + prescriptivo), no ML genérico.

> Nota: Las acciones son guías generales (no procedimientos oficiales).

---

## Escenario 1 — CLAY (Ataque de finos/arcillas)

### Firma (síntomas)
- `Overflow_Turb_NTU` / `Overflow_Turb_NTU_clean`: **sube drásticamente**, agua “lechosa”.
- `PSD_fines_index`: **alto** o en aumento.
- `Bed_level`: puede **bajar inicialmente** (finos no sedimentan) y luego **subir** si se acumulan.
- `Rake_torque`: puede subir como efecto secundario si la cama aumenta.

### Hipótesis/diagnóstico
Partículas coloidales (arcillas) demasiado pequeñas/cargadas: la sedimentación es sobrepasada y el floculante convencional puede no ser suficiente.

### Acciones inmediatas (modo “bombero”)
- Aumentar `Floc_dose` **cautelosamente** (puede requerir polímero específico, no solo más dosis).
- Aumentar `Feed_dilution` (bajar densidad de entrada).
- Reducir `Qf_m3h` / tonelaje (si es posible).
- Ajustar punto de inyección (más tiempo de mezcla) o dosificación dual (si aplica).

### Acciones estratégicas (modo “ingeniero”)
- Caracterización del relave (origen, mineralogía de arcillas).
- Jar testing para polímero/dosis.
- Evaluar uso de coagulantes/ayudantes de floculación.

### Recomendación de dashboard/alerta
**Alerta CLAY**: `Overflow_Turb_NTU > umbral` con condiciones de feed “estables”, + señal de finos alta.  
Sugerencia: “posible Clay Attack → revisar finos y aplicar protocolo”.

---

## Escenario 2 — UF (Degradación de capacidad de underflow)

### Firma (síntomas)
- `UF_density`: **baja**
- `Bed_level`: **sube**
- `Rake_torque`: **sube** (puede acercarse a límite)
- `UF_m3h`: restringido o incapaz de evacuar inventario (cuello de botella en descarga)

### Hipótesis/diagnóstico
Restricción en descarga: bomba desgastada, válvula/tubería restringida/obstruida, o reología desfavorable (pasta tixotrópica).

### Acciones inmediatas (modo “bombero”)
- Activar dilución en underflow (si existe) para bajar viscosidad.
- Aumentar velocidad/stroke de bomba UF (sacar más volumen aunque menos denso).
- Reducir momentáneamente alimentación.
- Activar lavado de cono (si existe).

### Acciones estratégicas (modo “ingeniero”)
- Inspección programada (bomba, válvulas, medidores).
- Revisar reología/mineralogía.
- Evaluar diseño del apex/cono (si aplica).

### Recomendación de dashboard/alerta
**Alerta UF** (firma fuerte): `Bed_level ↑` + `Rake_torque ↑` + `UF_density ↓`.  
Sugerencia: “verificar descarga UF y considerar dilución”.

---

## Escenario 3 — FLOC (Subdosificación de floculante)

### Firma (síntomas)
- `Overflow_Turb_NTU` / clean: **alta**
- `Bed_level`: **baja/estable**
- `UF_density`: **baja o normal**
- `Rake_torque`: **sin aumento** relevante

### Hipótesis/diagnóstico
Flóculos débiles o no formados: subdosificación, mala preparación, líneas tapadas o bomba descalibrada.

### Acciones inmediatas (modo “bombero”)
- Aumentar `Floc_dose` **agresivamente** (p.ej. +20–30%) y observar respuesta con lag 15–30 min.
- Verificar preparación del polímero (agua, edad de solución madre, concentración).
- Revisar puntos de inyección/obstrucciones.

### Acciones estratégicas (modo “ingeniero”)
- Calibración de bombas (catch test).
- Jar testing continuo para dosis óptima (más no siempre es mejor).

### Recomendación de dashboard/alerta
**Alerta FLOC**: `Overflow_Turb_NTU alta` + `Bed_level baja/estable` (y sin torque alto).  
Cruzar con `Floc_dose` por tonelaje y sugerir verificación de bomba/preparación.
