# PENSOLAR - Compressed Operating-Model Distillation (living)
Last pull: 2026-08-13 (run 3) | Vertical: Solar PV integration (residential + C&I), Penang / Peninsular MY
Scope: workflow, regulatory gates, cost structure, pain points. Maintain <=32KB.
Source base (run 1): SEDA NEM 3.0 [1], Northern Solar [2], Trexon [3], Eigen EPC [4], Ember [5], IEA-PVPS MY2025 [6].
Source base (run 2): Homi Solar ATAP guide [S1], solaratap.com.my process guide [S2], SEDA ATAP reportal [S3],
Samaiden SELCO update [S4], myTNB SELCO [S5], NREL O&M model TP-74840 [S6], pv-maps O&M [S7],
Trexon O&M service [S8], CommercialSolarGuy O&M [S9], SolarPowerEurope GMO [S10], Enerdata PV 2026 [S11].
Source base (run 3): Sunview SELCO-BESS 2026 [R1], Shu Pin & Assoc standby/BESS legal [R2], buySolar ATAP FAQ [R3],
Trexon install timeline [R4], Northern Solar commercial setup [R5], SolarDir RPVSP count [R6],
Northern Solar C&I cost [R7], Trexon C&I cost [R8].

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
- **STANDBY CHARGE + BESS RE-REVISED (2026-08-13, run 3 — corrects run 2):** the run-2 figure
  RM14/kWp/mo for ALL >72kWp SELCO was WRONG for the 72kWp–1MWp band. Per PETRA (27 Feb 2025)
  + ST (31 Dec 2025): SELCO 72kWp–1MWp is now EXEMPT from standby charge; ONLY >1MWp pays
  RM12/kWp/month (cut from RM14) [R1][R2]. BESS mandate threshold RAISED from 72kWp to >1MWac
  (effective 1 Jan 2026) — so PENSOLAR's typical SELCO C&I 72kWp–1MWac range needs NEITHER BESS
  NOR standby charge [R1][R2]. Materiality: the run-2 warning (RM1,400/mo on 100kWp) is VOID for
  the 72kWp–1MWp band; SELCO ROI for that band is BETTER than previously modelled. >1MWp still
  carries RM12/kWp/mo standby + mandatory BESS. Re-run SELCO ROI with the banded rule.
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
- Standby charge: EXEMPT for SELCO 72kWp–1MWp; RM12/kWp/mo ONLY for >1MWp (run-3 corrected). BESS mandatory only >1MWac. Hard-code the BANDED rule, not a flat RM14 into the ROI calculator.
- Build O&M/SLA backbone as recurring revenue: RM40-80/kW/yr C&I, RM500-900/yr residential,
  with an explicit inverter sinking fund. Instrument callback rate from day 1 (no external benchmark exists).
- Pre-qualify Tier-1 suppliers + dual-source; buy module price cover now, secure CREW/CP capacity for 2027-29.
- Maintain SEDA-Registered service-provider status — it is a legal prerequisite, i.e. a defensible moat.
- Track ATAP/SELCO/BESS rule changes; train sales/engineering on new caps & SMP crediting.

## 6. Run-3 fills (2026-08-13)
### 6a. CAS / TNB approval turnaround (KPI: timeline adherence) — was gap 1
- End-to-end contract→activation 8–14wk [R4]. Breakdown: SEDA notification up to 2 months
  (§15.5 GP/ST/No.60/2025), TNB approval 2–3wk, physical install 2–3 days, final TNB
  inspection + bidirectional meter 1–2wk [R4]. Northern Solar: grid approval 2–4wk [R5].
- IMPLICATION: for >72kW CAS jobs, CAS is EMBEDDED in the TNB approval band (2–4wk), not a
  separate longer pole. The long pole is SEDA's own notification (up to 8wk). Realistic C&I
  baseline = SEDA-notify 8wk + TNB 3wk + install/meter 3wk ≈ 14wk. Track SEDA-notify as its
  own external-wait clock, distinct from crew KPI.
- Residual: CAS rejection/derate rate by band still unpublished (see §7 gap 2).

### 6b. CP / RPVSP supply (KPI: procurement lead time + install cost/kW) — was gap 2
- SEDA-registered PV Service Providers (RPVSP): ~412 as of 2026 [R6], vs an older SEDA figure
  of 110. Market is WELL-POPULATED; the run-2 thesis that 'labour is the 2027–29 bottleneck' is
  OVERSTATED at the installer level.
- IMPLICATION: binding constraint is NOT installer headcount but (a) certified-Competent-Person
  sign-off throughput and (b) TNB/SEDA processing speed. Expect ample installer competition to
  keep crew rates in check; the real capacity play is pre-booking CP sign-off for peak 2027–29.

### 6c. C&I installed cost per kW (KPI: install cost/kW) — was gap 4
- C&I rooftop capex ≈ RM3,000–5,000/kWp (RM3–5/Wp): Northern Solar 50kWp–1MWp averages
  RM4,000–5,000/kWp [R7]; Trexon 50kWp from RM150k (=RM3,000/kWp), 100kWp RM300k, up to RM1.6M [R8].
- Residential anchor ~RM3,000–3,500/kWp [2][3] — C&I per-kWp is similar/slightly higher.
- Run-1 envelope RM100k–500k ≈ 33–125kWp at RM3–4k/Wp — internally consistent.
- Residual: clean module/inverter/racking/labour/fees SPLIT still unpublished (see §7 gap 6).

### 6d. Standby charge + BESS (KPI: install cost/kW) — was gap 3, RESOLVED
- Net 2026 rule: SELCO 72kWp–1MWp EXEMPT standby + no BESS; >1MWp RM12/kWp/mo + mandatory BESS
  >1MWac. See corrected §3 block. Re-run SELCO ROI with the BANDED rule, not the run-2 flat RM14.

## 7. Open gaps (feed next run, priority order)
1. Certified Competent Person (CP) individual count + sign-off queue wait (Peninsular MY) — the
   real 2027–29 constraint is CP throughput, not installer count (412 RPVSPs). KPI: timeline + cost/kW.
2. CAS rejection / derate rate by capacity band (72kW–1MW) — drives redesign loops. KPI: timeline.
3. MY-market inverter replacement RM quote (string vs central) + AMC sinking-fund sizing. KPI: callback cost.
4. Green-financing / GTFS-successor terms for C&I under ATAP (tenor, rate). KPI: cost/kW + closure.
5. Rework cost % of contract when design errors surface at commissioning. KPI: cost/kW + quality.
