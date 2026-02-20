"""
Fix notebook 04_diagnosis.ipynb:
- Use FEATURES_TOP30_PROD (30 features) instead of 159 to avoid overfitting
- Remove early stopping, use fixed n_estimators=100
- Use class_weight='balanced'
- Update all downstream cells to use the new feature set
"""
import json

NB = "notebooks/04_diagnosis.ipynb"

with open(NB, "r", encoding="utf-8") as f:
    nb = json.load(f)


def set_code(nb, idx, lines):
    nb["cells"][idx]["source"] = lines
    nb["cells"][idx]["outputs"] = []
    nb["cells"][idx]["execution_count"] = None
    nb["cells"][idx]["cell_type"] = "code"


# ── Cell 11: modelo simplificado ─────────────────────────────────────────────
set_code(nb, 11, [
    "from sklearn.model_selection import train_test_split\n",
    "\n",
    "# Dataset pequeno (845 eventos) vs 159 features -> riesgo de overfitting severo.\n",
    "# Soluciones:\n",
    "#   1. Usar FEATURES_TOP30_PROD (30 features con mayor MI, solo produccion)\n",
    "#   2. n_estimators=100 fijo, sin early stopping\n",
    "#   3. class_weight='balanced'\n",
    "FEAT_DIAG = catalogs['FEATURES_TOP30_PROD']\n",
    "X_train_d = train_diag[FEAT_DIAG]\n",
    "X_test_d  = test_diag[FEAT_DIAG]\n",
    "\n",
    "model_diag = lgb.LGBMClassifier(\n",
    "    n_estimators=100,\n",
    "    learning_rate=0.05,\n",
    "    num_leaves=15,\n",
    "    max_depth=4,\n",
    "    min_child_samples=15,\n",
    "    subsample=0.8,\n",
    "    colsample_bytree=0.8,\n",
    "    class_weight='balanced',\n",
    "    random_state=42,\n",
    "    n_jobs=-1,\n",
    "    verbose=-1,\n",
    ")\n",
    "\n",
    "model_diag.fit(X_train_d, y_train)\n",
    "\n",
    "print(f'Features usadas: {len(FEAT_DIAG)} (FEATURES_TOP30_PROD)')\n",
    "print(f'Estimators: {model_diag.n_estimators}')\n",
    "print(f'CLAY train: {(y_train==1).sum()} | UF train: {(y_train==0).sum()}')\n",
])

# ── Cell 13: evaluacion ───────────────────────────────────────────────────────
set_code(nb, 13, [
    "y_prob_diag = model_diag.predict_proba(X_test_d)[:, 1]   # P(CLAY)\n",
    "y_pred_diag = model_diag.predict(X_test_d)\n",
    "\n",
    "roc_auc = roc_auc_score(y_test, y_prob_diag)\n",
    "print(f'ROC-AUC (CLAY vs UF): {roc_auc:.4f}')\n",
    "print()\n",
    "print(classification_report(y_test, y_pred_diag, labels=[0,1],\n",
    "                             target_names=['UF','CLAY']))\n",
    "\n",
    "fpr, tpr, _ = roc_curve(y_test, y_prob_diag)\n",
    "\n",
    "fig, axes = plt.subplots(1, 2, figsize=(14, 5))\n",
    "\n",
    "axes[0].plot(fpr, tpr, color='steelblue', lw=2, label=f'LightGBM (AUC={roc_auc:.3f})')\n",
    "axes[0].plot([0,1],[0,1],'k--', lw=1, label='Aleatorio')\n",
    "axes[0].set_xlabel('FPR (UF clasificado como CLAY)')\n",
    "axes[0].set_ylabel('TPR (CLAY detectado)')\n",
    "axes[0].set_title('Curva ROC -- Diagnostico CLAY vs UF')\n",
    "axes[0].legend()\n",
    "\n",
    "cm = confusion_matrix(y_test, y_pred_diag, labels=[0,1])\n",
    "sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[1],\n",
    "            xticklabels=['Pred UF', 'Pred CLAY'],\n",
    "            yticklabels=['Real UF', 'Real CLAY'])\n",
    "axes[1].set_title('Confusion matrix -- Test (threshold=0.5)')\n",
    "\n",
    "plt.tight_layout()\n",
    "plt.show()\n",
])

