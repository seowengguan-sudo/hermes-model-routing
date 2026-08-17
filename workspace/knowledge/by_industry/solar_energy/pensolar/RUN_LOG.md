# PENSOLAR — RESEARCH RUN LOG

## 2026-08-14 (cold-start bootstrap of SUMMARY/_GAPS/RUN_LOG structure)
- **Query topics:** (1) ATAP/NEM application timeline; (2) MY solar cost per kW residential+commercial; (3) O&M SLA benchmarks; (4) Tier-1 panel procurement lead time/supply concentration.
- **Sources pulled:** SEDA NEM/ATAP [S1][S7]; Northern Solar ATAP+cost [S2][S6]; Trexon ATAP guide+cost [S3][S5]; Homifytech fees [S4]; IEA supply chains [S8]; Greensolver O&M [S9]; freight 2025 [S10]; FB anecdote [S11]. (11 sources)
- **Key finding:** Solar ATAP replaced NEM 3.0 on 1 Jan 2026 — residential funnel re-based; 6–14 wk assessment→switch-on; RM2.80–4.50/W residential, RM4–5/W C&I; China supply concentration; O&M MY-specific SLA data missing.
- **Prior intel folded:** C&I RM3–5k/Wp, 412 RPVSPs, CAS/TNB 2–4wk, inverter RM2.5–10k/10–15yr, rework 5–10% (from 2026-08-13 logs/ + modules/).
- **Gaps RESOLVED this run:** none pre-existing (cold start) — established foundation for all 4 KPIs.
- **Gaps ADDED (→_GAPS.md):** G1 ATAP approval variance/Penang CCC queue; G2 MY O&M SLA benchmarks; G3 Penang panel lead time; G4 ATAP export payback; G5 Penang CAS queue.
- **Cap status:** SUMMARY ~6KB, well under 32KB.

## 2026-08-16 (adaptive growth run #2 — fill G1/G3/G4, refine structure)
- **Query topics:** (1) TNB ATAP technical assessment study structure + CCC/CAS thresholds [G1/G5]; (2) ATAP export credit mechanics & SMP payback [G4]; (3) China→Penang panel freight lead time 2026 [G3]; (4) re-scan MY O&M SLA benchmarks [G2].
- **Sources pulled:** myTNB ATAP Technical Assessment Study Requirements [S12]; solaratap.com.my ATAP guide (SMP, retail offset, SuRIA, GITA, sizing, capacity) [S13]; SINO Shipping China→MY Aug-2026 freight [S14]; Couleenergy solar-panel China shipping [S15]; re-verified Homifytech 2–4 wk / RM7.50 / CCC-CAS [S4]. (5 sources; 4 new + 1 re-verify)
- **Key findings:**
  - **G4 RESOLVED:** Domestic export = retail tariff offset (RM0.27/0.37/kWh); C&I export = SMP RM0.20–0.40/kWh (market-based, WORSE than NEM3.0 fixed rate); credits non-carryover (same billing month). 100% MD sizing (was 75%); SuRIA rebate ≤RM5k; GITA 100% ITA extended 2026.
  - **G3 RESOLVED:** Ocean FCL 8–10 d to Port Klang/Penang, LCL 9–14 d; PO→site ≈ 6–10 wk (plan 8–10 wk buffer) incl. 2–4 wk production.
  - **G1/G5 PARTIAL:** TNB study structure pinned — CCC for >12kW≤425kW, CAS for >72kW LV, ≤12kW exempt; pre-approval prerequisite. Regional Penang queue days still unpinned.
  - **G2 UNRESOLVED:** Still only generic global O&M SLA frameworks; no MY-specific data after 2 runs.
- **Gaps RESOLVED/FILLED this run:** G3 (full), G4 (full), G1/G5 (structural partial). G2 remains open.
- **Gaps ADDED (→_GAPS.md as NG1–NG5):** NG1 Penang realized RM/kWp after rebate + ATAP payback; NG2 Penang/Perak TNB CCC/CAS+meter queue actual lead; NG3 MY O&M SLA (escalate to survey); NG4 Penang transshipment delta vs Port Klang; NG5 2026 Tier-1 panel $/W trend.
- **Cap status:** SUMMARY ~10KB (added §E + timeline/cost/procurement updates), well under 32KB. No prune needed.
