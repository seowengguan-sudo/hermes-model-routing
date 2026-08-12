# PENSOLAR - Compressed Operating-Model Distillation (living)
Last pull: 2026-08-11 (run 2) | Vertical: Solar PV integration (residential + C&I), Penang / Peninsular MY
Scope: workflow, regulatory gates, cost structure, pain points. Maintain <=32KB.
Source base (run 1): SEDA NEM 3.0 [1], Northern Solar [2], Trexon [3], Eigen EPC [4], Ember [5], IEA-PVPS MY2025 [6].
Source base (run 2): Homi Solar ATAP guide [S1], solaratap.com.my process guide [S2], SEDA ATAP reportal [S3],
Samaiden SELCO update [S4], myTNB SELCO [S5], NREL O&M model TP-74840 [S6], pv-maps O&M [S7],
Trexon O&M service [S8], CommercialSolarGuy O&M [S9], SolarPowerEurope GMO [S10], Enerdata PV 2026 [S11].

## 1. Regulatory frame (MY, Peninsular)
- SEDA = Implementing Agency; Energy Commission (EC) regulates; TNB = grid/distribution licensee.
- NEM 3.0 (Rakyat/GoMEn/NOVA) ran to Jun 2025; REPLACED by Solar ATAP from Jan 2026:
  no quota, continuous, higher caps (domestic 1-ph <=5kWac / 3-ph <=15kWac; non-domestic
  <=100% max demand capped 1,000kW). Domestic offset at retail tariff; non-domestic at SMP [1][6].
- SELCO (self-consumption, no export): 85% cap removed -> 100% demand; BESS mandatory >72kWp
  deferred to 31 Dec 2025; standby charge applies (see 3, CORRECTED) [6][S4].
- Other schemes: LSS, CGPP, CRESS (SAC 25c firm w/BESS / 45c non-firm), CREAM (CAC 9c/kWh) [6].
- Licensing: s.9 Electricity Supply Act for >24kW 1-ph / >72kW 3-ph [1].
- CAS (Connection Assessment Study) fees: RM1k (>72-180kW) to RM20k (>2-5MW); valid 1 yr [1].
- ATAP approval is now grid-stability-gated, NOT quota-gated — no slot scarcity, but local grid
  capacity check can still reject/derate a site [S2][S3]. Applications via eATAP portal (atap.seda.gov.my);
  applicant MUST appoint a SEDA-Registered Solar ATAP service provider [S3]. => PENSOLAR registration is a moat.
- Document gate: CCC/CF (or equivalent verification) required before TNB will swap to bidirectional
  meter. Older/unpermitted buildings are the #1 stall cause at this gate [S1].

## 2. Workflow phases (with parallel admin/accounting)
P1 Survey/Feasibility 2-4wk: field roof/load/3D; admin CRM+ROI+deposit+PE+ownership proof.
P2 Reg Design/Apply 1-4wk+wait: field Competent-Person design, ATAP+TNB, CAS>72kW;
   admin submissions, GAT, PE fees, CAS fees, licensing, financing docs.
P3 Procure/Mount 2-4wk: field Tier-1 panels, rails, waterproofing; admin POs, credit terms, logistics, warranties.
P4 Electrical/Commission 1wk: field inverter/SPD/earthing, testing, monitoring; admin test reports, certs, as-built.
P5 TNB Inspect/Connect 2-6wk: field TNB inspection, bidirectional meter; admin scheduling, approval, ATAP acct, handover.
P6 O&M/After-sales 20-25yr: field cleaning/inspection/monitoring; admin AMC, SLA, spares, warranty claims.

## 2b. TIMELINE VARIANCE BY PROJECT SIZE (run-2 fill, KPI: timeline adherence)
- Residential 5-10kW (ATAP domestic): SEDA approval 2-4wk; install 1-2 DAYS; end-to-end 4-8wk [S1][S2].
  Internal ATAP review cadence: wk1 submission/vetting, wk2-3 technical + capacity check, wk4 approval/COA [S1].
- Commercial 50kW+: install alone 1-2wk [S2]; plus CAS (>72kW), s.9 licensing, PE sign-off -> the
  3-5 month figure in pain-point #1 is a **C&I number, not a residential one**.
- IMPLICATION: the "3-5mo" KPI baseline was conflating segments. Residential should be run to an
  6-8wk SLA and C&I to 3-5mo. A PM system MUST branch its schedule template on segment, else
  residential jobs silently absorb C&I slack and look "on time" while cash sits idle.
- Remaining variance driver = TNB meter-swap scheduling (P5, 2-6wk) and CCC availability, both
  outside PENSOLAR's control -> track as explicit "external wait" clock, exclude from crew KPI.

## 3. Cost structure
- Commercial upfront RM100k-RM500k; payback 5-8 yr (sometimes 3) [2].
- Residential installed price band RM16.8k-RM72k; ~RM33k for 10kW, 25-yr panel warranty [3].
- Fees stack: CAS RM1k-20k + PE + TNB + licensing + standby charge.
- **ATAP processing fee RM7.50/kW, non-refundable, payable on submission** (10kW = RM75) [S1].
  Trivial per job but must be a billable line item, not absorbed.
- **STANDBY CHARGE CORRECTED: SELCO non-domestic >72kWp = RM14/kWp/month** [S4][S5]
  (run 1 recorded ~RM12/kWp/mo and pegged it at >1MWp — both wrong; threshold is 72kWp,
  new capacity threshold reported applying above 1MWac separately).
  Materiality: 100kWp SELCO = RM1,400/mo = RM16.8k/yr recurring against savings — can move
  payback by 1-2 yr. MUST appear in every SELCO ROI model or PENSOLAR mis-sells the payback.
