# Campaigns / Scenarios (Synthetic Regimes)

The simulator organizes the dataset into regimes that mimic common operational “campaigns”.
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
**Intent:** clay/fines increase, reology worsens.
**Typical signals:**
- `Clay_pct` and `PSD_fines_idx` increase
- higher floc demand; dilution action more likely
- `UF_YieldStress_Pa` increases (can increase torque even if Cp is not extreme)
- `Overflow_Turb_NTU_clean` more often in degraded/critical

### 3) UF
**Intent:** underflow capacity restrictions (pumping/valve/transport limitations).
**Typical signals:**
- `UF_capacity_factor` drops
- `Qu_m3h` reduces relative to feed
- bed level tends to rise
- turbidity may worsen due to process imbalance and residence time changes

### 4) FLOC
**Intent:** reagent preparation / dosing effectiveness problems.
**Typical signals:**
- `Floc_gpt` systematically below “need”
- turbidity worsens without necessarily large changes in UF capacity
- operator actions may increase floc

## Event typing (`event_type`)
During `event_now == 1`, events are assigned a dominant mode:
- `CLAY`: fines/clay-driven
- `UF`: underflow restriction-driven
- `FLOC`: floc underperformance-driven
- `NONE`: no event

This is a synthetic proxy to support diagnosis experiments.

## Practical use in notebooks
- Use `Regime` for narrative and controlled analysis.
- Use `event_type` as “diagnosis label” for a baseline classifier (optional).
- Always evaluate alert performance against `Overflow_Turb_NTU_clean`-based labels.
