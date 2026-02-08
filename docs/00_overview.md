# Project Overview — Thickener Water Recovery Sentinel (TWS)

## Purpose
Build a realistic thickener dataset and baseline models for:
1) **Early warning** of clarified water quality degradation (overflow turbidity),
2) **Diagnosis** of probable causes (CLAY / UF / FLOC),
3) **Data quality / sensor health** to avoid acting on faulty instrumentation.

This is designed to be credible to operations: many tags exist, but **trust varies**; turbidity sensors are often unreliable.

---

## Dataset structure: Truth vs Observed (SCADA-like)

### Truth / clean (process state)
- `Overflow_Turb_NTU_clean` — clarified water turbidity (ground truth)
- `UF_YieldStress_Pa` — underflow yield stress proxy (truth rheology)
- `Clay_pct`, `Clay_idx` — latent clay driver (truth; not assumed measured online)

### Observed / measured tags (may include failures)
- `Overflow_Turb_NTU` — measured turbidity (spikes/stuck/drift/missing)
- `Qf_m3h` — total feed flow SCADA tag (spikes/stuck/drift/missing)
- `Solids_u_pct` — underflow solids SCADA-like tag (spikes/stuck/drift/missing)

High-reliability operational signals (simulated clean for now):
- `RakeTorque_kNm`, `RakeTorque_pct` (very reliable in practice)
- `BedLevel_m` (often unreliable in practice; currently simulated clean)
- `Qu_m3h`, `Floc_gpt`, `ControlMode`, `OperatorAction`
- `FeedDilution_On`, `FeedDilution_factor`

---

## Layered scope

### Layer A — Core (non-negotiable)
Goal: robust early-warning + diagnosis using a realistic minimal signal set.

Core variables:
- Turbidity: `Overflow_Turb_NTU_clean`, `Overflow_Turb_NTU`
- Torque: `RakeTorque_kNm`, `RakeTorque_pct`
- Bed level: `BedLevel_m`
- Underflow: `Qu_m3h`, `Solids_u_pct`
- Control actions: `Floc_gpt`, `FeedDilution_On`
- Operator: `ControlMode`, `OperatorAction`
- Rheology truth: `UF_YieldStress_Pa`

Key realism principle (Ricardo):
- **Torque correlates with rheology (Yield Stress), not directly with Cp (% solids).**
  This supports scenarios where Cp can be high with low torque, or vice versa, depending on clay/rheology.

### Layer B — High-ROI realism (choose 1–2)
- `Feed_P80_um` intermittent measurement (sample-and-hold, e.g., every 4h)
- `Water_Conductivity_uS_cm` (robust online sensor)
- `pH_meas` (low reliability) + confidence scoring

Arcillas:
- Do **not** model clay as a reliable online measurement.
- Use `Clay_pct` only as latent truth for simulation/evaluation.
- Infer “clay probability” from proxies (P80 trend, torque/bed, floc efficiency, etc.)

---

## Labels

### Event definition
- `event_now = 1` when `Overflow_Turb_NTU_clean > 100 NTU` is sustained for `sustain_points` samples.
- Default: `freq_min = 5`, `sustain_points = 4` → **20 minutes sustained**

### Forecast target
- `target_event_30m = shift(event_now, -horizon_points)`
- Default: `horizon_points = 6` → **30 minutes**

### Cause tags
- `event_type` uses the dominant stress component during events: `CLAY`, `UF`, `FLOC` (or `NONE`)

---

## How to run

### Generate dataset
```bash
python src/simulate_fixed.py
```

### Validate quickly
```bash
python src/quick_checks.py
```

---

## EDA: 5 required figures (Definition of Done)

1) **Timeline operational**
- CLEAN vs measured turbidity
- bands: green <50, degraded 50–100, critical >100
- markers: `event_now`
- shading: `ControlMode == MANUAL`

2) **Event episodes**
- derive episodes from `event_now`
- scatter: duration vs severity (max CLEAN NTU)
- color by `event_type`

3) **Torque & rheology validation**
- scatter: `RakeTorque_kNm` vs `UF_YieldStress_Pa`
- comparison: `RakeTorque_kNm` vs `Solids_u_pct` (weaker relationship)

4) **Sensor error characterization**
- histogram of `(Overflow_Turb_NTU - Overflow_Turb_NTU_clean)`
- scatter measured vs clean

5) **Efficiency trade-off view (proxy)**
- proxy of water recovery vs turbidity quality
- relate to `Solids_u_pct` and `UF_YieldStress_Pa`

---

## Next steps (ML baseline)
- Build lag/rolling features from measured tags
- Temporal split (train early, test late)
- Operational metrics:
  - false alarms/day
  - missed events
  - lead time (how early we warn before sustained >100 NTU)
- Add a simple sensor-health score for turbidity (stuck/drift heuristics) and test its impact.
