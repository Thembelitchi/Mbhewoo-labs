# CLAUDE.md — Mbhewoo Labs Project Context

This file tells Claude Code about the Mbhewoo Labs project. Read it at the start of every session.

---

## What this project is

Mbhewoo Labs is a **collaborative forecasting platform for African biomedical and biotechnology research credibility**. Researchers and domain experts pool their judgement on which scientific findings will hold up under replication, which clinical trials will progress through phases, and which emerging research directions will produce robust evidence.

The platform aggregates these forecasts into a continuously updated credibility signal across the research literature, with depth in HIV/TB vaccine research and breadth across computational biology, biotech, bioprocessing, and bioeconomy.

**It is not gambling, not betting on clinical trials, not a verdict mechanism, not a peer-review replacement, not a clinical decision tool.** It is meta-research using publicly available data, with researcher dignity protections built in.

## Project goals

- **Primary**: Build a demo-quality MVP to showcase at Bio Africa Convention (Durban, August 2026)
- **Secondary**: Translate the MVP into a fundable commercial product post-launch
- **Tertiary**: Serve as a portfolio piece demonstrating graph-native data infrastructure for African research credibility

## Who the user is

- **Name**: Thembelihle (Litchi) Gumede
- **GitHub**: Thembelitchi
- **Background**: Data Scientist, AI Consultant, Neo4j Community Lead for Southern Africa, founder of Graph Database Africa
- **Domain experience**: Over a decade as a Biomedical Technologist in Clinical Pathology, clinical research at Wits RHI, SAMRC, and the Desmond Tutu Health Foundation
- **Build context**: Solo founder, building evenings and weekends, Windows 10 + Anaconda + VS Code

## Critical conventions

### Always do

- **Write tests for the LMSR market maker and Seeds ledger.** These are credibility-critical. Math bugs and ledger bugs are unforgivable.
- **Use type hints everywhere.** Pydantic v2 for API schemas, SQLAlchemy 2.0 typed mappings for models.
- **Use async/await for all I/O.** FastAPI, SQLAlchemy, httpx, Neo4j driver — all async.
- **Keep the synthetic forecaster system feature-flagged.** A single config flag should flip between "demo mode" (with synthetic forecasters) and "live mode" (real only).
- **Tag every synthetic record** with `is_synthetic = True` so they can be removed cleanly later.
- **Use clear, descriptive variable names.** This code will be read by Litchi, future collaborators, and reviewed at Bio Africa.
- **Add docstrings** to non-trivial functions explaining the why, not just the what.
- **Reference the PRD section** when implementing a major feature (e.g. "implements PRD Section 8.1 — Seed earning").

### Never do

- **Never hardcode secrets.** All credentials via environment variables loaded by pydantic-settings.
- **Never commit `.env` files.** Only `.env.example` with placeholder values.
- **Never use floats for Seeds amounts.** Use integers (Seeds are whole numbers) or `Decimal` for LMSR pricing math. Floating-point errors compound silently and destroy ledger trust.
- **Never bypass the conflict-of-interest check** on predictions. Graph-enforced, no exceptions.
- **Never let a researcher predict on their own paper.** Block at the API layer and at the graph traversal layer (defence in depth).
- **Never expose individual forecaster predictions publicly without aggregation.** Defamation risk.
- **Never use Celery on this project.** Use APScheduler or simple background tasks via FastAPI's `BackgroundTasks`. Celery's Windows support is broken and we don't need its complexity.
- **Never assume the user knows obscure tool behaviour.** Litchi is a competent Python and graph person; she is new to FastAPI, HTMX, SQLAlchemy 2.0 async, and Alembic. Explain when introducing these.

## Tech stack (locked)

### Backend
- **Python 3.13** (via Anaconda, native Windows)
- **FastAPI** — async web framework
- **SQLAlchemy 2.0** with async support — Postgres ORM
- **Alembic** — database migrations
- **Pydantic v2** — data validation and settings management
- **Neo4j Python driver** (async) — graph database
- **httpx** — async HTTP client for external API calls
- **pytest** + **pytest-asyncio** — testing
- **APScheduler** — background scheduled jobs (NOT Celery)

