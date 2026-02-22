# Campaigns / Scenarios (Synthetic Regimes)

The simulator organizes the dataset into regimes that mimic common operational campaigns.
These regimes are *not* perfect ground truth of root cause in real plants, but they create distinct signatures.

## Regimes

### 1) NORMAL
**Intent:** stable operation.
**Typical signals:**
- lower `PSD_fines_idx`, lower `Clay_pct`
- moderate `Floc_gpt` (~10–20 g/t)
- `Overflow_Turb_NTU_clean` mostly <50 NTU (green)
- `UF_YieldStress_Pa` mostly <10 Pa (good)

### 2) CLAY
**Intent:** clay/fines increase, rheology worsens.
**Typical signals:**
- `Clay_pct`, `Clay_idx`, and `PSD_fines_idx` increase
- `pH_feed` rises (Clay_idx → pH causal chain)
- `Floc_effectiveness` drops
- higher floc demand; dilution action more likely
- `UF_YieldStress_Pa` increases (can increase torque even if Cp is not extreme)
- `Overflow_Turb_NTU_clean` more often in degraded/critical

### 3) UF (Underflow Failure)
**Intent:** underflow capacity restrictions (pumping/valve/transport limitations).
**Typical signals:**
- `UF_capacity_factor` drops
- `Qu_m3h` reduces relative to feed
- bed level tends to rise
- turbidity may worsen due to process imbalance and residence time changes

## Campaign schedule (90-day dataset)

| Regime | Periods (start day, duration) |
|---|---|
| CLAY | (10, 5), (38, 6), (65, 5) → 16 days total |
| UF | (20, 4), (52, 4), (78, 4) → 12 days total |
| NORMAL | Remaining days |

## Event typing (`event_type`)
During `event_now == 1`, events are assigned a dominant mode:
- `CLAY`: fines/clay-driven
- `UF`: underflow restriction-driven
- `NONE`: no event

> **Note:** FLOC was removed from the simulator (2026-02-18). It represented only ~0.2% of events and was not learnable as a separate category. Diagnosis is binary: CLAY vs UF. See `bitacora/06_descarte_floc.md`.

## Practical use in notebooks
- Use `Regime` for narrative and controlled analysis.
- Use `event_type` as diagnosis label for classification (`04_diagnosis.ipynb`).
- Always evaluate alert performance against `Overflow_Turb_NTU_clean`-based labels.