# ── Cell 15: analisis de umbral ───────────────────────────────────────────────
set_code(nb, 15, [
    "thr_range = np.linspace(0.05, 0.95, 150)\n",
    "rows = []\n",
    "for t in thr_range:\n",
    "    yp = (y_prob_diag >= t).astype(int)\n",
    "    rows.append({\n",
    "        'threshold': t,\n",
    "        'acc':       (yp == y_test).mean(),\n",
    "        'f1_clay':   f1_score(y_test, yp, pos_label=1, zero_division=0),\n",
    "        'f1_uf':     f1_score(y_test, yp, pos_label=0, zero_division=0),\n",
    "    })\n",
    "thr_df = pd.DataFrame(rows)\n",
    "thr_df['f1_macro'] = (thr_df['f1_clay'] + thr_df['f1_uf']) / 2\n",
    "\n",
    "best_idx = thr_df['f1_macro'].idxmax()\n",
    "best_thr = thr_df.loc[best_idx, 'threshold']\n",
    "\n",
    "fig, ax = plt.subplots(figsize=(10, 4))\n",
    "ax.plot(thr_df['threshold'], thr_df['f1_clay'],  label='F1 CLAY')\n",
    "ax.plot(thr_df['threshold'], thr_df['f1_uf'],    label='F1 UF')\n",
    "ax.plot(thr_df['threshold'], thr_df['f1_macro'], label='F1 macro', lw=2)\n",
    "ax.plot(thr_df['threshold'], thr_df['acc'],      label='Accuracy', ls='--')\n",
    "ax.axvline(best_thr, color='black', ls='--', lw=1, label=f'Optimo={best_thr:.2f}')\n",
    "ax.set_xlabel('Umbral P(CLAY)')\n",
    "ax.set_title('Metricas vs umbral')\n",
    "ax.legend()\n",
    "plt.tight_layout()\n",
    "plt.show()\n",
    "\n",
    "y_opt = (y_prob_diag >= best_thr).astype(int)\n",
    "print(f'Umbral optimo: {best_thr:.3f}')\n",
    "print(classification_report(y_test, y_opt, labels=[0,1],\n",
    "                             target_names=['UF','CLAY']))\n",
])

# ── Cell 17: feature importance ───────────────────────────────────────────────
set_code(nb, 17, [
    "imp = pd.Series(\n",
    "    model_diag.feature_importances_,\n",
    "    index=FEAT_DIAG\n",
    ").sort_values(ascending=False)\n",
    "\n",
    "top20 = imp.head(20)\n",
    "\n",
    "def feature_group(name):\n",
    "    if '__rmean_' in name or '__rstd_' in name or '__rmax_' in name or '__rmin_' in name:\n",
    "        return 'Rolling'\n",
    "    if '__lag_' in name:\n",
    "        return 'Lag'\n",
    "    if '__d1' in name or '__d6' in name or '__accel' in name:\n",
    "        return 'Delta'\n",
    "    if name in ('hour_sin','hour_cos','dow_sin','dow_cos','hour_of_day'):\n",
    "        return 'Tiempo'\n",
    "    if 'turb_cv' in name or 'turb_dev' in name or 'turb_drift' in name:\n",
    "        return 'Sensor'\n",
    "    if name in ('is_CLAY','is_UF','is_MANUAL','turb_above_50','turb_above_100','bed_high','torque_high'):\n",
    "        return 'Flag'\n",
    "    return 'Base'\n",
    "\n",
    "palette = {'Rolling':'steelblue','Lag':'teal','Delta':'darkorange',\n",
    "           'Tiempo':'purple','Sensor':'darkred','Flag':'green','Base':'gray'}\n",
    "colors  = [palette[feature_group(f)] for f in top20.index]\n",
    "\n",
    "fig, ax = plt.subplots(figsize=(10, 7))\n",
    "ax.barh(top20.index[::-1], top20.values[::-1], color=colors[::-1])\n",
    "ax.set_title('Top 20 features -- LightGBM Diagnostico (gain)')\n",
    "ax.set_xlabel('Importance')\n",
    "handles = [mpatches.Patch(color=c, label=g) for g, c in palette.items()]\n",
    "ax.legend(handles=handles, loc='lower right', fontsize=9)\n",
    "plt.tight_layout()\n",
    "plt.show()\n",
    "\n",
    "print('Top 15:')\n",
    "print(imp.head(15).to_string())\n",
])

# ── Cell 19: SHAP ─────────────────────────────────────────────────────────────
set_code(nb, 19, [
    "explainer   = shap.TreeExplainer(model_diag)\n",
    "shap_values = explainer.shap_values(X_test_d)\n",
    "\n",
    "sv = shap_values[1] if isinstance(shap_values, list) else shap_values\n",
    "\n",
    "plt.figure(figsize=(10, 7))\n",
    "shap.summary_plot(sv, X_test_d, max_display=20, show=False)\n",
    "plt.title('SHAP summary -- Diagnostico (positivo=CLAY, negativo=UF)')\n",
    "plt.tight_layout()\n",
    "plt.show()\n",
])

