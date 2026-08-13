# PENSOLAR — Solution Framework (POC architecture)

Mental-model: **AI as the backbone that turns operational noise → director-grade signal.**

## Layers
```
1. CAPTURE layer      — project/permit/procurement/HR events entered once, anywhere
2. UNIFY layer        — single data model (no silos): Project ↔ Task ↔ Vendor ↔ People ↔ Money
3. SIGNAL layer (AI)  — agent flags exceptions, late permits, stalled procurement, low utilization
4. VISIBILITY layer   — Director dashboard: red/amber/green by exception, NOT raw lists
5. ACTION layer       — auto-draft PO, auto-summarize week → exec doc, auto-assign workforce
6. LEARN layer        — cron pulls solar/PM benchmarks → refines what "good" looks like
```

## Modules (7, mapped to Director's ask)
| # | Module | POC depth | Key AI assist |
|---|--------|-----------|---------------|
| 1 | Project Management | framework+deep | timeline risk flag, blocker detection |
| 2 | Admin Overview | framework | doc/permit status radar |
| 3 | Accounting Summary | framework | P&L roll-up from entries |
| 4 | Financial Control | framework | PPA cashflow vs CAPEX model |
| 5 | Procurement Auto | **DEEP** | PO draft from BOM, vendor compare, delay alert |
| 6 | Exec Reports | framework+deep | weekly → board-ready doc (the "wow") |
| 7 | HR Arrangement | framework | site allocation, utilization heatmap |

## Why this impresses (without overbuilding)
- Director opens ONE screen → sees only what needs attention.
- "Ask the system" in plain language → gets answer from live data (RAG over the unify layer).
- Weekly: auto-generated executive PDF he can forward to stakeholders.

## Tech posture (free-tier friendly)
- Local-first data (SQLite/JSON) → no vendor lock.
- AI layer: Nous/OpenRouter free models for summarization + agent flags.
- Reports: reportlab (already available) for executive PDF.
- No paid API unless client scale demands (propose then).

## Next build step
Scaffold the unify-layer data model + visibility dashboard mock, then deepen
procurement + exec-report modules. (Awaiting user "go" per phase.)
