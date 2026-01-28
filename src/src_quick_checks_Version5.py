"""
Quick sanity checks for the synthetic dataset.
- validates latest thickener_timeseries_deadband*_sp*.parquet if present
- reports BOTH clean and measured turbidity stats
- reports points above event_limit_NTU (warning) and spec_limit_NTU (spec)

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
    spec_limit = float(df["spec_limit_NTU"].iloc[0]) if "spec_limit_NTU" in df.columns else 80.0
    event_limit = float(df["event_limit_NTU"].iloc[0]) if "event_limit_NTU" in df.columns else 70.0

    print(f"\n🎯 1. PREVALENCIA DE EVENTOS (label sobre CLEAN @ {event_limit:.0f} NTU): {event_rate:.2%}")
    print(f"🎮 2. FRACCIÓN MODO MANUAL: {manual_rate:.2%}")

    clean_col = "Overflow_Turb_NTU_clean"
    meas_col = "Overflow_Turb_NTU"

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

    print(f"\n✅ 7. RESUMEN (usando CLEAN para rangos esperados):")
    if clean_col in df.columns:
        p95_clean = float(np.percentile(df[clean_col].dropna(), 95))
        p99_clean = float(np.percentile(df[clean_col].dropna(), 99))
        print("   • Eventos:       4-6% ✓" if 0.04 <= event_rate <= 0.06 else f"   • Eventos:       {event_rate:.1%} (esperado 4-6%)")
        print("   • Modo MANUAL:  15-30% ✓" if 0.15 <= manual_rate <= 0.30 else f"   • Modo MANUAL:  {manual_rate:.1%} (esperado 15-30%)")
        print("   • P95 CLEAN:     70-95 NTU ✓" if 70 <= p95_clean <= 95 else f"   • P95 CLEAN:     {p95_clean:.1f} NTU (esperado 70-95)")
        print("   • P99 CLEAN:     120-180 NTU ✓" if 120 <= p99_clean <= 180 else f"   • P99 CLEAN:     {p99_clean:.1f} NTU (esperado 120-180)")

    print("\n" + "=" * 60)
    print("✅ Validación completada")
    print("=" * 60)


if __name__ == "__main__":
    main()