"""
Quick sanity checks for the synthetic dataset.
- validates latest thickener_timeseries_deadband*_sp*.parquet if present
- reports BOTH clean and measured turbidity stats
- reports points above event_limit_NTU (warning) and spec_limit_NTU (spec)
- reports "zona verde / alerta / crítico" share based on metallurgist ranges

Run:
  python src/quick_checks.py
"""

from pathlib import Path
import pandas as pd
import numpy as np


def pick_latest_parquet(processed_dir: Path) -> Path:
    candidates = sorted(
        processed_dir.glob("thickener_timeseries_deadband*_sp*.parquet"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if candidates:
        return candidates[0]
    return processed_dir / "thickener_timeseries.parquet"


def turb_stats(series: pd.Series) -> dict:
    s = series.dropna()
    return {
        "min": float(s.min()),
        "median": float(s.median()),
        "p95": float(np.percentile(s, 95)),
        "p99": float(np.percentile(s, 99)),
        "max": float(s.max()),
    }


def in_range(s: pd.Series, lo: float, hi: float) -> pd.Series:
    return (s >= lo) & (s <= hi)


def main():
    print("=" * 60)
    print("VALIDACIÓN RÁPIDA DEL DATASET - ESPESADOR")
    print("=" * 60)

    processed_dir = Path("data/processed")
    path = pick_latest_parquet(processed_dir)

    if not path.exists():
        print("❌ ERROR: No se encontró ningún parquet en data/processed")
        print("💡 Ejecuta primero: python src/simulate_fixed.py")
        return

    df = pd.read_parquet(path)
    print(f"✅ Archivo cargado: {path}")
    print(f"📊 Dimensiones: {len(df)} filas × {len(df.columns)} columnas")

    event_rate = float(df["event_now"].mean())
    manual_rate = float((df["ControlMode"] == "MANUAL").mean())

    # thresholds (prefer columns; fallback to defaults)
    spec_limit = float(df["spec_limit_NTU"].iloc[0]) if "spec_limit_NTU" in df.columns else 200.0
    event_limit = float(df["event_limit_NTU"].iloc[0]) if "event_limit_NTU" in df.columns else 100.0

    print(f"\n🎯 1. PREVALENCIA DE EVENTOS (label sobre CLEAN @ {event_limit:.0f} NTU): {event_rate:.2%}")
    print(f"🎮 2. FRACCIÓN MODO MANUAL: {manual_rate:.2%}")

    clean_col = "Overflow_Turb_NTU_clean"
    meas_col = "Overflow_Turb_NTU"

    # --- turbidity stats
    if clean_col in df.columns:
        st = turb_stats(df[clean_col])
        print(f"\n📈 3A. TURBIEDAD CLEAN (proceso):")
        print(f"   • Mínimo:      {st['min']:.1f} NTU")
        print(f"   • Mediana:     {st['median']:.1f} NTU")
        print(f"   • P95:         {st['p95']:.1f} NTU")
        print(f"   • P99:         {st['p99']:.1f} NTU")
        print(f"   • Máximo:      {st['max']:.1f} NTU")

    st2 = turb_stats(df[meas_col])
    print(f"\n📈 3B. TURBIEDAD MEDIDA (con fallas):")
    print(f"   • Mínimo:      {st2['min']:.1f} NTU")
    print(f"   • Mediana:     {st2['median']:.1f} NTU")
    print(f"   • P95:         {st2['p95']:.1f} NTU")
    print(f"   • P99:         {st2['p99']:.1f} NTU")
    print(f"   • Máximo:      {st2['max']:.1f} NTU")

    # Point prevalence above thresholds (measured & clean)
    above_event_meas = float((df[meas_col] > event_limit).mean())
    above_spec_meas = float((df[meas_col] > spec_limit).mean())

    print(f"\n⚠️  4. PUNTOS SOBRE LÍMITE EN MEDIDA:")
    print(f"   • Sobre warning ({event_limit:.0f} NTU): {above_event_meas:.2%}")
    print(f"   • Sobre spec    ({spec_limit:.0f} NTU): {above_spec_meas:.2%}")
    print(f"   • Eventos (label, sostenidos sobre {event_limit:.0f} NTU): {event_rate:.2%}")

    if clean_col in df.columns:
        above_event_clean = float((df[clean_col] > event_limit).mean())
        above_spec_clean = float((df[clean_col] > spec_limit).mean())
        print(f"\n🧪 4B. PUNTOS SOBRE LÍMITE EN CLEAN (proceso):")
        print(f"   • Sobre warning ({event_limit:.0f} NTU): {above_event_clean:.2%}")
        print(f"   • Sobre spec    ({spec_limit:.0f} NTU): {above_spec_clean:.2%}")

    print(f"\n🏷️  5. DISTRIBUCIÓN DE TIPOS DE EVENTOS:")
    total_events = int(df["event_now"].sum())
    if total_events > 0:
        event_types = df.loc[df["event_now"] == 1, "event_type"].value_counts()
        for etype, count in event_types.items():
            print(f"   • {etype}: {int(count)} eventos ({(int(count)/total_events)*100:.1f}%)")
    else:
        print("   • No hay eventos en el dataset")

    missing_qf = float(df["Qf_m3h"].isna().mean())
    print(f"\n🔧 6. CALIDAD DE DATOS:")
    print(f"   • Valores faltantes en Qf_m3h: {missing_qf:.2%}")

    # --- NEW: operational green/alert/critical shares (metallurgist-aligned)
    # Define "green bands" (zona verde) based on metallurgist dashboard summary.
    # Evaluate on CLEAN turbidity (process truth) and on process tags (not corrupted ones).
    turb_green = in_range(df[clean_col], 20, 50) if clean_col in df.columns else pd.Series(False, index=df.index)
    uf_green = in_range(df["Solids_u_pct"], 62, 68) if "Solids_u_pct" in df.columns else pd.Series(False, index=df.index)
    bed_green = in_range(df["BedLevel_m"], 1.5, 2.5) if "BedLevel_m" in df.columns else pd.Series(False, index=df.index)
    tq_green = in_range(df["RakeTorque_pct"], 30, 50) if "RakeTorque_pct" in df.columns else pd.Series(False, index=df.index)

    green_all = turb_green & uf_green & bed_green & tq_green
    out_of_green = ~green_all

    # "critical" if any variable is in critical band
    turb_critical = (df[clean_col] > 100) if clean_col in df.columns else pd.Series(False, index=df.index)
    uf_critical = (df["Solids_u_pct"] < 58) | (df["Solids_u_pct"] > 72) if "Solids_u_pct" in df.columns else pd.Series(False, index=df.index)
    bed_critical = (df["BedLevel_m"] < 1.0) | (df["BedLevel_m"] > 3.0) if "BedLevel_m" in df.columns else pd.Series(False, index=df.index)
    tq_critical = (df["RakeTorque_pct"] > 70) if "RakeTorque_pct" in df.columns else pd.Series(False, index=df.index)

    critical_any = turb_critical | uf_critical | bed_critical | tq_critical

    # --- NEW: operational green/alert/critical shares (metallurgist-aligned)
    # Primary KPI: clarification (turbidity) using CLEAN truth.
    # Rationale: the metallurgist's "85% normal / 15% events" maps better to
    # time in green vs non-green turbidity bands than to "all tags simultaneously OK".
    if clean_col in df.columns:
        turb_clean = df[clean_col].dropna()
        turb_green = (df[clean_col] < 50)
        turb_degraded = (df[clean_col] >= 50) & (df[clean_col] <= 100)
        turb_critical = (df[clean_col] > 100)

        print(f"\n🟩 7. CLARIFICACIÓN — ZONA VERDE / DEGRADACIÓN (CLEAN, metalurgista):")
        print(f"   • Verde   (CLEAN < 50 NTU):        {float(turb_green.mean()):.2%}")
        print(f"   • Degrad. (50–100 NTU):            {float(turb_degraded.mean()):.2%}")
        print(f"   • Crítico (CLEAN > 100 NTU):       {float(turb_critical.mean()):.2%}")
        print(f"   • Sobre spec (CLEAN > {spec_limit:.0f}): {float((df[clean_col] > spec_limit).mean()):.2%}")

    # Secondary KPI: mechanical/UF health (reported independently, not ANDed)
    bed_alert = ((df["BedLevel_m"] < 1.5) | (df["BedLevel_m"] > 2.5)) if "BedLevel_m" in df.columns else pd.Series(False, index=df.index)
    tq_alert = ((df["RakeTorque_pct"] < 30) | (df["RakeTorque_pct"] > 50)) if "RakeTorque_pct" in df.columns else pd.Series(False, index=df.index)
    uf_alert = ((df["Solids_u_pct"] < 62) | (df["Solids_u_pct"] > 68)) if "Solids_u_pct" in df.columns else pd.Series(False, index=df.index)

    print(f"\n🛠️  7B. MECÁNICA/UF — % fuera de banda verde (referencial):")
    print(f"   • Bed fuera 1.5–2.5 m:             {float(bed_alert.mean()):.2%}")
    print(f"   • Torque fuera 30–50%:             {float(tq_alert.mean()):.2%}")
    print(f"   • UF density fuera 62–68%:         {float(uf_alert.mean()):.2%}")

    print(f"\n✅ 8. RESUMEN:")
    print("   • MANUAL 15–30% ✓" if 0.15 <= manual_rate <= 0.30 else f"   • MANUAL: {manual_rate:.1%} (esperado 15–30%)")

    if clean_col in df.columns:
        degraded_target_ok = 0.12 <= float(turb_degraded.mean()) <= 0.18
        print("   • Degradación (50–100) ~15% ✓" if degraded_target_ok else f"   • Degradación (50–100): {float(turb_degraded.mean()):.1%} (meta ~15%)")

    # Event rate is a separate concept: sustained crisis > event_limit for >= 20 min
    print("   • Eventos (crisis sostenida) 3–6% ✓" if 0.03 <= event_rate <= 0.06 else f"   • Eventos (crisis sostenida): {event_rate:.1%} (típico 3–6% para ML)")

    print("\n" + "=" * 60)
    print("✅ Validación completada")
    print("=" * 60)


if __name__ == "__main__":
    main()