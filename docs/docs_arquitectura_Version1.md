# Arquitectura (alto nivel)

## Flujo
1) `simulate_fixed.py`
- Simula proceso + campañas + modo de control
- Genera turbidez CLEAN
- Calibra parámetros para alcanzar prevalencia objetivo de eventos
- Inyecta fallas y produce turbidez MEDIDA
- Exporta dataset en parquet

2) `quick_checks.py`
- Reporta KPIs de distribución y calidad
- Diferencia warning vs spec
- Diferencia CLEAN vs MEDIDA

## Contrato de datos (conceptual)
- Labels: basados en CLEAN y `event_limit_NTU`
- Features: principalmente MEDIDA y variables de proceso/control
