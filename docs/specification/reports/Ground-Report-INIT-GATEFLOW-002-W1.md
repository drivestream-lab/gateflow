# Ground report — INIT-GATEFLOW-002 W1

| Field | Value |
|-------|-------|
| Wave | W1 — Per-node model + PR-at-start + metrics |
| Spec | `docs/specification/product/INIT-GATEFLOW-002-gateflow.md` |
| Date | 2026-07-24 |
| Branch | `feature/INIT-GATEFLOW-002-w1-model-pr-metrics` |
| Status | **human_approved** |
| Review deadline | 2026-07-28 |
| Deciders | Tech lead / reviewer: @nikd10x — human LGTM recorded 2026-07-24 |

## Automated check output

`ground_command`: N/A. Evidence: `make check`, `make test`, `.venv/bin/python -m tests.verify.verify_all` (shared `drivestream-postgres` / `drivestream-redis`; gateflow API on `:8080`).

Commit under review: `ad3feb0` (+ this ground report commit).

### `make check` (exit 0)

```
.venv/bin/black --line-length 100 src/ tests/
All done! 130 files left unchanged.
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
collected 65 items
65 passed
```

### Live verify `.venv/bin/python -m tests.verify.verify_all` (exit 0)

```
[OK] verify_health passed
[OK] verify_webhook passed (401 / 202 / duplicate)
[OK] verify_status_metrics passed (401 / 404 / 200 metrics incl. by_runner + by_model_id keys)
[OK] verify_wave_start passed (401 / 2xx start / detail timeline / list filter / label ingress ack)
[OK] verify_pr_thread passed (metrics dims keys; api_trigger on timeline; PR live assert skipped without GATEFLOW_VERIFY_WORKER=1)
[OK] verify_all passed
```

## FR checklist

W1 plan scope: FR-16 runtime resolve + persist; FR-19 PR-at-start; FR-21/22 metrics dims + events; Cursor happy path (V-3 stub OK). W0 FRs remain in force. FR-24…26 are **W2**.

| FR | Spec claim | Verified artifact | Status |
|----|-----------|-------------------|--------|
| FR-15 | API wave-start only; label disabled | W0 + still live `verify_wave_start` | **pass** (inherited + live) |
| FR-16 | Per-node runner/model resolve; persist four fields; invalid override blocked at start | `node_model_resolver.resolve_node_dispatch`; orchestrator stage create; `test_node_model_resolver` (≥2 profiles); `test_wave_start` unknown node 422; programme overrides for `loop-spec` / `ground-spec` | **pass** (unit) |
| FR-17 | Cursor implemented; stubs registered; Cursor path produces runner/model fields | AdapterRegistry (W0) + `CursorAgentRunner` stub path; `test_cursor_agent_runner` | **pass** (unit; SDK deferred per V-3) |
| FR-18 | Fail-closed stub/config; invalid override at start | SlotValidator + WaveStartService `_validate_model_overrides` (known pin nodes + profile resolve) | **pass** (unit) |
| FR-19 | PR open/update at run start; comments on that PR; no auto-merge; `notify_pending` on PR failure | `ForgeClient.create_or_update_pull_request`; orchestrator `_ensure_run_pr` before stage; Notifier uses `pr_number`; `test_forge_client`; `test_pr_opened_before_stage_when_run_has_no_pr` | **pass** (unit); **partial live** — PR number assert needs worker (`GATEFLOW_VERIFY_WORKER=1`) |
| FR-20 | Run list/detail | W0 + live verify unchanged | **pass** (inherited + live) |
| FR-21 | Metrics by `workflow_node`, `runner`, `model_id` | `MetricsEmitter.aggregate_run_metrics` → `by_runner` / `by_model_id`; `test_metrics_emitter`; live keys in `verify_pr_thread` / `verify_status_metrics` | **pass** (unit + live keys; populated dims when stage events exist) |
| FR-22 | Multi-stage metrics events incl. API trigger | `record_api_trigger` on wave start; `stage_completed` with runner/model_id payload; `run_stopped`; live `api_trigger` on timeline | **pass** (unit + live for api_trigger / stages; findings-loop events still from INIT-001 stop path) |
| FR-23 | GitHub notifier live; Slack/Teams stubs | W0 registry + Notifier → ForgeClient; comments target run PR when `pr_number` set | **pass** (inherited; wired to PR number) |
| FR-24…26 | Board / gh-free | W2 scope | **deferred** — not W1 |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| ForgeClient / AgentRunner = infra; orchestrator / metrics / resolver = business | ADR-003 | **pass** |
| Programme `pr.*` + overrides in YAML; secrets in env | ADR-004 | **pass** — `PrConfig` + sample overrides in `config/programme.yaml` |
| Fail-closed adapter selection still gates start | ADR-006 | **pass** — unknown override node / missing profile → 422 |
| Programme-token control-plane reads unchanged; no new board writes | ADR-005 | **pass** — W1 adds no board mutation routes |
| Dual process; durable stages with runner/model fields | ADR-001 | **pass** — stage columns reused (no new Alembic in W1) |
| No auto-merge / gate-approval labels | ADR-003 / ForgeClient | **pass** — forbid methods still raise |
| Models in `src/models/`; import-linter layers | pydantic-schemas / python-tooling | **pass** |
| Structured logging kwargs | logging-loguru | **pass** — `runner`, `model_id`, `pr_number` on key paths |

