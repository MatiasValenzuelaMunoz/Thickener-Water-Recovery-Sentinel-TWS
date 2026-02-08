# Thickener Water Recovery Sentinel (TWS)

Synthetic dataset + baseline analytics for a tailings thickener **early-warning** system focused on **overflow turbidity** (clarified water quality), with realistic operational behavior:
- **Clean process truth** (`Overflow_Turb_NTU_clean`)
- **Measured tags with instrumentation failures** (`Overflow_Turb_NTU`, etc.)
- **Event labels** derived from sustained high clean turbidity
- Operator actions / manual vs auto mode
- Thickener mechanics proxy: **rake torque** and **underflow rheology (yield stress)**

## Quick start

### 1) Create / update dataset
```bash
python src/simulate_fixed.py
```

Outputs:
- `data/processed/thickener_timeseries.parquet` (latest)
- `data/processed/thickener_timeseries_deadband{...}_sp{...}.parquet` (versioned)

### 2) Validate dataset (sanity checks)
```bash
python src/quick_checks.py
```

This prints:
- event prevalence (`event_now`)
- manual vs auto fraction (`ControlMode`)
- turbidity distribution (clean vs measured)
- points above warning/spec thresholds
- event type distribution

## Dataset: two-layer design

### Layer A — Core (non-negotiable)
**Primary outcome / truth**
- `Overflow_Turb_NTU_clean` (process truth)

**SCADA-like measured tags (may include failures)**
- `Overflow_Turb_NTU` (measured turbidity; contains spikes/stuck/drift/missing)
- `RakeTorque_kNm`, `RakeTorque_pct` (highly reliable operational signal)
- `BedLevel_m` (state proxy)
- `Qu_m3h`, `Solids_u_pct` (underflow flow & density proxies)
- `Floc_gpt` (flocculant dose)
- `FeedDilution_On` (explicit dilution action)
- `ControlMode` / `OperatorAction`

**Rheology truth**
- `UF_YieldStress_Pa` (truth proxy; torque correlates with yield stress rather than Cp)

### Layer B — High-ROI realism (optional additions)
Planned (choose 1–2):
- `Feed_P80_um` sample-and-hold every ~4h
- `Water_Conductivity_uS_cm` (robust)
- `pH_meas` + confidence flag (low reliability)

## Labels
- `event_now`: 1 when `Overflow_Turb_NTU_clean` is **sustained above 100 NTU** for `sustain_points` samples
- `target_event_30m`: event label shifted by 30 minutes (`horizon_points`)
- `event_type`: dominant driver during event (e.g., `CLAY`, `UF`, `FLOC`)
- `Regime`: regime schedule used by the simulator

## EDA “Definition of Done”
The portfolio deliverable targets:
1. Timeline: CLEAN vs measured turbidity + bands + events + manual shading
2. Event episodes: duration vs severity
3. Torque vs Yield Stress (and Torque vs Cp comparison)
4. Turbidity sensor error analysis (measured - clean)
5. Efficiency trade-off view (water recovery proxy vs quality, plus UF density & rheology context)

## Notes
- The simulator calibrates turbidity scale to hit a target event rate (default ~5%).
- Instrumentation failures are injected **only** into measured tags (never into `Overflow_Turb_NTU_clean`).
