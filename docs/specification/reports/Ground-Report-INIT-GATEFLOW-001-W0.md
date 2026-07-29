# Ground report — INIT-GATEFLOW-001 W0

| Field | Value |
|-------|-------|
| Wave | W0 — Control plane skeleton |
| Spec | `docs/specification/product/INIT-GATEFLOW-001-gateflow.md` |
| Date | 2026-07-23 |
| Branch | `feature/INIT-GATEFLOW-001-w0-control-plane` |
| Status | **human_approved** |
| Review deadline | 2026-07-27 |
| Deciders | Tech lead / reviewer: @nikd10x — human LGTM recorded 2026-07-23 (live verify green) |


> **Living supersession (config carrier):** `config/programme.yaml` / YAML `ProgrammeConfig` load are **removed**. Live authority is env (`GATEFLOW_*`), wave-start API, and pin `workflow.yaml` — ADR-004, INIT-002 A-7, as-built, and `docs/specification/reports/README.md`. Mentions below are wave-time evidence only.

## Automated check output

`ground_command`: N/A (no Makefile ground target). Evidence: `make check`, `make test`, live `verify_all`.

### `make check` / `make test`

Prior ground run: exit 0 (24 unit tests). Re-run before merge if uncommitted enqueue/verify fixes are included.

### Live verify `.venv/bin/python -m tests.verify.verify_all`

Human-confirmed **pass** on 2026-07-23 after:

- RunStore Alembic revision applied (`36b36d3d4fc9_first_version`)
- Org GitHub App `gateflow-dev` (App ID `4374982`) + `GITHUB_WEBHOOK_SECRET` in `.env`
- Fix: `BasePostgresRepository.create` includes Pydantic defaults (`exclude_unset=False`) so `jobs.status_type` persists as `pending`
- Aggregator: `verify_health` then `verify_webhook` (401 / 202 / duplicate 202)

## FR checklist

W0 scope (plan §1–§2): FR-1, FR-5, FR-6, FR-7 (resolve only), FR-12 (comments + forbid), FR-17 (partial worker), FR-18.

| FR | Spec claim | Verified artifact | Status |
|----|-----------|-------------------|--------|
| FR-1 | Webhook signature + idempotency + enqueue; 401/503 | `POST /webhooks/github`; live `verify_webhook` / `verify_all` | **pass** |
| FR-5 | Postgres RunStore (runs/stages/events/jobs) | ORM + repos + applied migration `36b36d3d4fc9` | **pass** |
| FR-6 | HandoffReader (ref + globs) | unit fixtures | **pass** (unit) |
| FR-7 | WorkflowEngine resolve next node (no dispatch) | unit against pin | **pass** (resolve-only; PolicyEngine W1) |
| FR-12 | ForgeClient comments; forbid gate labels/auto-merge | unit forbid tests | **pass** (unit/inspection) |
| FR-17 | API + async worker; job claim | worker stub + unit claim | **partial** — stub only; live worker/docker deferred (D-W0-V2) |
| FR-18 | Programme config load fail-fast | unit missing/invalid | **pass** |

Out-of-wave (W1 — expected fail/not started): FR-2–4, FR-8–11, FR-13–16, FR-19.

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Dual process API + worker; jobs in Postgres | ADR-001 | **pass** (code); live worker claim deferred |
| Webhook on `public_paths`; signature zone | ADR-002 | **pass** |
| ForgeClient infra; handoff/workflow business | ADR-003 | **pass** |
| Programme/runtime config fail-fast (living: env settings) | ADR-004 | **pass** (wave used YAML; carrier later removed — see supersession) |
| Models in `src/models/`; repos map ORM→Pydantic | pydantic-schemas / repository-pattern | **pass** |
| import-linter layers | python-tooling | **pass** |
| Human-owned Alembic revisions | database-migrations | **pass** — first RunStore revision applied |
| Fail-fast missing programme config / webhook secret | fail-fast / ADR-002 | **pass** |

## Discrepancies

| ID | FR | Finding | Severity | Resolution |
|----|----|---------|----------|------------|
| D-W0-M1 | FR-5 | Human Alembic revision missing | Critical | **cleared** — revision applied |
| D-W0-V1 | FR-1 | Live `verify_webhook` not green | Critical | **cleared** — `verify_all` human pass |
| D-W0-V2 | FR-17 | Live worker claim vs docker-compose not executed | Medium | **accepted deferral** to W1 / ops soak |

## Contracts produced by this wave

Usable as W1 `/pre-implement` baseline.

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Programme/runtime config load (wave: YAML; living: env — see supersession) | programme config loader + models (wave) / `OrchestrationSettings` (living) | startup load | YAML path (wave) / env (living) | Validated knobs | Missing/invalid fails start | W1 |
| Webhook enqueue | webhook ingress + route | `enqueue_webhook_job` / `POST /webhooks/github` | delivery id, event, payload, sig | job id or duplicate no-op; 401/503 | Idempotent on delivery id | W1 TriggerRouter |
| Job claim stub | job worker + worker entry | `claim_and_process_one` | pending jobs | claimed then processed (stub) | SKIP LOCKED; no agent dispatch | W1 RunOrchestrator |
| RunStore persistence | schema + repositories | create/enqueue/claim/mark_* | Pydantic create DTOs | Pydantic models | Create dumps include defaults | W1 status/metrics |
| Handoff read | HandoffReader | resolve / find / parse | workspace + globs | HandoffEnvelope | No chat fallback | W1 PolicyEngine |
| Workflow resolve | WorkflowEngine | `load_pin` / `resolve_next` | stage+outcome + pin | ResolvedWorkflowNode | No hardcoded allowlists | W1 PolicyEngine |
| Forge comments | ForgeClient | `post_comment`; forbid labels/auto-merge | owner/repo/issue + body | comment id | No gate labels; no auto-merge | W1 Notifier |

## PR instructions

Branch:   `feature/INIT-GATEFLOW-001-w0-control-plane`
PR title: `[INIT-GATEFLOW-001 W0] control-plane — implementation + ground report`
Required reviewer: prayog-pe-team / CODEOWNERS

After merge:
  → `/pre-implement` for W1

## Ready for human checkpoint?

**yes — human_approved** (2026-07-23). Live `verify_all` green; D-W0-M1/D-W0-V1 cleared; D-W0-V2 deferred.

- [x] Review FR checklist — W0 FRs pass or explicitly deferred (FR-17 live worker)
- [x] Review §Contracts produced — baseline for W1
- [x] Mark as-built: INIT-GATEFLOW-001 W0 = human_approved

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: human_approved
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-001-W0.md
    digest: sha256:f2b9f5a52bc89eafb14efc9074ff1b0a6bf02c11b4d4f1ca84da8da7d02759fb
  blockers: []
  signals:
    wave: W0
    contracts_produced: 7
    wave_code_complete: true
    unit_pass: true
    live_verify_pass: true
    human_migration_applied: true
    verify_command: .venv/bin/python -m tests.verify.verify_all
    board_issue: https://github.com/drivestream-lab/gateflow/issues/6
    branch: feature/INIT-GATEFLOW-001-w0-control-plane
  next_candidates:
    - pre-implement
  human_checkpoint: true
  external_action: false
```
