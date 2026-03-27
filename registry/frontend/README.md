# ai-skills Registry Frontend

Next.js frontend for the ai-skills public registry.

## What Is Implemented

- Persistent app shell with sticky header, mobile nav, and footer
- Homepage (`/`) with:
  - Hero + search
  - Live skill stats
  - Execution-type summary cards
  - Recently published skills
  - Publishing/get-started CTAs
- Browse page (`/skills`) with:
  - Debounced search (URL-driven)
  - Filters: execution type, tag, sort
  - Pagination
  - Loading, empty, and error states
- Skill detail page (`/skills/[author]/[id]`) with:
  - Metadata header + install command
  - Tabs: Overview, Benchmarks, YAML Source, Versions
  - Copy buttons, loading skeleton, and not-found state
- Publish guide (`/publish`) with step-by-step CLI workflow

## Development

From `registry/frontend`:

```bash
npm install
npm run dev
```

Open `http://localhost:3000`.

## API Configuration

Set backend base URL with:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

If not set, the frontend falls back to `http://localhost:8000`.

For the hosted deployment, set:

```bash
NEXT_PUBLIC_API_URL=https://ai-skills-production-f4f0.up.railway.app
```

The backend CORS configuration allows requests from `https://ai-skills-omega.vercel.app`.

## Required Backend Endpoints

- `GET /skills`
- `GET /skills/search`
- `GET /skills/tags`
- `GET /skills/{author}/{id}`
- `GET /auth/me` (used when signed-in flows are wired)

## Type Checking

```bash
npx tsc --noEmit
```
