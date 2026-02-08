# Roadmap (Portfolio-first, Product-ready)

This roadmap avoids scope creep by keeping a strict Core layer, then adding only high-ROI realism.

## Phase 0 — Lock the simulator (done)
- [x] Clean truth turbidity + measured turbidity failures
- [x] Event labeling (sustained >100 NTU)
- [x] Operator mode + actions + dilution action
- [x] Rheology realism: `UF_YieldStress_Pa`
- [x] Torque in kNm and % derived from kNm

## Phase 1 — EDA deliverable (next)
**Definition of Done: 5 figures**
- [ ] Fig1: timeline clean vs measured + bands + events + manual shading
- [ ] Fig2: event episodes (duration vs severity)
- [ ] Fig3: torque vs yield stress; torque vs Cp comparison
- [ ] Fig4: turbidity sensor error (measured - clean)
- [ ] Fig5: efficiency trade-off view (proxy)

Acceptance criteria:
- Plots are interpretable and consistent with thickener narratives (CLAY/UF/FLOC).
- Shows why sensor health matters.

## Phase 2 — Baseline ML (time split)
- [ ] Build lag/rolling features from measured tags
- [ ] Temporal split (train early, test late)
- [ ] Metrics that matter operationally:
  - false alarms/day
  - missed events
  - lead time to sustained event
- [ ] Baseline model: logistic regression / XGBoost (keep interpretable first)

## Phase 3 — Sensor-health module (rules + score)
- [ ] Turbidity stuck/flatline detection
- [ ] Drift heuristic
- [ ] Confidence score `conf_turbidity` and demonstrate improved alerting
- [ ] (Optional) similar confidence for bed level and pH if added

## Phase 4 — Playbook + case studies (portfolio polish)
- [ ] Write `docs/PLAYBOOK.md` with actions per mode (CLAY/UF/FLOC)
- [ ] Include 2 case studies (one CLAY, one UF/FLOC):
  - timeline snapshot
  - recommended actions
  - expected trade-offs in 4 KPIs (water quantity, water quality, UF density, UF rheology)

## Phase 5 — High-ROI realism (choose 1–2)
Pick only what improves diagnosis / lead time / trust:
- [ ] `Feed_P80_um` intermittent sample-and-hold (~4h)
- [ ] `Water_Conductivity_uS_cm`
- [ ] `pH_meas` + confidence flag

## Phase 6 — Product demo (optional)
- [ ] Streamlit dashboard: current state + alert + diagnosis + confidence
- [ ] Export “event report” weekly PDF/HTML