### Frontend
- **Jinja2 templates** — server-side rendering
- **HTMX** — dynamic interactions without React
- **Tailwind CSS** via CDN initially, Tailwind CLI later
- **Alpine.js** — small client-side reactivity where HTMX falls short

### Cloud services
- **Supabase** — managed Postgres (project: mbhewoo-labs, region: Cape Town if available)
- **Neo4j AuraDB Free** — managed graph
- **Upstash Redis** — caching and rate limiting (defer until needed)
- **Resend** — transactional email (defer until needed)
- **Railway or Render** — app hosting (defer until ready to deploy)

### Tooling
- **uv** or **pip** — package management
- **ruff** — linting and formatting
- **pre-commit** — code quality hooks (defer until repo stable)

### Development environment
- Windows 10 Pro (no WSL)
- Anaconda Python distribution
- VS Code with Claude Code extension
- Anaconda Prompt for command line work

## Architecture decisions

1. **Monolith, not microservices.** One FastAPI app, one codebase, one deploy.
2. **Postgres for state, Neo4j for graph.** Postgres is source-of-truth; Neo4j syncs from it.
3. **Server-rendered HTML, not React.** HTMX gives 80% of the SPA experience with 20% of the complexity.
4. **Cloud databases only.** No local Postgres or Neo4j. Supabase and AuraDB from day one.
5. **DARPA SCORE as foundation dataset.** ~3,000 resolved replication markets imported as demo data.
6. **Synthetic African forecasters** for demo populated leaderboards. Easily removed for live launch.

## Folder structure

```
mbhewoo-labs/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings via pydantic-settings
│   ├── database.py          # Postgres + Neo4j connections
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic schemas (API contracts)
│   ├── routes/              # FastAPI route handlers
│   ├── services/            # Business logic (LMSR, Brier scoring, etc.)
│   ├── ingestion/           # External data clients (OpenAlex, PACTR, etc.)
│   ├── markets/             # LMSR market engine
│   ├── ledger/              # Seeds accounting (double-entry)
│   ├── graph/               # Neo4j operations and Cypher queries
│   ├── templates/           # Jinja2 HTML
│   └── static/              # CSS, JS, images
├── tests/                   # pytest tests
├── alembic/                 # Database migrations
├── scripts/                 # One-off scripts (seeding, imports, demos)
├── docs/                    # Internal docs
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── README.md
└── CLAUDE.md                # This file
```

## Core domain concepts

### Markets
A market is a binary, time-boxed forecasting question about a research claim, paper, or trial milestone. Examples:
- "Will the primary finding of [paper X] replicate by 2028?"
- "Will [trial Y] advance to Phase 3 by Q2 2027?"
- "Will [preprint Z] be accepted at a top-quartile journal within 18 months?"

Markets have a creator (admin in MVP), opens_at, closes_at, settles_at, resolution_source, and resolution_outcome.

### Seeds
The platform currency. Non-monetary, non-transferable, non-convertible. Forecasters earn Seeds through accurate predictions and spend them placing new positions. Starter endowment: 100 Seeds.

**Critical**: Seeds are integers. Never floats.

### Forecasters
Users who place predictions. Identified by verified ORCID iD or institutional email. Cannot predict on their own work or close collaborators' work (graph-enforced).

### Tiers
Five tiers based on track record (not Seed balance):
1. **Seedling** (0-50 resolved markets)
2. **Sapling** (50-200 resolved, Brier < 0.22)
3. **Rooted** (200-500 resolved, Brier in top 30% of domain)
4. **Mfukula** (500+ resolved, Brier in top 15%, well-calibrated) — verified expert
5. **Marula** (1000+ resolved, top 5% in domain, sustained 12+ months) — top tier

### Brier score
The accuracy metric. Squared deviation from outcome. Lower is better. 0.25 = random; below 0.18 = genuinely accurate. Tracked per domain, recency-weighted.