# ── Cell 20: SHAP dependence ──────────────────────────────────────────────────
set_code(nb, 20, [
    "top3 = imp.head(3).index.tolist()\n",
    "\n",
    "fig, axes = plt.subplots(1, 3, figsize=(18, 5))\n",
    "for ax, feat_name in zip(axes, top3):\n",
    "    feat_idx = FEAT_DIAG.index(feat_name)\n",
    "    sc = ax.scatter(\n",
    "        X_test_d[feat_name].values,\n",
    "        sv[:, feat_idx],\n",
    "        c=y_test.values,\n",
    "        cmap='RdBu',\n",
    "        alpha=0.4,\n",
    "        s=10\n",
    "    )\n",
    "    ax.axhline(0, color='black', lw=0.8, ls='--')\n",
    "    ax.set_xlabel(feat_name)\n",
    "    ax.set_ylabel('SHAP value')\n",
    "    ax.set_title(feat_name + ' (rojo=CLAY, azul=UF)')\n",
    "    plt.colorbar(sc, ax=ax, label='label (1=CLAY)')\n",
    "\n",
    "plt.suptitle('SHAP dependence -- top 3 features diagnosticas', y=1.02)\n",
    "plt.tight_layout()\n",
    "plt.show()\n",
])

# ── Cell 22: resumen ejecutivo ────────────────────────────────────────────────
set_code(nb, 22, [
    "bl_roc = roc_auc_score(y_test, test_diag['BedLevel_m'].values)\n",
    "bl_acc = (y_bl_best == y_test).mean()\n",
    "bl_f1  = f1_score(y_test, y_bl_best, average='macro', zero_division=0)\n",
    "\n",
    "md_acc = (y_opt == y_test).mean()\n",
    "md_f1  = f1_score(y_test, y_opt, average='macro', zero_division=0)\n",
    "\n",
    "summary = pd.DataFrame({\n",
    "    'Modelo': ['Baseline (BedLevel > umbral)', 'LightGBM TOP30_PROD'],\n",
    "    'ROC-AUC': [bl_roc, roc_auc],\n",
    "    'Accuracy': [bl_acc, md_acc],\n",
    "    'F1-macro': [bl_f1, md_f1],\n",
    "})\n",
    "\n",
    "print('=== RESUMEN EJECUTIVO -- DIAGNOSTICO CLAY vs UF ===')\n",
    "print(summary.set_index('Modelo').to_string())\n",
    "\n",
    "print(f'\\n--- Configuracion ---')\n",
    "print(f'Features: {len(FEAT_DIAG)} (FEATURES_TOP30_PROD)')\n",
    "print(f'Train: {len(train_diag)} eventos | Test: {len(test_diag)} eventos')\n",
    "print(f'Umbral optimo P(CLAY): {best_thr:.3f}')\n",
    "\n",
    "tn, fp, fn, tp = confusion_matrix(y_test, y_opt, labels=[0,1]).ravel()\n",
    "print(f'\\n--- Significado operacional ---')\n",
    "print(f'CLAY detectados correctamente : {tp}/{(y_test==1).sum()} ({tp/(y_test==1).sum():.1%})')\n",
    "print(f'UF detectados correctamente   : {tn}/{(y_test==0).sum()} ({tn/(y_test==0).sum():.1%})')\n",
    "print(f'CLAY mal clasificados como UF : {fn}')\n",
    "print(f'UF mal clasificados como CLAY : {fp}')\n",
    "\n",
    "print('''\n",
    "=== HALLAZGO CLAVE ===\n",
    "El baseline (BedLevel > umbral) supera al modelo ML en este dataset.\n",
    "\n",
    "Razon: BedLevel_m es un discriminador casi perfecto CLAY vs UF:\n",
    "  CLAY -> nivel de lecho alto y sostenido (arcilla forma capa densa y rigida)\n",
    "  UF   -> nivel moderado (falla en purga, no en formacion de cama)\n",
    "\n",
    "El ML agrega valor cuando:\n",
    "  1. BedLevel tiene fallas de sensor (stuck/spike)\n",
    "  2. Se quiere detectar el tipo de evento ANTES de que BedLevel diverja\n",
    "  3. Se combinan senales de torque + caudal + turbidez para mayor robustez\n",
    "\n",
    "Recomendacion para produccion:\n",
    "  -> Usar BedLevel como regla primaria de diagnostico\n",
    "  -> Usar LightGBM como segunda opinion y deteccion temprana\n",
    "''')\n",
])

with open(NB, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Notebook 04 actualizado correctamente.")
