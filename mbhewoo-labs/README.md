# Mbhewoo Labs MVP

Collaborative credibility forecasting platform for African biomedical and biotechnology research.

Researchers, authors, and biotechnology domain experts pool their judgment/predictions on whether specific biomedical research findings (clinical trial outcomes, drug discovery publications, bioprocessing yield reports, and biotech claims) will successfully reproduce or hold up upon verification or peer-review. This generates a continuous credibility signal for research funders, corporate sponsors, and publishers.

## Project Structure

```
mbhewoo-labs/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings via pydantic-settings
│   ├── database.py          # SQLAlchemy + Neo4j connection setup
│   ├── models/              # SQLAlchemy database models
│   │   └── __init__.py
│   ├── schemas/             # Pydantic schemas (request/response)
│   │   └── __init__.py
│   ├── routes/              # FastAPI route handlers
│   │   ├── __init__.py
│   │   └── health.py        # Health metrics and status routes
│   ├── services/            # Core business logic layer
│   │   └── __init__.py
│   ├── ingestion/           # External academic indexing clients (e.g., OpenAlex)
│   │   └── __init__.py
│   ├── markets/             # Logarithmic Market Scoring Rule (LMSR) forecasting engine
│   │   └── __init__.py
│   ├── ledger/              # Seed token & trade balance accounting ledger
│   │   └── __init__.py
│   ├── graph/               # Neo4j graph traversal and co-citation operations
│   │   └── __init__.py
│   ├── templates/           # Jinja2 server-rendered HTML components
│   │   └── base.html        # Base site layout styled with Tailwind CSS & embedded HTMX
│   └── static/              # Static media assets, stylesheets, and client-side scripts
├── tests/
│   ├── __init__.py
│   └── test_health.py       # Pytest suite targeting health routes
├── alembic/                 # Alembic migration environment (configured in next session)
├── scripts/                 # Administration and setup helpers
├── .env.example             # Environment configuration template
├── .gitignore               # Python execution ignores
├── pyproject.toml           # PEP 621 metadata, dependencies & dev tool settings
└── requirements.txt         # Replicable environment lock list 
```

## Quick Start (Local Setup)

1. **Prerequisites**: Python 3.13 and [Anaconda](https://www.anaconda.com/) or typical virtualenv setups.
2. **Clone and Configure**:
   ```bash
   cp .env.example .env
   # Update variables in .env as needed
   ```
3. **Environment Setup**:
   Using `venv`:
   ```bash
   python -m venv .venv
   source .env/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. **Run the Server**:
   ```bash
   uvicorn app.main:app --reload
   ```
   Open `http://localhost:8000/health` to confirm the installation!

5. **Run the Test Suite**:
   ```bash
   pytest
   ```
