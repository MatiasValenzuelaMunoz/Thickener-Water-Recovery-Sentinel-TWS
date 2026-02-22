# Architecture — Thickener Water Recovery Sentinel (TWS)

## Implemented scope (v1.0)

1. **Early warning**: forecast sustained turbidity crises (>100 NTU clean) at 30 minutes — Model A (RandomForest).
2. **Cause diagnosis**: CLAY vs Underflow Failure — BedLevel rule + LightGBM complement.
3. **Early alert (2h)**: honest evaluation; concluded that sensor-only data is insufficient — Model B.

**Not implemented:** sensor health / instrument failure detection (deferred), dashboard / API (out of scope for v1.0).

---

## System layers

### A) Data generation (synthetic but operationally realistic)

- `src/simulate_fixed.py` generates a thickener time-series dataset with:
  - clean truth turbidity (`Overflow_Turb_NTU_clean`) and measured turbidity (`Overflow_Turb_NTU`) with failures
  - torque (`RakeTorque_kNm`, `RakeTorque_pct`), underflow (`Qu_m3h`), overflow (`Qo_m3h`)
  - latent drivers: `Clay_idx`, `pH_clean`, `Floc_effectiveness`
  - measured pH with failures (`pH_feed`)
  - operator mode/actions and explicit feed dilution action
  - event labels (`event_now`, `target_event_30m`, `event_type`)

- `src/quick_checks.py` validates prevalence, distributions, and KPI targets.

### B) Feature engineering

- `notebooks/02_feature_engineering.ipynb` generates 324 features → `FEATURES_PROD` (221 production features, no latent variables).
- Output: `thickener_features.parquet` (25,872 × 327).

### C) Modeling notebooks

| Notebook | Component | Algorithm | Key result |
|---|---|---|---|
| `03_modeling.ipynb` | Model A — Early Warning | RandomForest | PR-AUC 0.587, Recall 70% |
| `04_model_B.ipynb` | Model B — Early Alert 2h | LightGBM | PR-AUC 0.134 (sensor-only limit) |
| `04_diagnosis.ipynb` | CLAY vs UF Diagnosis | BedLevel rule + LightGBM | 93.1% accuracy |

### D) Report

- `reports/reporte_final.ipynb` — executive report in Spanish for operators and stakeholders.
- Generated HTML: `jupyter nbconvert --to html --no-input --output-dir reports reports/reporte_final.ipynb`

---

## Data model philosophy: truth vs measured

- **Truth**: process reality (used for labels and evaluation).
- **Measured**: what SCADA sees; may be missing, drifting, stuck, or spiky.
- Core "high trust" signal: torque is typically reliable in real operations; turbidity is often unreliable.

---

## Runtime / data flow

```
simulate_fixed.py → data/processed/thickener_timeseries.parquet
       ↓
quick_checks.py (KPI validation)
       ↓
01_eda.ipynb → exploratory analysis
       ↓
02_feature_engineering.ipynb → thickener_features.parquet
       ↓
03_modeling.ipynb → Model A (RandomForest)
04_model_B.ipynb → Model B (2h alert)
04_diagnosis.ipynb → CLAY vs UF
       ↓
reports/reporte_final.ipynb → executive report
```

---

## Non-goals (v1.0)

- No "online clay sensor" claim — clay is latent truth; inference uses proxies.
- No sensor health / confidence module — deferred to future phase.
- No dashboard or API — out of scope for this proof-of-concept.
- No seawater chemistry modeling.
