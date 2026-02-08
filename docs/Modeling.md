# Modeling Guide — TWS (Baseline ML + Operational Metrics)

## Objectives
Build baseline models that are:
- operationally meaningful (early warning, low false-alarm rate)
- robust to sensor imperfections (missing/drift/stuck)
- interpretable enough for a portfolio/demo

Primary target:
- `target_event_30m` (forecast sustained event 30 minutes ahead)

Optional secondary targets:
- `event_type` classification during events (diagnosis)
- soft-sensors (estimate `UF_YieldStress_Pa` from measured tags)

---

## Data splits (critical)
Use **time-based** splits, never random splits.

Recommended:
- Train: first 60% of time
- Validation: next 20%
- Test: final 20%

Rationale:
- avoids leakage from temporal autocorrelation
- resembles real deployment (future unknown)

---

## Feature engineering (baseline)
Start with measured tags that would exist in SCADA:

**Core measured features (examples)**
- `Overflow_Turb_NTU` (measured)
- `Qf_m3h`
- `Solids_u_pct`
- `Qu_m3h`
- `BedLevel_m`
- `RakeTorque_kNm` or `RakeTorque_pct`
- `Floc_gpt`
- `FeedDilution_On`
- `ControlMode` (one-hot)

### Lags and rolling stats
For each continuous feature `x`, create:
- lags: `x(t-1)`, `x(t-2)`, `x(t-6)` (5–30 minutes)
- rolling mean: 30 min, 60 min
- rolling std: 30 min, 60 min
- optional deltas: `x - rolling_mean_60m`

Do not create thousands of features at first; keep it compact.

---

## Handling missing data
Measured tags may have NaNs (injected failures).
Options:
- simple forward-fill with max-gap limits
- add missingness indicators `isna_x`
- for tree models (XGBoost/LightGBM), NaNs can be handled natively

For portfolio clarity: start with:
- forward fill up to a limit
- missingness flags for key tags (turbidity, solids, feed flow)

---

## Baseline models
### Model 1: Logistic Regression
- pros: interpretable, fast, good baseline
- cons: may underfit nonlinearities

### Model 2: Gradient Boosted Trees (XGBoost/LightGBM)
- pros: handles nonlinearities and interactions
- cons: needs care with temporal leakage and calibration

Recommendation:
- train logistic regression first
- then one tree model

---

## Evaluation metrics (operational)
Classic ML metrics (AUC, F1) are not enough. Report:

### 1) False alarms per day
Define an alarm as `p(event in 30m) > threshold`.
Count:
- alarms when no event occurs in the forecast horizon
- normalize per day

### 2) Missed events
Fraction of true events where the model never raised an alarm in the lead window.

### 3) Lead time
For each event episode, compute how early the alarm triggers before event onset.

### 4) Confusion matrix by regime (optional)
Check performance across `Regime` to see if model fails in certain modes.

---

## Thresholding strategy
Pick threshold to hit a target false-alarm rate, e.g.:
- 0.5 alarms/day
- or 1 alarm/day

Then report recall and lead time under that constraint.

---

## Diagnosis (optional)
If using `event_type`:
- Only evaluate diagnosis during `event_now == 1` (or near-event windows)
- Beware of class imbalance (often CLAY dominates)

---

## Sensor-health integration (recommended)
Add simple turbidity confidence rules:
- flatline/stuck detection
- drift suspicion
- compare measured vs virtual estimate (later)

Then test:
- model performance using turbidity as-is
- vs using a “cleaned / confidence-weighted” turbidity feature

---

## Deliverables checklist
- Notebook: baseline model with temporal split
- Plots: ROC/PR + alarms/day vs recall curve
- Table: false alarms/day, recall, missed events, median lead time
- Short text: how sensor failures affect performance and how confidence helps
