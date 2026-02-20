"""
Patch notebooks/02_feature_engineering.ipynb:
- Elimina ActionScore_turb, ActionScore_torque, Feedwell_Solids_pct de PRODUCTION
- Actualiza filtro FEATURES_PROD
- Corrige PATH a ../data/processed/
"""
import json

NB = "notebooks/02_feature_engineering.ipynb"

with open(NB, "r", encoding="utf-8") as f:
    nb = json.load(f)


def set_code(nb, idx, source):
    nb["cells"][idx]["source"] = [source]
    nb["cells"][idx]["outputs"] = []
    nb["cells"][idx]["execution_count"] = None
    nb["cells"][idx]["cell_type"] = "code"


# ── Cell 1: fix PATH ─────────────────────────────────────────────────────────
src1 = "".join(nb["cells"][1]["source"])
src1 = src1.replace(
    "r'data/processed/thickener_timeseries_deadband0p27_sp4.parquet'",
    "r'../data/processed/thickener_timeseries_deadband0p27_sp4.parquet'"
)
nb["cells"][1]["source"] = [src1]
nb["cells"][1]["outputs"] = []
nb["cells"][1]["execution_count"] = None

# ── Cell 3: PRODUCTION limpiado — quitar ActionScore_* y Feedwell_Solids_pct ─
set_code(nb, 3, """\
# Columnas que son labels/targets (no usar como features)
LABELS = ['event_now', 'target_event_30m', 'event_type', 'event_type_raw']

# Columnas de metadatos/constantes (no informativas como features)
META = ['spec_limit_NTU', 'event_limit_NTU', 'Regime', 'ControlMode',
        'OperatorAction', 'RecommendedAction', 'ExpectedTradeoff']

# ── Features de proceso — disponibles en producción (sensores e instrumentos reales) ──
PRODUCTION = [
    'Qf_m3h',            # Caudal feed total medido (medidor de flujo)
    'Qf_pulp_m3h',       # Flujo pulpa sin dilución
    'Qf_dilution_m3h',   # Flujo dilución (válvula DCS)
    'Qf_total_m3h',      # Suma total
    'Solids_f_pct',      # % sólidos feed (densímetro/viscosímetro)
    'FeedDilution_On',   # Dilución activa (señal binaria DCS)
    'FeedDilution_factor',
    'Qu_m3h',            # Caudal underflow (medidor de flujo)
    'Qu_sp_delta_m3h',   # Delta setpoint underflow (acción operador)
    'BedLevel_m',        # Nivel de lecho (sensor ultrasónico / presión)
    'RakeTorque_kNm',    # Torque rastrillo (corriente motor)
    'RakeTorque_pct',
    'Floc_gpt',          # Dosis floculante (rotámetro)
    'Solids_u_pct',      # % sólidos underflow (densímetro)
    'Overflow_Turb_NTU', # Turbidez medida (turbidímetro — con fallas inyectadas)
    'WaterRecovery_proxy',  # Derivable de Qu + densidades → incluible
]

# ── Variables LATENTES — solo disponibles en simulación, NO en planta ────────
SIMULATION_LATENT = [
    'Clay_pct', 'Clay_idx',      # contenido arcilla (requiere lab/PSA)
    'PSD_fines_idx',             # distribución granulométrica (analizador PSA)
    'UF_capacity_factor',        # parámetro interno del simulador
    'Qu_base_m3h',               # variable interna del simulador
    'UF_YieldStress_Pa',         # reología (no medida en línea)
    'Bogging_factor',            # parámetro interno del simulador
    'Overflow_Turb_NTU_clean',   # ground truth — NUNCA usar como feature
]

# ── Excluidas explícitamente (simulación, no presentes en DCS real) ──────────
EXCLUDED = [
    'Feedwell_Solids_pct',  # estado interno del feedwell, no instrumentado
    'ActionScore_turb',     # scoring del simulador prescriptivo
    'ActionScore_torque',   # scoring del simulador prescriptivo
]

print('--- FEATURES BASE ---')
print(f'Producción (reales):      {len(PRODUCTION)}')
print(f'Latentes simulación:      {len(SIMULATION_LATENT)}')
print(f'Excluidas explícitamente: {len(EXCLUDED)}')
print(f'Labels/targets:           {len(LABELS)}')
print(f'\\n⚠  Overflow_Turb_NTU_clean: NUNCA usar como feature (es equivalente al label)')
""")

# ── Cell 20: BASE_FEAT_COLS — excluir EXCLUDED ───────────────────────────────
set_code(nb, 20, """\
BASE_FEAT_COLS = (
    PRODUCTION
    + [c for c in SIMULATION_LATENT if c != 'Overflow_Turb_NTU_clean']
)

base_df = df[BASE_FEAT_COLS].copy()
feat = pd.concat([feat, base_df], axis=1)

# Adjuntamos targets al dataframe de features (no son features, solo para análisis)
feat['target_event_30m'] = df['target_event_30m']
feat['event_type']       = df['event_type']
feat['event_now']        = df['event_now']

print(f'Dimensiones antes de limpieza: {feat.shape}')
""")

