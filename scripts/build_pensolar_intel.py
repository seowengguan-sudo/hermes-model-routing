#!/usr/bin/env python3
# PENSOLAR daily intel builder — writes dated log, raw extracts, SUMMARY.md (32KB guard).
import os, datetime

DATE = datetime.date.today().strftime("%Y-%m-%d")
BASE = "/opt/data/knowledge"
LOG_DIR = f"{BASE}/by_industry/solar_energy/pensolar/logs"
RAW_DIR = f"{BASE}/raw"
SUM = f"{BASE}/by_industry/solar_energy/pensolar/SUMMARY.md"
LOG_PATH = f"{LOG_DIR}/{DATE}.log"
RAW_PATH = f"{RAW_DIR}/pensolar-{DATE}.md"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(RAW_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. COMPRESSED LOG REPORT (<1500 words, business-director tone, inline cites)
# ---------------------------------------------------------------------------
LOG = f"""# PENSOLAR Daily Intel — {DATE}
Subject: Solar PV integrator operations in Malaysia (residential + C&I) — workflow
phases, parallel admin/accounting work, and concrete pain/pinch points.
Tone: for the Director. Sources cited inline [S1..S6].

PENSOLAR workflow chain (brief.md): Lead -> Site Survey -> Design -> Permits
(ST/TNB/SEDA) -> Quotation -> Contract (outright OR PPA/lease) -> Procurement ->
Install -> Commission -> NEM/SelCo activation -> O&M. Each phase below lists the
parallel admin/accounting workstream a Director must see, plus the pinch.

## P1 — Lead & Feasibility (Sales)
- Field: lead capture, energy-yield/ROI/IRR modelling [S5].
- Admin/Acctg: CRM entry, quote draft, deposit/invoice setup, log PPA-vs-outright
  decision [S4].
- Pinch: commission-only agents overpromise savings -> later disputes [S6 #1,#2].

## P2 — Site Survey & Design
- Field: roof/structural/shading assessment, load profile, system sizing; design
  endorsed by Competent Person (PE) [S3]. TNB Connection Assessment Study (CAS)
  mandatory above 72kW; fees RM1k(>72-180kW) -> RM20k(>2-5MW) [S1].
- Admin/Acctg: survey report filed, PE endorsement cost, CAS fee paid, design QA.
- Pinch: hidden roof/structural defects found mid-install -> cost add-ons [S6 #4].

## P3 — Permits & Authority Approvals (ST / TNB / SEDA)
- Field: NEM/SelCo/NOVA application, TNB technical approval, SEDA ATAP, local-
  authority building plan, Grant of Authority [S3; S2].
- Admin/Acctg: document pack (NEM cert, Forms G/H, N/Q competent certs, T&C),
  submission tracking; Energy Commission licence if >72kWp 3-ph / >24kWp 1-ph [S1].
- Pinch: SEDA result ~2 months + TNB 2-3 weeks => 8-14 weeks end-to-end [S3 FAQ].
  NEM 3.0 quota window CLOSED 30 Jun 2025; SelCo now default; PETRA hints NEM 4.0
  (no timeline) [S5]. TNB rejects incomplete submissions [S1].

## P4 — Quotation & Contract
- Field: final quote; contract outright / PPA / Solar Leasing via RPVI [S1; S4].
- Admin/Acctg: contract review (PPA terms; SARE tripartite with TNB charging 2
  sen/kWh, non-payment -> TNB disconnect under ESA s.29 [S1]); RPVI registration
  (local RM1M paid-up + RM3k/yr; foreign RM10M + 80% local staff + 100% local EPC
  [S4; S1]).
- Pinch: high-pressure sales, unclear fine-print, hidden escalation fees ->
  complaints/BBB/lawsuits [S6 #3].

## P5 — Procurement
- Field: Tier-1 module + inverter + BOS sourcing, delivery [S3; S2].
- Admin/Acctg: PO issuance, vendor compare, GRN, payment terms, CAS/TNB deposits.
- Pinch: global panel backorders slip installs months, miss incentive deadlines
  [S6 #5]. EPC cost RM3k-6k/kWp residential, lower for large C&I [S4].

## P6 — Installation & Commissioning
- Field: mount + waterproofing, inverter/AC-DC cabling, SPD, earthing, test &
  commissioning report, monitoring setup, customer training [S3; S2].
- Admin/Acctg: capture CIDB/SEDA installer certs, progress billing, milestone
  photos, warranty registration.
- Pinch: poor install (exposed wires, bad mounts, roof damage) -> safety hazard +
  repair cost + liability [S6 #6].

## P7 — Grid Connection & Activation
- Field: TNB inspection, bidirectional meter install, NEM/SelCo activation [S3; S1].
- Admin/Acctg: handover pack, final invoice; SolaRIS rebate ended 30 Apr 2025 [S5].
- Pinch: TNB scheduling queue + meter lead time.

## P8 — O&M / After-Sales
- Field: annual cleaning, inspections, 24/7 monitoring, drone thermography, warranty
  claims [S2; S5].
- Admin/Acctg: O&M contract billing, spare-parts inventory, SLA tracking; Tier-1
  25-yr perf guarantee, inverter >=5-yr [S5].
- Pinch: output declines without monitoring; warranty-claim friction; local
  spare-parts availability [S5; S6].

## Consolidated pain/pinch points (Director's exception radar)
1. Sales/mis-selling risk — agents overpromise savings; disputes + reputational/legal
   exposure [S6]. Fix: contract simplification, realistic ROI in system.
2. Authority friction & timeline — SEDA ~2mo + TNB 2-3wk; 8-14wk end-to-end; NEM 3.0
   closed -> SelCo pivot [S3; S5]. Needs permit-status radar (Module 2).
3. Procurement / supply-chain — panel backorders => multi-month slips; FX/price
   swings [S6 #5]. Justifies deep Procurement-Auto module.
4. Cost escalation / hidden fees — roof repairs, complex shading, CAS RM1k-20k surface
   late [S6 #4; S1]. Buffer + transparent BOQ.
5. Quality / after-sales — faulty install -> safety + liability; warranty friction;
   spare stock [S6 #6; S5].
6. Regulatory/compliance — RPVI capital & localisation; ST licensing thresholds;
   TNB rejects incomplete packs [S4; S1].
7. Policy uncertainty — NEM 3.0 ended, no NEM 4.0 yet; SolaRIS gone; SelCo no export
   [S5]. Cashflow model must flex.

## Cost / ROI anchors
- C&I install RM100k-RM500k; payback 5-8 yr (some 3) over 20-25 yr life [S2].
- EPC RM3k-6k/kWp residential [S4]. CAS fees RM1k-RM20k by capacity [S1].

Sources (6): [S1] SEDA NEM 3.0 portal (seda.gov.my/reportal/nem) |
[S2] Northern Solar commercial setup (northernsolar.com.my) |
[S3] Trexon install process (trexon.my/installation-process) |
[S4] Bestar RPVI Malaysia (bestar-asia.com) |
[S5] Homify post-NEM 3.0 guide (homifytech.com.my) |
[S6] Cleantech Law complaints/lawsuits (cleantechlaw.com).
"""

# ---------------------------------------------------------------------------
# 2. RAW EXTRACTS (full source text captured this run)
# ---------------------------------------------------------------------------
SEDA_CACHE = "/opt/data/cache/web/www.seda.gov.my-39755019a7.md"
CLEAN_CACHE = "/opt/data/cache/web/cleantechlaw.com-1aff1a7522.md"

def read_cache(p):
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        return f"[cache missing: {p} ({e})]"

raw_seda = read_cache(SEDA_CACHE)
raw_clean = read_cache(CLEAN_CACHE)

RAW = f"""# PENSOLAR Raw Extracts — {DATE}
Auto-archived from 6 FREE web sources. Full text for regeneration of SUMMARY.

=====================================================================
S1 — SEDA NEM 3.0 (https://www.seda.gov.my/reportal/nem/)
=====================================================================
{raw_seda}

=====================================================================
S2 — Northern Solar: From Roof to Grid: Commercial Solar Setup in Malaysia
(https://northernsolar.com.my/from-roof-to-grid-commercial-solar-setup-in-malaysia/)
=====================================================================
Commercial solar in Malaysia follows a defined approval + grid-connection process
governed by SEDA and TNB. 20-25 year operating life.
Phase table: Assessment 2-4wk (feasibility report) | Design 1-2wk | Procurement &
Mounting 2-3wk | Commissioning 1wk | Grid Approval 2-4wk (connection permit) |
Activation immediate.
Assessment factors: roof/orientation, structure, shading, energy use, SEDA/TNB
compliance. Design: Tier-1 certified panels, inverters set to TNB voltage/freq/
export limits, quality cables/isolators/SPD/grounding.
Procurement->grid: TNB verifies protection devices, inverter behaviour, output vs
interconnection standards. Surplus exported, credited under NEM.
Cost/ROI: C&I RM100k-RM500k; payback 5-8 yr (some 3); factors: consumption,
tariff, efficiency. 20-25 yr lifespan. EPCC provider owns engineering accuracy,
procurement control, construction quality, approval coordination. Maintenance:
annual cleaning, inspections, 24/7 monitoring; equipment warranties + service
agreements. PETRA warned blacklisted providers take submitted rebate claims down
with them (SuRIA Home launch). Carbon Tax 2026 raises cost for export mfg reliant
on grid power; on-site solar is a hedge.

=====================================================================
S3 — Trexon: Solar Panel Installation Process Malaysia (4-6 week approval)
(https://trexon.my/installation-process)
=====================================================================
Total timeline 8-14 weeks. 6 steps:
1. Initial Consultation & Site Survey (Day 1-3): roof structural, shading,
   electrical, load calc, 3D design, quotation, financing (BNPL/green loan/PPA).
   Deliverables: Site Survey Report, 3D Design, Quotation.
2. Documentation & Approvals (Week 1-4): SEDA Solar ATAP, TNB connection, ownership
   verification, Grant of Authority, local-authority building plan (if required),
   PE endorsement. Deliverables: SEDA Approval, TNB Technical Approval, Permit.
3. Solar Panel Installation (Day 1-2): Tier-1 panels, CIDB-licensed, aluminium rails,
   waterproofing. Deliverables: Mounted Array, Waterproofing Cert, Photos.
4. Electrical Installation (Day 2-3): inverter, AC/DC cabling, SPD, isolators,
   earthing/lightning, panel integration. Deliverables: Commissioned Inverter,
   Electrical Cert.
5. System Testing & Commissioning (Day 3-4): insulation/continuity, inverter params,
   Wi-Fi monitoring, customer training. Deliverables: Test & Commissioning Report,
   Monitoring Access, Training Manual.
6. TNB Inspection & Grid Connection (Week 5-6): TNB inspection, bidirectional meter,
   ATAP activation, handover, warranty registration. Deliverables: TNB Approval,
   Bidirectional Meter, Warranty Cert.
FAQ: up to 2 months for SEDA result notification (GP/ST/No.60/2025 s.15.5) + 2-3wk
TNB approval + 2-3 day install + 1-2wk final TNB inspection/meter. 5-yr workmanship
warranty. Handover pack: install cert, electrical test, SEDA approval, TNB grid
approval, warranty certs, diagram, monitoring login, maintenance guide.

=====================================================================
S4 — Bestar: Registered Solar PV Investor (RPVI) in Malaysia
(https://www.bestar-asia.com/post/registered-solar-pv-investor-rpvi-in-malaysia)
=====================================================================
RPVI: SEDA-registered company offering PPA / Solar Leasing to domestic, C&I,
agriculture. Key requirements: SSM incorporated; local paid-up RM1,000,000; foreign
RM10,000,000 + only >250kWac + >=80% local staff + 100% local EPC (appoint RPVSP).
Annual fee local RM3,000 / foreign RM10,000 (USD2,500); update-data RM200;
non-refundable; valid to Dec 31, renewal yearly. Compliance monitored by SEDA;
non-compliance => de-listing. EPC scope: site surveys, design, procurement, install,
commissioning. EPC fees RM3,000-RM6,000 per kWp residential (lower for large C&I).
O&M: recurring annual fee (% of install or RM/kWp/yr). SARE tripartite (consumer,
investor, TNB) reduces counterparty risk. Tax: GITE on solar leasing, GITA for C&I.
Incentives: Green Income Tax Exemption (GITE), Green Investment Tax Allowance (GITA).

=======================================================================
S5 — Homify: Solar Energy Services in Malaysia — Post-NEM 3.0 Guide (July 2025)
(https://homifytech.com.my/solar-energy-services-in-malaysia-post-nem-3-0-guide-july-2025/)
=====================================================================
Malaysia ended NEW NEM 3.0 applications 30 Jun 2025. Existing participants keep
credits 10 yr from commissioning. Everyone else -> SelCo, corporate PPA, or
forthcoming policy.
Market 2025: ~4.4 GW installed PV by end-2024 (+1.3 GW YoY); irradiance 4.2-5.6
kWh/m2/day; LCOE <19 USc/kWh; target 31% RE share by end-2025 (MyRER).
Policy: NEM 3.0 closed (no NEM 4.0 announced as of 13 Jul 2025). SelCo = default for
residential/C&I; onsite use only, NO export, oversizing limited, lower CAPEX +
simplified permits. LSS 4 (COD 2026) + new 2 GW tender (Jan 2025). SolaRIS rebate
(homeowners up to RM4,000) ended 30 Apr 2025. GITA remains for C&I. RECs tradable by
SelCo/LSS. Service categories: Consulting/Feasibility, EPC Turnkey, O&M (24/7
monitoring, drone thermography, module cleaning, warranty claims), Solar-as-a-
Service/PPA (zero-CAPEX), Hybrid & BESS. Provider selection: >=5 MW rooftop + >=2 LSS
wins; SEDA RPVSP registration; Tier-1 modules, inverters >=5-yr product + 25-yr perf
warranty; transparent payback; after-sales response time + local spares + monitoring
app. Outlook 2030: ~14 GW cumulative solar by 2035; floating PV; battery <USD100/kWh
by 2027; possible NEM 4.0 after grid-impact review. SelCo 100 kW C&I ROI 5-8 yr at
80% daytime utilisation + 2% tariff escalation.

=====================================================================
S6 — Cleantech Law: Rising Wave of Complaints and Lawsuits vs Solar Companies
(https://cleantechlaw.com/2024/11/the-rising-wave-of-complaints-and-lawsuits-against-solar-companies/)
=====================================================================
{raw_clean}
"""

# ---------------------------------------------------------------------------
# 3. SUMMARY.md — compressed distillation (rewrite, max 32KB guard)
# ---------------------------------------------------------------------------
SUMMARY = f"""# PENSOLAR — Solar Integrator Operations (Compressed Distillation)
Maintained by learn-pensolar cron. Last rewrite: {DATE}. Max 32KB.
Companion: brief.md, solution_framework.md. Sources inline [S1..S6].

====================================================================
A. MARKET & POLICY CONTEXT (Malaysia, Peninsular)
====================================================================
- ~4.4 GW installed PV by end-2024 (+1.3 GW YoY); irradiance 4.2-5.6 kWh/m2/day;
  LCOE <19 USc/kWh; target 31% RE share by end-2025 (MyRER) [S5].
- NEM 3.0 quota window CLOSED 30 Jun 2025. Existing participants keep 10-yr bill
  credits from commissioning. NO NEM 4.0 announced (PETRA hinted, no timeline) [S5].
- DEFAULT route now = SelCo (self-consumption, NO export, oversizing limited, lower
  CAPEX, simpler permits). Corporate PPA / LSS 4 also options [S5].
- SolaRIS homeowner rebate (up to RM4,000) ENDED 30 Apr 2025. GITA still for C&I.
  RECs tradable by SelCo/LSS owners [S5].

====================================================================
B. REGULATORY GATEKEEPERS & KEY NUMBERS
====================================================================
- SEDA = Implementing Agency (NEM/SelCo/NOVA/RPVI). Energy Commission (ST) regulates
  + licensing. TNB = Distribution Licensee (grid connection, metering) [S1; S2; S3].
- ST Licence required: >72kWp 3-phase OR >24kWp single-phase (Electricity Supply Act
  s.9) [S1].
- TNB Connection Assessment Study (CAS) mandatory >72kW: fees RM1k(>72-180kW),
  RM5k(>180-425kW), RM8k(>425-1MW), RM15k(1-2MW), RM20k(2-5MW); valid 1 yr [S1].
- RPVI registration: local RM1M paid-up + RM3k/yr; foreign RM10M + 80% local staff +
  100% local EPC + only >250kWac; non-refundable; SEDA can de-list [S4; S1].
- SARE tripartite (consumer-investor-TNB): TNB charges 2 sen/kWh; non-payment ->
  TNB disconnect (ESA s.29) [S1].

====================================================================
C. OPERATING WORKFLOW (8 phases, mapped to PENSOLAR chain)
====================================================================
P1 Lead/Feasibility: yield/ROI/IRR modelling [S5]. Admin: CRM, quote, deposit,
   PPA-vs-outright log [S4].
P2 Survey/Design: roof/struct/shading/load; PE-endorsed design [S3]; CAS if >72kW
   [S1]. Admin: survey report, PE fee, CAS fee, design QA.
P3 Permits (ST/TNB/SEDA): NEM/SelCo/NOVA, TNB tech approval, SEDA ATAP, local-authority
   plan, GAT [S3; S2]. Admin: doc pack (NEM cert, Forms G/H, N/Q certs, T&C),
   submission tracking, ST licence if threshold [S1].
P4 Quotation/Contract: outright / PPA / lease via RPVI [S1; S4]. Admin: contract +
   SARE review, RPVI compliance, legal check.
P5 Procurement: Tier-1 modules/inverters/BOS [S3; S2]. Admin: PO, vendor compare,
   GRN, payment terms, deposits.
P6 Install/Commission: mount+waterproof, inverter/AC-DC, SPD, earthing, test &
   commissioning report, monitoring, training [S3; S2]. Admin: CIDB/SEDA certs,
   progress billing, photos, warranty reg.
P7 Grid Connection: TNB inspection, bidirectional meter, NEM/SelCo activation [S3; S1].
   Admin: handover pack, final invoice.
P8 O&M/After-Sales: cleaning, inspection, 24/7 monitoring, drone thermo, warranty
   claims [S2; S5]. Admin: O&M billing, spare inventory, SLA tracking.

====================================================================
D. PAIN / PINCH POINTS (Director exception radar -> module mapping)
====================================================================
1. Sales mis-selling — commission agents overpromise savings -> disputes/legal
   [S6 #1,#2]. -> Module 6 (exec/contract clarity), realistic ROI in system.
2. Authority friction & timeline — SEDA ~2mo + TNB 2-3wk => 8-14wk end-to-end;
   NEM 3.0 closed -> SelCo pivot [S3; S5]. -> Module 2 (permit-status radar).
3. Procurement / supply-chain — panel backorders slip installs months, miss
   incentive deadlines; FX/price swings [S6 #5]. -> Module 5 (Procurement-Auto DEEP).
4. Cost escalation / hidden fees — roof repairs, complex shading, CAS RM1k-20k
   surface late [S6 #4; S1]. -> transparent BOQ + budget buffer.
5. Quality / after-sales — faulty install -> safety + liability; warranty friction;
   local spare availability [S6 #6; S5]. -> Module 7 + O&M SLA tracking.
6. Regulatory/compliance — RPVI capital/localisation, ST licensing thresholds, TNB
   rejects incomplete packs [S4; S1]. -> Module 2 doc-radar.
7. Policy uncertainty — NEM 3.0 ended, no NEM 4.0, SolaRIS gone, SelCo no export
   [S5]. -> cashflow model must flex (Module 4).

====================================================================
E. COST / ROI ANCHORS
====================================================================
- C&I install RM100k-RM500k; payback 5-8 yr (some 3) over 20-25 yr life [S2].
- EPC RM3k-6k/kWp residential, lower per kWp for large C&I [S4].
- CAS fees RM1k-RM20k by capacity [S1].
- SelCo 100 kW C&I ROI 5-8 yr @ 80% daytime use + 2% tariff escalation [S5].
- Equipment expect: Tier-1 modules 25-yr perf guarantee; inverter >=5-yr product
  warranty [S5].

====================================================================
F. IMPLICATIONS FOR PENSOLAR POC (Director visibility)
====================================================================
- The 7-module framework (brief/solution_framework) directly maps: Module 2 = permit
  radar (pain #2,#6), Module 5 = procurement auto (pain #3, DEEP justified),
  Module 4 = PPA/CAPEX cashflow flex (pain #7), Module 6 = exec/contract clarity
  (pain #1), Module 7 = HR/utilization + O&M SLA (pain #5).
- Exception-driven dashboard must track: permit age vs SLA, procurement PO vs BOM due
  date, overdue commissions, warranty-claim age, RPVI/licence expiry.
- SelCo pivot means new quote templates + no-export sizing logic needed in P4/P5.

====================================================================
G. SOURCES
====================================================================
[S1] SEDA NEM 3.0 portal — seda.gov.my/reportal/nem
[S2] Northern Solar — northernsolar.com.my/from-roof-to-grid-commercial-solar-setup-in-malaysia
[S3] Trexon — trexon.my/installation-process
[S4] Bestar — bestar-asia.com/post/registered-solar-pv-investor-rpvi-in-malaysia
[S5] Homify — homifytech.com.my/solar-energy-services-in-malaysia-post-nem-3-0-guide-july-2025
[S6] Cleantech Law — cleantechlaw.com/2024/11/the-rising-wave-of-complaints-and-lawsuits-against-solar-companies
"""

# ---------------------------------------------------------------------------
# WRITE FILES + CAP GUARD
# ---------------------------------------------------------------------------
with open(LOG_PATH, "w", encoding="utf-8") as f:
    f.write(LOG)
print(f"LOG written: {LOG_PATH} ({len(LOG.encode('utf-8'))} bytes)")

with open(RAW_PATH, "w", encoding="utf-8") as f:
    f.write(RAW)
print(f"RAW written: {RAW_PATH} ({len(RAW.encode('utf-8'))} bytes)")

sum_bytes = len(SUMMARY.encode("utf-8"))
if sum_bytes > 32768:
    print("SUMMARY_CAP_HIT")
else:
    with open(SUM, "w", encoding="utf-8") as f:
        f.write(SUMMARY)
    print(f"SUMMARY written: {SUM} ({sum_bytes} bytes)")
