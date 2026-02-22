# Data Dictionary (Synthetic Thickener Dataset — v9)

This dataset is designed with **truth vs measured** separation to mimic operational reality.

## Conventions
- `_clean`: truth / process reality (no instrumentation failure)
- measured tags may include spikes / stuck / drift / missing (injected via `inject_failures()`)
- units are included in column names where helpful

## Timestamp / indexing
| Column | Type | Unit | Description |
|---|---:|---:|---|
| `timestamp` | datetime | — | Time index at 5-min cadence. 90 days → 25,920 rows. |

## Feed (to thickener)
| Column | Type | Unit | Description |
|---|---:|---:|---|
| `Qf_pulp_m3h` | float | m³/h | Pulp flow before dilution water is added. |
| `Qf_dilution_m3h` | float | m³/h | Added dilution water flow (0 when dilution off). |
| `Qf_total_m3h` | float | m³/h | Total feed flow entering thickener (pulp + dilution). |
| `Qf_m3h` | float | m³/h | SCADA-like total feed flow tag (equals `Qf_total_m3h`; may be corrupted by failures). |
| `Solids_f_pct` | float | % | Feed solids after dilution mixing. |
| `Feedwell_Solids_pct` | float | % | Feedwell solids concentration. |

## Control actions / operator
| Column | Type | Unit | Description |
|---|---:|---:|---|
| `FeedDilution_On` | int | 0/1 | Explicit feed dilution action active. |
| `FeedDilution_factor` | float | — | Multiplier applied to target feed solids when dilution is on (e.g., 0.75–0.90). |
| `ControlMode` | category | — | `AUTO` / `MANUAL`. |
| `OperatorAction` | category | — | Operator action label (e.g., `INCREASE_UF`, `INCREASE_FLOC`, `NONE`). |

## Reagents
| Column | Type | Unit | Description |
|---|---:|---:|---|
| `Floc_gpt` | float | g/t | Flocculant dose. Typical 10–20 g/t, higher in CLAY episodes. |
| `Floc_effectiveness` | float | 0–1 | **Latent.** True flocculant effectiveness (not measurable online). Driven by Clay_idx and pH. Excluded from `FEATURES_PROD`. |

## Internal state / mechanics
| Column | Type | Unit | Description |
|---|---:|---:|---|
| `BedLevel_m` | float | m | Bed/interface level (simulated clean). Key diagnosis signal: CLAY events → BedLevel > 1.9 m. |
| `RakeTorque_kNm` | float | kNm | Rake torque (primary mechanical signal). |
| `RakeTorque_pct` | float | % | Derived: `100 × kNm / torque_max_kNm`. |
| `UF_YieldStress_Pa` | float | Pa | Underflow yield stress proxy (truth rheology). Torque is driven primarily by yield stress (Ricardo principle). |
| `Bogging_factor` | float | 0–1 | Torque penalty factor under high-stress conditions. |

## Underflow
| Column | Type | Unit | Description |
|---|---:|---:|---|
| `Qu_m3h` | float | m³/h | Underflow discharge flow. |
| `Solids_u_pct` | float | % | Underflow solids concentration (SCADA-like; may be corrupted by failures). |
| `UF_capacity_factor` | float | 0–1 | Underflow capacity factor (decreases in UF regime). |

## Overflow
| Column | Type | Unit | Description |
|---|---:|---:|---|
| `Qo_m3h` | float | m³/h | Overflow (clarified water) flow. Used in water recovery proxy. |
| `WaterRecovery_proxy` | float | 0–1 | `Qw_uf / Qw_feed` — ratio of water in underflow to water in feed. |

## pH
| Column | Type | Unit | Description |
|---|---:|---:|---|
| `pH_clean` | float | pH | **Latent.** True pH (no instrumentation failure). Increases with Clay_idx; drives Floc_effectiveness down. Excluded from `FEATURES_PROD`. |
| `pH_feed` | float | pH | Measured pH with injected failures (spikes, stuck, drift, missing). Available as ML feature. |

## Latent drivers (truth, not assumed measured online)
| Column | Type | Unit | Description |
|---|---:|---:|---|
| `PSD_fines_idx` | float | 0–1 | Fines index proxy (higher in CLAY). Latent. |
| `Clay_pct` | float | % | Latent clay content driver. |
| `Clay_idx` | float | 0–1 | Normalized clay index derived from `Clay_pct`. Causal chain: Clay_idx↑ → pH↑ → Floc_effectiveness↓ → turbidity↑. |

## Turbidity (quality)
| Column | Type | Unit | Description |
|---|---:|---:|---|
| `Overflow_Turb_NTU_clean` | float | NTU | **Ground truth** turbidity (process reality). Used for labels and KPI evaluation. |
| `Overflow_Turb_NTU` | float | NTU | Measured turbidity tag (corrupted: spikes, stuck, drift, missing). Used as ML feature. |

## Labels / metadata
| Column | Type | Unit | Description |
|---|---:|---:|---|
| `spec_limit_NTU` | float | NTU | Spec threshold (200 NTU). |
| `event_limit_NTU` | float | NTU | Event threshold (100 NTU). |
| `event_now` | int | 0/1 | 1 if `Overflow_Turb_NTU_clean` sustained >100 NTU for ≥4 consecutive points (20 min). |
| `target_event_30m` | int | 0/1 | `event_now` shifted −6 points (30 min ahead). **Main prediction target.** |
| `event_type` | category | — | Dominant mode during events: `CLAY`, `UF`, or `NONE`. |
| `Regime` | category | — | Simulator regime schedule: `NORMAL`, `CLAY`, `UF`. |

## Failure injection (measured tags)
Failures are injected **after** clean simulation via `inject_failures()`:

| Tag | Failure types |
|---|---|
| `Overflow_Turb_NTU` | random missing, spikes, stuck values, drift segments |
| `Qf_m3h` | random missing, spikes, stuck values, drift segments |
| `Solids_u_pct` | random missing, spikes, stuck values, drift segments |
| `pH_feed` | random missing, spikes, stuck values |

## Feature set summary (from `02_feature_engineering.ipynb`)
| Set | Size | Description |
|---|---|---|
| `FEATURES_ALL` | 324 | All engineered features including latent variables |
| `FEATURES_PROD` | 221 | Production-safe: no latent variables (`pH_clean`, `Floc_effectiveness` excluded) |
| `FEATURES_B` | ~221 | `FEATURES_PROD` minus `is_CLAY`/`is_UF` regime leakage flags + 6 slope features |
| `FEATURES_TOP30_PROD` | 30 | Top features by SHAP importance |
