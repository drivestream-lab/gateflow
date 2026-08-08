# Ground report — INIT-GATEFLOW-012 W4

| Field | Value |
|-------|-------|
| Wave | W4 — Repo-scoped NO_CONCURRENT_RUN |
| Spec | `docs/specification/product/INIT-GATEFLOW-012-gateflow.md` |
| Initiative | INIT-GATEFLOW-012 |
| Date | 2026-08-08 |
| Wave head (exact) | Pass-1 tip `1720ef44dbb233f1057e21f2bee3fd4846b5b9d2`; merge on `develop` @ `20965abc6c8d2210fa0c2b57dd375185032c58b6` |
| PR URL | https://github.com/drivestream-lab/gateflow/pull/195 |
| Board wave | [#189](https://github.com/drivestream-lab/gateflow/issues/189) |
| Status | Retrospective Pass-2 after merge (closeout was skipped before wave-signoff) |
| Review deadline | 2026-08-12 |
| Deciders | Human merge by @nikd10x already completed; this report backfills contracts for W5 `/pre-implement` |
| Outcome | **pass** |
| Outcome reason | REQ-23–25 map to unit/inspection evidence on merged tip; Contracts produced for W5; GF-01 Verify-only (missing `wave-accepted`); no Blocking GF-* |
| Assigned REQs | REQ-23, REQ-24, REQ-25 |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution | **456 passed** at loop-spec; concurrency subset **6 passed** (2026-08-08); TASK-W4-01…04 green; FF-06 xfail flipped |
| Ground | Manual `src/` + `tests/**` scan (no `{ground_command}`) | `find_active_run(org, repo)` only; wave-start/trigger_router/closure callers; verify script probes; no isolation packages |
| Accept | **Retrospective** — [#195](https://github.com/drivestream-lab/gateflow/pull/195) merged by @nikd10x (2026-08-08T11:40:42Z); **no** `wave-accepted` label on timeline | Process gap recorded as GF-01 / L-01 |
| Learning | `Learning-Extract-INIT-GATEFLOW-012-W4.md` | `human_fix_detected: false`; **L-01** SKILL open |

## Automated ground check output

`{ground_command}` is **not defined** in `.harness/profile.yaml` — SKIPPED with reason: perform manual source + tests scan.

```text
make test → 456 passed (loop-spec 2026-08-08)
pytest tests/unit/test_run_store_concurrency.py + concurrent wave_start → 6 passed (2026-08-08)
git show develop:src/database/postgres/repository/run_store_repository.py → find_active_run(org, repo) only
```

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-23 | Reject new run when ACTIVE exists for same org+repo (broadened key) | `RunRepository.find_active_run(session, org, repo)`; wave-start `ConflictError` + `precondition_id=PC-06-…`; trigger_router `NO_CONCURRENT_RUN`; units `test_run_store_concurrency`, `test_implement_concurrent_409`; live `verify_wave_start` same-repo 409 | pass |
| REQ-24 | Different repos never block each other | Query always binds requested repo; unit `test_ff06_cross_repo_*`; live optional `GATEFLOW_VERIFY_CROSS_ORG`/`_REPO` | pass |
| REQ-25 | No new worktree/lock/isolation mechanism | Query-only change; source inspection in FF-06; no new isolation modules under `src/` | pass |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Query-only broaden (no new concurrency subsystem) | plan / ADR-001 / REQ-25 | pass — repository WHERE change + call-site simplify |
| Keep existing NO_CONCURRENT_RUN / Conflict surface | product negative path | pass — `PC-06-no-concurrent-active-run` in Conflict details; trigger_router unchanged id |
| Repository pattern — business does not craft SQL | repository-pattern.mdc | pass — services call `find_active_run` only |
| Fail-fast same-repo second start | fail-fast.mdc | pass — 409 before enqueue |
| Harness gate still before shared-workspace mutation | Ground-Report W3 | pass — concurrency check remains at persist; harness path unchanged |
| No agent Alembic `versions/` | database-migrations.mdc | pass — no DDL this wave |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Wave-start persist + concurrency probe | Ground-Report W3 / product | yes — call now org+repo only |
| Trigger-router NO_CONCURRENT_RUN | Ground-Report W3 | yes — PC-06 retained; check when org+repo present |
| Harness gate before coding hop | Ground-Report W3 | yes — not weakened |
| Workspace / branch bind | Ground-Report W1/W2 | yes — concurrency protects shared dir (D10) |

## Discrepancies (must fix before human checkpoint)

| ID | REQ | Finding | Severity |
|----|-----|---------|----------|
| GF-01 | — | Draft tip never received `wave-accepted`; Pass-2 closeout ran after merge | Verify — process; merge already done; do not block W5 contracts |

## Learning cited

| L-id | Class | How it affects this ground |
|------|-------|----------------------------|
| L-01 | SKILL | Explains GF-01; W5+ should not skip Pass-2 / `wave-accepted` before wave-signoff |

## Contracts produced by this wave

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Repo-scoped ACTIVE lookup | `RunRepository` | `find_active_run` | session, org, repo | optional ACTIVE run | Ignores initiative/wave/PR/issue; org+repo+ACTIVE only | W5+ must not re-narrow without ADR |
| Wave-start concurrency reject | `WaveStartService` | `_enqueue_wave` active check | org, repo | HTTP 409 Conflict; details include `precondition_id=PC-06-…` | Synchronous before create/enqueue | W5 dormant delete_branch unrelated |
| Trigger-router concurrency | `TriggerRouter` | `authorize_and_check` | org+repo on api_trigger | `PreconditionFailure` NO_CONCURRENT_RUN | Same query; exclude current run_id when set | Later |
| Closure-start concurrency | `ClosureStartService` | start persist | org, repo | Conflict when ACTIVE on repo | Same broadened query | Later |
| Live concurrency probes | `tests/verify/verify_wave_start.py` | module main | API + programme token | exit 0 includes same-repo 409; optional cross-repo env | First start may leave ACTIVE | W5 P15 N/A |
| No isolation infra | inspection | — | — | no new lock/worktree types | REQ-25 | W5 must not invent isolation for delete_branch |

## Exact-head merge package (for wave-signoff)

> **Already merged.** This Ground Report is a **retrospective** Pass-2 backfill. Publish Learning/Ground/as-built onto `develop` via `/commit-workspace`. Do not re-merge [#195](https://github.com/drivestream-lab/gateflow/pull/195).

- PR URL / merge: https://github.com/drivestream-lab/gateflow/pull/195 → `20965abc6c8d2210fa0c2b57dd375185032c58b6`
- Reviewed Pass-1 tip: `1720ef44dbb233f1057e21f2bee3fd4846b5b9d2`
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-012-W4.md`
- Accept evidence: human merge (label `wave-accepted` missing — GF-01)
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-012-W4.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-012-W4.md`
- As-built: W4 marked `human_approved` retrospectively from merge + this closeout
- Required merge fields: `reviewed_head_sha=1720ef4…`, `merge_commit_sha=20965ab…` (already known)

### Human merge checklist (wave-signoff)

- [x] Merge already completed (human)
- [ ] Publish Pass-2 artifacts onto `develop` via `/commit-workspace`
- [ ] Board [#189](https://github.com/drivestream-lab/gateflow/issues/189) → Done if not already (`wave-done-action`)

## Ready for wave-signoff (merge)?

**n/a — already merged.** Ready for Pass-2 publish on `develop` + W5 `/pre-implement` consuming §Contracts produced.

### Checks G1–G10

| ID | Result |
|----|--------|
| G1 Wave scope | PASS — W4 REQs only (REQ-23–25) |
| G2 Ground command / evidence | PASS — ground_command absent → manual scan + unit cited |
| G3 Assigned-REQ coverage | PASS — REQ-23–25 |
| G4 Acceptance evidence | PASS with caveat — merge accept; GF-01 Verify for missing `wave-accepted` |
| G5 ADR boundaries | PASS — ADR-001 query-only; ADR-010 consume |
| G6 MDC boundaries | PASS — repository / fail-fast / testing |
| G7 Contracts consumed / produced | PASS — W3 contracts match; §Contracts produced complete for W5 |
| G8 Learning citations | PASS — L-01 cited |
| G9 Stable GF-* | PASS — GF-01 Verify only |
| G10 Complete handoff | PASS — retrospective package; forge publish to `develop` |

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-012-W4.md
  blockers: []
  signals:
    wave: W4
    contracts_produced: 6
    assigned_reqs: [REQ-23, REQ-24, REQ-25]
    reviewed_head_sha: 1720ef44dbb233f1057e21f2bee3fd4846b5b9d2
    merge_commit_sha: 20965abc6c8d2210fa0c2b57dd375185032c58b6
    draft_pr: "https://github.com/drivestream-lab/gateflow/pull/195"
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/189"
    retrospective_pass2: true
    gf_verify: [GF-01]
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    status: done
    ticket: "189"
    commit_workspace: required
    head_ref: develop
    base_ref: develop
```