## Cross-spec contracts consumed

Source: `Ground-Report-INIT-GATEFLOW-002-W0.md` §Contracts produced.

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Wave start HTTP | Ground-Report-002-W0 | yes — plus `api_trigger` metrics event at accept |
| Dual identity resolve | Ground-Report-002-W0 | yes |
| Slot fail-closed | Ground-Report-002-W0 | yes — extended with pin-known override nodes + resolve |
| Adapter catalogue | Ground-Report-002-W0 | yes |
| Label start policy | Ground-Report-002-W0 | yes |
| API trigger job | Ground-Report-002-W0 | yes — worker still reuses `run_id` |
| Run list / detail timeline | Ground-Report-002-W0 | yes |
| Programme config v2 | Ground-Report-002-W0 | yes — extended with required-shape `pr.*` (defaults) |
| Wave identity store | Ground-Report-002-W0 | yes — stage model fields already present |
| Forge comments | Ground-Report-002-W0 | yes — target is run PR when assigned |
| Job orchestration | Ground-Report-002-W0 | yes — PR-at-start + per-node resolve added before/during dispatch |

## Discrepancies (must fix before human checkpoint)

| ID | FR | Finding | Severity |
|----|----|---------|----------|
| D-W1-V1 | FR-19 | Live `verify_pr_thread` asserts metrics keys + `api_trigger`; full `pr_number` assert requires `GATEFLOW_VERIFY_WORKER=1` + worker + forge credentials (unit owns PR call-order) | Medium — accept for W1 exit; deepen with worker soak / dogfood (carries D-W0-V1) |
| D-W1-A1 | FR-17 / V-3 | Real Cursor SDK still stubbed; W1 exit uses `mock-*` / `GATEFLOW_AGENT_STUB` per TDD deferred default | Low — document as deferred; SDK follow-on |
| D-W1-B1 | FR-19 | `create_or_update_pull_request` opens/updates PR by head ref; does not separately mint a remote branch via refs API — forge may require branch to exist for create in some orgs | Low — monitor in worker live path; extend ForgeClient if needed |

No blocking discrepancies for W1 exit if PE accepts D-W1-V1 / D-W1-A1 / D-W1-B1 as in-scope.

