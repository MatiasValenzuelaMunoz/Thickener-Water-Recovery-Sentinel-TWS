# Thickener Water Recovery Sentinel (TWS)

A data science / ML proof-of-concept for **early detection of overflow turbidity crises** in a conventional Cu/Mo thickener. Built on a synthetic but operationally calibrated dataset (90 days · 5-min intervals · 25,920 records).

---

## Key Results

| Component | What it does | Performance |
|---|---|---|
| **Early Warning (30 min)** | Predicts sustained turbidity crisis 30 min ahead | Recall 70% · PR-AUC 0.587 · beats NTU>80 baseline |
| **Cause Diagnosis** | Classifies crisis as CLAY or Underflow Failure | 93.1% accuracy with a single process rule |
| **Early Alert (2h)** | Detects green→degraded transition 2h ahead | PR-AUC 0.134 — limited by sensor-only data |

> Full technical report: [`reports/reporte_final.html`](reports/reporte_final.html)

---

## Repository Structure

```
src/
  simulate_fixed.py       # Synthetic dataset generator (SimConfig dataclass)
  quick_checks.py         # KPI validator — event rate, turbidity distribution
  lead_time_analysis.py   # Episode-level lead time characterization

notebooks/
  01_eda.ipynb            # Exploratory data analysis
  02_feature_engineering.ipynb  # 324 features → FEATURES_PROD (221)
  03_modeling.ipynb       # Early warning model (Model A) — RandomForest tuned
  04_model_B.ipynb        # Early alert model (Model B) — green→degraded transition
  04_diagnosis.ipynb      # CLAY vs UF diagnosis — rule + LightGBM

reports/
  reporte_final.ipynb     # Executive report (Spanish)
  reporte_final.html      # Rendered report — open in browser
  figures/                # Figures used in the report

bitacora/                 # Engineering log — design decisions in Markdown
data/processed/           # Generated dataset (gitignored — run simulator first)
```

---

## Quick Start

**1. Activate environment**
```bash
source .venv/Scripts/activate   # Git Bash
# or
.venv\Scripts\activate          # CMD / PowerShell
```

**2. Generate dataset**
```bash
python src/simulate_fixed.py
```
Outputs `data/processed/thickener_timeseries.parquet` (and a versioned copy).

**3. Validate dataset KPIs**
```bash
PYTHONIOENCODING=utf-8 python src/quick_checks.py
```

**4. Run notebooks in order**
```bash
jupyter notebook notebooks/
```

---

## Dataset Design

Two turbidity columns exist by design:

| Column | Purpose |
|---|---|
| `Overflow_Turb_NTU_clean` | Ground truth — used for labels and KPI evaluation |
| `Overflow_Turb_NTU` | Measured signal with injected spikes, drift, stuck values, missings — used as ML feature |

**Labels**
- `event_now` — 1 if clean turbidity sustained >100 NTU for ≥20 min
- `target_event_30m` — `event_now` shifted 30 min ahead (main prediction target)

**Operational regimes** — `CLAY` and `UF` campaigns injected across 90 days:
- CLAY: ingress of fine clay → high rigid bed, elevated flocculant consumption
- UF (Underflow Failure): degraded purge system → solids accumulation, falling underflow flow

**Calibrated KPIs**

| Zone | Criterion | Fraction |
|---|---|---|
| Green | Turbidity < 50 NTU | ~66% |
| Degraded | 50–100 NTU | ~24% |
| Crisis | >100 NTU sustained ≥20 min | ~5% |

---

## Models

### Model A — Early Warning (30 min horizon)
- **Algorithm**: RandomForest (tuned, `n_iter=20`)
- **Features**: `FEATURES_PROD` — 221 features, no latent variables
- **Split**: temporal, train days 0–60 / test days 60–90
- **CV**: `TimeSeriesSplit(n_splits=3)`, primary metric PR-AUC
- **Test results**: PR-AUC 0.587 · ROC-AUC 0.980 · Recall 70.1% · Threshold 0.586
- **Top signals**: rolling turbidity (15–30 min), underflow flow (Qu), bed level

### Model B — Early Alert (2h horizon)
- Operates only when process is in the green zone (NTU < 50)
- **Honest performance without regime leakage**: Test PR-AUC ≈ 0.134
- **Conclusion**: 2h anticipation requires upstream mineralogy data (grain size assays, mine planning) not available in the standard DCS sensor stream

### Diagnosis — CLAY vs Underflow Failure
- **Primary rule**: `BedLevel > 1.9 m → CLAY`, else `UF` — 93.1% accuracy
- **ML complement** (LightGBM): ROC-AUC 0.836 — acts as second opinion when bed level sensor fails or divergence hasn't yet occurred

---

## Next Steps

| Phase | Goal | Status |
|---|---|---|
| 0 — Proof of concept | Validate framework on synthetic data | ✅ Complete |
| 1 — Real data validation | Retrain and evaluate on plant historian | Pending |
| 2 — Lab data integration | Add grain size assays for 2h early alert | Pending |
| 3 — Operational prototype | Control room dashboard · DCS integration | Pending |

---

## Contact

**Matias Valenzuela** — [linkedin.com/in/matiasvalenzuelam](https://www.linkedin.com/in/matiasvalenzuelam/)

If you work with instrumented thickeners and have access to historical process data, this is an open invitation to collaborate on Phase 1.
