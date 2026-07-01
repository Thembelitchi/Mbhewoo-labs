# AI Studio Prototype (archived)

This directory holds the original **Google AI Studio** export for Mbhewoo Labs —
a React + Vite + Tailwind landing page generated early in the project.

It is **archived for design reference only** and is not part of the running
application. The production stack is server-rendered per `CLAUDE.md`:

> Server-rendered HTML, not React. HTMX gives 80% of the SPA experience with
> 20% of the complexity.

The live frontend is built with **Jinja2 + HTMX + Tailwind + Alpine.js** under
`app/templates/` and `app/static/`. Nothing here is imported by the FastAPI app.

## Contents

- `src/App.tsx` — the generated landing/scaffold page (~1,200 lines)
- `index.html`, `main.tsx`, `index.css` — Vite entry points
- `package.json`, `vite.config.ts`, `tsconfig.json` — Node/Vite tooling
- `metadata.json` — AI Studio app metadata
- `assets/` — static assets from the export

## Running it (optional, reference only)

```bash
cd docs/ai-studio-prototype
npm install
npm run dev
```

Requires a `GEMINI_API_KEY` in a local `.env` if you exercise the Gemini calls.