### LMSR
Logarithmic Market Scoring Rule. The market maker mechanism, from Robin Hanson (2003). Same parameters as DARPA SCORE: b = 100, 100-Seed starter endowment.

Key formulas:
- Cost function: `C(q) = b * ln(e^(q_yes/b) + e^(q_no/b))`
- Price of Yes: `p_yes = e^(q_yes/b) / (e^(q_yes/b) + e^(q_no/b))`
- Cost to move from q to q': `ΔC = C(q') − C(q)`

Maximum maker loss per binary market: `b * ln(2) ≈ 69 Seeds`.

### Domains (MVP)
1. HIV and TB vaccines and prevention (core focus)
2. Computational biology and bioinformatics
3. Biotech and pharmaceutical sciences
4. Bioprocessing
5. Bioeconomy and translational research

## Data sources (all free APIs)

1. **OpenAlex** — paper metadata, citations, authors, institutions (~250M works)
2. **PACTR** — Pan African Clinical Trials Registry (SAMRC-hosted)
3. **ClinicalTrials.gov** — global trials registry
4. **SANCTR** — South African National Clinical Trial Register
5. **Crossref** — DOI metadata, publication status
6. **Retraction Watch** — retraction signals
7. **Semantic Scholar** — AI-enhanced bibliographic data
8. **DARPA SCORE archive** — ~3,000 resolved replication markets

All sources have free tiers sufficient for MVP. No paid APIs in the budget.

## Ethics and legal posture

- **Not gambling**: no cash in/out, Seeds non-convertible. Falls outside SA National Gambling Act.
- **Not human-subjects research**: meta-research using publicly available data. NHREC/HREC ethics approval not required.
- **POPIA-compliant**: explicit consent, right to export/delete, data retention policy.
- **Defamation mitigation**: forecasts framed as forecasts not judgements, right-of-reply for subject researchers, opt-out available.
- **Public health responsibility**: no markets on intervention efficacy until results formally published. Plain-language disclaimers on every public confidence score.

## Working style preferences

### When generating code
- Show me the file structure before writing files
- Write one logical unit at a time, then pause for review
- Run tests after writing testable code
- If something is ambiguous, ask before assuming
- Use Litchi's domain knowledge — she has decades of clinical research experience; ask her about resolution criteria, methodology choices, edge cases

### When explaining
- Brief and direct
- Show, don't tell — code examples over abstract description
- Flag genuine risks honestly; don't sugarcoat
- If I'm about to make a mistake, push back

### When stuck
- Web search for current best practice (libraries change)
- Check the official docs, not Stack Overflow first
- If multiple valid approaches exist, present trade-offs and let Litchi decide

## Current status

- **PRD**: v1.0 complete, see `docs/PRD.docx`
- **Setup**: Python 3.13 via Anaconda installed, Git installed, VS Code with Claude Code extension ready
- **Cloud accounts**: Supabase account exists. Neo4j AuraDB pending. Anthropic Console pending (or Pro subscription used).
- **GitHub repo**: pending creation
- **First file written**: none yet (this CLAUDE.md is the first)

## Bio Africa demo target

- **Event**: Bio Africa Convention, Durban, August 2026 (~12 weeks from project start)
- **Audience**: SAMRC, IAVI, HVTN, Wellcome Africa, Gates Foundation, Gilead, EDCTP, African Academy of Sciences
- **Demo deliverable**: working web app at app.mbhewoolabs.com with DARPA SCORE foundation data, 20-50 live markets, 50-100 synthetic + 10-20 real forecasters, working LMSR engine, Brier scoring, leaderboards, graph-powered conflict detection, Letter of Accuracy PDF download

## Key references

- Hanson (2003) — Logarithmic Market Scoring Rules
- Dreber et al. (2015) — Using prediction markets to estimate reproducibility
- DARPA SCORE / Royal Society Open Science (2020) — Replication rates across academic fields
- Open Science Collaboration (2015) — Estimating reproducibility of psychological science
- NHREC Ethics Guidelines, 3rd ed. (2024)

---

**End of CLAUDE.md. Welcome to Mbhewoo Labs. Let's build something that helps African research.**
