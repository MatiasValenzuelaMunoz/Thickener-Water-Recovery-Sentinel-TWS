# Project Overview — Thickener Water Recovery Sentinel (TWS)

## Purpose

Proof-of-concept ML system for **early detection of overflow turbidity crises** in a conventional Cu/Mo thickener, built on a synthetic but operationally calibrated dataset (90 days · 5-min intervals · 25,920 records).

**Implemented components (v1.0 — complete):**

1. **Early Warning (Model A)**: binary forecast of sustained turbidity crisis (>100 NTU clean, ≥20 min) at 30-minute horizon — RandomForest, PR-AUC 0.587, Recall 70%.
2. **Cause Diagnosis**: classify crisis as CLAY vs Underflow Failure — 93.1% accuracy via BedLevel rule; LightGBM as complement.
3. **Early Alert (Model B)**: honest evaluation of 2h horizon — sensor-only data is insufficient; mineralogy required.

**Out of scope (by design):**
- Sensor health / instrument failure detection — deferred to a future phase.
- FLOC mode — removed; represented only ~0.2% of events, not learnable (see `bitacora/06_descarte_floc.md`).
- Prescriptive playbook — simplified to diagnosis-driven action table in `reports/reporte_final.ipynb`.

---

## Dataset structure: Truth vs Observed (SCADA-like)

### Truth / clean (process state)
- `Overflow_Turb_NTU_clean` — clarified water turbidity (ground truth, no instrument failures)
- `UF_YieldStress_Pa` — underflow yield stress proxy (truth rheology)
- `Clay_pct`, `Clay_idx` — latent clay driver (not assumed measured online)
- `pH_clean` — true pH (latent; used for simulation only)
- `Floc_effectiveness` — latent flocculant effectiveness driver

### Observed / measured tags (with injected failures)
- `Overflow_Turb_NTU` — measured turbidity (spikes / stuck / drift / missing)
- `Qf_m3h` — total feed flow SCADA tag (spikes / stuck / drift / missing)
- `Solids_u_pct` — underflow solids (spikes / stuck / drift / missing)
- `pH_feed` — measured pH with injected failures

High-reliability operational signals (simulated clean):
- `RakeTorque_kNm`, `RakeTorque_pct`
- `BedLevel_m`
- `Qu_m3h`, `Qo_m3h`, `Floc_gpt`, `ControlMode`, `OperatorAction`
- `FeedDilution_On`, `FeedDilution_factor`

---

## Labels

### Event definition
- `event_now = 1` when `Overflow_Turb_NTU_clean > 100 NTU` is sustained for `sustain_points` samples.
- Default: `freq_min = 5`, `sustain_points = 4` → **20 minutes sustained**

### Forecast target
- `target_event_30m = shift(event_now, -horizon_points)`
- Default: `horizon_points = 6` → **30 minutes**

### Cause tags
- `event_type`: dominant stress component during events — `CLAY`, `UF`, or `NONE`

---

## Operational KPIs (v9 dataset — deadband=0.27)

| Zone | Criterion | Fraction |
|---|---|---|
| Green | `Overflow_Turb_NTU_clean` < 50 NTU | ~66.5% |
| Degraded | 50–100 NTU | ~24.0% |
| Crisis | >100 NTU sustained ≥20 min | ~5.0% |
| Manual fraction | `ControlMode == MANUAL` | ~27% |

---

## How to run

### Generate dataset
```bash
python src/simulate_fixed.py
```

### Validate KPIs
```bash
PYTHONIOENCODING=utf-8 python src/quick_checks.py
```

### Run notebooks
```bash
jupyter notebook notebooks/
```

### Generate HTML report
```bash
jupyter nbconvert --to html --no-input --output-dir reports reports/reporte_final.ipynb
```
