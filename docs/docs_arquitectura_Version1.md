# Arquitectura (alto nivel)

## Flujo
1. `src/simulate_fixed.py`
   - simula proceso + campañas + control + turbidez CLEAN
   - calibra escala para lograr prevalencia de eventos sobre warning
   - genera `event_now` y `target_event_30m`
   - inyecta fallas y produce turbidez MEDIDA

2. `src/quick_checks.py`
   - valida KPIs de distribución
   - reporta warning vs spec
   - reporta clean vs measured

## Decisión clave
Separar:
- **ground truth del proceso** (CLEAN) para labels
- **medición con fallas** (MEDIDA) para features