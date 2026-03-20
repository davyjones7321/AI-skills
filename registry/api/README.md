# Registry Backend API

## Overview
The FastAPI registry backend provides the central hub for discovering, publishing, and managing AI skills. It serves as the authoritative source for skill metadata, enabling users to search the public registry and download the latest skill versions.

## Requirements
Python 3.10+, pip packages: `fastapi`, `uvicorn`, `sqlalchemy`, `pydantic-settings`, `pyyaml`

## Setup
1. `cd registry/api`
2. `pip install fastapi uvicorn sqlalchemy pydantic-settings pyyaml`
3. Copy `.env.example` to `.env` and configure tokens
4. `python -m registry.api.seed` to seed the database
5. `uvicorn registry.api.main:app --reload` to start the server
6. Visit `http://localhost:8000/docs` for interactive API docs

## Auth
Set `API_TOKENS` in `.env` as a JSON dict mapping tokens to usernames, e.g. `{"dev-token-aiskills": "ai-skills-team"}`. Note that GitHub OAuth replaces this in production.

## Endpoints
| Method | Path | Auth Required | Description |
|--------|------|---------------|-------------|
| GET | `/skills/` | No | List all skills with pagination |
| GET | `/skills/search` | No | Search skills by name, description, tag, or execution type |
| POST | `/skills/` | Yes | Publish a new skill to the registry |
| GET | `/skills/{author}/{skill_id}` | No | Get the latest version of a skill by author and ID |
| GET | `/skills/{author}/{skill_id}/{version}` | No | Get a specific version of a skill |
| DELETE | `/skills/{author}/{skill_id}/{version}` | Yes | Yank (delete) a specific version of a skill |
| GET | `/health` | No | Health check endpoint |

## Environment Variables
| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Database connection URL |
| `ENVIRONMENT` | Environment mode |
| `SECRET_KEY` | Secret key for operations |
| `REGISTRY_URL` | The public URL of the registry |
| `GITHUB_CLIENT_ID` | GitHub OAuth client ID |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth client secret |
| `API_TOKENS` | JSON dictionary mapping tokens to usernames |

## Known Limitations (MVP)
- no rate limiting
- SQLite only
- token auth not GitHub OAuth
- tag filtering is post-processed in Python
