"""
simulate_fixed.py (v5) - synthetic tailings thickener dataset with:
- clean process truth turbidity (Overflow_Turb_NTU_clean)
- measured turbidity with instrumentation failures (Overflow_Turb_NTU)
- events labeled from clean turbidity (ground truth)
- explicit feed dilution action with physically consistent total feed flow:
    Qf_pulp_m3h (pulp stream)
    Qf_dilution_m3h (added water)
    Qf_total_m3h (pulp + added water)
    Qf_m3h is kept for backward compatibility and equals Qf_total_m3h

Outputs:
- data/processed/thickener_timeseries.parquet (latest)
- data/processed/thickener_timeseries_deadband{...}_sp{...}.parquet (versioned)

Run:
  python src/simulate_fixed.py
Then:
  python src/quick_checks.py
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class SimConfig:
    seed: int = 42
    days: int = 90
    freq_min: int = 5

    spec_limit_NTU: float = 80.0
    event_limit_NTU: float = 70.0
    sustain_points: int = 4          # 20 min sustained
    horizon_points: int = 6          # 30 min

    target_event_rate: float = 0.05
    target_tolerance: float = 0.006

    clay_days: int = 14
    uf_days: int = 14
    floc_days: int = 14
    base_turb_min: float = 10.0
    base_turb_max: float = 30.0
    turb_max: float = 160.0

    deadband: float = 0.33
    turb_power: float = 1.75

    # explicit feed dilution (operational action)
    feed_dilution_events_per_30d: float = 3.0
    feed_dilution_duration_min: Tuple[int, int] = (60, 240)
    feed_dilution_factor_range: Tuple[float, float] = (0.75, 0.90)  # target multiplier on Solids_f_pct

    # failures
    missing_rate_per_tag: float = 0.01
    spikes_per_day_per_tag: float = 2.0
    stuck_events_per_30d_per_tag: float = 2.0
    stuck_duration_min: Tuple[int, int] = (120, 360)
    drift_events_per_90d_per_tag: float = 1.0
    drift_magnitude: Dict[str, float] | None = None

    # calibration search upper bound (needs to be high with turb_power=1.6)
    scale_search_hi: float = 2500.0


def _default_drift_magnitude() -> Dict[str, float]:
    # Qf_m3h now represents total feed flow to thickener (pulp + dilution)
    return {"Qf_m3h": 0.08, "Solids_u_pct": -0.04, "Overflow_Turb_NTU": -10.0}


def rolling_std(x: np.ndarray, window: int) -> np.ndarray:
    return pd.Series(x).rolling(window=window, min_periods=max(3, window // 5)).std().bfill().fillna(0.0).to_numpy()


def rolling_mean(x: np.ndarray, window: int) -> np.ndarray:
    return pd.Series(x).rolling(window=window, min_periods=max(3, window // 5)).mean().bfill().fillna(float(x[0])).to_numpy()


def normalize_01(x: np.ndarray) -> np.ndarray:
    lo = np.nanpercentile(x, 1)
    hi = np.nanpercentile(x, 99)
    if hi - lo < 1e-9:
        return np.zeros_like(x)
    return np.clip((x - lo) / (hi - lo), 0.0, 1.0)


def sustained_above(x: np.ndarray, threshold: float, sustain_points: int) -> np.ndarray:
    above = x > threshold
    s = pd.Series(above.astype(int)).rolling(window=sustain_points, min_periods=sustain_points).sum()
    return (s == sustain_points).fillna(False).to_numpy()


def day_to_idx(day: int, cfg: SimConfig) -> int:
    return int(day * 24 * 60 / cfg.freq_min)


def build_regime_schedule(cfg: SimConfig, n: int) -> np.ndarray:
    regime = np.array(["NORMAL"] * n, dtype=object)
    start_day = 14
    clay_start = start_day
    uf_start = clay_start + cfg.clay_days
    floc_start = uf_start + cfg.uf_days

    clay_i0, clay_i1 = day_to_idx(clay_start, cfg), day_to_idx(clay_start + cfg.clay_days, cfg)
    uf_i0, uf_i1 = day_to_idx(uf_start, cfg), day_to_idx(uf_start + cfg.uf_days, cfg)
    floc_i0, floc_i1 = day_to_idx(floc_start, cfg), day_to_idx(floc_start + cfg.floc_days, cfg)

    regime[clay_i0:clay_i1] = "CLAY"
    regime[uf_i0:uf_i1] = "UF"
    regime[floc_i0:floc_i1] = "FLOC"
    return regime


def simulate_clean(cfg: SimConfig) -> tuple[pd.DataFrame, dict]:
    if cfg.drift_magnitude is None:
        object.__setattr__(cfg, "drift_magnitude", _default_drift_magnitude())

    rng = np.random.default_rng(cfg.seed)
    index = pd.date_range("2026-01-01", periods=int(cfg.days * 24 * 60 / cfg.freq_min), freq=f"{cfg.freq_min}min")
    n = len(index)

    regime = build_regime_schedule(cfg, n)

    # Feed (pulp stream, before dilution water is added)
    qf_base = rng.uniform(450, 650)
    diurnal = 80 * np.sin(np.linspace(0, 2 * np.pi * cfg.days, n))
    qf_rw = np.cumsum(rng.normal(0, 0.8, n))
    Qf_pulp = np.clip(qf_base + diurnal + qf_rw + rng.normal(0, 25, n), 250, 900)

    Sol_f_base = np.clip(
        14 + 2.0 * np.sin(np.linspace(0, 4 * np.pi * cfg.days, n)) + 0.002 * (Qf_pulp - 550) + rng.normal(0, 1.2, n),
        8,
        22,
    )

    # ---------------------------------------------------------------------
    # Explicit feed dilution schedule
    # ---------------------------------------------------------------------
    FeedDilution_On = np.zeros(n, dtype=int)
    FeedDilution_factor = np.ones(n, dtype=float)

    points_per_hour = int(60 / cfg.freq_min)

    dilution_segments = int(cfg.feed_dilution_events_per_30d * (cfg.days / 30.0))
    for _ in range(dilution_segments):
        # bias start times toward CLAY window
        if rng.random() < 0.75:
            idx_candidates = np.where(regime == "CLAY")[0]
        else:
            idx_candidates = np.arange(n)
        if len(idx_candidates) == 0:
            continue

        start = int(rng.choice(idx_candidates))
        dur_min = rng.integers(cfg.feed_dilution_duration_min[0], cfg.feed_dilution_duration_min[1] + 1)
        dur = max(1, int(dur_min / cfg.freq_min))
        end = min(n, start + dur)

        # factor is the target multiplier on final Solids_f_pct
        factor = rng.uniform(cfg.feed_dilution_factor_range[0], cfg.feed_dilution_factor_range[1])

        FeedDilution_On[start:end] = 1
        FeedDilution_factor[start:end] = factor

    # Convert factor -> required dilution water to achieve lower solids%, keeping solids mass with pulp stream.
    # If target is: Sol_f_final = Sol_f_base * factor,
    # then Qf_total = Qf_pulp / factor  =>  Qf_dilution = Qf_total - Qf_pulp = Qf_pulp*(1/factor - 1)
    Qf_dilution = np.zeros(n, dtype=float)
    mask_dil = FeedDilution_On.astype(bool)
    Qf_dilution[mask_dil] = Qf_pulp[mask_dil] * (1.0 / FeedDilution_factor[mask_dil] - 1.0)

    Qf_total = Qf_pulp + Qf_dilution

    # Recompute final feed solids % by mixing.
    # solids mass proxy from pulp stream stays constant; only total volumetric flow increases.
    Ms = Qf_pulp * (Sol_f_base / 100.0)
    Sol_f = np.clip(100.0 * Ms / np.maximum(Qf_total, 1e-6), 6, 22)

    # Fines
    PSD = np.zeros(n)
    for i in range(n):
        r = regime[i]
        if r == "CLAY":
            target = rng.uniform(0.55, 0.80)
        elif r == "NORMAL":
            target = rng.uniform(0.10, 0.30)
        else:
            target = rng.uniform(0.15, 0.40)
        PSD[i] = 0.982 * (PSD[i - 1] if i > 0 else target) + 0.018 * target + rng.normal(0, 0.01)
    PSD = np.clip(PSD, 0.05, 0.85)

    # solids load now uses total feed flow and final solids %
    solids_load = Qf_total * (Sol_f / 100.0)
    load_norm = normalize_01(solids_load)

    # Floc
    floc_auto = 10 + 16 * PSD + 10 * load_norm + rng.normal(0, 1.4, n)
    floc_auto = np.where(regime == "FLOC", floc_auto * rng.uniform(0.55, 0.75), floc_auto)
    Floc = np.clip(floc_auto, 5, 40)

    # UF capacity (more frequent, stronger degradations)
    UF_capacity = np.ones(n)
    uf_mask = (regime == "UF")
    if uf_mask.any():
        points_per_hour = int(60 / cfg.freq_min)
        uf_idx = np.where(uf_mask)[0]
        for _ in range(int(cfg.uf_days * 3.0)):
            start = rng.integers(uf_idx[0], uf_idx[-1])
            duration = rng.integers(2 * points_per_hour, 4 * points_per_hour + 1)
            cap = rng.uniform(0.70, 0.92)
            UF_capacity[start:start + duration] = np.minimum(UF_capacity[start:start + duration], cap)

    # Underflow depends on total feed flow (what thickener actually sees)
    Qu = np.clip((0.35 * Qf_total + rng.normal(0, 18, n)) * UF_capacity, 80, 450)

    # Bed + torque
    bed = np.zeros(n)
    torque = np.zeros(n)
    bed[0] = rng.uniform(1.0, 2.0)
    torque[0] = rng.uniform(20, 45)
    for i in range(1, n):
        load_effect = 0.014 * (load_norm[i] - 0.5) + 0.018 * (PSD[i] - 0.3)
        uf_effect = 0.022 * ((1.0 - UF_capacity[i]) * 3.0)
        drawdown = 0.0010 * ((Qu[i] - 220) / 220.0)
        bed[i] = np.clip(bed[i - 1] + load_effect + uf_effect - drawdown + rng.normal(0, 0.01), 0.5, 3.5)
        torque_target = 20 + 16 * bed[i] + 22 * PSD[i]
        torque[i] = np.clip(0.97 * torque[i - 1] + 0.03 * torque_target + rng.normal(0, 1.0), 10, 95)

    Sol_u = np.clip(58 + 5.0 * (bed - 1.5) - 7.0 * PSD - 0.010 * (Qu - 220) + rng.normal(0, 1.4, n), 45, 68)

    # ControlMode (tuned to hit 15-30%)
    control_mode = np.array(["AUTO"] * n, dtype=object)
    torque_rm = rolling_mean(torque, window=12)
    bed_rm = rolling_mean(bed, window=12)

    manual_prob = np.clip(
        0.10
        + 0.22 * (torque_rm > 70).astype(float)
        + 0.18 * (bed_rm > 2.6).astype(float)
        + 0.12 * (regime == "FLOC").astype(float)
        + 0.10 * (regime == "UF").astype(float),
        0.03,
        0.85,
    )

    rng2 = np.random.default_rng(cfg.seed + 101)
    for i in range(1, n):
        if control_mode[i - 1] == "AUTO":
            control_mode[i] = "MANUAL" if (rng2.random() < manual_prob[i] * 0.12) else "AUTO"
        else:
            calm = (torque_rm[i] < 55) and (bed_rm[i] < 2.2)
            p_exit = 0.03 + (0.08 if calm else 0.0)
            control_mode[i] = "AUTO" if (rng2.random() < p_exit) else "MANUAL"

    # OperatorAction + penalty (small effect on turbidity)
    OperatorAction = np.array(["NONE"] * n, dtype=object)
    action_penalty = np.zeros(n)
    points_per_hour = int(60 / cfg.freq_min)

    for i in range(n):
        if control_mode[i] != "MANUAL":
            continue
        bed_high = bed[i] > 2.6
        torque_high = torque[i] > 75
        floc_need_i = 8 + 16 * PSD[i] + 10 * load_norm[i]
        floc_low = Floc[i] < (floc_need_i - 3.0)

        if bed_high or torque_high:
            action = "INCREASE_UF" if (rng.random() < 0.85) else "DECREASE_UF"
        elif floc_low:
            action = "INCREASE_FLOC" if (rng.random() < 0.85) else "DECREASE_FLOC"
        else:
            if rng.random() < 0.94:
                continue
            action = rng.choice(["INCREASE_FLOC", "INCREASE_UF", "DECREASE_FLOC", "DECREASE_UF"], p=[0.45, 0.35, 0.10, 0.10])

        OperatorAction[i] = action
        duration = rng.integers(int(0.33 * points_per_hour), int(1.0 * points_per_hour) + 1)
        j0, j1 = i, min(n, i + duration)

        if action == "INCREASE_UF":
            action_penalty[j0:j1] += rng.uniform(3, 10)
        elif action == "DECREASE_UF":
            action_penalty[j0:j1] += rng.uniform(0, 3)
        elif action == "INCREASE_FLOC":
            action_penalty[j0:j1] -= rng.uniform(1, 6)
        elif action == "DECREASE_FLOC":
            action_penalty[j0:j1] += rng.uniform(1, 7)

    # Stress components
    fines_c = normalize_01(PSD)
    load_c = normalize_01(solids_load)
    var_c = normalize_01(rolling_std(Qf_total, window=12) + rolling_std(Sol_f, window=12))
    floc_need = 8 + 16 * PSD + 10 * load_c
    floc_deficit = np.clip((floc_need - Floc) / 25.0, 0.0, 1.0)
    floc_c = floc_deficit
    uf_c = normalize_01((1.0 - UF_capacity) + np.clip((220 - Qu) / 220.0, 0, 1))

    w = np.array([0.18, 0.22, 0.12, 0.22, 0.26])
    stress = w[0]*fines_c + w[1]*load_c + w[2]*var_c + w[3]*floc_c + w[4]*uf_c
    stress += np.where(regime == "CLAY", 0.03 * fines_c, 0.0)
    stress += np.where(regime == "UF", 0.03 * uf_c, 0.0)
    stress += np.where(regime == "FLOC", 0.03 * floc_c, 0.0)
    stress = np.clip(stress, 0.0, 1.0)

    # Turbidity (clean) with deadband
    lag6 = np.roll(stress, 6); lag6[:6] = lag6[6]
    lag12 = np.roll(stress, 12); lag12[:12] = lag12[12]
    stress_term = np.clip(0.65 * lag6 + 0.35 * lag12, 0.0, 1.0)
    effective = np.clip((stress_term - cfg.deadband) / (1.0 - cfg.deadband), 0.0, 1.0)

    base_turb = rng.uniform(cfg.base_turb_min, cfg.base_turb_max, size=n)
    noise = rng.normal(0, 3.0, n)

    def turb_with_scale(scale: float) -> np.ndarray:
        t = base_turb + scale * (effective ** cfg.turb_power) + action_penalty + noise
        return np.clip(t, 5.0, cfg.turb_max)

    # Calibrate scale on CLEAN turbidity
    lo, hi = 0.0, float(cfg.scale_search_hi)
    best_scale = None
    best_rate = None
    for _ in range(26):
        mid = (lo + hi) / 2.0
        t = turb_with_scale(mid)
        ev = sustained_above(t, cfg.event_limit_NTU, cfg.sustain_points).astype(int)
        rate = float(ev.mean())
        best_scale, best_rate = mid, rate
        if abs(rate - cfg.target_event_rate) <= cfg.target_tolerance:
            break
        if rate < cfg.target_event_rate:
            lo = mid
        else:
            hi = mid

    turb_clean = turb_with_scale(float(best_scale))
    event_now = sustained_above(turb_clean, cfg.event_limit_NTU, cfg.sustain_points).astype(int)

    dominant = np.array(["CLAY", "UF", "FLOC"], dtype=object)[np.argmax(np.vstack([fines_c, uf_c, floc_c]).T, axis=1)]
    event_type = np.array(["NONE"] * n, dtype=object)
    event_type[event_now == 1] = dominant[event_now == 1]

    df = pd.DataFrame(
        {
            "timestamp": index,

            # Feed flows (explicit)
            "Qf_pulp_m3h": Qf_pulp,
            "Qf_dilution_m3h": Qf_dilution,
            "Qf_total_m3h": Qf_total,

            # Backward-compatible SCADA-like tag for feed to thickener
            "Qf_m3h": Qf_total,

            # Feed solids after dilution mixing
            "Solids_f_pct": Sol_f,

            # Explicit dilution action
            "FeedDilution_On": FeedDilution_On,
            "FeedDilution_factor": FeedDilution_factor,

            # Process / control
            "PSD_fines_idx": PSD,
            "Floc_gpt": Floc,
            "UF_capacity_factor": UF_capacity,
            "Qu_m3h": Qu,
            "Solids_u_pct": Sol_u,
            "BedLevel_m": bed,
            "RakeTorque_pct": torque,
            "Overflow_Turb_NTU_clean": turb_clean,  # ground truth process
            "Overflow_Turb_NTU": turb_clean,        # measured (will be corrupted later)
            "ControlMode": control_mode,
            "OperatorAction": OperatorAction,

            # constants and labels
            "spec_limit_NTU": cfg.spec_limit_NTU,
            "event_limit_NTU": cfg.event_limit_NTU,
            "event_now": event_now,
            "event_type": event_type,
            "Regime": regime,
        }
    )

    df["target_event_30m"] = df["event_now"].shift(-cfg.horizon_points).fillna(0).astype(int)

    debug = {
        "deadband": cfg.deadband,
        "sustain_points": cfg.sustain_points,
        "effective_q50": float(np.quantile(effective, 0.50)),
        "effective_q95": float(np.quantile(effective, 0.95)),
        "effective_q99": float(np.quantile(effective, 0.99)),
        "scale": float(best_scale),
        "event_rate": float(df["event_now"].mean()),
        "dilution_on_rate": float(df["FeedDilution_On"].mean()),
        "qf_total_q95": float(np.quantile(Qf_total, 0.95)),
    }
    return df, debug


def inject_failures(cfg: SimConfig, df: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(cfg.seed + 7)
    out = df.copy()
    n = len(out)

    points_per_day = int(24 * 60 / cfg.freq_min)
    points_per_hour = int(60 / cfg.freq_min)

    # NOTE: only corrupt measured turbidity and SCADA-like tags, never the clean truth
    # Qf_m3h is treated as the SCADA tag for total feed flow to thickener
    tags = ["Qf_m3h", "Solids_u_pct", "Overflow_Turb_NTU"]

    for tag in tags:
        x = out[tag].to_numpy().copy()

        # spikes
        expected_spikes = int(cfg.spikes_per_day_per_tag * cfg.days)
        idx = rng.integers(0, n, size=expected_spikes)
        for i in idx:
            if tag == "Qf_m3h":
                x[i] += rng.uniform(-250, 250)
            elif tag == "Solids_u_pct":
                x[i] += rng.uniform(-15, 15)
            else:
                x[i] += rng.uniform(-40, 40)

        # stuck
        stuck_segments = int(cfg.stuck_events_per_30d_per_tag * (cfg.days / 30.0))
        for _ in range(stuck_segments):
            start = rng.integers(0, n - 2 * points_per_hour)
            dur_min = rng.integers(cfg.stuck_duration_min[0], cfg.stuck_duration_min[1] + 1)
            dur = int(dur_min / cfg.freq_min)
            x[start:start + dur] = x[start]

        # drift
        drift_segments = int(cfg.drift_events_per_90d_per_tag)
        for _ in range(drift_segments):
            start = rng.integers(int(0.2 * n), int(0.8 * n))
            dur = rng.integers(7 * points_per_day, 12 * points_per_day)
            end = min(n, start + dur)

            mag = (cfg.drift_magnitude or _default_drift_magnitude()).get(tag, 0.0)
            if tag == "Qf_m3h":
                x[start:end] *= (1.0 + mag)
            elif tag == "Solids_u_pct":
                x[start:end] *= (1.0 + mag)
            else:
                x[start:end] += mag

        # missing
        missing_n = int(cfg.missing_rate_per_tag * n)
        miss_idx = rng.choice(np.arange(n), size=missing_n, replace=False)
        x[miss_idx] = np.nan

        # clip
        if tag == "Qf_m3h":
            x = np.clip(x, 0.0, 1200.0)  # allow total flow including dilution
        elif tag == "Solids_u_pct":
            x = np.clip(x, 0.0, 100.0)
        else:
            x = np.clip(x, 0.0, cfg.turb_max)

        out[tag] = x

    return out


def main() -> None:
    cfg = SimConfig()
    df_clean, debug = simulate_clean(cfg)
    df = inject_failures(cfg, df_clean)

    out_dir = Path("data/processed")
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / f"thickener_timeseries_deadband{str(cfg.deadband).replace('.','p')}_sp{cfg.sustain_points}.parquet"
    df.to_parquet(out_path, index=False)

    # convenience file
    df.to_parquet(out_dir / "thickener_timeseries.parquet", index=False)

    print("DEBUG SUMMARY:", debug)
    print("Wrote:", out_path)


if __name__ == "__main__":
    main()