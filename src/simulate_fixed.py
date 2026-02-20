"""
simulate_fixed.py (v8.0) - Operationally realistic thickener dataset (portfolio-grade).

Goals supported:
1) Early warning: forecast sustained clean turbidity crises (>100 NTU clean) at 30 minutes.
2) Diagnosis: cause mode (CLAY / UF).
3) Sensor health: measured turbidity failures + quality context.
4) Playbook: recommended operator actions + trade-offs; includes operator interventions.

Key modeling choices (to keep coherence + stability):
- Keep "truth" process variables (clean turbidity, YS, bed) separate from measured tags (failures injected).
- Model CLAY/UF as campaigns.
- Use a torque PROXY (kNm-like) driven by YieldStress and Bed + clay bogging term.
  It is NOT dimensioned by D and K to avoid runaway scaling; it is an operational indicator.
- Closed-loop operator: actions change manipulated variables with small, bounded gains:
    - UF valve / pump (affects Qu a bit; trade-off: carryover increases turbidity)
    - Feed dilution (already present; trade-off: lowers YS/torque, may reduce water recovery proxy)
- Add playbook columns:
    - RecommendedAction (heuristic)
    - ExpectedTradeoff (text label)
    - ActionScore_turb / ActionScore_torque (simple signed scores)

Outputs:
- data/processed/thickener_timeseries.parquet (latest)
- data/processed/thickener_timeseries_deadband{...}_sp{...}.parquet (versioned)
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

    spec_limit_NTU: float = 200.0
    event_limit_NTU: float = 100.0
    sustain_points: int = 4          # 20 min
    horizon_points: int = 6          # 30 min

    target_event_rate: float = 0.05
    target_tolerance: float = 0.006

    # Múltiples episodios distribuidos en los 90 días (start_day, duration_days)
    # CLAY: planificación de mina → episodios más largos y espaciados
    # UF: falla mecánica → episodios más cortos y abruptos
    clay_episodes: tuple = ((10, 5), (38, 6), (65, 5))   # 16 días total
    uf_episodes:   tuple = ((20, 4), (52, 4), (78, 4))   # 12 días total

    # turbidity response
    base_turb_min: float = 20.0
    base_turb_max: float = 45.0
    turb_max: float = 600.0
    deadband: float = 0.27
    turb_power: float = 1.55
    scale_search_hi: float = 6000.0

    # explicit dilution action schedule (operator-initiated sometimes)
    feed_dilution_events_per_30d: float = 3.0
    feed_dilution_duration_min: Tuple[int, int] = (60, 240)
    feed_dilution_factor_range: Tuple[float, float] = (0.75, 0.90)
    feedwell_solids_target_range_pct: Tuple[float, float] = (12.0, 18.0)

    # torque proxy scaling (kept stable and not saturating)
    torque_rated_kNm: float = 20.0
    torque_clip_kNm: float = 80.0
    torque_noise_kNm: float = 0.35

    # torque/yield stress limits (for gates)
    ys_limit_Pa: float = 20.0

    # clay ranges
    clay_pct_min: float = 1.0
    clay_pct_max: float = 12.0

    # sensor failures
    missing_rate_per_tag: float = 0.01
    spikes_per_day_per_tag: float = 2.0
    stuck_events_per_30d_per_tag: float = 2.0
    stuck_duration_min: Tuple[int, int] = (120, 360)
    drift_events_per_90d_per_tag: float = 1.0
    drift_magnitude: Dict[str, float] | None = None

    # event typing thresholds
    event_type_override_th_uf: float = 0.55

    # operator closed-loop gains (small and bounded)
    qu_setpoint_step: float = 12.0          # m3/h step per action
    qu_setpoint_clip: Tuple[float, float] = (-60.0, 60.0)

    # carryover penalty when pushing UF hard (trade-off)
    carryover_gain_NTU: float = 0.12        # NTU per (m3/h) of positive Qu setpoint delta


def _default_drift_magnitude() -> Dict[str, float]:
    return {"Qf_m3h": 0.08, "Solids_u_pct": -0.04, "Overflow_Turb_NTU": -10.0}


def rolling_std(x: np.ndarray, window: int) -> np.ndarray:
    return (
        pd.Series(x)
        .rolling(window=window, min_periods=max(3, window // 5))
        .std()
        .bfill()
        .fillna(0.0)
        .to_numpy()
    )


def rolling_mean(x: np.ndarray, window: int) -> np.ndarray:
    return (
        pd.Series(x)
        .rolling(window=window, min_periods=max(3, window // 5))
        .mean()
        .bfill()
        .fillna(float(x[0]))
        .to_numpy()
    )


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
    for start, dur in cfg.clay_episodes:
        i0, i1 = day_to_idx(start, cfg), day_to_idx(start + dur, cfg)
        regime[i0:i1] = "CLAY"
    for start, dur in cfg.uf_episodes:
        i0, i1 = day_to_idx(start, cfg), day_to_idx(start + dur, cfg)
        regime[i0:i1] = "UF"
    return regime


def simulate_clean(cfg: SimConfig) -> tuple[pd.DataFrame, dict]:
    if cfg.drift_magnitude is None:
        object.__setattr__(cfg, "drift_magnitude", _default_drift_magnitude())

    rng = np.random.default_rng(cfg.seed)
    index = pd.date_range(
        "2026-01-01",
        periods=int(cfg.days * 24 * 60 / cfg.freq_min),
        freq=f"{cfg.freq_min}min",
    )
    n = len(index)

    regime = build_regime_schedule(cfg, n)

    # ------------------ Feed (pulp) + dilution schedule ------------------
    qf_base = rng.uniform(450, 650)
    diurnal = 80 * np.sin(np.linspace(0, 2 * np.pi * cfg.days, n))
    qf_rw = np.cumsum(rng.normal(0, 0.8, n))
    Qf_pulp = np.clip(qf_base + diurnal + qf_rw + rng.normal(0, 25, n), 250, 900)

    Sol_f_base = 32.0 + 3.0 * np.sin(np.linspace(0, 4 * np.pi * cfg.days, n))
    Sol_f_base += 0.003 * (Qf_pulp - 550)
    Sol_f_base += rng.normal(0, 1.8, n)
    Sol_f_base = np.clip(Sol_f_base, 20, 45)

    FeedDilution_On = np.zeros(n, dtype=int)
    FeedDilution_factor = np.ones(n, dtype=float)

    dilution_segments = int(cfg.feed_dilution_events_per_30d * (cfg.days / 30.0))
    for _ in range(dilution_segments):
        idx_candidates = np.where(regime == "CLAY")[0] if (rng.random() < 0.75) else np.arange(n)
        if len(idx_candidates) == 0:
            continue
        start = int(rng.choice(idx_candidates))
        dur_min = rng.integers(cfg.feed_dilution_duration_min[0], cfg.feed_dilution_duration_min[1] + 1)
        dur = max(1, int(dur_min / cfg.freq_min))
        end = min(n, start + dur)
        factor = rng.uniform(cfg.feed_dilution_factor_range[0], cfg.feed_dilution_factor_range[1])

        FeedDilution_On[start:end] = 1
        FeedDilution_factor[start:end] = factor

    Qf_dilution = np.zeros(n, dtype=float)
    mask_dil = FeedDilution_On.astype(bool)
    Qf_dilution[mask_dil] = Qf_pulp[mask_dil] * (1.0 / FeedDilution_factor[mask_dil] - 1.0)

    Qf_total = Qf_pulp + Qf_dilution
    Ms = Qf_pulp * (Sol_f_base / 100.0)
    Sol_f = np.clip(100.0 * Ms / np.maximum(Qf_total, 1e-6), 18, 45)

    # feedwell solids
    Feedwell_Solids_pct = Sol_f.copy()
    fw_target = rng.uniform(cfg.feedwell_solids_target_range_pct[0], cfg.feedwell_solids_target_range_pct[1], size=n)
    Feedwell_Solids_pct[mask_dil] = fw_target[mask_dil] + rng.normal(0, 0.9, int(mask_dil.sum()))
    Feedwell_Solids_pct[~mask_dil] = Sol_f[~mask_dil] + rng.normal(0, 0.6, int((~mask_dil).sum()))
    Feedwell_Solids_pct = np.clip(Feedwell_Solids_pct, 8.0, 45.0)

    # ------------------ Latent drivers ------------------
    PSD = np.zeros(n)
    Clay_pct = np.zeros(n)

    clay_target_normal = rng.uniform(1.0, 4.0)
    clay_target_clay = rng.uniform(6.0, 10.0)
    clay_target_other = rng.uniform(2.0, 6.0)

    for i in range(n):
        r = regime[i]
        if r == "CLAY":
            clay_target = clay_target_clay + rng.normal(0, 0.6)
            psd_target = rng.uniform(0.55, 0.80)
        elif r == "NORMAL":
            clay_target = clay_target_normal + rng.normal(0, 0.4)
            psd_target = rng.uniform(0.10, 0.30)
        else:
            clay_target = clay_target_other + rng.normal(0, 0.5)
            psd_target = rng.uniform(0.15, 0.40)

        Clay_pct[i] = 0.985 * (Clay_pct[i - 1] if i > 0 else clay_target) + 0.015 * clay_target + rng.normal(0, 0.08)
        PSD[i] = 0.982 * (PSD[i - 1] if i > 0 else psd_target) + 0.018 * psd_target + rng.normal(0, 0.01)

    Clay_pct = np.clip(Clay_pct, cfg.clay_pct_min, cfg.clay_pct_max)
    Clay_idx = normalize_01(Clay_pct)
    PSD = np.clip(PSD, 0.05, 0.85)

    solids_load = Qf_total * (Sol_f / 100.0)
    load_norm = normalize_01(solids_load)

    # ------------------ Floc dose (process variable; no prep-fail incidents) ------------------
    floc_need = 12 + 18 * PSD + 14 * load_norm + 10 * Clay_idx + rng.normal(0, 1.2, n)
    Floc_gpt = np.clip(floc_need + rng.normal(0, 1.5, n), 5, 35)

    # ------------------ UF capacity + base Qu ------------------
    UF_capacity = np.ones(n)
    uf_mask = (regime == "UF")
    if uf_mask.any():
        points_per_hour = int(60 / cfg.freq_min)
        uf_idx = np.where(uf_mask)[0]
        total_uf_days = sum(dur for _, dur in cfg.uf_episodes)
        n_dropouts = int(total_uf_days * 3.0)
        for _ in range(n_dropouts):
            start = int(rng.choice(uf_idx))          # solo índices UF reales
            duration = rng.integers(2 * points_per_hour, 4 * points_per_hour + 1)
            cap = rng.uniform(0.70, 0.92)
            UF_capacity[start:start + duration] = np.minimum(
                UF_capacity[start:start + duration], cap)

    Qu_base = np.clip((0.35 * Qf_total + rng.normal(0, 18, n)) * UF_capacity, 80, 450)

    # ------------------ Closed-loop operator: setpoint deltas ------------------
    Qu_sp_delta = np.zeros(n, dtype=float)
    OperatorAction = np.array(["NONE"] * n, dtype=object)
    ControlMode = np.array(["AUTO"] * n, dtype=object)

    # We use "observable" proxies to decide actions (no future info)
    # Here we use truth for simplicity; later you can use measured tags if desired.
    # We'll compute bed/YS first pass with base Qu, then do a second pass applying setpoints.
    # For stability, we do a single pass with lagged signals.

    # Placeholder arrays; computed later after bed/YS exists
    # We'll fill OperatorAction/ControlMode after first bed/YS estimate.

    # ------------------ Bed dynamics (using Qu_base for first pass) ------------------
    bed = np.zeros(n)
    bed[0] = rng.uniform(1.0, 2.0)
    for i in range(1, n):
        load_effect = 0.014 * (load_norm[i] - 0.5) + 0.018 * (PSD[i] - 0.3)
        uf_effect = 0.028 * ((1.0 - UF_capacity[i]) * 3.0)
        drawdown = 0.0010 * ((Qu_base[i] - 220) / 220.0)
        bed[i] = np.clip(bed[i - 1] + load_effect + uf_effect - drawdown + rng.normal(0, 0.01), 0.5, 3.5)

    # ------------------ Underflow density (first pass) ------------------
    Sol_u = 64.0 + 4.0 * (bed - 1.8) - 6.5 * (PSD - 0.25) - 0.006 * (Qu_base - 260)
    Sol_u += rng.normal(0, 1.6, n)
    Sol_u += np.where(regime == "UF", -2.0 * (1.0 - UF_capacity) * 3.0, 0.0)
    Sol_u += np.where(regime == "CLAY", -1.5 * PSD, 0.0)
    Sol_u = np.clip(Sol_u, 50, 75)

    # ------------------ Yield stress (truth) base ------------------
    dens_term = np.exp(0.10 * (Sol_u - 60.0))
    clay_amp = 1.0 + 2.5 * Clay_idx
    fines_amp = 1.0 + 0.8 * np.clip(PSD - 0.25, 0.0, 0.6)

    UF_YieldStress_Pa_base = 4.5 * dens_term * clay_amp * fines_amp + rng.normal(0, 0.8, n)
    UF_YieldStress_Pa_base = np.clip(UF_YieldStress_Pa_base, 0.5, 60.0)

    # ------------------ Torque proxy base (truth) ------------------
    # Torque increases with YS and bed; add mild clay bogging interaction.
    ys = UF_YieldStress_Pa_base
    ys_gate = np.clip((ys - cfg.ys_limit_Pa) / 20.0, 0.0, 1.0)
    Bogging_factor = 1.0 + 0.25 * Clay_idx * ys_gate

    RakeTorque_kNm_base = (
        0.35 * ys + 2.0 * bed
    ) * Bogging_factor + rng.normal(0, cfg.torque_noise_kNm, n)
    RakeTorque_kNm_base = np.clip(RakeTorque_kNm_base, 0.0, cfg.torque_clip_kNm)
    RakeTorque_pct_base = 100.0 * RakeTorque_kNm_base / cfg.torque_rated_kNm

    # ------------------ Decide operator mode/actions (based on lagged observables) ------------------
    bed_rm = rolling_mean(bed, window=12)
    torque_rm = rolling_mean(RakeTorque_pct_base, window=12)

    rng2 = np.random.default_rng(cfg.seed + 101)

    for i in range(1, n):
        # probability of manual when stressed
        manual_prob = np.clip(
            0.08
            + 0.18 * float(torque_rm[i] > 85)
            + 0.15 * float(bed_rm[i] > 2.6)
            + 0.10 * float(regime[i] == "UF"),
            0.02, 0.75
        )

        if ControlMode[i - 1] == "AUTO":
            ControlMode[i] = "MANUAL" if (rng2.random() < manual_prob * 0.12) else "AUTO"
        else:
            calm = (torque_rm[i] < 70) and (bed_rm[i] < 2.2)
            p_exit = 0.03 + (0.08 if calm else 0.0)
            ControlMode[i] = "AUTO" if (rng2.random() < p_exit) else "MANUAL"

        if ControlMode[i] != "MANUAL":
            continue

        # Action logic (bounded setpoints)
        bed_high = bed_rm[i] > 2.6
        torque_high = torque_rm[i] > 90

        if bed_high or torque_high:
            OperatorAction[i] = "INCREASE_UF"
            Qu_sp_delta[i] = np.clip(Qu_sp_delta[i - 1] + cfg.qu_setpoint_step, *cfg.qu_setpoint_clip)
        else:
            # sometimes do nothing or minor tweaks
            if rng2.random() < 0.85:
                Qu_sp_delta[i] = Qu_sp_delta[i - 1]
            else:
                OperatorAction[i] = "INCREASE_UF"
                Qu_sp_delta[i] = np.clip(Qu_sp_delta[i - 1] + 0.5 * cfg.qu_setpoint_step, *cfg.qu_setpoint_clip)

        # small relaxation of setpoints in AUTO to avoid drifting forever
        if ControlMode[i] == "AUTO":
            Qu_sp_delta[i] = 0.98 * Qu_sp_delta[i]

    # forward-fill setpoints (piecewise constant)
    Qu_sp_delta = pd.Series(Qu_sp_delta).replace(0.0, np.nan).ffill().fillna(0.0).to_numpy()

    # ------------------ Apply operator setpoints to manipulated variables ------------------
    Qu = np.clip(Qu_base + Qu_sp_delta, 60, 500)

    UF_YieldStress_Pa = 4.5 * dens_term * clay_amp * fines_amp + rng.normal(0, 0.6, n)
    UF_YieldStress_Pa = np.clip(UF_YieldStress_Pa, 0.5, 60.0)

    # Recompute torque proxy with final YS (this is what operator sees)
    ys = UF_YieldStress_Pa
    ys_gate = np.clip((ys - cfg.ys_limit_Pa) / 20.0, 0.0, 1.0)
    Bogging_factor = 1.0 + 0.25 * Clay_idx * ys_gate
    RakeTorque_kNm = (0.35 * ys + 2.0 * bed) * Bogging_factor + rng.normal(0, cfg.torque_noise_kNm, n)
    RakeTorque_kNm = np.clip(RakeTorque_kNm, 0.0, cfg.torque_clip_kNm)
    RakeTorque_pct = 100.0 * RakeTorque_kNm / cfg.torque_rated_kNm

    # ------------------ Stress components for turbidity ------------------
    fines_c = normalize_01(PSD)
    load_c = normalize_01(solids_load)
    var_c = normalize_01(rolling_std(Qf_total, window=12) + rolling_std(Sol_f, window=12))

    uf_c = normalize_01((1.0 - UF_capacity) + np.clip((220 - Qu) / 220.0, 0, 1))

    # Carryover trade-off: pushing UF increases turbidity slightly
    carryover_penalty = cfg.carryover_gain_NTU * np.clip(Qu_sp_delta, 0.0, 200.0)

    # Weights renormalized after removing floc component: (fines, load, var, uf)
    w = np.array([0.24, 0.26, 0.15, 0.35])
    stress = w[0] * fines_c + w[1] * load_c + w[2] * var_c + w[3] * uf_c
    stress += np.where(regime == "CLAY", 0.03 * fines_c, 0.0)
    stress += np.where(regime == "UF", 0.03 * uf_c, 0.0)
    stress = np.clip(stress, 0.0, 1.0)

    lag6 = np.roll(stress, 6); lag6[:6] = lag6[6]
    lag12 = np.roll(stress, 12); lag12[:12] = lag12[12]
    stress_term = np.clip(0.65 * lag6 + 0.35 * lag12, 0.0, 1.0)
    effective = np.clip((stress_term - cfg.deadband) / (1.0 - cfg.deadband), 0.0, 1.0)

    base_turb = rng.uniform(cfg.base_turb_min, cfg.base_turb_max, size=n)
    noise = rng.normal(0, 3.0, n)

    def turb_with_scale(scale: float) -> np.ndarray:
        t = base_turb + scale * (effective ** cfg.turb_power) + carryover_penalty + noise
        return np.clip(t, 5.0, cfg.turb_max)

    lo, hi = 0.0, float(cfg.scale_search_hi)
    best_scale = 0.0
    for _ in range(26):
        mid = (lo + hi) / 2.0
        t = turb_with_scale(mid)
        ev = sustained_above(t, cfg.event_limit_NTU, cfg.sustain_points).astype(int)
        rate = float(ev.mean())
        best_scale = mid
        if abs(rate - cfg.target_event_rate) <= cfg.target_tolerance:
            break
        if rate < cfg.target_event_rate:
            lo = mid
        else:
            hi = mid

    turb_clean = turb_with_scale(float(best_scale))
    event_now = sustained_above(turb_clean, cfg.event_limit_NTU, cfg.sustain_points).astype(int)

    # ------------------ Diagnosis / event typing (CLAY vs UF) ------------------
    dominant_raw = np.array(["CLAY", "UF"], dtype=object)[
        np.argmax(np.vstack([fines_c, uf_c]).T, axis=1)
    ]
    event_type_raw = np.array(["NONE"] * n, dtype=object)
    event_type_raw[event_now == 1] = dominant_raw[event_now == 1]

    event_type = event_type_raw.copy()
    ev_mask = (event_now == 1)

    uf_override = ev_mask & (regime == "UF") & (uf_c > cfg.event_type_override_th_uf)
    event_type[uf_override] = "UF"

    # ------------------ Playbook recommendation (heuristic) ------------------
    # Provide a recommended action and a simple trade-off annotation.
    RecommendedAction = np.array(["NONE"] * n, dtype=object)
    ExpectedTradeoff = np.array([""] * n, dtype=object)
    ActionScore_turb = np.zeros(n, dtype=float)
    ActionScore_torque = np.zeros(n, dtype=float)

    for i in range(n):
        if turb_clean[i] < 60 and RakeTorque_pct[i] < 80 and bed[i] < 2.4:
            continue

        # if UF constrained -> recommend increase UF (trade-off carryover)
        if (regime[i] == "UF") or (uf_c[i] > 0.60) or (bed[i] > 2.7):
            RecommendedAction[i] = "INCREASE_UF_WATCH_CARRYOVER"
            ExpectedTradeoff[i] = "↓bed/↓torque, possible ↑turbidity via carryover"
            ActionScore_turb[i] = -0.2
            ActionScore_torque[i] = +0.7
        # if clay/fines high -> recommend dilution and floc optimization
        elif (regime[i] == "CLAY") or (Clay_idx[i] > 0.65):
            RecommendedAction[i] = "START_DILUTION_AND_OPTIMIZE_FLOC"
            ExpectedTradeoff[i] = "↓YS/↓torque, likely ↓turbidity, but ↑water use"
            ActionScore_turb[i] = +0.6
            ActionScore_torque[i] = +0.5
        else:
            RecommendedAction[i] = "MONITOR_AND_TUNE"
            ExpectedTradeoff[i] = "small adjustments"
            ActionScore_turb[i] = +0.1
            ActionScore_torque[i] = +0.1

    # ------------------ Water recovery proxy ------------------
    solids_out_proxy = Qu * (Sol_u / 100.0)
    solids_in_proxy = Qf_total * (Sol_f / 100.0)
    water_recovery_proxy = 1.0 - (solids_out_proxy / np.maximum(solids_in_proxy, 1e-6))
    water_recovery_proxy = np.clip(water_recovery_proxy, -1.0, 1.0)

    df = pd.DataFrame(
        {
            "timestamp": index,
            "Qf_pulp_m3h": Qf_pulp,
            "Qf_dilution_m3h": Qf_dilution,
            "Qf_total_m3h": Qf_total,
            "Qf_m3h": Qf_total,
            "Solids_f_pct": Sol_f,
            "Feedwell_Solids_pct": Feedwell_Solids_pct,
            "FeedDilution_On": FeedDilution_On,
            "FeedDilution_factor": FeedDilution_factor,
            "PSD_fines_idx": PSD,
            "Clay_pct": Clay_pct,
            "Clay_idx": Clay_idx,
            "Floc_gpt": Floc_gpt,
            "UF_capacity_factor": UF_capacity,
            "Qu_base_m3h": Qu_base,
            "Qu_sp_delta_m3h": Qu_sp_delta,
            "Qu_m3h": Qu,
            "Solids_u_pct": Sol_u,
            "BedLevel_m": bed,
            "UF_YieldStress_Pa": UF_YieldStress_Pa,
            "Bogging_factor": Bogging_factor,
            "RakeTorque_kNm": RakeTorque_kNm,
            "RakeTorque_pct": RakeTorque_pct,
            "Overflow_Turb_NTU_clean": turb_clean,
            "Overflow_Turb_NTU": turb_clean,
            "ControlMode": ControlMode,
            "OperatorAction": OperatorAction,
            "RecommendedAction": RecommendedAction,
            "ExpectedTradeoff": ExpectedTradeoff,
            "ActionScore_turb": ActionScore_turb,
            "ActionScore_torque": ActionScore_torque,
            "WaterRecovery_proxy": water_recovery_proxy,
            "spec_limit_NTU": cfg.spec_limit_NTU,
            "event_limit_NTU": cfg.event_limit_NTU,
            "event_now": event_now,
            "event_type_raw": event_type_raw,
            "event_type": event_type,
            "Regime": regime,
        }
    )

    df["target_event_30m"] = df["event_now"].shift(-cfg.horizon_points).fillna(0).astype(int)

    debug = {
        "deadband": cfg.deadband,
        "scale": float(best_scale),
        "event_rate": float(df["event_now"].mean()),
        "manual_rate": float((df["ControlMode"] == "MANUAL").mean()),
        "torque_pct_p95": float(np.nanquantile(df["RakeTorque_pct"], 0.95)),
        "turb_clean_p50": float(np.nanquantile(df["Overflow_Turb_NTU_clean"], 0.50)),
    }
    return df, debug


def inject_failures(cfg: SimConfig, df: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(cfg.seed + 7)
    out = df.copy()
    n = len(out)

    points_per_day = int(24 * 60 / cfg.freq_min)
    points_per_hour = int(60 / cfg.freq_min)

    tags = ["Qf_m3h", "Solids_u_pct", "Overflow_Turb_NTU"]

    for tag in tags:
        x = out[tag].to_numpy().copy()

        expected_spikes = int(cfg.spikes_per_day_per_tag * cfg.days)
        idx = rng.integers(0, n, size=expected_spikes)
        for i in idx:
            if tag == "Qf_m3h":
                x[i] += rng.uniform(-250, 250)
            elif tag == "Solids_u_pct":
                x[i] += rng.uniform(-15, 15)
            else:
                x[i] += rng.uniform(-40, 40)

        stuck_segments = int(cfg.stuck_events_per_30d_per_tag * (cfg.days / 30.0))
        for _ in range(stuck_segments):
            start = rng.integers(0, n - 2 * points_per_hour)
            dur_min = rng.integers(cfg.stuck_duration_min[0], cfg.stuck_duration_min[1] + 1)
            dur = int(dur_min / cfg.freq_min)
            x[start:start + dur] = x[start]

        drift_segments = int(cfg.drift_events_per_90d_per_tag)
        for _ in range(drift_segments):
            start = rng.integers(int(0.2 * n), int(0.8 * n))
            dur = rng.integers(7 * points_per_day, 12 * points_per_day)
            end = min(n, start + dur)

            mag = (cfg.drift_magnitude or _default_drift_magnitude()).get(tag, 0.0)
            if tag in ("Qf_m3h", "Solids_u_pct"):
                x[start:end] *= (1.0 + mag)
            else:
                x[start:end] += mag

        missing_n = int(cfg.missing_rate_per_tag * n)
        miss_idx = rng.choice(np.arange(n), size=missing_n, replace=False)
        x[miss_idx] = np.nan

        if tag == "Qf_m3h":
            x = np.clip(x, 0.0, 1200.0)
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
    df.to_parquet(out_dir / "thickener_timeseries.parquet", index=False)

    print("DEBUG SUMMARY:", debug)
    print("Wrote:", out_path)


if __name__ == "__main__":
    main()
