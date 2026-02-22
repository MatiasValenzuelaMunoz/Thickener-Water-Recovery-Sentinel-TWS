# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Thickener Water Recovery Sentinel (TWS)** — a portfolio data science/ML project for mining-metallurgical process optimization. It focuses on early detection of overflow turbidity crises in a conventional copper/molybdenum thickener (espesador), using a synthetic but operationally realistic dataset.

**Implemented components (v1.0 — complete):**
1. **Early Warning (Model A)**: binary forecast of sustained turbidity crisis (>100 NTU clean, ≥20 min) at 30-minute horizon (`target_event_30m`) — RandomForest, PR-AUC 0.587, Recall 70%
2. **Early Alert (Model B)**: green→degraded transition alert at 2-hour horizon — honest conclusion: sensor-only data insufficient, mineralogy required
3. **Cause Diagnosis**: classify crisis as CLAY vs UF — 93.1% accuracy via BedLevel rule; LightGBM as complement

**Not implemented (by design):**
- Sensor health / instrument failure detection — deferred to future phase
- Prescriptive playbook — simplified to diagnosis-driven action table in report

## Environment

Python 3.11.9 with a local venv at `.venv/`. Activate with:

```bash
.venv\Scripts\activate        # Windows CMD/PowerShell
source .venv/Scripts/activate # Git Bash
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## Key Commands

```bash
# Generate the synthetic dataset (outputs to data/processed/)
python src/simulate_fixed.py

# Validate dataset KPIs against operational targets
PYTHONIOENCODING=utf-8 python src/quick_checks.py

# Launch Jupyter for EDA and modeling
jupyter notebook notebooks/

# Export final report to HTML
jupyter nbconvert --to html --no-input --output-dir reports reports/reporte_final.ipynb
```

## Repository Structure

```
src/
  simulate_fixed.py         # Synthetic dataset generator
  quick_checks.py           # KPI validator
  lead_time_analysis.py     # Episode-level lead time characterization

notebooks/
  01_eda.ipynb              # Exploratory data analysis
  02_feature_engineering.ipynb  # Feature generation (FEATURES_PROD=221)
  03_modeling.ipynb         # Model A — Early Warning (RandomForest)
  04_model_B.ipynb          # Model B — Early Alert 2h + leakage analysis
  04_diagnosis.ipynb        # CLAY vs UF diagnosis

reports/
  reporte_final.ipynb       # Executive report (Spanish, for operators/stakeholders)
  figures/                  # PNG figures used in report

bitacora/                   # Engineering log — decision rationale in Markdown
data/processed/             # Generated dataset (gitignored — run simulator first)
```

## Data Architecture

The dataset is **not committed** (gitignored). It must be generated before running notebooks.

**Two turbidity columns exist by design:**
- `Overflow_Turb_NTU_clean` — ground truth process state (no instrument failures); used for labels and KPI evaluation
- `Overflow_Turb_NTU` — realistic measured signal with injected spikes, stuck values, drift, and missings; used as an ML feature

**Labels:**
- `event_now` — 1 if sustained `>event_limit_NTU` CLEAN for ≥4 points (20 min)
- `target_event_30m` — `event_now` shifted −6 points (30 min ahead); the main prediction target

**Operational regimes** (`Regime` column): `NORMAL`, `CLAY`, `UF` — distributed across 90 days:
- CLAY episodes: days (10,5), (38,6), (65,5) → 16 days total
- UF episodes: days (20,4), (52,4), (78,4) → 12 days total
- Motivation: balanced train/test event rate with SPLIT_DAY=60 (~5.6% train / ~4.1% test)

## Simulation Architecture (`src/simulate_fixed.py`)

`SimConfig` (frozen dataclass) holds all parameters. Key calibration parameters:
- `deadband` — controls shape of stress→turbidity curve; current value in code: **0.27**
- `event_limit_NTU` / `spec_limit_NTU` — 100 / 200 NTU
- `target_event_rate` — 0.05 (±0.006 tolerance); achieved via binary search on `scale`
- Stress weights (post-FLOC removal): `w = [0.22, 0.24, 0.13, 0.31, 0.10]` (fines, load, var, uf, floc_c)

The simulator runs in two passes: first a base pass to estimate bed/torque, then a control-action pass that applies operator setpoints. Sensor failures are injected afterward via `inject_failures()`.

**Output filename convention:** `thickener_timeseries_deadband{X}_sp{Y}.parquet` plus a fixed alias `thickener_timeseries.parquet`. `quick_checks.py` auto-selects the latest versioned file.

**Dataset version used for modeling (v9 — 43 columns):**
`thickener_timeseries_deadband0p27_sp4.parquet`

Added vs v8: `pH_clean`, `pH_feed` (with failures), `Floc_effectiveness` (latent), `Qo_m3h` (overflow flow), corrected `WaterRecovery_proxy` formula.

## Operational KPI Targets (current — deadband=0.27, v9)

| KPI | Target | Current |
|-----|--------|---------|
| Verde (`Overflow_Turb_NTU_clean` < 50 NTU) | ~65–70% | 66.5% |
| Degradado (50–100 NTU) | ~15% | 24.0% |
| Eventos sostenidos (>100 NTU, ≥20 min) | 3–6% | 4.99% |
| Fracción MANUAL | 15–30% | ~27% |

## Key Design Decisions

- **FLOC removed (2026-02-18):** FLOC mode represented only 0.2% of events — not learnable. Diagnosis simplified to binary CLAY vs UF. See `bitacora/06_descarte_floc.md`.
- **SMOTE rejected:** always hurt PR-AUC in experiments. Use `class_weight='balanced'` instead.
- **Temporal CV only:** never shuffle-split on time series. Use `TimeSeriesSplit`.
- **PR-AUC as primary metric:** correct for ~5% class imbalance; ROC-AUC is misleading here.
- **Model B conclusion:** 2h early alert requires mineralogy data (grain size assays), not available in standard DCS sensor stream.

## Bitácora (Engineering Log)

The `bitacora/` directory contains decision rationale in Markdown. Read before modifying simulation parameters:
- `01_dataset_sintetico_calibracion_Version1.md` — early label definitions (⚠️ thresholds superseded: now 100 NTU, not 70)
- `05_bitacora.md` — calibration runs A/B/C; Corrida C selected (deadband=0.30 at the time; later updated to 0.27 with pH additions)
- `06_descarte_floc.md` — decision to remove FLOC mechanism
- `project_walkthrough.md` — **complete decision log** for all components; structured for four reader profiles