# ── Cell 32: FEATURES_PROD — añadir exclusiones explícitas ───────────────────
set_code(nb, 32, """\
# ---- Feature set completo (todos los grupos) ----
FEATURES_ALL = feature_cols

# ---- Feature set de producción (sin variables latentes ni excluidas) ----
LATENT_PREFIXES = (
    'Clay_pct', 'Clay_idx', 'PSD_fines_idx',
    'UF_capacity_factor', 'UF_YieldStress_Pa',
    'Bogging_factor', 'Qu_base_m3h',
)

# Excluidas explícitamente (simulación, no disponibles en DCS/planta)
EXCLUDED_BASE = {
    'Feedwell_Solids_pct',
    'ActionScore_turb',
    'ActionScore_torque',
    'clay_high',
    'uf_degraded',
    'clay_x_psd',
    'ys_x_bed',
    'uf_stress',
}

FEATURES_PROD = [
    c for c in FEATURES_ALL
    if not any(c.startswith(p) or c == p for p in LATENT_PREFIXES)
    and not any(c.startswith(e) or c == e for e in EXCLUDED_BASE)
]

# ---- Top 30 por MI (para modelos ligeros / interpretabilidad) ----
FEATURES_TOP30 = mi_series.head(30).index.tolist()

# ---- Top 30 PROD: top MI restringido a FEATURES_PROD ----
FEATURES_TOP30_PROD = [f for f in mi_series.index if f in FEATURES_PROD][:30]

print('=== Resumen de feature sets ===')
print(f'FEATURES_ALL       : {len(FEATURES_ALL):3d} features')
print(f'FEATURES_PROD      : {len(FEATURES_PROD):3d} features (sin latentes ni excluidas)')
print(f'FEATURES_TOP30     : {len(FEATURES_TOP30):3d} features (top MI — incluye latentes)')
print(f'FEATURES_TOP30_PROD: {len(FEATURES_TOP30_PROD):3d} features (top MI — solo producción)')

groups = {
    'Rolling stats' : [c for c in FEATURES_ALL if '__rmean_' in c or '__rstd_' in c or '__rmax_' in c or '__rmin_' in c],
    'Lag'           : [c for c in FEATURES_ALL if '__lag_' in c],
    'Delta'         : [c for c in FEATURES_ALL if '__d1' in c or '__d6' in c or '__accel' in c],
    'Tiempo cíclico': [c for c in FEATURES_ALL if c in ('hour_sin','hour_cos','dow_sin','dow_cos','hour_of_day')],
    'Flags'         : [c for c in FEATURES_ALL if c in ('is_CLAY','is_UF','is_MANUAL','is_dilution',
                                                          'turb_above_50','turb_above_100','bed_high','torque_high')],
    'Sensor anomaly': [c for c in FEATURES_ALL if 'turb_cv' in c or 'turb_stuck' in c or 'turb_zscore' in c
                       or 'turb_spike' in c or 'turb_dev' in c or 'turb_drift' in c],
    'Interacciones' : [c for c in FEATURES_ALL if c in ('turb_x_torque','solids_flux_ratio')],
    'Base variables': BASE_FEAT_COLS,
}
print('\\nFeatures por grupo (en FEATURES_ALL):')
for g, cols_g in groups.items():
    n_in = len([c for c in cols_g if c in FEATURES_ALL])
    n_prod = len([c for c in cols_g if c in FEATURES_PROD])
    print(f'  {g:<20s}: {n_in:3d} total | {n_prod:3d} en PROD')
""")

# ── Cell 34: guardar — añadir FEATURES_TOP30_PROD al catálogo ────────────────
set_code(nb, 34, """\
import json
from pathlib import Path

out_dir = Path('../data/processed')

# --- Guardar dataset con features engineered + targets ---
TARGET_COLS = ['target_event_30m', 'event_type', 'event_now']
save_cols = FEATURES_ALL + TARGET_COLS
feat_out = feat[save_cols].reset_index()  # timestamp de vuelta como columna
feat_path = out_dir / 'thickener_features.parquet'
feat_out.to_parquet(feat_path, index=False)
print(f'Guardado: {feat_path}  ({feat_out.shape[0]:,} filas × {feat_out.shape[1]} cols)')

# --- Guardar catálogos de feature sets como JSON ---
catalogs = {
    'FEATURES_ALL':        FEATURES_ALL,
    'FEATURES_PROD':       FEATURES_PROD,
    'FEATURES_TOP30':      FEATURES_TOP30,
    'FEATURES_TOP30_PROD': FEATURES_TOP30_PROD,
    'TARGETS':             TARGET_COLS,
    'EXCLUDED':            sorted(EXCLUDED_BASE),
}
catalog_path = out_dir / 'feature_catalogs.json'
with open(catalog_path, 'w') as f:
    json.dump(catalogs, f, indent=2)
print(f'Guardado: {catalog_path}')

# --- Resumen final ---
ev = feat[feat['event_now'] == 1]
clay = ev[ev['event_type'] == 'CLAY']
uf   = ev[ev['event_type'] == 'UF']
print(f'\\n=== FEATURE SET FINAL ===')
print(f'Filas             : {feat_out.shape[0]:,}')
print(f'FEATURES_ALL      : {len(FEATURES_ALL)}')
print(f'FEATURES_PROD     : {len(FEATURES_PROD)}  ← usar en modelado')
print(f'FEATURES_TOP30_PROD: {len(FEATURES_TOP30_PROD)}  ← usar para modelos ligeros')
print(f'Balance target_event_30m: {feat["target_event_30m"].mean():.2%} positivos')
print(f'Balance event_type (eventos): CLAY={len(clay):,} | UF={len(uf):,}')
""")

with open(NB, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Notebook 02 actualizado.")
