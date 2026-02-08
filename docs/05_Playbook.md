# Operational Playbook (Synthetic) — Thickener Water Recovery Sentinel (TWS)

This playbook translates detected conditions into **operator-oriented actions** with explicit trade-offs across the 4 efficiency dimensions:

1) **Water quantity recovered**  
2) **Water quality recovered** (overflow clarity/turbidity)  
3) **Underflow density** (% solids)  
4) **Underflow rheology** (yield stress / pumpability / torque risk)

> Note: This is a simplified, synthetic playbook for portfolio/demo purposes. Real plants require site calibration and safety/engineering review.

---

## Shared definitions

### Clarification bands (based on CLEAN truth)
- **Green:** `Overflow_Turb_NTU_clean < 50`
- **Degraded:** `50–100`
- **Critical:** `>100` (event risk, especially if sustained)
- **Spec (reference):** `>200`

### Mechanical / rheology risk bands (proxy)
- **Good rheology:** `UF_YieldStress_Pa < 10 Pa`
- **Alert:** `10–20 Pa`
- **Limit:** `20–30 Pa`
- **High risk:** `>30 Pa`

Torque is expected to correlate with yield stress more strongly than with underflow density (Cp).

---

## Mode 1 — CLAY-like (fines/clay driven degradation)

### Typical signature
- Rising `Overflow_Turb_NTU_clean` into degraded/critical
- `PSD_fines_idx` elevated (latent), `Clay_pct` elevated (latent)
- `UF_YieldStress_Pa` rising → torque may increase even if Cp is not extreme
- Floc demand rises; dilution can help mixing and floc growth

### Primary objective
Recover clarity early while preventing rheology/torque escalation.

### Recommended actions (ordered)
1) **Enable / increase feedwell dilution** (`FeedDilution_On`)
   - **Pros:** improves mixing, can reduce turbidity and stabilize flocculation.
   - **Cons:** increases total feed flow; may impact residence time and downstream water handling.

2) **Optimize flocculant dose (`Floc_gpt`) within practical band**
   - Typical operational band: **~10–20 g/t** (site-dependent)
   - **Pros:** improves settling and clarity.
   - **Cons:** beyond a “max-effect” region, improvement saturates while rheology/torque may worsen.

3) **Watch rheology / torque**
   - If `UF_YieldStress_Pa` approaches 20–30 Pa (or torque trends up), prioritize actions that reduce rheology risk over chasing density.

### What NOT to do (common failure modes)
- Keep increasing floc indefinitely: may stop improving clarity and still increase torque risk.
- Ignore torque/yield stress while focusing only on turbidity.

---

## Mode 2 — UF restriction-like (underflow limitation)

### Typical signature
- `UF_capacity_factor` decreases (latent driver)
- `Qu_m3h` decreases relative to feed
- `BedLevel_m` rises
- Turbidity may degrade due to process imbalance
- Underflow density may drift lower (more trapped water)

### Primary objective
Restore mass balance and avoid mechanical overload.

### Recommended actions (ordered)
1) **Increase UF discharge capacity**
   - Equivalent to: open valve / increase pump speed / reduce restriction (represented by operator action `INCREASE_UF`)
   - **Pros:** reduces bed accumulation; stabilizes operation.
   - **Cons:** may reduce underflow density (more water out), impacts water recovery and downstream pumping.

2) **Stabilize bed level**
   - If bed keeps rising, prioritize UF recovery over clarity optimization.

3) **Only then tune floc**
   - Floc changes may help, but UF restriction is the primary bottleneck.

### What NOT to do
- Overcorrect with floc when UF is restricted: can worsen rheology without fixing the constraint.

---

## Mode 3 — FLOC underperformance (dosing/preparation issues)

### Typical signature
- `Floc_gpt` below implied need (or reduced effectiveness)
- Turbidity degrades while UF capacity/bed is not the main driver
- Torque may stay moderate initially

### Primary objective
Restore flocculation effectiveness quickly.

### Recommended actions (ordered)
1) **Increase/restore effective floc**
   - Increase `Floc_gpt` toward typical target band.
   - **Pros:** fast turbidity recovery.
   - **Cons:** if already near max-effect region, extra floc may increase torque/YS.

2) **Verify “preparation quality” (conceptual)**
   - In real plants, poor preparation destroys polymer chains; dose alone is misleading.

3) **Monitor torque / yield stress as second-order constraint**
   - If torque/YS rises, stop increasing floc and reassess.

---

## Sensor-health overlays (operator trust)

### Turbidity sensor suspicion rules (examples)
- If measured turbidity is nearly constant for >2 hours (flatline), treat as **low confidence**.
- If torque and bed trends indicate a disturbance but turbidity does not respond, suspect fouling/stuck sensor.

Recommended action:
- Flag: “Turbidity sensor likely dirty/stuck. Use virtual estimate / rely on clean proxy features.”

---

## Case study templates (for portfolio)
For each case study, capture:
- Timeline snapshot (7–24h window)
- Current band (green/degraded/critical)
- Mode classification (CLAY/UF/FLOC)
- Confidence notes (e.g., turbidity sensor low confidence)
- Recommended actions + expected trade-offs across 4 KPIs
