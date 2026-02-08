# Data Dictionary (Synthetic Thickener Dataset)

This dataset is designed with **truth vs measured** separation to mimic operational reality.

## Conventions
- `_clean`: truth / process reality (no instrumentation failure)
- measured tags may include spikes/stuck/drift/missing (currently injected for a subset)
- units are included in column names where helpful

## Timestamp / indexing
| Column | Type | Unit | Description |
|---|---:|---:|---|
| `timestamp` | datetime | - | Time index at `freq_min` cadence (default 5 min). |

## Feed (to thickener)
| Column | Type | Unit | Description |
|---|---:|---:|---|
| `Qf_pulp_m3h` | float | m³/h | Pulp flow before dilution water is added. |
| `Qf_dilution_m3h` | float | m³/h | Added dilution water flow (0 when dilution off). |
| `Qf_total_m3h` | float | m³/h | Total feed flow entering thickener (pulp + dilution). |
| `Qf_m3h` | float | m³/h | Backward-compatible SCADA-like total feed flow tag (equals `Qf_total_m3h`, then may be corrupted in failures). |
| `Solids_f_pct` | float | % | Feed solids after dilution mixing. |

## Control actions / operator
| Column | Type | Unit | Description |
|---|---:|---:|---|
| `FeedDilution_On` | int | 0/1 | Explicit feed dilution action active. |
| `FeedDilution_factor` | float | - | Multiplier applied to target feed solids when dilution is on (e.g., 0.75–0.90). |
| `ControlMode` | category | - | `AUTO` / `MANUAL`. |
| `OperatorAction` | category | - | Operator action label (e.g., `INCREASE_UF`, `INCREASE_FLOC`, etc.). |

## Reagents
| Column | Type | Unit | Description |
|---|---:|---:|---|
| `Floc_gpt` | float | g/t | Flocculant dose. Typical 10–20 g/t, higher in CLAY; underdose in `FLOC` regime. |

## Internal state / mechanics
| Column | Type | Unit | Description |
|---|---:|---:|---|
| `BedLevel_m` | float | m | Bed/interface proxy state (simulated clean). |
| `RakeTorque_kNm` | float | kNm | Rake torque (primary mechanical signal). |
| `RakeTorque_pct` | float | % | Derived from kNm: `100 * kNm / torque_max_kNm`. |
| `UF_YieldStress_Pa` | float | Pa | Underflow yield stress proxy (truth rheology). Torque is driven primarily by yield stress (Ricardo principle). |

## Underflow
| Column | Type | Unit | Description |
|---|---:|---:|---|
| `Qu_m3h` | float | m³/h | Underflow discharge flow. |
| `Solids_u_pct` | float | % | Underflow solids concentration (SCADA-like; currently corrupted in failures). |
| `UF_capacity_factor` | float | 0–1 | Underflow capacity factor (UF restrictions in `UF` regime). |

## Latent drivers (truth, not assumed measured online)
| Column | Type | Unit | Description |
|---|---:|---:|---|
| `PSD_fines_idx` | float | 0–1 | Fines index proxy (higher in CLAY). |
| `Clay_pct` | float | % | Latent clay content driver. |
| `Clay_idx` | float | 0–1 | Normalized clay index derived from `Clay_pct`. |

## Turbidity (quality)
| Column | Type | Unit | Description |
|---|---:|---:|---|
| `Overflow_Turb_NTU_clean` | float | NTU | Clean truth turbidity (process reality). Used for labels. |
| `Overflow_Turb_NTU` | float | NTU | Measured turbidity tag (corrupted in failures to simulate fouling/stuck/drift). |

## Labels / metadata
| Column | Type | Unit | Description |
|---|---:|---:|---|
| `spec_limit_NTU` | float | NTU | Spec threshold (default 200). |
| `event_limit_NTU` | float | NTU | Event threshold (default 100). |
| `event_now` | int | 0/1 | 1 if sustained above `event_limit_NTU` for `sustain_points`. |
| `target_event_30m` | int | 0/1 | Forecast label (shifted by `horizon_points`, default 30 min). |
| `event_type` | category | - | Dominant mode during events: `CLAY`, `UF`, `FLOC`, else `NONE`. |
| `Regime` | category | - | Simulator regime schedule: `NORMAL`, `CLAY`, `UF`, `FLOC`. |

## Notes on “measured vs truth”
Currently failures are injected into:
- `Qf_m3h`
- `Solids_u_pct`
- `Overflow_Turb_NTU`

Planned: extend to turbidity confidence flags and additional “weak” sensors if needed.
