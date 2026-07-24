# Ground report — INIT-GATEFLOW-002 W2

| Field | Value |
|-------|-------|
| Wave | W2 — Board APIs + gh-free deploy path |
| Spec | `docs/specification/product/INIT-GATEFLOW-002-gateflow.md` |
| Date | 2026-07-24 |
| Branch | `feature/INIT-GATEFLOW-002-w2-board` |
| Status | Draft |
| Review deadline | 2026-07-28 |
| Deciders | Tech lead / reviewer: @nikd10x — explicit LGTM required |

## Automated check output

`ground_command`: N/A. Evidence: `make check`, `make test`, `.venv/bin/python -m tests.verify.verify_all` (shared `drivestream-postgres` / `drivestream-redis`; gateflow API on `:8080` during loop-spec verify).

Commit under review: `dec19bf` (+ this ground report commit).

### `make check` (exit 0)

```
.venv/bin/black --line-length 100 src/ tests/
All done! 136 files left unchanged.
.venv/bin/ruff check --fix src/ tests/
All checks passed!
.venv/bin/pyright
0 errors, 0 warnings, 0 informations
.venv/bin/lint-imports
Layered architecture — no cross-layer imports KEPT
Contracts: 1 kept, 0 broken.
```

### `make test` (exit 0)

```
collected 76 items
76 passed
```

### Live verify `.venv/bin/python -m tests.verify.verify_all` (exit 0)

Recorded during `/loop-spec` on 2026-07-24 (API restarted with W2 code):

```
[OK] verify_health passed
[OK] verify_webhook passed
[OK] verify_status_metrics passed
[OK] verify_wave_start passed
[OK] verify_pr_thread passed (PR live assert skipped without GATEFLOW_VERIFY_WORKER=1)
[OK] verify_board passed
     — GET /api/v1/board/tickets without token → 401
     — PATCH empty status fields → 400
     — forge mutations skipped (GITHUB_PERSONAL_ACCESS_TOKEN unset)
[OK] verify_all passed
```

## FR checklist

W2 plan scope: FR-24 board dumb primitives; FR-25 / FR-26a production `gh`-free; FR-26b laptop policy docs; Q-4 exit gate. Prior-wave FRs remain in force.

| FR | Spec claim | Verified artifact | Status |
|----|-----------|-------------------|--------|
| FR-15…23 | Inherited W0/W1 control plane | Prior Ground Reports + live `verify_all` (non-board steps) | **pass** (inherited) |
| FR-24 | Board APIs: status, link, create, list; EPIC/Feature idempotent; Idempotency-Key; partial-failure body; worker must not invoke | `board_routes.py` TDD §3.3 paths; `BoardService`; ForgeClient `board_*`; `test_board_service` (idempotent + partial); `test_process_job_never_calls_board_forge_mutations`; live `verify_board` auth/400 | **pass** (unit + live auth/validation); **partial live forge** — create/list/status/link need PAT (see D-W2-V1) |
| FR-25 | Production forge path via ForgeClient only; no `gh` CLI | `test_forge_client_source_has_no_gh_subprocess`; PAT rejected in production (`_resolve_token`); checklist `docs/runbooks/gh-free-production-path-checklist.md` | **pass** (unit + inspection) |
| FR-26a | Deployed board/forge apply uses ForgeClient only | BoardService → ForgeClient only; same source guard as FR-25 | **pass** |
| FR-26b | Document laptop `gh` vs deploy ForgeClient; do not replace board-seed | `docs/runbooks/laptop-gh-vs-deploy-forgeclient.md` | **pass** (inspection) |
| Q-4 / A-4 | App/Projects permission matrix before W2 exit | Narrowed Issues MVP documented: `docs/specification/reports/Q4-PERMISSION-MATRIX-INIT-GATEFLOW-002-W2.md` | **pass** (exit via narrow MVP — Projects not required) |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Board I/O in ForgeClient (infra); BoardService = business; routes thin | ADR-003 / architecture | **pass** |
| Programme-token on board mounts; `/api/v1/board` on `public_paths` | ADR-005 | **pass** |
| No WorkManifest / governance parsing in board APIs | product FR-24 | **pass** — caller-supplied fields only |
| Worker / orchestrator never calls board ForgeClient mutations | FR-24 | **pass** — unit isolation audit |
| No auto-merge / gate-approval labels | ADR-003 | **pass** — forbid methods unchanged |
| Models in `src/models/` only | pydantic-schemas | **pass** — `board_models.py` |
| Import-linter layers | python-tooling | **pass** |
| Structured logging kwargs (`operation=board_*`) | logging-loguru | **pass** |
| No agent Alembic in W2 | database-migrations | **pass** — forge-backed Issues MVP |

## Cross-spec contracts consumed

Source: `Ground-Report-INIT-GATEFLOW-002-W1.md` §Contracts produced.

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Programme-token AuthN + public_paths pattern | Ground-Report-002-W0/W1 | yes — extended with `/api/v1/board` |
| Forge PR open/update + comments | Ground-Report-002-W1 | yes — unchanged; board ops added alongside |
| Forbidden forge side effects | Ground-Report-002-W1 | yes |
| PR-at-run-start / orchestrator | Ground-Report-002-W1 | yes — still no board link/status from worker |
| Per-node model resolve / metrics dims | Ground-Report-002-W1 | yes — unchanged |
| Cursor stub path | Ground-Report-002-W1 | yes — SDK still deferred (not W2) |
| DI ForgeClient singleton | Ground-Report-002-W1 | yes — BoardService injects ForgeClient |

