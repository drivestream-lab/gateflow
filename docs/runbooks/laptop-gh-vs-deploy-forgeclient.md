# Laptop `gh` vs deploy ForgeClient (FR-26b)

## Split

| Context | Transport | Who decides *what* to seed |
|---------|-----------|----------------------------|
| **Laptop / engineer machine** | Local `gh` **may** be used by skills such as `board-seed` | board-seed / PE judgment remains SSOT |
| **Gateflow deploy (API + worker)** | **ForgeClient only** (GitHub REST; credential mode per INIT-001 TDD §3.5a — production must resolve to App) | Callers of `/api/v1/board/*` supply fields; Gateflow does not parse WorkManifest |

Gateflow runtime does **not** enforce laptop policy and must **not** shell to `gh`
on the production path (FR-25 / FR-26a). This document does **not** replace or
delete the board-seed skill.

## Board APIs (dumb apply)

Programme-token routes under `/api/v1/board` (see TDD §3.3):

- `PATCH /api/v1/board/tickets/{ticket_id}/status`
- `POST /api/v1/board/tickets/{ticket_id}/links`
- `POST /api/v1/board/tickets` (EPIC/Feature idempotent on `initiative_id` + type)
- `GET /api/v1/board/tickets` (narrow filters: `initiative_id`, `type`, `state`, `org`, `repo`)

Optional header `Idempotency-Key` on create. Partial failures return `partial: true`
with `created_resources` / `failed_resources`.

**Wave worker must never call these APIs** (or equivalent ForgeClient board
mutations) on start/finish.

## Production path check (FR-25 / FR-26a)

1. Confirm `APP_ENVIRONMENT=production` rejects effective auth mode `pat` /
   `GITHUB_PERSONAL_ACCESS_TOKEN` use (ADR-003; INIT-001 TDD §3.5a).
2. Confirm `GITHUB_AUTH_MODE=app` in production (explicit; no `auto`).
3. Confirm `src/infra_services/forge_client.py` has no `subprocess` / `gh` CLI invocation
   (`make test` → `test_forge_client_source_has_no_gh_subprocess`).
4. Confirm board + PR/comment writes go through `httpx` REST only.

## Live verify

```bash
set -a && source .env && set +a
.venv/bin/python -m tests.verify.verify_board
# or
.venv/bin/python -m tests.verify.verify_all
```

Forge-backed create/list/status/link requires outbound credentials for the
**configured** mode (`GITHUB_AUTH_MODE=pat` + PAT, or `=app` + App mint).
Without matching credentials, startup or verify must fail fast — no mode inference.
