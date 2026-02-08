# Architecture — Thickener Water Recovery Sentinel (TWS)

## Goal
Deliver a portfolio-grade system that *resembles a real operations product*:

1) **Early warning**: forecast sustained turbidity crises (>100 NTU clean) at 30 minutes.
2) **Diagnosis**: likely cause mode (CLAY / UF / FLOC).
3) **Sensor health / data quality**: detect bad instrumentation (esp. turbidity) and expose confidence.
4) **Playbook**: recommended operator actions + trade-offs across key KPIs.

## System layers

### A) Data generation (synthetic but operationally realistic)
Source of truth:
- `src/simulate_fixed.py` generates a thickener time-series dataset with:
  - clean truth turbidity (`Overflow_Turb_NTU_clean`)
  - measured turbidity (`Overflow_Turb_NTU`) with failures
  - torque in kNm and % (`RakeTorque_kNm`, `RakeTorque_pct`)
  - underflow rheology truth proxy (`UF_YieldStress_Pa`)
  - operator mode/actions and explicit feed dilution action
  - event labels (`event_now`, `target_event_30m`, `event_type`)

Data validation:
- `src/quick_checks.py` validates prevalence, distributions, and sanity targets.

### B) Analytics layer (notebooks / baseline models)
**EDA notebook** (portfolio deliverable):
- 5 key plots:
  1) timeline (clean vs measured + bands + events + manual)
  2) event episodes (duration vs severity)
  3) torque vs yield stress (and vs Cp)
  4) turbidity sensor error characterization
  5) efficiency trade-off (proxy)

**Baseline ML notebook**:
- time-based split
- lag/rolling features from measured tags
- outputs: probability of event in 30 minutes, plus diagnosis classification

### C) “Product-like” layer (dashboard + alerts)
(Not required for portfolio, but feasible as extension.)
- A dashboard page with:
  - current state & bands
  - confidence per signal
  - alert + recommended action (playbook)
  - episode view and trend analysis

## Data model philosophy: truth vs measured
- **Truth**: process reality (used for labels and evaluation).
- **Measured**: what SCADA sees; may be missing, drifting, stuck, or spiky.
- Core “high trust” signal: torque is typically reliable in real operations; turbidity is often unreliable.

## Runtime / data flow
1) `simulate_fixed.py` writes parquet to `data/processed/`
2) `quick_checks.py` prints validation
3) notebooks load parquet for EDA/ML

## Non-goals (to avoid scope creep)
- No “online clay sensor” claim. Clay is latent truth; inference uses proxies.
- No seawater chemistry modeling (for now).
- No plugging event that fully stops operation (out of MVP scope).
