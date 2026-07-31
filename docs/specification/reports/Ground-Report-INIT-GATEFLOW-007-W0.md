# Ground report — INIT-GATEFLOW-007 W0

| Field | Value |
|-------|-------|
| Wave | W0 — Closeout start API + Pass-2 walker + smoke verify |
| Spec | `docs/specification/product/INIT-GATEFLOW-007-gateflow.md` |
| Initiative | INIT-GATEFLOW-007 |
| Date | 2026-07-31 |
| Wave head (exact) | `feature/INIT-GATEFLOW-007-w0-closeout-start` — **working tree at ground**; expected reviewed SHA = tip **after** `/commit-workspace` publishes this package |
| PR URL | n/a — open Draft PR after commit (board [#85](https://github.com/drivestream-lab/gateflow/issues/85)) |
| Board | https://github.com/drivestream-lab/gateflow/issues/85 |
| Status | Draft |
| Review deadline | 2026-08-04 |
| Deciders | Tech lead / reviewer — explicit LGTM required (human merge at wave-signoff) |
| Outcome | **pass** |
| Outcome reason | Wave-assigned REQs verified against code + unit + human live smoke; no Blocking GF-*; Contracts produced ready for W1 `/pre-implement` |
| Assigned REQs | REQ-1, REQ-2, REQ-3, REQ-4, REQ-5, REQ-6, REQ-7, REQ-8, REQ-13, REQ-16, REQ-17 — from plan TASK-W0-01…07 |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution | **204 passed** at ground time; `test_wave_closeout` + pin Pass-2 handoff asserts |
| Ground | `{ground_command}` undefined — manual `src/` + `tests/**` scan | Entry points and tests mapped below |
| Live | `Live-Verify-INIT-GATEFLOW-007-W0.md` | Human **approved** closeout smoke |

## Automated ground check output

`{ground_command}` not defined in harness profile — **SKIPPED** (manual source + tests scan used).

Manual re-proof at ground time:

- `make check` → exit 0
- `make test` → **204 passed**
- Route present: `POST /api/v1/waves/closeout/start` in `src/api/v1/waves_routes.py`
- Enter-at constant: `CLOSEOUT_START_NODE = "learning-extract"`
- Verify module: `tests/verify/verify_wave_closeout.py`

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-1 | Authenticated `POST /api/v1/waves/closeout/start` | Route + programme token; `verify_wave_closeout` 401 smoke; unit enqueue | **pass** |
| REQ-2 | Fixed Enter-at `learning-extract`; no client `start_node` | `CloseoutWaveStartRequest` forbids field; service uses `CLOSEOUT_START_NODE`; pin orchestrated check | **pass** |
| REQ-3 | New run + required PR bind; ACTIVE → 409 | `start_closeout_wave` creates run with `pr_number`; unit concurrent 409 | **pass** |
| REQ-4 | Body fields; `extra=forbid`; absolute workspace; branch targeting | Model validators; TDD §3.1 updated; unit rejects relative/missing PR | **pass** |
| REQ-5 | Bind to pin `learning-extract` schema (Gateflow-owned baton) | Baton `handoff_path` defined at accept; Enter-at orchestrated skill required before enqueue | **pass** (hop-time PromptResolver reuse; same lane-start pattern) |
| REQ-6 | Both lanes; meta not required | No meta fields on closeout model; `extra=forbid` rejects meta | **pass** |
| REQ-7 | Walker Pass-2 → `wave-signoff`; no auto verify | Pin unit: learning-extract → ground-spec → wave-signoff; verify remains manual | **pass** (unit/pin; full live dogfood = W2) |
| REQ-8 | Handoff + baton dual-write path | `handoff_path` on run + job payload; ADR-008 ingest unchanged | **pass** |
| REQ-13 | Optional `prior_run_id` audit-only | Field on body/job payload; unit unknown → 400; omit OK | **pass** |
| REQ-16 | Checkpoint id hygiene in unit mocks | `test_trigger_policy` / `test_notifier` use `wave-signoff`; no `wave-human-decision` in `tests/unit` | **pass** (W0 mock slice; full `src/` grep = W2) |
| REQ-17 | As-built + feature map | as-built INIT-007 W0 rows; `tests/README` closeout row + smoke section | **pass** |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Third start contract (ADR-010 §6) | ADR-010 | **pass** — distinct body; fixed Enter-at; new run |
| Programme token write | ADR-005 / route Depends | **pass** |
| Models in `src/models/` only | `architecture.mdc`, `pydantic-schemas.mdc` | **pass** |
| Fail closed validation / 409 | `fail-fast.mdc` | **pass** |
| Verify vs pytest separation | `testing-verify-flows.mdc` | **pass** — smoke in verify; logic in unit |
| No Alembic versions by agent | `database-migrations.mdc` | **pass** — W0 no DDL |
| No learning ingest yet | plan W1 | **pass** — out of W0 scope |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Lane start enqueue core (`_enqueue_wave`) | INIT-006 / `WaveStartService` | **yes** — closeout reuses |
| Pass-1 pin remount; `learning-extract` orchestrated | #76 / Ground-Report INIT-008 / pin | **yes** |
| ADR-010 closeout amendment Accepted | ADR-010 §6 | **yes** |
| W0 first wave of INIT-007 — no prior 007 Ground Report | Pre-Implement / board | **yes** — N/A prior 007 contracts |

## Discrepancies (must fix before human checkpoint)

| ID | REQ | Finding | Severity |
|----|-----|---------|----------|
| — | — | none | — |

## Learning cited

| L-id | Class | How it affects this ground |
|------|-------|----------------------------|
| *(none)* | — | No `Learning-Extract-INIT-GATEFLOW-007-W0.md` this wave (Pass-2 learning-extract / ingest is W1+; G8 SKIPPED with reason) |

## Contracts produced by this wave

(REQUIRED — input for `/pre-implement` W1.)

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Closeout start HTTP | `src/api/v1/waves_routes` | `POST /api/v1/waves/closeout/start` | `CloseoutWaveStartRequest` + programme token | `WaveStartResponse` | 401 without token; no client `start_node`/meta | W1 ingest after hop; W2 dogfood |
| Closeout body | `src/models/wave_start_models` | `CloseoutWaveStartRequest` | identity + required `pr_number` + absolute workspace + branch targeting + runner/model; optional `prior_run_id` | validated model | `extra=forbid`; Enter-at projected as `learning-extract` | W1+ callers |
| Closeout accept | `src/business_services/wave_start_service` | `start_closeout_wave` | closeout request | new ACTIVE run + job; baton path | fixed Enter-at; ACTIVE → 409; prior_run must exist if set | W1 orchestrator hook after learning-extract hop |
| Fixed Enter-at constant | same models | `CLOSEOUT_START_NODE` | — | `"learning-extract"` | server-owned only | W1/W2 must not reintroduce client start_node |
| Pass-2 pin graph | pin + `WorkflowEngine` | resolve after learning-extract / ground-spec | handoff stage+outcome | next ground-spec / wave-signoff | verify stays manual | W1 ingest ordering; W2 live stop |
| Closeout smoke verify | `tests/verify/verify_wave_closeout` | module main | `features.wave_closeout` | exit 0 smoke | W0 = auth/validation/enqueue; dogfood depth = W2 | W2 extends same script |

## Exact-head human sign-off package

> Ground Report and as-built updates written **locally**. Emit Forge readiness for publication. Do **not** commit, push, merge, or apply labels from this skill. Human reviews the **exact wave head**, records approval, and merges manually at `wave-signoff`.

- PR URL / wave head: open after `/commit-workspace` on `feature/INIT-GATEFLOW-007-w0-closeout-start` — **expected reviewed head SHA** = publish tip
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-007-W0.md`
- Live evidence path: `docs/specification/reports/Live-Verify-INIT-GATEFLOW-007-W0.md`
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-007-W0.md`
- As-built row prepared locally: INIT-007 W0 → **pending human_approved** (not marked `human_approved` by this skill)
- Required checkpoint evidence fields (human fills at `wave-signoff`; not `handoff.forge`): `reviewed_head_sha`, `merge_commit_sha`

### Human sign-off / merge checklist

- [ ] Review REQ checklist — all wave-assigned REQs pass or explicitly deferred
- [ ] Review §Contracts produced — accurate and complete for next wave
- [ ] Confirm reviewed head SHA matches tip after commit + Draft PR
- [ ] Mark as-built: INIT-GATEFLOW-007 W0 = human_approved (human only)
- [ ] Merge the wave PR manually (human only) — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge; no approval-label auto-merge

## Ready for human checkpoint?

**yes** — G1–G10 satisfied; no Blocking GF-*; Contracts produced complete. Publish code + Ground/Live/Wave-Execution via `/commit-workspace`, open Draft PR, then human `wave-signoff` on exact head.

## Checks G1–G10

| ID | Result |
|----|--------|
| G1 Wave scope | **PASS** — W0 assigned REQs only (not W1 learning / W2 dogfood) |
| G2 Ground / evidence | **PASS** — ground_command N/A; manual + `make test` + Live-Verify cited |
| G3 Assigned-REQ coverage | **PASS** — REQ-1…8,13,16,17 covered |
| G4 Acceptance evidence | **PASS** — Wave-Execution + unit + human live smoke |
| G5 ADR boundaries | **PASS** — ADR-010 §6 / ADR-005 / ADR-008 |
| G6 MDC boundaries | **PASS** — models, fail-fast, testing-verify |
| G7 Contracts consumed / produced | **PASS** — section complete for W1 |
| G8 Learning citations | **SKIPPED** — no Learning-Extract for 007-W0 (expected; learning W1) |
| G9 GF-* findings | **PASS** — none open |
| G10 Complete handoff | **PASS** — report + as-built pending + envelope; no commit/merge by this skill |

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-007-W0.md
    digest: sha256:a228a73026cc8dc68105d3017dfed5ac2da4dd1475ba842151e4853da105a085
  blockers: []
  signals:
    wave: W0
    initiative: INIT-GATEFLOW-007
    board_issue: "85"
    contracts_produced: 6
    assigned_reqs:
      - REQ-1
      - REQ-2
      - REQ-3
      - REQ-4
      - REQ-5
      - REQ-6
      - REQ-7
      - REQ-8
      - REQ-13
      - REQ-16
      - REQ-17
    learning_item_count: 0
    test_passed: 204
    live_verify: human_approved
  next_candidates:
    - wave-signoff
  human_checkpoint: true
  external_action: false
  forge:
    action: commit_workspace
    draft: false
    title: "[INIT-GATEFLOW-007] W0 — Closeout start API + Pass-2 walker + smoke verify"
    body_path: docs/specification/reports/PR-body-INIT-GATEFLOW-007-W0.md
    head_ref: feature/INIT-GATEFLOW-007-w0-closeout-start
    base_ref: develop
```