## Contracts produced by this wave

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Per-node model resolve | node_model_resolver | `resolve_node_dispatch` | programme config + workflow node id | `{ runner, model_profile, model_id, model_provider }` | Unset node → defaults; unknown/empty profile fails; no hardcoded node allowlists | W2 |
| Override gate at start | WaveStartService | `_validate_model_overrides` | programme overrides + pin node set | void or 422 structured | Override keys must be pin-known; profiles must resolve | W2 |
| Stage field persist | RunOrchestrator + StageRepository | stage create after dispatch | resolved dispatch fields | stage row with four fields | Persist from config resolution (not agent narrative alone) | W2 / ops |
| PR config | ProgrammeConfig | `pr.*` load | YAML `branch_prefix`, title/body templates, `base_branch` | validated `PrConfig` | Same templates for success and failure naming | W2 |
| Forge PR open/update | ForgeClient | `create_or_update_pull_request` | owner/repo, title, body, head, base | PR number | No auto-merge; no gate labels; update if open PR with same head exists | W2 (board may reuse forge) |
| PR-at-run-start | RunOrchestrator | `_ensure_run_pr` | run + programme `pr.*` + payload identity | run with `pr_number` **or** `notify_pending` | Called before first orchestrated stage; PR failure does not invent success | W2 |
| Run PR comments | Notifier + orchestrator | `post_run_event_comment` | org/repo + issue/PR number from run | comment id or notify_pending | Comments target run PR when assigned | W2 |
| API trigger metrics event | MetricsEmitter + WaveStartService | `record_api_trigger` | run id + initiative/wave | `run_events` row `event_type=api_trigger` | Emitted on accepted API start | W2 / ops |
| Metrics dimensions | MetricsEmitter + metrics route | `aggregate_run_metrics` / `GET /api/v1/metrics/runs` | Bearer + retention window | `{ retention_days, by_workflow_node, by_runner, by_model_id }` | Dims from `stage_completed` payload fields when present | W2 / ops |
| Cursor stub path | CursorAgentRunner | `run_skill` | workspace, skill, model fields | AgentRunResult | Success under `mock-*` or `GATEFLOW_AGENT_STUB`; real SDK deferred (V-3) | W2 / follow-on |
| PR-thread verify | tests.verify | `verify_pr_thread` / `verify_all` | running API + token + DB | exit 0 | Asserts metric keys + api_trigger; optional PR with worker flag | W2 verify extend |

## PR instructions

> Commit this report + updated as-built row to the wave branch (last commit before PR is marked ready). Ground report and code are reviewed together on the same PR — do not open a separate PR for the ground report.

```
Branch:   feature/INIT-GATEFLOW-002-w1-model-pr-metrics
PR title: [INIT-GATEFLOW-002 W1] model-pr-metrics — implementation + ground report
Issue:    #13
Spec:     docs/specification/product/INIT-GATEFLOW-002-gateflow.md
Verify:   make check && make test ; .venv/bin/python -m tests.verify.verify_all
```

Required reviewer: per CODEOWNERS / prayog-pe-team  
Review deadline: 2026-07-28

After reviewer approves:
  Update as-built: INIT-GATEFLOW-002 W1 → human_approved
  Merge PR
  → `/pre-implement` for W2 (reads §Contracts produced above)

## Ready for human checkpoint?

**yes — human_approved** (2026-07-24). Live `verify_all` green on shared drivestream Postgres/Redis; D-W1-V1 / D-W1-A1 / D-W1-B1 accepted for W1 exit.

- [x] Review FR checklist — all pass or explicitly deferred
- [x] Review §Contracts produced — accurate for W2 consumers
- [x] Mark as-built: INIT-GATEFLOW-002 W1 = human_approved

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-002-W1.md
    digest: sha256:a7908318f43143b7d262cfcfb470eb0cf36b11d18f0c793dc29e5b8d93ad9e17
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-002
    wave: W1
    board_issue: https://github.com/drivestream-lab/gateflow/issues/13
    branch: feature/INIT-GATEFLOW-002-w1-model-pr-metrics
    commit: ad3feb0
    contracts_produced: 11
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_all
    unit_tests: 65 passed
    live_verify: passed
    deferred_frs: [FR-24, FR-25, FR-26a, FR-26b]
    discrepancies: [D-W1-V1, D-W1-A1, D-W1-B1]
    human_approved: true
  next_candidates:
    - wave-complete
  human_checkpoint: false
  external_action: true
```