## Discrepancies (must fix before human checkpoint)

| ID | FR | Finding | Severity |
|----|----|---------|----------|
| D-W2-V1 | FR-24 | Live `verify_board` asserts 401 + 400 without forge token; full create/list/status/link live path skipped when `GITHUB_PERSONAL_ACCESS_TOKEN` unset (unit owns ForgeClient board methods) | Medium — accept for W2 exit if PE accepts Issues MVP + unit coverage; deepen with PAT in local verify |
| D-W2-Q4 | Q-4 / A-4 | GitHub Projects column APIs not implemented — board column is Issues label (`gateflow/column:*`) per narrowed MVP | Low — intentional exit gate resolution; document follow-on if Projects required |
| D-W1-A1 | FR-17 / V-3 | Real Cursor SDK still stubbed (carried; out of W2 scope) | Low — follow-on |
| D-W1-V1 | FR-19 | Full PR-at-start live assert still needs `GATEFLOW_VERIFY_WORKER=1` | Medium — carried; not blocking W2 board exit |

No blocking discrepancies for W2 exit if PE accepts D-W2-V1 / D-W2-Q4 and carried W1 notes.

## Contracts produced by this wave

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Board status update | BoardService + board routes | `PATCH /api/v1/board/tickets/{ticket_id}/status` | programme token + `{ org, repo, state?, column? }` | ticket resource | At least one of state/column; bad payload 400; forge errors surface | initiative complete / ops |
| Board PR link | BoardService + board routes | `POST /api/v1/board/tickets/{ticket_id}/links` | programme token + `{ org, repo, pr_number }` | `{ ticket_id, pr_number, link_ref }` | Positive pr_number; comment-based link primitive | initiative complete / ops |
| Board create | BoardService + board routes | `POST /api/v1/board/tickets` | body + optional `Idempotency-Key` | create response with `partial` / `created_resources` / `failed_resources` | EPIC/Feature idempotent on initiative_id+type; multi-step issue then labels | initiative complete / ops |
| Board list | BoardService + board routes | `GET /api/v1/board/tickets` | query: org, repo, initiative_id?, type?, state | `{ tickets: [...] }` | Narrow filters only (Q-3); no governance parsing | initiative complete / ops |
| Forge board ops | ForgeClient | `update_issue_status` / `link_pull_request` / `create_issue` / `find_issues_by_labels` / `apply_issue_labels` | owner/repo + issue fields | forge JSON / comment id | httpx REST only; `operation=board_*`; no gh CLI | initiative complete |
| Worker board isolation | RunOrchestrator | `process_job` | claimed job | run summary | Zero board ForgeClient mutations on complete | initiative complete |
| gh-free production path | ForgeClient + runbooks | source guard + checklist | production env | fail if PAT / gh CLI used | ADR-003 PAT ban; inspection checklist | ops |
| Laptop vs deploy policy | runbook | `docs/runbooks/laptop-gh-vs-deploy-forgeclient.md` | — | documented split | Laptop gh allowed outside runtime; board-seed not replaced | ops / skills |
| Q-4 exit matrix | report | `Q4-PERMISSION-MATRIX-INIT-GATEFLOW-002-W2.md` | — | Issues MVP permission table | Projects deferred; Issues write sufficient for W2 | PE follow-on if Projects needed |
| Board live verify | tests.verify | `verify_board` / `verify_all` | running API + token (+ optional PAT) | exit 0 | Auth/400 always; forge mutations when PAT set | ops |

## PR instructions

> Commit this report + updated as-built row to the wave branch (last commit before PR is marked ready). Ground report and code are reviewed together on the same PR — do not open a separate PR for the ground report.

```
Branch:   feature/INIT-GATEFLOW-002-w2-board
PR title: [INIT-GATEFLOW-002 W2] board — implementation + ground report
Issue:    #14
Spec:     docs/specification/product/INIT-GATEFLOW-002-gateflow.md
Verify:   make check && make test ; .venv/bin/python -m tests.verify.verify_all
```

Required reviewer: per CODEOWNERS / prayog-pe-team  
Review deadline: 2026-07-28

After reviewer approves:
  Update as-built: INIT-GATEFLOW-002 W2 → human_approved
  Merge PR
  → Initiative INIT-GATEFLOW-002 complete (no W3 in plan); optional follow-ons: Cursor SDK, Projects board transport, forge-live board verify with PAT

## Ready for human checkpoint?

**yes** — automated checks green; FR-24…26b + Q-4 exit documented; D-W2-V1 / D-W2-Q4 explicitly deferred for PE acceptance.

- [ ] Review FR checklist — all pass or explicitly deferred
- [ ] Review §Contracts produced — accurate (no W3 consumer; ops/initiative-complete consumers)
- [ ] Mark as-built: INIT-GATEFLOW-002 W2 = human_approved

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-002-W2.md
    digest: sha256:4ce8ea4d035505e2bb11cc2aea8c316f80a831615b411b690db20988bd818618
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-002
    wave: W2
    board_issue: https://github.com/drivestream-lab/gateflow/issues/14
    branch: feature/INIT-GATEFLOW-002-w2-board
    commit: dec19bf
    contracts_produced: 10
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_all
    unit_tests: 76 passed
    live_verify: passed
    deferred_notes: [D-W2-V1, D-W2-Q4, D-W1-A1, D-W1-V1]
    q4_exit: narrowed_issues_mvp
    human_approved: false
  next_candidates:
    - wave-human-decision
  human_checkpoint: true
  external_action: false
```
