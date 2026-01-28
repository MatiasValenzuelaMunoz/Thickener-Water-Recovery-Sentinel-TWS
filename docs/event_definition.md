# Definición de Eventos - Espesador de Relaves
## Versión 1.0

---

## 🎯 EVENTO PRINCIPAL: OVERFLOW TURBIO

### **Condición Técnica**
```python
# Parámetros
spec_limit_NTU = 80.0          # Límite de especificación
sustain_points = 3             # 3 puntos consecutivos = 15 minutos
horizon_points = 6             # 6 puntos = 30 minutos

# Lógica de event_now
def es_evento_actual(turbidez_series):
    """
    turbidez_series: array de turbiedad [NTU]
    Retorna: array booleano del mismo tamaño
    """
    above = turbidez_series > spec_limit_NTU
    # Suma móvil de últimos 3 puntos
    rolling_sum = pd.Series(above).rolling(
        window=sustain_points, 
        min_periods=sustain_points
    ).sum()
    return (rolling_sum == sustain_points).fillna(False)