# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Thickener Water Recovery Sentinel (TWS)** — a portfolio data science/ML project for mining-metallurgical process optimization. It focuses on early detection of overflow turbidity crises in a conventional copper/molybdenum thickener (espesador), using a synthetic but operationally realistic dataset.

ML goals:
1. **Early warning**: binary forecast of sustained turbidity crisis (>100 NTU clean, ≥20 min) at 30-minute horizon (`target_event_30m`)
2. **Diagnosis**: classify cause mode — CLAY / UF
3. **Sensor health**: detect instrument failures on measured tags
4. **Prescriptive playbook**: recommend operator actions with trade-offs

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
python src/quick_checks.py

# Launch Jupyter for EDA
jupyter notebook notebooks/
```

## Data Architecture

The dataset is **not committed** (gitignored). It must be generated before running notebooks.

**Two turbidity columns exist by design:**
- `Overflow_Turb_NTU_clean` — ground truth process state (no instrument failures); used for labels and KPI evaluation
- `Overflow_Turb_NTU` — realistic measured signal with injected spikes, stuck values, drift, and missings; used as an ML feature

**Labels:**
- `event_now` — 1 if sustained `>event_limit_NTU` CLEAN for ≥4 points (20 min)
- `target_event_30m` — `event_now` shifted −6 points (30 min ahead); the main prediction target

**Operational regimes** (`Regime` column): `NORMAL`, `CLAY`, `UF` — campaigns injected on days 14–28 and 28–42 respectively.

## Simulation Architecture (`src/simulate_fixed.py`)

`SimConfig` (frozen dataclass) holds all parameters. Key calibration parameters:
- `deadband` — controls shape of stress→turbidity curve; 0.30 is the preferred value
- `event_limit_NTU` / `spec_limit_NTU` — 100 / 200 NTU (latest calibration)
- `target_event_rate` — 0.05 (±0.006 tolerance); achieved via binary search on `scale`

The simulator runs in two passes: first a base pass to estimate bed/torque, then a control-action pass that applies operator setpoints. Sensor failures are injected afterward via `inject_failures()`.

**Output filename convention:** `thickener_timeseries_deadband{X}_sp{Y}.parquet` plus a fixed alias `thickener_timeseries.parquet`. `quick_checks.py` auto-selects the latest versioned file.

## Operational KPI Targets (calibrated)

| KPI | Target | Current (deadband=0.30) |
|-----|--------|------------------------|
| Verde (`Overflow_Turb_NTU_clean` < 50 NTU) | ~77–80% | 77.78% |
| Degradado (50–100 NTU) | ~15% | 12.78% |
| Eventos sostenidos (>100 NTU, ≥20 min) | 3–6% | 5.10% |
| Fracción MANUAL | 15–30% | ~27% |

## Bitácora (Engineering Log)

The `bitacora/` directory contains decision rationale in Markdown. Read these before modifying simulation parameters:
- `01_dataset_sintetico_calibracion_Version1.md` — label definitions and realism criteria
- `05_bitacora.md` — latest calibration run (Corrida C, deadband=0.30), selected configuration
- `06_descarte_floc.md` — decision to remove FLOC mechanism; diagnosis simplified to CLAY vs UF
