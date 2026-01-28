# Campañas, firmas y acciones (unificado)

## Objetivo
- Simular mecanismos reales de planta (no ruido aleatorio).
- Permitir:
  1) predicción de `target_event_30m`
  2) explicación operacional (drivers)
  3) extensión prescriptiva (acción sugerida)

## Campañas (mecanismo)
- **CLAY**: ataque de finos/arcillas → clarificación sobrepasada.
- **UF**: restricción de descarga → bed/torque suben, underflow se degrada.
- **FLOC**: subdosificación/preparación → flóculos débiles, turbidez alta sin firma mecánica.

## Tabla de impacto (dirección esperada)
Leyenda: ↑ aumenta, ↓ disminuye, ↔ neutro/variable

| Variable | CLAY | UF | FLOC |
|---|---:|---:|---:|
| `PSD_fines_idx` | ↑↑ | ↔ | ↔ |
| `UF_capacity_factor` | ↔ | ↓↓ | ↔ |
| `BedLevel_m` | ↓ luego ↑ | ↑↑ | ↔ / ↓ |
| `RakeTorque_pct` | ↔ / ↑ | ↑↑ | ↔ |
| `Solids_u_pct` | ↔ / ↓ | ↓ | ↓ / ↔ |
| `Floc_gpt` | ↑ (acción cauta) | ↔ | ↓↓ (causa) / ↑↑ (acción) |
| `FeedDilution_On` | ↑ (acción típica) | ↔ | ↔ |
| `Solids_f_pct_diluted` | ↓ | ↔ | ↔ |
| `Overflow_Turb_*` | ↑↑ | ↑ | ↑↑ |

## Firmas operacionales (para clasificación y recomendación)

### CLAY — “Overflow lechoso”
**Firma**: turbidez ↑↑ + finos ↑ + bed variable (↓ luego ↑).  
**Acción sugerida**: activar dilución de feed para ganar tiempo + revisar ajuste de floc (cauteloso).

### UF — “Triada descarga”
**Firma**: bed ↑ + torque ↑ + `UF_capacity_factor` bajo (y/o `Solids_u_pct` baja).  
**Acción sugerida**: aliviar descarga (operación de UF) y reducir carga momentáneamente.

### FLOC — “Turbidez alta sin firma mecánica”
**Firma**: turbidez ↑ + bed baja/estable + torque normal.  
**Acción sugerida**: subir floc de forma más directa + revisar preparación/calibración.

## Objetivos de modelado
- **Principal**: predecir `target_event_30m` con split temporal.
- **Secundario**: explicar drivers (importancias/SHAP).
- **Avanzado**: clasificar `event_type` durante eventos para soportar prescripción.
