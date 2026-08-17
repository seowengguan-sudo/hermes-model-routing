# PENSOLAR — Solar PV Ops Intelligence SUMMARY
*Canonical store for Project-Management POC. Owner: Ops Director lens. Updated 2026-08-16.*
*KPIs tracked: (A) timeline adherence survey→approval→meter; (B) install cost/kW; (C) after-sales callback (O&M SLA+spares); (D) procurement lead time; (E) ATAP export economics & payback.*

> SCHEME ALERT (2026-08-14): Solar ATAP (Solar Accelerated Transition Action Programme) launched 1 Jan 2026 under PETRA/SEDA, replacing NEM 3.0 (residential quota closed Dec 2025). Residential rooftop programme is now ATAP — open, no quota, 10-yr export contract. Prior NEM-3.0-era intel below remains valid for commercial/NOVA/LSS layers but residential funnel must be re-based on ATAP. [S2][S3]

---

## A. PROJECT TIMELINE (KPI: survey→ATAP→meter, currently 3–5 mo)

**Canonical ATAP sequence (residential)** [S2][S3]:
1. Confirm eligibility (TNB domestic Tariff A, single-owner, no active NEM).
2. Engage SEDA-registered RPVSP (mandatory — uncertified installer cannot submit valid app).
3. Site assessment + system design (roof, shading, load profile → capacity).
4. TNB technical clearance: **CCC** (Connection Confirmation Check) for most residential; **CAS** (Connection Assessment Study) for larger systems.
5. SEDA submission via **eATAP** portal by RPVSP → SEDA reference + technical review.
6. Installation + commissioning (must be AFTER approvals; installing before approval voids standing).
7. TNB bi-directional meter install → 10-yr export contract starts.

**Measured durations (2026 field data):**
- SEDA approval: ~3–5 weeks per Trexon (200+ installs); 2–4 weeks per Homifytech. [S3][S4]
- TNB meter-replacement queue: 2–6 weeks — the longest step, area-dependent. [S3]
- **Total assessment→switch-on: 6–14 weeks** (Trexon, n=200+). [S3]
- Community anecdote: 27 days to approval letter, 39 days to SEDA completion (incl. holidays). [S11]
- → Confirms the "3–5 mo" director benchmark for residential; commercial/CAS path adds study lead.

**Fee stack inside timeline (KPI B driver):** ATAP processing RM7.50/kW [S4]; CAS (commercial) RM1,000–20,000 by capacity [S7]; ST license required >24kW single-phase / >72kW three-phase [S7]; PE/Competent-Person design endorsement required [S7].

**NEW 2026-08-16 — TNB technical assessment study structure (refines G1/G5):** The study is a PRE-APPROVAL prerequisite that must complete before SEDA approval. CCC (Connection Confirmation Check) required for RE installations >12kW up to 425kW; CAS (Connection Assessment Study) required for >72kW LV (commercial/industrial) and domestic aggregated >72kW. **≤12kW residential is exempt from CCC/CAS.** [S12][S4]
- → Residential 12–72kW adds a CCC step (days–few weeks); >72kW adds CAS (RM1k–20k + 2–4 wk). Confirms the structural split between G1 (residential flow) and G5 (>72kW commercial CAS). Penang/Perak regional queue time for CCC/CAS and the TNB meter swap is still NOT pinned (see _GAPS NG2).

**Prior-intel note (2026-08-13 runs):** CAS/TNB generic clearance 2–4 wk; NEM-era quota dynamics now superseded by ATAP open model. BESS/standby + GTFS-i 5.0 (RM1B / 2% / 60% guar to 31Dec26) referenced in prior logs — verify these still apply under ATAP-era guidelines before reuse. [prior logs]

---

## B. INSTALL COST PER kW (KPI: RM100k–RM500k currently)

**Residential (turnkey, all-in, Tier-1 panels + inverter + mount + SEDA/ATAP + warranty):** [S5]
- RM 2.80–4.50 /W average; most homes 8–12 kW pay RM19.5k–35k.
- Turnkey table: 3kW RM16.5–19.5k (≈RM5.5–6.5/W); 8kW RM26.5–30.5k (≈RM3.3–3.8/W); 20kW RM58–72k (≈RM2.9–3.6/W).
- Average residential ≈ RM3.50/W; drops to RM2.80/W for commercial >50kWp.

**Commercial / C&I (50kWp–1MWp):** RM4,000–5,000 /kWp (RM4–5/W) per Northern Solar [S6]; consistent with prior-run "C&I RM3–5k/Wp" [prior logs].
- → RM100k–500k director band ≈ 20–100kWp C&I / multi-family systems at RM4–5/W. Holds.

**Fee stack components (what eats the RM/kW):** panels+inverter+BOS (~70–80% of RM), CAS study (RM1k–20k, scales with capacity) [S7], PE/CP endorsement, TNB connection RM7.50/kW [S4], ST license (admin, above thresholds) [S7].

**NEW 2026-08-16 — 2026 incentives reducing net RM/kW:** [S13]
- **SuRIA Home rebate** up to **RM5,000** (RM3,000 SuRIA + up to RM2,000 installer bonus) for domestic rooftop — direct subtraction from net installed cost.
- **GITA** (Green Investment Tax Allowance): 100% Investment Tax Allowance on qualifying solar + BESS expenditure, **extended through 2026** (MIDA).
- **Sizing loosened:** commercial can install up to **100% of Maximum Demand** (was 75% under NEM 3.0), capped at 1MWac — larger offset base per site.

---

## C. AFTER-SALES / O&M SLA (KPI: callback rate)

