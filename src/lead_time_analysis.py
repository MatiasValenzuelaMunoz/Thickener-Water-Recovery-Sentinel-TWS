"""
Lead Time Analysis — TWS
========================
Pregunta central: cuando el modelo (o cualquier señal) dispara una alarma,
¿cuánto tiempo REAL falta antes de que la crisis comience?

Metodología:
1. Para cada episodio de crisis (event_now=1 sostenido), identificar t_crisis = primer punto.
2. Analizar cuántos minutos antes de t_crisis la turbidez limpia cruza cada umbral.
3. Analizar cuántos minutos antes de t_crisis las features upstream (pH, BedLevel, Floc)
   muestran señal distinguible (media/std de la ventana pre-crisis vs baseline).
4. Simular el comportamiento de un "modelo trend-follower" (umbral en NTU rolling 15m)
   y medir su lead time real respecto al inicio de la crisis.

Output: texto + CSV con lead times por episodio.
"""

import sys
import pathlib

sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

# ── Rutas ─────────────────────────────────────────────────────────────────────
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "processed"

ts_path = DATA / "thickener_timeseries.parquet"
feat_path = DATA / "thickener_features.parquet"

ts = pd.read_parquet(ts_path)
feat = pd.read_parquet(feat_path)

FREQ_MIN = 5          # minutos por punto
EVENT_MIN_POINTS = 4  # ≥4 puntos consecutivos = crisis (20 min)

print("=" * 65)
print("  ANÁLISIS DE LEAD TIME REAL — TWS")
print("=" * 65)
print(f"  Dataset: {ts.shape[0]} filas × {ts.shape[1]} cols")
print(f"  Frecuencia: {FREQ_MIN} min/punto")
print()

# ── 1. Identificar episodios de crisis ────────────────────────────────────────
# Un episodio es una secuencia contigua de event_now=1 con al menos EVENT_MIN_POINTS puntos.

def find_crisis_episodes(series, min_points=4):
    """Retorna lista de (idx_start, idx_end) de cada episodio."""
    episodes = []
    in_ep = False
    start = None
    for i, v in enumerate(series):
        if v == 1 and not in_ep:
            in_ep = True
            start = i
        elif v == 0 and in_ep:
            if i - start >= min_points:
                episodes.append((start, i - 1))
            in_ep = False
    if in_ep and len(series) - start >= min_points:
        episodes.append((start, len(series) - 1))
    return episodes

episodes = find_crisis_episodes(ts["event_now"].values)
print(f"  Episodios de crisis encontrados: {len(episodes)}")
print()

# ── 2. Lead time de la turbidez limpia antes de cada umbral ──────────────────
LOOK_BACK = 72   # puntos hacia atrás (6 horas) para buscar señal previa
THRESH_50  = 50   # inicio zona degradada
THRESH_80  = 80   # zona de alerta alta
THRESH_100 = 100  # inicio crisis (event_limit)

results = []

for ep_idx, (t0, t1) in enumerate(episodes):
    row = {"episode": ep_idx + 1, "t_crisis_idx": t0,
           "t_crisis_day": t0 * FREQ_MIN / 60 / 24,
           "regime": ts["Regime"].iloc[t0]}

    # Ventana pre-crisis (hasta 6h antes)
    pre_start = max(0, t0 - LOOK_BACK)
    pre_ntu = ts["Overflow_Turb_NTU_clean"].iloc[pre_start:t0].values

    # ¿Cuántos puntos antes cruzó cada umbral (primera vez)?
    for thresh, name in [(THRESH_50, "lead_50NTU"), (THRESH_80, "lead_80NTU")]:
        crossings = np.where(pre_ntu >= thresh)[0]
        if len(crossings) > 0:
            # Primer cruce dentro de la ventana de 6h
            first = crossings[0]
            lead_points = len(pre_ntu) - first
            row[name + "_min"] = lead_points * FREQ_MIN
        else:
            row[name + "_min"] = np.nan   # no cruzó en las 6h previas (señal limpia antes)

    # Turbidez en el punto de inicio de la crisis y 30/60 min antes
    row["NTU_at_crisis"]   = ts["Overflow_Turb_NTU_clean"].iloc[t0]
    row["NTU_30min_before"] = ts["Overflow_Turb_NTU_clean"].iloc[max(0, t0 - 6)]  # 6 pts = 30 min
    row["NTU_60min_before"] = ts["Overflow_Turb_NTU_clean"].iloc[max(0, t0 - 12)] # 12 pts = 60 min

    # ── Señal upstream: pH_feed ──
    if "pH_feed" in ts.columns:
        pre_ph = ts["pH_feed"].iloc[pre_start:t0].dropna().values
        pre_ph_baseline = ts["pH_feed"].iloc[max(0, pre_start - 144):pre_start].dropna().values
        row["pH_mean_pre6h"] = np.nanmean(pre_ph) if len(pre_ph) > 0 else np.nan
        row["pH_mean_baseline"] = np.nanmean(pre_ph_baseline) if len(pre_ph_baseline) > 0 else np.nan
        row["pH_delta_vs_baseline"] = row["pH_mean_pre6h"] - row["pH_mean_baseline"] if not np.isnan(row.get("pH_mean_pre6h", np.nan)) else np.nan

    # ── Señal upstream: BedLevel ──
    if "BedLevel_m" in ts.columns:
        pre_bed = ts["BedLevel_m"].iloc[pre_start:t0].values
        bed_baseline = ts["BedLevel_m"].iloc[max(0, pre_start - 144):pre_start].values
        row["bed_mean_pre6h"] = np.nanmean(pre_bed)
        row["bed_mean_baseline"] = np.nanmean(bed_baseline) if len(bed_baseline) > 0 else np.nan

    # ── Señal upstream: Floc_gpt ──
    if "Floc_gpt" in ts.columns:
        pre_floc = ts["Floc_gpt"].iloc[pre_start:t0].values
        floc_baseline = ts["Floc_gpt"].iloc[max(0, pre_start - 144):pre_start].values
        row["floc_mean_pre6h"] = np.nanmean(pre_floc)
        row["floc_mean_baseline"] = np.nanmean(floc_baseline) if len(floc_baseline) > 0 else np.nan

    results.append(row)

