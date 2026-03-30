# Web Publishing Status

## Completed

- Added shared category constants in `registry/api/categories.py` so the web publish flow can use the fixed 12-category taxonomy.
- Added a nullable `category` column migration in `registry/api/database.py` and persisted category on the `Skill` model in `registry/api/models.py`.
- Updated `registry/api/schemas.py` so skill payloads and responses include optional `category`, with category validation.
- Reworked `POST /skills` in `registry/api/routers/skills.py` to:
  - keep authenticated JSON publishing working for the CLI
  - accept authenticated multipart uploads with a `file` field containing raw `skill.yaml`
  - parse YAML, validate required skill structure, validate execution-specific fields, and override author from the authenticated GitHub user
  - return `422` with clear validation messages and `409` for duplicate versions
- Added `python-multipart` to `requirements.txt` for multipart form parsing.
- Added frontend category definitions in `registry/frontend/lib/skill-categories.ts`.
- Extended frontend skill types and API helpers in `registry/frontend/lib/types.ts` and `registry/frontend/lib/api.ts`, including a publish helper and better surfaced backend error messages.
- Replaced the static `/publish` guide with a real interactive publish flow in `registry/frontend/app/publish/page.tsx` and `registry/frontend/components/registry/publish-studio.tsx`.
- Built the two-tab publish experience:
  - `Upload YAML` with auth gate, drag-and-drop file picker, preview, publish action, inline backend errors, and success state
  - `Build Form` with client-side validation, YAML preview generation, publish action, and shared success/error handling
- Added reusable client-side publishing helpers and tests in `registry/frontend/lib/publish-utils.ts` and `registry/frontend/tests/unit/publish-utils.test.ts`.
- Updated `registry/frontend/components/layout/site-header.tsx` to add a prominent Publish button that links to `/publish` for logged-in users and `/login?next=/publish` otherwise.
- Updated `registry/frontend/components/registry/skill-detail-view.tsx` to show an `Unreviewed` badge when `reviewed` is `false`.

## Files Touched

- `WEB_PUBLISHING_STATUS.md`
- `requirements.txt`
- `registry/api/categories.py`
- `registry/api/database.py`
- `registry/api/models.py`
- `registry/api/routers/skills.py`
- `registry/api/schemas.py`
- `registry/frontend/app/publish/page.tsx`
- `registry/frontend/components/layout/site-header.tsx`
- `registry/frontend/components/registry/publish-studio.tsx`
- `registry/frontend/components/registry/skill-detail-view.tsx`
- `registry/frontend/lib/api.ts`
- `registry/frontend/lib/publish-utils.ts`
- `registry/frontend/lib/skill-categories.ts`
- `registry/frontend/lib/types.ts`
- `registry/frontend/package.json`
- `registry/frontend/tests/unit/publish-utils.test.ts`

## Verification

- `npm run test` in `registry/frontend`: passed
- `npm run lint` in `registry/frontend`: passed
- `npm run build` in `registry/frontend`: passed
- Backend bytecode/manual verification could not be completed in this shell because `py` exists but no installed Python runtime is available.
- Manual OAuth login and end-to-end publish testing could not be completed from this environment for the same reason.
