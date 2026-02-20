"""
Patch notebooks/01_eda.ipynb to work with the post-FLOC dataset (39 cols).
Removes references to: FlocActivity_factor, FlocEffective_gpt,
FlocPrepFail_On, Floc_sp_delta_gpt.
"""
import json

with open("notebooks/01_eda.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)


def set_code(nb, idx, source):
    nb["cells"][idx]["source"] = [source]
    nb["cells"][idx]["outputs"] = []
    nb["cells"][idx]["execution_count"] = None
    nb["cells"][idx]["cell_type"] = "code"


def set_md(nb, idx, source):
    nb["cells"][idx]["source"] = [source]
    nb["cells"][idx]["cell_type"] = "markdown"
    if "outputs" in nb["cells"][idx]:
        del nb["cells"][idx]["outputs"]
    if "execution_count" in nb["cells"][idx]:
        del nb["cells"][idx]["execution_count"]


# ── Cell 1: describe — quitar cols FLOC ──────────────────────────────────────
set_code(nb, 1, """\
# Tipos y nulos
na = df.isna().mean().sort_values(ascending=False)
print("Top NA rates:\\n", na.head(15))

# Rangos de variables clave (post-FLOC removal)
cols = [
    "Overflow_Turb_NTU_clean", "Overflow_Turb_NTU",
    "event_now", "target_event_30m", "event_type",
    "Clay_idx", "PSD_fines_idx", "UF_capacity_factor",
    "Qu_m3h", "BedLevel_m", "UF_YieldStress_Pa",
    "RakeTorque_kNm", "RakeTorque_pct",
    "Floc_gpt", "ControlMode"
]
print(df[cols].describe(include="all").T)

# Rango temporal
print(df["timestamp"].min(), df["timestamp"].max())
""")

# ── Cell 3: FEATURES_REALISTIC — quitar Floc_sp_delta_gpt, clasificar ───────
set_code(nb, 3, """\
# Variables disponibles en un espesador real instrumentado
FEATURES_REALISTIC = [
    # Alimentación
    "Qf_total_m3h",       # medidor de flujo
    "Qf_pulp_m3h",        # flujo pulpa (sin dilución)
    "Qf_dilution_m3h",    # flujo dilución
    "Solids_f_pct",       # % sólidos feed (densímetro)
    # Underflow
    "Qu_m3h",             # medidor de flujo underflow
    "Solids_u_pct",       # % sólidos underflow (densímetro)
    # Setpoints y acciones del operador
    "Qu_sp_delta_m3h",    # delta setpoint underflow
    "FeedDilution_On",    # dilución activa (señal DCS)
    # Física observable (sensores de campo)
    "BedLevel_m",         # sensor ultrasónico / presión
    "RakeTorque_kNm",     # corriente motor rastrillo
    "RakeTorque_pct",
    "Floc_gpt",           # dosis floculante (rotámetro)
    # Control
    "ControlMode",
    # Turbidez medida (con fallas de instrumento)
    "Overflow_Turb_NTU",
]

# Variables LATENTES — solo en simulación, NO medibles en planta real
LATENT_VARS = [
    "Clay_pct", "Clay_idx",   # contenido arcilla (requiere lab/PSA)
    "PSD_fines_idx",           # distribución granulométrica (requiere analizador)
    "UF_capacity_factor",      # parámetro de simulación
    "UF_YieldStress_Pa",       # reología (no medida en línea)
    "Bogging_factor",          # parámetro de simulación
    "Qu_base_m3h",             # variable interna del simulador
    "Overflow_Turb_NTU_clean", # ground truth — NUNCA usar como feature
]

print(f"Features realistas (producción): {len(FEATURES_REALISTIC)}")
print(f"Variables latentes (solo simulación): {len(LATENT_VARS)}")
""")

# ── Cell 8: prevalencias — quitar FlocPrepFail_On ───────────────────────────
set_code(nb, 8, """\
rates = {
    "event_now_rate":        df["event_now"].mean(),
    "target_event_30m_rate": df["target_event_30m"].mean(),
    "manual_rate":           (df["ControlMode"] == "MANUAL").mean(),
    "floc_mean_gpt":         df["Floc_gpt"].mean(),
    "floc_std_gpt":          df["Floc_gpt"].std(),
}
for k, v in rates.items():
    print(f"{k}: {v:.4f}")
""")

# ── Cell 11: título diagnosis — quitar FLOC ──────────────────────────────────
set_md(nb, 11, "## Diagnosis: separabilidad de CLAY vs UF (solo durante evento)\n")

# ── Cell 15: pairplot — quitar FlocEffective_gpt ─────────────────────────────
set_code(nb, 15, """\
ev = df[df["event_now"] == 1].copy()
evs = ev.sample(min(2500, len(ev)), random_state=42)

# Variables con firma diagnóstica (latentes — solo disponibles en simulación)
vars_ = ["Clay_idx", "PSD_fines_idx", "UF_capacity_factor",
         "Qu_m3h", "BedLevel_m", "UF_YieldStress_Pa"]
sns.pairplot(evs, vars=vars_, hue="event_type", corner=True,
             plot_kws=dict(s=10, alpha=0.4))
plt.suptitle("Pairplot diagnóstico: CLAY vs UF (variables latentes del simulador)", y=1.01)
plt.show()
""")

# ── Cell 16: observaciones pairplot ──────────────────────────────────────────
set_md(nb, 16, """\
## Firmas diagnósticas CLAY vs UF

**CLAY**: valores altos y variables en `Clay_idx` y `PSD_fines_idx` (>0.6–0.8);
mayor `UF_YieldStress_Pa` y `RakeTorque_pct` con alta dispersión.

**UF**: `Clay_idx` y `PSD_fines_idx` bajos (<0.5);
diferenciador maestro = caída de `UF_capacity_factor` (única variable que distingue UF).

> ⚠ Todas las variables del pairplot son **latentes**.
> En producción real, el diagnóstico deberá basarse en firmas indirectas:
> evolución temporal de torque, nivel de lecho y caudal underflow.
""")

# ── Cell 18: boxplots diagnóstico — quitar FlocEffective_gpt ─────────────────
set_code(nb, 18, """\
ev = df[df["event_now"] == 1].copy()

features_latent = ["Clay_idx", "UF_capacity_factor", "PSD_fines_idx", "UF_YieldStress_Pa"]
features_real   = ["BedLevel_m", "RakeTorque_pct", "Qu_m3h", "Floc_gpt"]
features = features_latent + features_real

fig, axes = plt.subplots(2, 4, figsize=(20, 8))
axes = axes.flatten()

for ax, f in zip(axes, features):
    sns.boxplot(ev, x="event_type", y=f, ax=ax)
    label = " [LAT]" if f in features_latent else " [REAL]"
    ax.set_title(f + label)

plt.suptitle(
    "Distribución por tipo de evento — [LAT]=latente (solo simulación), [REAL]=medible en planta",
    y=1.01
)
plt.tight_layout()
plt.show()
""")

# ── Cell 19: observaciones boxplots ──────────────────────────────────────────
set_md(nb, 19, """\
## Resumen de firmas por tipo de evento

| Variable | CLAY | UF | Medible en planta |
|---|---|---|---|
| `Clay_idx` [LAT] | Alto (>0.6), muy variable | Bajo (<0.4) | ❌ Requiere lab/PSA |
| `PSD_fines_idx` [LAT] | Alto y estable | Bajo (<0.4) | ❌ Requiere analizador |
| `UF_capacity_factor` [LAT] | ~1.0 (normal) | Cae (<0.9) — **firma maestra UF** | ❌ Simulación |
| `UF_YieldStress_Pa` [LAT] | Alto, muy disperso | Moderado | ❌ Reología |
| `BedLevel_m` [REAL] | Alto (>3 m) | Moderado | ✅ Sensor campo |
| `RakeTorque_pct` [REAL] | Muy alto, disperso | Moderado | ✅ Motor rastrillo |
| `Qu_m3h` [REAL] | Variable | Bajo (UF bajo → falla) | ✅ Medidor flujo |
| `Floc_gpt` [REAL] | Normal a alto | Normal | ✅ Rotámetro |
""")

# ── Cell 21: KDE early warning — quitar FlocEffective_gpt ───────────────────
set_code(nb, 21, """\
cols = ["Overflow_Turb_NTU_clean", "Clay_idx", "PSD_fines_idx",
        "BedLevel_m", "UF_YieldStress_Pa",
        "RakeTorque_pct", "Qu_m3h", "Floc_gpt", "Solids_u_pct"]

sample = df.sample(8000, random_state=1).copy()
sample["target_event_30m"] = sample["target_event_30m"].astype(int)

fig, axes = plt.subplots(3, 3, figsize=(18, 14))
axes = axes.flatten()

for ax, c in zip(axes, cols):
    sns.kdeplot(sample, x=c, hue="target_event_30m", common_norm=False, ax=ax)
    ax.set_title(c)

plt.suptitle(
    "Early warning: distribuciones en t vs target_event_30m\\n(0=normal, 1=evento en 30 min)",
    y=1.01
)
plt.tight_layout()
plt.show()
""")

# ── Cell 23: delta_over_IQR — quitar FlocEffective_gpt, añadir vars reales ──
set_code(nb, 23, """\
features = [
    # Variables reales (producción)
    "Overflow_Turb_NTU",
    "BedLevel_m",
    "RakeTorque_pct",
    "Qu_m3h",
    "Floc_gpt",
    "Solids_u_pct",
    "Solids_f_pct",
    # Variables latentes (solo simulación — referencia)
    "Overflow_Turb_NTU_clean",
    "Clay_idx",
    "PSD_fines_idx",
    "UF_capacity_factor",
    "UF_YieldStress_Pa",
]

REAL_SET = {
    "Overflow_Turb_NTU", "BedLevel_m", "RakeTorque_pct",
    "Qu_m3h", "Floc_gpt", "Solids_u_pct", "Solids_f_pct"
}

tmp = df.dropna(subset=["target_event_30m"]).copy()
g0 = tmp[tmp["target_event_30m"] == 0]
g1 = tmp[tmp["target_event_30m"] == 1]

rows = []
for f in features:
    m0  = float(g0[f].median())
    m1  = float(g1[f].median())
    iqr = float(tmp[f].quantile(0.75) - tmp[f].quantile(0.25)) + 1e-9
    rows.append({
        "feature":        f,
        "median_target0": m0,
        "median_target1": m1,
        "delta":          m1 - m0,
        "IQR_all":        iqr,
        "delta_over_IQR": (m1 - m0) / iqr,
        "disponible":     "REAL" if f in REAL_SET else "LATENTE",
    })

eff = (pd.DataFrame(rows)
         .sort_values("delta_over_IQR", ascending=False)
         .reset_index(drop=True))
print(eff.to_string(index=False))
""")

# ── Cell 24: barplot delta_over_IQR — colorear por disponibilidad ─────────────
set_code(nb, 24, """\
import matplotlib.patches as mpatches

top = eff.copy()
colors = ["steelblue" if d == "REAL" else "salmon" for d in top["disponible"]]

plt.figure(figsize=(10, 7))
plt.barh(top["feature"], top["delta_over_IQR"], color=colors)
plt.title(
    "Early warning: separación de features (delta mediana / IQR)\\n"
    "target_event_30m: 1 vs 0"
)
plt.xlabel("delta_over_IQR (mayor = mejor separación)")
legend = [
    mpatches.Patch(color="steelblue", label="REAL — medible en planta"),
    mpatches.Patch(color="salmon",    label="LATENTE — solo simulación"),
]
plt.legend(handles=legend, loc="lower right")
plt.tight_layout()
plt.show()

print("\\n=== Variables REALES con mayor separación ===")
real_eff = top[top["disponible"] == "REAL"][["feature", "delta_over_IQR"]]
print(real_eff.to_string(index=False))
""")

# ── Cell 31: sección floculante — nuevo título ────────────────────────────────
set_md(nb, 31, "## Floculante: dosis y relación con eventos\n")

# ── Cell 32: quitar FlocPrepFail_On, nuevo análisis de dosis ─────────────────
set_code(nb, 32, """\
tmp = df[df["event_now"] == 1].copy()

# Dosis de floculante durante eventos por tipo
plt.figure(figsize=(10, 4))
sns.boxplot(tmp, x="event_type", y="Floc_gpt")
plt.title("Dosis de floculante (gpt) por tipo de evento (event_now==1)")
plt.tight_layout()
plt.show()

# Relación dosis floculante vs turbidez
fig, ax = plt.subplots(1, 2, figsize=(14, 4))
sns.kdeplot(df, x="Floc_gpt", hue="event_now", common_norm=False, ax=ax[0])
ax[0].set_title("Dosis floculante: normal vs evento")

sample_plot = df.sample(5000, random_state=42)
sc = ax[1].scatter(sample_plot["Floc_gpt"], sample_plot["Overflow_Turb_NTU_clean"],
                   c=sample_plot["event_now"], cmap="RdYlGn_r", alpha=0.3, s=5)
ax[1].set_xlabel("Floc_gpt")
ax[1].set_ylabel("Turbidez clean (NTU)")
ax[1].set_title("Floculante vs turbidez real")
plt.colorbar(sc, ax=ax[1], label="event_now")
plt.tight_layout()
plt.show()
""")

with open("notebooks/01_eda.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Notebook actualizado correctamente.")