df = pd.DataFrame(results)

# ── 3. Resumen de lead times ──────────────────────────────────────────────────
print("─" * 65)
print("  LEAD TIME DE TURBIDEZ ANTES DE LA CRISIS (por episodio)")
print("─" * 65)
print(f"  {'Ep':>3}  {'Régimen':<8}  {'NTU-60m':>8}  {'NTU-30m':>8}  {'NTU@crisis':>10}  "
      f"{'Lead >50 (min)':>14}  {'Lead >80 (min)':>14}")
print("  " + "-"*63)
for _, r in df.iterrows():
    l50 = f"{r['lead_50NTU_min']:.0f}" if not np.isnan(r.get("lead_50NTU_min", np.nan)) else "  >6h"
    l80 = f"{r['lead_80NTU_min']:.0f}" if not np.isnan(r.get("lead_80NTU_min", np.nan)) else "  >6h"
    print(f"  {r['episode']:>3}  {r['regime']:<8}  "
          f"{r['NTU_60min_before']:>8.1f}  {r['NTU_30min_before']:>8.1f}  "
          f"{r['NTU_at_crisis']:>10.1f}  {l50:>14}  {l80:>14}")

print()
print("  Interpretación:")
print("  - NTU-60m/30m > 50: la turbidez YA estaba degradada antes de la crisis")
print("  - Lead >50 pequeño: la zona degradada aparece poco antes de la crisis")
print("  - Lead >80 ≈ 0-10 min: el modelo basado en NTU tiene lead time real ~10 min")
print()

# Estadísticas agregadas
print("─" * 65)
print("  ESTADÍSTICAS AGREGADAS")
print("─" * 65)
ntu_30 = df["NTU_30min_before"].dropna()
ntu_60 = df["NTU_60min_before"].dropna()
lead50  = df["lead_50NTU_min"].dropna()
lead80  = df["lead_80NTU_min"].dropna()

print(f"  NTU 30 min antes de crisis:  media={ntu_30.mean():.1f}  mediana={ntu_30.median():.1f}  "
      f"min={ntu_30.min():.1f}  max={ntu_30.max():.1f}")
print(f"  NTU 60 min antes de crisis:  media={ntu_60.mean():.1f}  mediana={ntu_60.median():.1f}  "
      f"min={ntu_60.min():.1f}  max={ntu_60.max():.1f}")
print()
print(f"  Episodios donde NTU >50 ya a -30 min:  {(df['NTU_30min_before'] > 50).sum()} / {len(df)}")
print(f"  Episodios donde NTU >80 ya a -30 min:  {(df['NTU_30min_before'] > 80).sum()} / {len(df)}")
print(f"  Episodios donde NTU <50 a -60 min:     {(df['NTU_60min_before'] < 50).sum()} / {len(df)}")
print()
if len(lead50) > 0:
    print(f"  Lead time hasta zona degradada (>50 NTU):  media={lead50.mean():.0f} min  "
          f"mediana={lead50.median():.0f} min")
if len(lead80) > 0:
    print(f"  Lead time hasta zona de alerta (>80 NTU):  media={lead80.mean():.0f} min  "
          f"mediana={lead80.median():.0f} min")
