# Mbhewoo Labs

**A collaborative forecasting platform for African biomedical and biotechnology research credibility.**

Researchers and domain experts pool their judgement on which scientific findings
will hold up under replication and which clinical trials will progress through
phases. The platform aggregates these forecasts into a continuously updated
credibility signal across the research literature — with depth in HIV/TB vaccine
research and breadth across computational biology, biotech, bioprocessing, and
bioeconomy.

> It is **not** gambling, not betting on clinical trials, not a verdict
> mechanism, and not a peer-review replacement. It is meta-research using
> publicly available data, with researcher-dignity protections built in.

See [`CLAUDE.md`](CLAUDE.md) for the full project context, domain model, and
conventions.

## Tech stack

- **Backend**: Python 3.13, FastAPI (async), SQLAlchemy 2.0 (async), Alembic
- **Data**: Postgres (Supabase) for state, Neo4j (AuraDB) for the graph
- **Frontend**: Jinja2 + HTMX + Tailwind + Alpine.js (server-rendered, not React)
- **Validation/config**: Pydantic v2 + pydantic-settings
- **Testing**: pytest + pytest-asyncio
- **Scheduling**: APScheduler (not Celery)

## Project layout

```
app/
  config.py       # settings via pydantic-settings (.env)
  database.py     # async Postgres engine + Neo4j driver
  main.py         # FastAPI app, lifespan, routers
  routes/         # HTTP route handlers (health, ...)
  models/         # SQLAlchemy ORM models
  schemas/        # Pydantic API contracts
  services/       # business logic (LMSR, Brier scoring, ...)
  markets/        # LMSR market engine
  ledger/         # Seeds accounting (double-entry)
  graph/          # Neo4j operations and Cypher
  ingestion/      # external data clients (OpenAlex, PACTR, ...)
  templates/      # Jinja2 HTML
  static/         # CSS, JS, images
tests/            # pytest tests
alembic/          # database migrations
scripts/          # one-off scripts (seeding, imports, demos)
docs/             # internal docs (incl. archived AI Studio prototype)
```

## Getting started (Windows 10 + Anaconda)

Open **Anaconda Prompt**:

```bat
:: 1. Create and activate an environment
conda create -n mbhewoo python=3.13 -y
conda activate mbhewoo

:: 2. Install dependencies
pip install -r requirements.txt

:: 3. Create your local env file and fill in credentials
copy .env.example .env

:: 4. Run the app (auto-reload)
uvicorn app.main:app --reload
```

Then visit:

- http://127.0.0.1:8000/         — welcome payload
- http://127.0.0.1:8000/health   — health check
- http://127.0.0.1:8000/docs     — interactive Swagger UI

`DATABASE_URL` and `NEO4J_*` may be left blank during early development — the app
starts without them.

## Testing

```bat
pytest
```

## Notes

- `docs/ai-studio-prototype/` contains the original Google AI Studio React export,
  kept as a design reference only. It is not part of the running application.
