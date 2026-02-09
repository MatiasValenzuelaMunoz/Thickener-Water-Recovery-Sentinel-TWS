# Simulator Changelog (high level)

## v7.0 (2026-02-09) — Baseline (frozen)
- Reframed simulator to support an operations-product narrative:
  - early warning (30 min), diagnosis (CLAY/UF/FLOC), sensor health, playbook
- Introduced **closed-loop operator** with bounded setpoints:
  - `ControlMode`, `OperatorAction`
  - `Qu_sp_delta_m3h`, `Floc_sp_delta_gpt`
- Added playbook fields:
  - `RecommendedAction`, `ExpectedTradeoff`, `ActionScore_turb`, `ActionScore_torque`
- Kept FLOC as **incidents** (`FlocPrepFail_On`) with preserved minima in `FlocActivity_factor`.
- Torque remains a **proxy** (not KD²-dimensioned) to avoid scaling instability.

### v7.0.1 — calibration
- Tuned deadband to control prevalence of degradation/crisis while maintaining event_rate target.

### v7.0 baseline freeze parameters
- `deadband = 0.27`
- `sustain_points = 4`
- Output: `thickener_timeseries_deadband0p27_sp4.parquet`
