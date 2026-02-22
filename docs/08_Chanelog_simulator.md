# Simulator Changelog

## v9.0 (2026-02-18) — Final dataset for modeling (frozen)
**Primary output:** `thickener_timeseries_deadband0p27_sp4.parquet` (43 columns, 25,920 rows)

### Added vs v8
- `pH_clean` — latent true pH; driven by `Clay_idx` (causal: Clay_idx↑ → pH↑ → Floc_effectiveness↓ → turbidity↑)
- `pH_feed` — measured pH with injected failures (spikes, stuck, drift, missing)
- `Floc_effectiveness` — latent flocculant effectiveness; excluded from `FEATURES_PROD`
- `Qo_m3h` — overflow (clarified water) volumetric flow
- Corrected `WaterRecovery_proxy` formula: `Qw_uf / Qw_feed` (water mass balance ratio)

### Removed vs v8
- FLOC mechanism fully removed (decision: 2026-02-18). See `bitacora/06_descarte_floc.md`.
  - `FlocPrepFail_On` and `FlocActivity_factor` columns removed
  - `Regime` now only takes `NORMAL`, `CLAY`, `UF`
  - `event_type` now only `CLAY`, `UF`, `NONE`

### Stress weights (post-FLOC removal)
`w = [0.22, 0.24, 0.13, 0.31, 0.10]` → (fines, load, variability, uf, floc_c)

---

## v8.0 (2026-02-09) — Pre-pH baseline
- Closed-loop operator with bounded setpoints (`ControlMode`, `OperatorAction`)
- Operator actions: `INCREASE_UF`, `INCREASE_FLOC`, `FEED_DILUTION`, `NONE`
- `WaterRecovery_proxy` column added (preliminary formula)
- Campaign distribution revised: 3 CLAY + 3 UF over 90 days
  - CLAY: days (10,5), (38,6), (65,5) = 16 days total
  - UF: days (20,4), (52,4), (78,4) = 12 days total
- FLOC modeled as preparation incidents (`FlocPrepFail_On`), not as a campaign regime
- `deadband = 0.27`, `sustain_points = 4`
- Event rate target: 5% ± 0.6% achieved via binary search on `scale`

---

## v7.0 (2026-02-07) — Operations-product reframe
- Reframed simulator to support an operations-product narrative:
  - early warning (30 min), diagnosis (CLAY / UF / FLOC), playbook
- Introduced closed-loop operator with bounded setpoints
- Added playbook fields: `RecommendedAction`, `ExpectedTradeoff`, `ActionScore_turb`, `ActionScore_torque`
- Torque remains a **proxy** (not KD²-dimensioned) to avoid scaling instability

### v7.0.1 — calibration
- Tuned `deadband` to control prevalence of degradation/crisis while maintaining event_rate target
- Final value: `deadband = 0.27`
- Output: `thickener_timeseries_deadband0p27_sp4.parquet`