print()

# ── 4. Señal upstream pre-crisis ──────────────────────────────────────────────
if "pH_delta_vs_baseline" in df.columns:
    print("─" * 65)
    print("  SEÑAL UPSTREAM PRE-CRISIS")
    print("─" * 65)
    print(f"  {'Ep':>3}  {'Régimen':<8}  {'pH pre-6h':>10}  {'pH baseline':>12}  "
          f"{'ΔpH':>8}  {'BedLv pre-6h':>13}  {'Floc pre-6h':>12}")
    print("  " + "-"*63)
    for _, r in df.iterrows():
        ph_pre = f"{r['pH_mean_pre6h']:.2f}" if "pH_mean_pre6h" in r and not np.isnan(r["pH_mean_pre6h"]) else "N/A"
        ph_bas = f"{r['pH_mean_baseline']:.2f}" if "pH_mean_baseline" in r and not np.isnan(r["pH_mean_baseline"]) else "N/A"
        dph    = f"{r['pH_delta_vs_baseline']:+.2f}" if "pH_delta_vs_baseline" in r and not np.isnan(r["pH_delta_vs_baseline"]) else "N/A"
        bed    = f"{r['bed_mean_pre6h']:.2f}" if "bed_mean_pre6h" in r else "N/A"
        floc   = f"{r['floc_mean_pre6h']:.1f}" if "floc_mean_pre6h" in r else "N/A"
        print(f"  {r['episode']:>3}  {r['regime']:<8}  {ph_pre:>10}  {ph_bas:>12}  "
              f"{dph:>8}  {bed:>13}  {floc:>12}")
    print()
    clay_mask = df["regime"] == "CLAY"
    uf_mask   = df["regime"] == "UF"
    if clay_mask.any():
        print(f"  CLAY — ΔpH medio pre-crisis: {df.loc[clay_mask, 'pH_delta_vs_baseline'].mean():+.2f}")
    if uf_mask.any():
        print(f"  UF   — ΔpH medio pre-crisis: {df.loc[uf_mask,   'pH_delta_vs_baseline'].mean():+.2f}")
    print()

# ── 5. ¿Cuándo dispararía un "trend-follower" de NTU? ────────────────────────
print("─" * 65)
print("  SIMULACIÓN: ALARMA POR UMBRAL EN NTU_CLEAN (trend-follower)")
print("─" * 65)
print("  Umbral simulado: NTU_clean > 70 NTU (zona pre-crisis)")
print()
ALARM_THRESH = 70
tf_leads = []
for ep_idx, (t0, t1) in enumerate(episodes):
    pre_start = max(0, t0 - LOOK_BACK)
    pre_ntu = ts["Overflow_Turb_NTU_clean"].iloc[pre_start:t0].values
    crossings = np.where(pre_ntu >= ALARM_THRESH)[0]
    if len(crossings) > 0:
        first = crossings[0]
        lead_pts = len(pre_ntu) - first
        lead_min = lead_pts * FREQ_MIN
    else:
        lead_min = np.nan  # nunca cruzó antes → lead > 6h (señal muy limpia)
    tf_leads.append(lead_min)
    regime = ts["Regime"].iloc[t0]
    lead_str = f"{lead_min:.0f} min" if not np.isnan(lead_min) else ">6h (señal limpia)"
    print(f"  Ep {ep_idx+1:>2} ({regime:<5}): alarma @NTU>70 con {lead_str} de anticipación real")

tf_arr = np.array([x for x in tf_leads if not np.isnan(x)])
print()
if len(tf_arr) > 0:
    print(f"  Trend-follower (NTU>70): lead time real  media={tf_arr.mean():.0f} min  "
          f"mediana={np.median(tf_arr):.0f} min  min={tf_arr.min():.0f} min")
    print()
    print("  INTERPRETACIÓN CLAVE:")
    if tf_arr.mean() <= 15:
        print("  ⚠  Lead time < 15 min — el modelo trend-follower NO da ventana operativa útil.")
        print("     Un operador necesita ~15-30 min para reaccionar (ajustar Floc, abrir dilución).")
    elif tf_arr.mean() <= 30:
        print("  ~  Lead time 15-30 min — ventana marginal; depende de qué tan rápido reacciona el operador.")
    else:
        print("  ✓  Lead time > 30 min — el trend-follower ya da ventana razonable.")
        print("     Pero ojo: esto es con NTU_clean; en la práctica NTU medido tiene ruido adicional.")
print()

# ── 6. Guardar resultados ─────────────────────────────────────────────────────
out_path = DATA / "lead_time_analysis.csv"
df.to_csv(out_path, index=False)
print(f"  Resultados guardados en: {out_path.name}")
print("=" * 65)