- MD (maximum demand) / power-factor surcharge: for supply <132kV, 1.5% of energy+demand+AFA
  charges per 0.01 below 0.85 PF [S5-adj] — solar+BESS pitch lever for C&I.
- 2025 Q3 tariff hike hits industrial; TOU / AFA (replaces ICPT) changes cash-flow planning [6].
- Module prices low near-term (China oversupply) but upward pressure from VAT rebate cut (13%->9%) into 2026 [6].
- SuRIA Home rebate up to RM3,000 (+ installer bonus, market-driven) live in 2026 residential
  campaigns [S2] — a closing lever, verify current status before quoting.

## 3b. O&M / AFTER-SALES BENCHMARKS (run-2 fill, KPI: callback rate)
- Global benchmark annual O&M: USD12-30/kW/yr, avg ~USD18/kW/yr; large plants ~1% of capex/yr [S6][S9].
- Utility/large-scale EU: EUR15-20/kWp/yr typical; inverter service EUR200-400/yr per string unit
  (<100kW), EUR2,000-3,000/yr per central unit (>1MW) [S7].
- MY residential reality: ~RM500/yr inspection prevents RM1,500+ repair bills; inverter is the
  dominant replacement risk item over 25-yr life [S8].
- Degradation 0.5-0.8%/yr => ~80-88% output at yr 25; performance-ratio drift, not hard failure,
  is what quietly kills client ROI and triggers disputes [S8-adj].
- IMPLICATION: price AMC at RM40-80/kW/yr for C&I (converts USD18/kW benchmark + local labour)
  and a flat RM500-900/yr residential tier. Inverter sinking-fund should be explicit in the AMC,
  because inverter replacement at yr 10-12 is the single biggest after-sales dispute source.
- No published Malaysian callback-rate benchmark found (see gaps) — PENSOLAR must instrument its
  own baseline from ticket 1. This is a build requirement for the PM system, not a research gap
  that a future search will close.

## 4. Pain points (ranked, with source)
1. Approval lead time: C&I 3-5 mo; residential 4-8 wk [3][4][S1][S2]. TNB/AUTH
2. Incomplete docs / late stakeholders / multi-reviewer friction [4][3]. TNB/AUTH
   -> now specifically: missing CCC/CF blocks meter swap [S1].
3. Roof/structural constraints cap size & ROI; reinforcement needed [4]. RESOURCE
4. C&I ops-continuity risk during install [4]. RESOURCE
5. Design errors surface at commissioning -> rework [4]. QUALITY
6. Rushed handover -> no performance visibility [4]. QUALITY/AFTER-SALES
7. PETRA blacklist drags client rebate claims [2]. QUALITY/T&C
8. Weak O&M -> lost export credits over 20-25yr [2]. AFTER-SALES
9. High upfront capital + fee stack (CAS/licensing/ATAP RM7.50/kW) [2][1][S1]. COST
10. Tariff volatility / TOU re-planning [6]. COST
11. Module-price uncertainty (VAT rebate, trade) [6]. COST/GLOBAL
12. Global supply concentration: US duties forced majors to exit MY [6]. GLOBAL PARTS
13. NEM->ATAP transition relearn (caps/crediting SMP) [6]. TNB/AUTH
14. Licensing/BESS/standby-charge compliance [6][S4]. T&C
15. CRESS/CREAM/SELCO charging & cap changes [6]. T&C
16. **SELCO standby charge RM14/kWp/mo mis-modelled in ROI** -> post-sale trust damage [S4]. COST/T&C
17. **Imported equipment lead time adds 3-6 mo when supply tightens** [S10]. GLOBAL PARTS

## 4b. PROCUREMENT / SUPPLY (run-2 fill, KPI: procurement lead time)
- Historical stress case: imported-equipment procurement added 3-6 months to lead times during
  supply-chain disruption [S10]. Current market is the opposite regime — global module shipments
  FELL 6% to 643GW in 2026, first decline after 4 years of expansion, i.e. buyer's market [S11].
- Malaysia demand outlook: ~11.8GW addable 2026-2030, installation peak 2027-2029 [S12-adj].
  => Local demand ramp will tighten installer/crew and possibly racking supply BEFORE it tightens
  modules. Constraint shifts from panels to labour + TNB/SEDA throughput.
- IMPLICATION: lock 2026-27 module pricing opportunistically (soft market), but hedge the real
  2027-29 bottleneck = certified crews and Competent Persons. Contract PE/CP capacity early.

## 5. Strategic implications for PENSOLAR
- Compress P1-P2 with disciplined early site assessment + document checklist + single-point PM.
- Segment the schedule: residential 6-8wk SLA vs C&I 3-5mo. Never one blended timeline KPI.
- Gate every job on CCC/CF verification at P1, not P5 — cheapest place to kill a stall.
- Protect margin against fee stack & tariff volatility via fixed-price quotes + escalation clauses.
- Standby charge (RM14/kWp/mo >72kWp SELCO) must be hard-coded into the ROI calculator.
- Build O&M/SLA backbone as recurring revenue: RM40-80/kW/yr C&I, RM500-900/yr residential,
  with an explicit inverter sinking fund. Instrument callback rate from day 1 (no external benchmark exists).
- Pre-qualify Tier-1 suppliers + dual-source; buy module price cover now, secure CREW/CP capacity for 2027-29.
- Maintain SEDA-Registered service-provider status — it is a legal prerequisite, i.e. a defensible moat.
- Track ATAP/SELCO/BESS rule changes; train sales/engineering on new caps & SMP crediting.
