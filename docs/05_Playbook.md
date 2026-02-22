# Operational Playbook — Thickener Water Recovery Sentinel (TWS)

This playbook translates detected conditions into **operator-oriented actions** with explicit trade-offs across the 4 efficiency dimensions:

1. **Water quantity recovered**
2. **Water quality recovered** (overflow clarity / turbidity)
3. **Underflow density** (% solids)
4. **Underflow rheology** (yield stress / pumpability / torque risk)

> Note: This is a simplified, synthetic playbook for portfolio/demo purposes. Real plants require site calibration and safety/engineering review.

---

## Clarification bands (based on CLEAN truth)
- **Green:** `Overflow_Turb_NTU_clean < 50`
- **Degraded:** `50–100`
- **Critical:** `>100` (event risk, especially if sustained ≥20 min)
- **Spec (reference):** `>200`

## Mechanical / rheology risk bands (proxy)
- **Good rheology:** `UF_YieldStress_Pa < 10 Pa`
- **Alert:** `10–20 Pa`
- **Limit:** `20–30 Pa`
- **High risk:** `>30 Pa`

Torque correlates with yield stress more strongly than with underflow density (Cp).

---

## Mode 1 — CLAY-like (fines/clay driven degradation)

### Diagnosis signal
- `BedLevel_m > 1.9 m` → CLAY (primary rule, 93.1% accuracy)
- `Clay_idx` elevated (latent), `pH_feed` rising
- `Floc_effectiveness` dropping → turbidity degrades despite normal floc dose

### Typical signature
- Rising `Overflow_Turb_NTU_clean` into degraded/critical
- `UF_YieldStress_Pa` rising → torque may increase even if Cp is not extreme
- Floc demand rises; dilution can help mixing and floc growth

### Primary objective
Recover clarity early while preventing rheology/torque escalation.

### Recommended actions (ordered)
1. **Enable / increase feedwell dilution** (`FeedDilution_On`)
   - **Pros:** improves mixing, can reduce turbidity and stabilize flocculation.
   - **Cons:** increases total feed flow; may impact residence time and downstream water handling.

2. **Optimize flocculant dose (`Floc_gpt`) within practical band**
   - Typical operational band: ~10–20 g/t (site-dependent).
   - **Pros:** improves settling and clarity.
   - **Cons:** beyond a "max-effect" region, improvement saturates while rheology/torque may worsen.

3. **Watch rheology / torque**
   - If `UF_YieldStress_Pa` approaches 20–30 Pa (or torque trends up), prioritize actions that reduce rheology risk over chasing density.

### What NOT to do
- Keep increasing floc indefinitely: may stop improving clarity and still increase torque risk.
- Ignore torque/yield stress while focusing only on turbidity.

---

## Mode 2 — UF Failure-like (underflow capacity restriction)

### Diagnosis signal
- `BedLevel_m ≤ 1.9 m` + stress pattern → UF (primary rule complement)
- `Qu_m3h` decreasing relative to feed
- `BedLevel_m` rising

### Typical signature
- `UF_capacity_factor` decreases (latent driver)
- `Qu_m3h` reduces relative to feed
- Bed level tends to rise
- Turbidity may degrade due to process imbalance and residence time changes
- Underflow density may drift lower (more trapped water)

### Primary objective
Restore mass balance and avoid mechanical overload.

### Recommended actions (ordered)
1. **Increase UF discharge capacity**
   - Open valve / increase pump speed / reduce restriction (`INCREASE_UF` operator action).
   - **Pros:** reduces bed accumulation; stabilizes operation.
   - **Cons:** may reduce underflow density (more water out), impacts water recovery and downstream pumping.

2. **Stabilize bed level**
   - If bed keeps rising, prioritize UF recovery over clarity optimization.

3. **Only then tune floc**
   - Floc changes may help, but UF restriction is the primary bottleneck.

### What NOT to do
- Overcorrect with floc when UF is restricted: can worsen rheology without fixing the constraint.

---

## Notes

> **FLOC mode was removed** from the simulator and diagnosis scope (2026-02-18). It represented only ~0.2% of events in the dataset and was not learnable as a separate category. All observed crisis events are now attributed to CLAY or UF. See `bitacora/06_descarte_floc.md`.
