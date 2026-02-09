# Baseline Dataset — Thickener Simulator v7.0 (frozen)

**Status:** frozen baseline  
**Date:** 2026-02-09  
**Primary output:** `data/processed/thickener_timeseries_deadband0p27_sp4.parquet`  
**Secondary output (latest):** `data/processed/thickener_timeseries.parquet`

## Project goals supported
This dataset is designed to enable a portfolio-grade “operations product”:

1. **Early warning:** forecast sustained turbidity crises on **clean turbidity** (>100 NTU) at **+30 minutes**.
2. **Diagnosis:** classify likely cause mode: **CLAY / UF / FLOC**.
3. **Sensor health / data quality:** simulate bad instrumentation (especially turbidity) and provide context for confidence.
4. **Playbook:** produce recommended operator actions and trade-offs across KPIs; includes simulated operator intervention.

---

## Baseline configuration (v7.0)
### Timebase
- Horizon: **90 days**
- Sampling: **5 minutes**
- Label: sustained exceedance above **100 NTU clean** for **4 consecutive points** (20 min).
- Forecast label: `target_event_30m = event_now shifted -6 points` (30 min).

### Campaign regimes (ground-truth)
The simulator schedules campaigns to mimic operational regimes:
- `Regime = NORMAL` (default)
- `Regime = CLAY` for **14 days**
- `Regime = UF` for **14 days**
These regimes modulate latent drivers and constraints.

### FLOC failures (incidents, not campaigns)
FLOC is modeled as preparation incidents:
- `FlocPrepFail_On`: short events (2–12 hours), ~4 events/30d
- During incident: `FlocActivity_factor` is forced low (0.25���0.55) with mild smoothing to preserve minima.

---

## What is “truth” vs “measured”
### Process truth (no instrumentation failures)
- `Overflow_Turb_NTU_clean`: **true** process turbidity (used for labeling and evaluation).
- Reology/mechanics truth proxies:
  - `UF_YieldStress_Pa`
  - `BedLevel_m`
  - `RakeTorque_kNm`, `RakeTorque_pct` (proxy; not dimensioned by thickener diameter)

### Measured tags (with failures injected)
Instrumentation failures are injected **after** clean simulation for:
- `Overflow_Turb_NTU` (measured turbidity)
- `Qf_m3h`
- `Solids_u_pct`

Injected failure types:
- random missing
- spikes
- stuck values
- drift segments

This supports **sensor health** and “confidence” modeling.

---

## Operator intervention (closed-loop, light)
The dataset includes operational realism via a bounded feedback loop:

- `ControlMode ∈ {AUTO, MANUAL}`
- `OperatorAction ∈ {NONE, INCREASE_UF, INCREASE_FLOC, ...}`
- Manipulated variables (setpoint deltas):
  - `Qu_sp_delta_m3h` (UF / underflow withdrawal action proxy)
  - `Floc_sp_delta_gpt` (floc setpoint adjustment)
- Trade-off: increased UF can raise turbidity via `carryover_penalty` (small additive NTU effect).
- Over-floc trade-off: excessive `Floc_gpt` can increase yield stress (reology penalty).

**Design intent:** intervention exists and is observable, but does **not** dominate turbidity dynamics.

---

## Diagnosis labels
### Event definition
- `event_now = 1` when `Overflow_Turb_NTU_clean` sustained >100 NTU for `sustain_points`.

### Event type
- `event_type_raw`: dominant stress contributor among CLAY / UF / FLOC components.
- `event_type`: overrides applied for:
  - UF regime and strong UF constraint
  - FLOC incidents with sufficient floc deficit

Possible values:
- `NONE`, `CLAY`, `UF`, `FLOC`

---

## Playbook outputs (recommendations)
The simulator provides a simple rule-based playbook:
- `RecommendedAction`
- `ExpectedTradeoff`
- `ActionScore_turb` (positive = likely turbidity improvement)
- `ActionScore_torque` (positive = likely torque/mechanics improvement)

This supports a product-like UX: “what to do next + why + trade-off”.

---

## Baseline metrics (frozen run @ deadband=0.27)
From the frozen run:

- **Event rate (clean, sustained >100):** ~5.02%
- **Manual fraction:** ~25.04%
- **Clarification zones (clean):**
  - Green (<50): ~79.63%
  - Degradation (50–100): ~12.05%
  - Critical (>100): ~8.32%
  - Spec (>200): ~2.28%
- **Event-type distribution (events only):**
  - CLAY ~63.6%
  - UF ~33.2%
  - FLOC ~3.2%

These values are expected to be stable for the chosen seed/config.

---

## Dataset columns (high-level)
### Core process
- `timestamp`
- `Qf_*`, `Solids_f_pct`, `Feedwell_Solids_pct`
- `PSD_fines_idx`, `Clay_pct`, `Clay_idx`
- `UF_capacity_factor`, `Qu_m3h`, `BedLevel_m`, `Solids_u_pct`
- `UF_YieldStress_Pa`
- `Overflow_Turb_NTU_clean`, `Overflow_Turb_NTU`

### Flocculation
- `Floc_gpt`, `FlocActivity_factor`, `FlocEffective_gpt`, `FlocPrepFail_On`
- `Floc_sp_delta_gpt`

### Mechanics proxies
- `RakeTorque_kNm`, `RakeTorque_pct`, `Bogging_factor`

### Operations
- `ControlMode`, `OperatorAction`
- `RecommendedAction`, `ExpectedTradeoff`, `ActionScore_turb`, `ActionScore_torque`

### Labels
- `event_now`, `event_type_raw`, `event_type`
- `target_event_30m`

---

## Reproducibility
- Random seed fixed in `SimConfig.seed`.
- File naming includes deadband and sustain_points:
  - `thickener_timeseries_deadband0p27_sp4.parquet`

---

## Known simplifications
- `RakeTorque_*` is a **proxy**, not dimensioned by thickener diameter/drive design.
- Operator logic is heuristic and intended to create realistic patterns, not optimal control.
- Water recovery is a proxy (`WaterRecovery_proxy`), not a mass-balance validated metallurgical KPI.

---

## Next steps (after baseline freeze)
1. Early warning model (`target_event_30m`) with time-based split.
2. Diagnosis model (`event_type`) evaluated on high-risk windows.
3. Sensor health model for `Overflow_Turb_NTU` with confidence scoring.
4. Playbook policy evaluation: compare `RecommendedAction` vs `OperatorAction` and KPI deltas.
