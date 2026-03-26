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
GitHub OAuth authentication is used for the registry. The API_TOKENS env variable acts as an administrator fallback if needed.

## Endpoints
| Method | Path | Auth Required | Description |
|--------|------|---------------|-------------|
| GET | `/skills/` | No | List all skills with pagination |
| GET | `/skills/tags` | No | Return deduplicated tag list across all published skills |
| GET | `/skills/search` | No | Search skills by name, description, tag, or execution type |
| POST | `/skills/` | Yes | Publish a new skill to the registry |
| GET | `/auth/github` | No | Redirect to GitHub OAuth login |
| GET | `/auth/github/callback` | No | GitHub OAuth callback |
| GET | `/auth/me` | Yes | Get the currently logged-in user profile |
| POST | `/auth/logout` | No | Stateless logout acknowledgement |
| GET | `/skills/{author}/{skill_id}` | No | Get the latest version of a skill by author and ID |
| GET | `/skills/{author}/{skill_id}/{version}` | No | Get a specific version of a skill |
| DELETE | `/skills/{author}/{skill_id}/{version}` | Yes | Yank (delete) a specific version of a skill |
| GET | `/health` | No | Health check endpoint |

### Response shape highlights

- List/search endpoints return:
  - `{ skills, total_count, page, limit }`
- Skill detail endpoints return:
  - top-level metadata (`id`, `author`, `version`, `name`, `description`, etc.)
  - raw `yaml_content`
  - parsed fields from YAML: `inputs`, `outputs`, `execution`, `compatible_with`

### Query parameters

- `GET /skills/`
  - `page` (default `1`)
  - `limit` (default `20`, max `100`)
  - `sort` (`newest`, `most_downloaded`, `lowest_latency`)
- `GET /skills/search`
  - `q` (optional text query)
  - `tag` (optional exact tag)
  - `type` (`prompt`, `tool_call`, `code`, `chain`)
  - `page`, `limit`
  - `sort` (`newest`, `most_downloaded`, `lowest_latency`)

## Environment Variables
| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Database connection URL |
| `ENVIRONMENT` | Environment mode |
| `SECRET_KEY` | Secret key for operations |
| `REGISTRY_URL` | The public URL of the registry |
| `FRONTEND_URL` | The frontend app URL used after OAuth completes |
| `GITHUB_CLIENT_ID` | GitHub OAuth client ID |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth client secret |
| `JWT_SECRET` | Secret used to sign and verify registry JWTs |

## Known Limitations (MVP)
- no rate limiting
- SQLite only
- tag filtering is post-processed in Python
- sorting is currently done in-memory for MVP simplicity