**Confirmed framework (generic, not MY-specific):** O&M contract core metrics = System Availability % and Response/Resolution time; corrective maintenance covers inverter/cabling/mounting; spares inventory + warranty management expected. [S9]
**Prior-intel (2026-08-13):** inverter RM2.5k–10k, life 10–15 yr; rework 5–10% of contract value. [prior logs]
**GAP (still OPEN after 2 runs — G2→NG3):** No Malaysia-specific residential/C&I O&M SLA benchmark (response hrs, availability %, local inverter spares lead) found in free search — only generic global frameworks (response 24–48hr, resolution variable, availability 98–99% typical). Treat prior rework % as the only local anchor. Needs field/installer-survey method, not web search.

---

## D. PROCUREMENT LEAD TIME (KPI: Tier-1 panel, supply concentration)

**Supply concentration:** Global PV manufacturing (polysilicon→wafers→cells→modules) concentrated in China (>80% share); single-point geopolitical/logistics risk. [S8]
**Inbound logistics to MY:** SE-Asia ocean freight 20–30 days regional; 2025 freight rates below 2024 levels; Asia port congestion has >1% passthrough to rates, recent congestion added 4–6 wk buffer (Seko). [S10]
**Implied Tier-1 panel lead to Penang:** ex-works (China) + ~10–14 d ocean to Port Klang + customs/last-mile — full pipeline typically 4–12 wk; congestion can extend. *Not precisely pinned for Penang inbound — see _GAPS G3.*

**NEW 2026-08-16 — Inbound Tier-1 panel lead to Penang RESOLVED (G3):** [S14][S15]
- China→MY sea **FCL 8–10 days** to Port Klang / Penang / Pasir Gudang (Aug 2026 rates $450–550/20GP, $855–1,045/40GP); **LCL 9–14 days**. [S14]
- Solar-specific door-to-door **5–7 weeks (35–47 d)** incl. **2–4 wk supplier production**; port-to-port 25–35 d. [S15]
- **Defensible planning number:** PO → site-ready ≈ supplier production 2–4 wk + ocean 8–14 d + customs/last-mile 1–2 wk ≈ **6–10 wk; plan 8–10 wk buffer** from PO. [S14][S15]
- Penang transshipment delta vs Port Klang direct (does Penang add days?) still open — see _GAPS NG4.

**Prior-intel:** 412 RPVSPs registered (competitive installer market, supports shorter local fulfilment). [prior logs]

---

## E. ATAP EXPORT MECHANICS & PAYBACK (KPI B — resolves G4) [NEW 2026-08-16]

**Export credit mechanics (ATAP 2026):** [S13]
- **Domestic** export credit = **retail tariff offset**: RM0.27/kWh (≤1,500 kWh/mo usage) / RM0.37/kWh (>1,500 kWh/mo).
- **Non-domestic (C&I)** export credit = **SMP (System Marginal Price)** — market-based wholesale clearing price set by TNB Grid System Operator, typically **RM0.20–0.40/kWh**.
- **KEY delta vs NEM 3.0:** NEM 3.0 non-domestic used a fixed FiT-like rate; ATAP commercial export is now SMP (market, below retail) → **export-rich C&I sites get WORSE payback under ATAP**. Domestic offset mechanics ≈ unchanged.
- **Credit validity:** ATAP credits must be consumed within the **same billing month (no carryover)** — caps benefit for low-consumption / export-heavy sites. This materially affects which system sizes still clear the hurdle rate.
- **Market context:** MY solar >5.7GW (Apr 2026); 82,000+ rooftop systems, ~1.7GW rooftop capacity; RE 32% of capacity (Feb 2026), target 40% (2035) / 70% (2050). [S13]

---

## SOURCES
[S1] SEDA Malaysia — NEM 3.0 / ATAP portals (seda.gov.my/reportal/nem/, /atap/)
[S2] Northern Solar — "Make Your Residential Solar Pay with Solar ATAP" (northernsolar.com.my)
[S3] Trexon Energy — Solar ATAP Malaysia 2026 Definitive Guide + solar-cost (trexon.my)
[S4] Homifytech — ATAP Application Guide 2026: RM7.50/kW, 2–4 wk, CCC/CAS explained (homifytech.com.my)
[S5] Trexon — Solar Panel Cost Malaysia 2026 (trexon.my/solar-cost)
[S6] Northern Solar — Commercial Solar Panels Cost / Business ROI (northernsolar.com.my)
[S7] SEDA — NEMAS/CAS fee table + licensing thresholds (seda.gov.my/reportal/nem/)
[S8] IEA — Solar PV Global Supply Chains (iea.org)
[S9] Greensolver — Key Solar O&M Contract Elements (greensolver.net)
[S10] Freight market updates 2025 (Freightos, Seko, Dimerco)
[S11] Community anecdote — Facebook Solar NEM/MY group (approval timing)
[S12] myTNB — Solar ATAP portal: Technical Assessment Study Requirements (CCC >12kW ≤425kW; CAS >72kW LV) (mytnb.com.my/renewable-energy/solar-accelerated-transition-action-programme)
[S13] solaratap.com.my — ATAP guide: SMP RM0.20–0.40, domestic retail offset RM0.27/0.37, 100% MD sizing, SuRIA RM5k rebate, GITA 2026, MY capacity >5.7GW
[S14] SINO Shipping — China→Malaysia freight Aug 2026: FCL 8–10d, LCL 9–14d, rates (sino-shipping.com)
[S15] Couleenergy — Ship solar panels from China: 5–7 wk door-to-door, 2–4 wk production (couleenergy.com)

*Prior runs (2026-08-13, logs/ + modules/ under this path) contributed: C&I RM3–5k/Wp, 412 RPVSPs, CAS/TNB 2–4wk, inverter RM2.5–10k/10–15yr, rework 5–10%, GTFS-i 5.0 terms — folded above where still valid; verify scheme-specific items against ATAP era.*
