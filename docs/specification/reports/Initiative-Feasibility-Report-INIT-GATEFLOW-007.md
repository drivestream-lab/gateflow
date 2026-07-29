# Feasibility report — INIT-GATEFLOW-007

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-007 |
| Spec | `docs/specification/product/INIT-GATEFLOW-007-gateflow.md` |
| Spec digest | `sha256:242e249f64d46e2e31ea98d9310cb408aee79f743c714c64008c8eb62fe9b825` |
| PRD digest | TBD — no meta PRD (spec header) |
| Impact map / revision | TBD / TBD |
| Repo scope digest | TBD |
| Approved meta PR head | TBD |
| Impact-map approval | TBD — Gate 1 open (spec Q-1) |
| Source freshness | **STALE / WAIVED** — Gate 1 digests and APPROVED meta head absent; PE-directed engineering INIT from prayog-skills Pass-1/Pass-2 brief (same waiver pattern as INIT-006). Do **not** claim CURRENT until Q-1 closes. |
| Repo | drivestream-lab/gateflow |
| Date | 2026-07-29 |
| Branch | `chore/INIT-GATEFLOW-007-spec-gateflow` — Draft spec PR [#77](https://github.com/drivestream-lab/gateflow/pull/77) |
| Initiative segment | `INIT-GATEFLOW-007` |
| Status | Draft |
| Review deadline | 2026-08-01 |
| Deciders | PM: programme PM · Domain SME: prayog-pe-team |

## Summary

INIT-GATEFLOW-007 is **buildable** on the remounted Pass-1/Pass-2 pin (#76) and the
INIT-001…006 control plane (lane starts, packaged Cursor, baton ingest, forge
publish). Product work is concentrated in three gaps: (1) a third programme-token
intake surface `POST /api/v1/waves/closeout/start` with fixed Enter-at
`learning-extract` + required PR bind, (2) worker-owned Learning-Extract YAML →
Postgres ingest (no skill→HTTP), (3) Pass-2 live verify + feature-map rows. No
Critical ADR contradiction. Gate 1 freshness is waived, not CURRENT — formal
`spec-lgtm` package still needs Q-1. Recommendation: keep `spec-pending`, run
`/spec-technical-review` next (PE questions + learning data contract).

**Findings:** 12 total (0 Critical, 5 Should fix, 4 Verify, 3 Gap)

## Baseline snapshot (F1)

| Area | Current state | Evidence |
|------|---------------|----------|
| Unit tests | `tests/unit/` — wave-start (implement/spec), orchestrator walker, handoff pin graph (`learning-extract`→`ground-spec`), forge, prompt resolver | `test_wave_start.py`, `test_run_orchestrator.py`, `test_handoff_workflow.py`; `Makefile` `test` |
| Live verify | Pass-1 implement-lane stops at `live-verify`; no closeout verify script | `tests/verify/verify_implement_lane.py` (`_PASS1_STOP_NODE = "live-verify"`); no `verify_wave_closeout.py` |
| As-built | Pass-1 remount (#76); INIT-007 draft rows = not implemented | `docs/specification/as-built/implementation-status.md` §INIT-GATEFLOW-007 |
| Toolchain | `make check` / `make test`; CI placeholder | `Makefile`, `.github/workflows/ci.yml` |
| Source | Lane starts only; no closeout route; no learning ORM tables | `src/api/v1/waves_routes.py`; `src/database/postgres/schema/run_store_schema.py` (runs/stages/jobs only) |
| Pin | Pass-2 graph + `learning-extract` package present | `prayog-skills/workflow.yaml` (`learning-extract`→`ground-spec`→`wave-signoff`); `prayog-skills/skills/development/learning-extract/` |

## ADR pass (pre-T2)

| ADR id | Domain matched | Status |
|--------|----------------|--------|
| ADR-001 | Postgres SSOT; dual API+worker; human Alembic | Accepted — aligned (learning tables additive) |
| ADR-002 | Edge trust / public_paths | Accepted — aligned (programme-token mutation; no public closeout) |
| ADR-003 | Business vs infra slot ownership | Accepted — aligned (ingest/orchestration in business; Cursor infra) |
| ADR-004 | Programme config / pin consume | Accepted — aligned (no laptop overlay) |
| ADR-005 | Programme-token control-plane mutations | Accepted — aligned (closeout = new mutation surface) |
| ADR-006 | Adapter registry fail-closed | Accepted — aligned (Cursor-only) |
| ADR-007 | Bound prompt inputs / message contract | Accepted — aligned (cite pin `schema.yaml`) |
| ADR-008 | Packaged handoff ingest from stored path | Accepted — aligned (REQ-8) |
| ADR-009 | Pin forge publish/mutate | Accepted — aligned (optional/required commit on Pass-2 nodes) |
| ADR-010 | Lane intake (implement vs spec) | Accepted — **constrains** closeout as *third* intake; confirm extension vs NEW-ADR in TDD (FF-05) |

## MDC pass (pre-T2)

| MDC file | Domain covered | Read / skipped |
|----------|----------------|----------------|
| `architecture.mdc` | Layout; API→business→repo | read |
| `http-api-conventions.mdc` | Body-only POST; models in `src/models/` | read |
| `pydantic-schemas.mdc` | Request/DTO models; enums; JSONB | read |
| `repository-pattern.mdc` | ORM only in repos; learning tables | read |
| `database-migrations.mdc` | Human-owned Alembic | read |
| `dependency-injection.mdc` | Service `@inject` | read |
| `fail-fast.mdc` | Fail closed accept/bind/ingest | read |
| `strong-typing.mdc` | Typed learning models | read |
| `testing-verify-flows.mdc` | unit vs live verify | read |
| `logging-loguru.mdc` | Structured kwargs | skipped — no wording conflict |
| `infra-services.mdc` | Forge/Cursor unchanged | skipped — reuse |
| `python-imports.mdc` / `python-tooling.mdc` | Tooling | skipped |
| `spec-driven-development.mdc` | Process | skipped |
| `code-guidelines-index.mdc` | Index | skipped |

## Traceability matrix

| Spec REQ / wave | Spec claim | Code evidence | Unit | Verify | Status |
|-----------------|------------|---------------|------|--------|--------|
| REQ-1 / W0 | `POST /api/v1/waves/closeout/start` + programme token | Only `implement/start` + `spec/start` in `waves_routes.py` | none for closeout | none | **gap** |
| REQ-2 / W0 | Fixed Enter-at `learning-extract`; reject client `start_node` | Pin node orchestrated (`workflow.yaml`); no closeout accept path | `test_handoff_workflow` (pin only) | — | **gap** (pin ready) |
| REQ-3 / W0 | New run + PR bind; concurrent ACTIVE fail | `WaveStartService` + `find_active_run` (ACTIVE only) — reusable; PR not required on implement start today | `test_wave_start` concurrent 409 | — | **partial** (reuse + tighten PR required) |
| REQ-4 / W0 | Closeout body fields + `extra=forbid` | `ImplementWaveStartRequest` / `SpecWaveStartRequest` — no closeout model | — | — | **gap** |
| REQ-5 / W0 | Bind to pin `learning-extract` schema | `BoundPromptInputs` + `PromptResolver` exist; schema vars: ticket, handoff_path, workspace, skill_id (+ optional initiative) | `test_prompt_resolver` | — | **partial** (wire on closeout start) |
| REQ-6 / W0 | Both lanes, one route; meta fields not required | No closeout route yet; ADR-010 lane starts separate | — | — | **gap** |
| REQ-7 / W0 | Walker Pass-2 → `wave-signoff` | Walker generic; pin outcomes ready; no Enter-at closeout job yet | `test_run_orchestrator` multi-hop; pin tests | Pass-1 only | **partial** |
| REQ-8 / W0 | Handoff + baton dual-write | ADR-008 path live (`read_path`); skill packages dual-write | orchestrator ingest tests | — | **exists** (reuse) |
| REQ-9…11 / W1 | Learning Postgres ingest; no skill HTTP | No learning schema/repo/parser | none | none | **gap** |
| REQ-12 / W1 | Ground cites L-* | Pin `ground-spec` SKILL owns cite; Gateflow does not author | — | inspection later | **partial** (pin-owned) |
| REQ-13 / W0 | Optional `prior_run_id` | No field on start models / runs link column | — | — | **gap** |
| REQ-14…15 / W2 | Live closeout prove-it | No `verify_wave_closeout` | — | missing | **gap** |
| REQ-16 / W2 | No hardcoded old checkpoint ids in `src/` | `src/` clean; tests still mock `wave-human-decision` | `test_trigger_policy.py`, `test_notifier.py` | — | **partial** |
| REQ-17 / W2 | As-built + feature map | Draft as-built rows; `tests/README.md` mentions closeout in Pass-1 prose only | — | — | **partial** |

## ADR traceability (F13)

| Spec REQ / wave | Relevant ADR(s) | Status | Finding |
|-----------------|-----------------|--------|---------|
| REQ-1…6 / W0 | ADR-005, ADR-010 (intake surfaces) | aligned + PE confirm closeout vs NEW-ADR | FF-05 |
| REQ-5 / W0 | ADR-007 | aligned | — |
| REQ-7…8 / W0 | ADR-008, ADR-009 | aligned | — |
| REQ-9…11 / W1 | ADR-001 (+ TDD data contract) | aligned; schema TBD | FF-04 |
| REQ-11 | ADR-003 (business owns ingest) | aligned | — |
| Overall | Spec “no new ADR by default” | OK if TDD extends ADR-010/005 narrative; else NEW-ADR | FF-05 |

## Governance findings (F13–F14)

| ID | Check | Spec quote | Governing doc | Finding |
|----|-------|------------|---------------|---------|
| FF-05 | F13 | “No new ADR by default — closeout is a named wave-start phase” | ADR-010 (two lane starts only) | Closeout is a **third** authenticated mutation surface. Not a contradiction yet — TDD must either extend ADR-010/005 or open NEW-ADR. |
| FF-06 | F14 | Body in `src/models/`; POST JSON | `http-api-conventions.mdc`, `pydantic-schemas.mdc` | Spec aligns; implementation must not inline models in `api/`. |
| FF-07 | F14 | Human Alembic for learning tables | `database-migrations.mdc`, ADR-001 | Spec aligns; agent must not commit `versions/` DDL. |

## Findings by severity

### Critical

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| — | — | None | No Accepted ADR contradiction |

### Should fix

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-01 | F1 / freshness | Gate 1 digests APPROVED head missing — freshness STALE; blocks formal CURRENT / `spec-lgtm` package | Spec header TBD fields; Q-1 |
| FF-02 | F3 / F6 | Spec names `verify_wave_closeout` (REQ-14) but no script and no feature-map row yet | `tests/verify/` listing; `tests/README.md` Pass-1 only |
| FF-03 | F4 | No planned unit module named for closeout accept / learning ingest yet | No `test_wave_closeout.py` / learning parser tests |
| FF-04 | F2 / F13 | Learning table/column contract deferred entirely to TDD (CTR-G2) — must land before W1 implement | Spec REQ-9/10; no ORM beyond run store |
| FF-05 | F13 | Confirm ADR-010/005 extension vs NEW-ADR for closeout intake authority | Spec Architecture line vs ADR-010 option B (two starts) |

### Verify

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-08 | F10 / A-7 | Park-ack API for `live-verify`→`wave-awaiting-closeout` deferred — confirm closeout allowed after `stopped@live-verify` only | Spec A-7 / Q-3; pin park terminal |
| FF-09 | F10 / Q-4 | Ingest timing (after `learning-extract` vs after `ground-spec`) unresolved | Spec Q-4; default after learning-extract hop |
| FF-10 | F7 | Separate unit (accept/bind/ingest) from live Pass-2 journey — avoid duplicating full HTTP in pytest | `testing-verify-flows.mdc`; planned `verify_wave_closeout` |
| FF-11 | F3 / concurrency | Document that `find_active_run` only blocks **ACTIVE** — stopped Pass-1 must not block closeout on same PR/wave | `run_store_repository.py` `find_active_run`; REQ-3 |

### Gap

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-12 | F2 | Closeout route, models, service method absent | `waves_routes.py` |
| FF-13 | F2 | Learning parse/repo/schema absent | `run_store_schema.py` |
| FF-14 | F16 | Unit mocks still use `wave-human-decision` (not `src/` runtime) | `test_trigger_policy.py`, `test_notifier.py` |

## Impact surface

| Wave / area | Likely files/modules | Test touch |
|-------------|----------------------|------------|
| W0 closeout API | `waves_routes.py`, `wave_start_models.py` (or `wave_closeout_models.py`), `wave_start_service.py` (or dedicated service), DI getters | `test_wave_closeout.py`, extend programme-token API tests |
| W0 walker Enter-at | Job payload `start_node=learning-extract`; reuse orchestrator | `test_run_orchestrator` Pass-2 chain fixture |
| W1 learning ingest | New schema module under `database/postgres/schema/`, repository, pydantic models, orchestrator/business ingest hook | parser unit + repo unit |
| W2 prove-it | `tests/verify/verify_wave_closeout.py`, `tests/README.md`, as-built | live opt-in |
| Hygiene | Retarget mock node ids in policy/notifier tests | `test_trigger_policy`, `test_notifier` |

## Risks & assumptions

| ID | Risk / assumption | Mitigation |
|----|-------------------|------------|
| R-1 | Gate 1 never lands → package cannot claim CURRENT | Q-1 waive or thin meta PRD before board-seed |
| R-2 | Spec-lane Pass-1 still pin-manual → closeout live for spec deferred | REQ-15 / Q-6; implement-first live |
| R-3 | Learning YAML shape drifts vs pin template | Cite pin template; fail closed on unknown class |
| R-4 | Treating closeout as “just another start_node” on lane routes | Spec forbids — keep dedicated route (REQ-1/2) |
| A-7 | No park-ack API in v1 | Default Q-3; revisit if UI needs park status |

## Recommended spec edits

- Record feasibility digest + link this report in as-built INIT-007 notes (on merge/wave) — optional on this PR.
- After PE answers Q-3/Q-4/Q-5/Q-7, update Spec questions Status column (same branch).
- Do **not** invent learning DDL in the product INIT — leave CTR-G2 to TDD (already stated).

---

## Open items by lane

| ID | Lane | Question / item | Blocking | Owner | Status | Required by | Default if deferred | Evidence | Resolution reference |
|----|------|-----------------|----------|-------|--------|-------------|---------------------|----------|----------------------|
| Q-1 | PM | Retrospective Gate 1 meta PRD / Impact-Map vs PE waive | yes for formal Gate 2 CURRENT | PE/PM | open | board-seed / spec-lgtm | Engineering draft proceeds waived | Spec header TBD; FF-01 | pending |
| Q-3 | PE | Explicit park-ack API `live-verify`→`wave-awaiting-closeout`? | no | PE | open | TDD W0 | No — closeout after `stopped@live-verify` | Spec A-7; FF-08 | pending TDD |
| Q-4 | PE | Learning ingest after `learning-extract` vs after `ground-spec`? | no | PE | open | TDD W1 | After successful `learning-extract` hop | Spec Q-4; FF-09 | pending TDD |
| Q-5 | PE | `prior_run_id` optional vs required? | no | PE | open | TDD W0 | Optional (REQ-13) | Spec Q-5 | pending TDD |
| Q-6 | PE | Spec-lane live prove-it in W2 vs implement-first? | no | PE | open | plan W2 | Both in scope; implement live first if time-box | Spec Q-6 / REQ-15 | pending TDD/plan |
| Q-7 | PE | Learning HTTP read API in 007? | no | PE | open | TDD W1 | DB + repository only | Spec Q-7 | pending TDD |
| FF-05 | PE | ADR-010/005 extension vs NEW-ADR for closeout intake | no for draft; yes before plan if ADR_REQUIRED | PE | open | technical review | Extend ADR-010 narrative; no NEW-ADR | ADR-010 vs REQ-1 | pending TDD |
| FF-04 | PE | Learning table / JSONB item shape (CTR-G2) | yes for W1 implement | PE | open | technical review | TDD data-contract section | REQ-9/10 | pending TDD |
| FF-02 | auto-fix | Add feature-map + verify script name when W2 lands | no | eng | open | W2 | `verify_wave_closeout` as named in REQ-14 | FF-02 | plan TASK |
| FF-14 | auto-fix | Retarget test mocks off `wave-human-decision` | no | eng | open | W2 / hygiene | Use `wave-signoff` / `live-verify` in mocks | `test_trigger_policy.py` | plan TASK |

### PM questions (product scope, UX, priority)

#### Blocking — must resolve before formal Gate 2 CURRENT / board-seed
1. **Q-1** — Provide retrospective meta PRD + Impact-Map + APPROVED head, or explicit PE waive of Gate 1 for this pin-driven INIT.

#### Defer — can proceed with documented assumption
1. None beyond Q-1 waive already assumed for engineering Draft.

### PE questions (engineering decisions — resolved by `/spec-technical-review`)

#### Blocking for implementation plan
1. **FF-04** — Learning data contract (tables, item JSONB/Pydantic, indexes, link to `run_id` / initiative / wave / PR).
2. **FF-05** — Closeout intake authority: extend ADR-010/005 vs NEW-ADR.

#### Defer with default
1. **Q-3** — No park-ack API (default).
2. **Q-4** — Ingest after `learning-extract` hop (default); publish-before-ingest if forge applies.
3. **Q-5** — `prior_run_id` optional.
4. **Q-6** — Implement live first; spec parity unit + as-built deferral if needed.
5. **Q-7** — No public learning read API in 007.
6. **FF-11** — Concurrent ACTIVE only; document Pass-1 stopped → closeout OK.

### Domain clarifications (business source-of-truth)

| # | Question | Suggested SME | Blocks |
|---|----------|---------------|--------|
| — | None identified beyond pin taxonomy (SPEC/SKILL/HARNESS/ENV) already closed upstream | prayog-skills | — |

### Auto-fixable (agent resolves — no human needed)

| # | Item | Fix |
|---|------|-----|
| AF-1 | Feature map / verify script when W2 coded | Add `verify_wave_closeout` + README row |
| AF-2 | Mock checkpoint ids in unit tests | Prefer `wave-signoff` / `live-verify` |
| AF-3 | As-built INIT-007 matrix after waves | Fill code/unit/live columns |

---

## Check summary

| Check | Status | Findings |
|-------|--------|----------|
| F1 Baseline snapshot | PASS | Baseline recorded; freshness WAIVED (FF-01) |
| F2 Spec → code map | FAIL | Closeout + learning gaps (FF-12, FF-13) — expected |
| F3 Spec → verify map | FAIL | No `verify_wave_closeout` (FF-02) |
| F4 Spec → unit map | FAIL | No closeout/learning units yet (FF-03) |
| F5 As-built drift | PASS | Spec baseline matches as-built “not implemented” |
| F6 Docs drift | PARTIAL | README mentions Pass-2 in prose; no closeout feature row (FF-02) |
| F7 Overlap risk | PASS | Plan unit vs live separation (FF-10) |
| F8 CI vs live | PASS | CI = check/test; closeout live opt-in like implement-lane |
| F9 Cross-service | PASS | Pin packages + CTRs cited; forge reuse |
| F10 Assumptions | PARTIAL | A-7/Q-3/Q-4 open (FF-08, FF-09) |
| F11 Effort drivers | PASS | See Impact surface — new API + schema + verify |
| F12 PM questions | PASS | Q-1 numbered |
| F13 ADR conformance | PASS | No Critical conflict; FF-05/FF-04 PE |
| F14 MDC conformance | PASS | FF-06/FF-07 notes only |

---

## Next steps

> This report lives on the Draft spec PR [#77](https://github.com/drivestream-lab/gateflow/pull/77) (`spec-pending`).

**PM questions** → meta PRD PR when Q-1 opens; until then PE waive is the path.

**PE questions** → discuss on Draft spec PR; run **`/spec-technical-review`** next
(findings outcome — learning data contract + closeout ADR disposition).

**Domain clarifications** — none.

**Auto-fixable** → at implement/W2, not blocking TDD.

```
Draft spec PR: chore/INIT-GATEFLOW-007-spec-gateflow  (#77, spec-pending)
When ready:
  [ ] Source freshness is CURRENT (or PE-recorded Gate 1 waive)
  [ ] Blocking PM Q-1 answered or waived in writing
  [ ] Proceed: /spec-technical-review  ← next (PE questions exist)
  [ ] Then /spec-implementation-plan
  [ ] PE sets spec-lgtm + Approve on exact head → Ready for review → merge
  [ ] After merge: /create-board-tickets from plan §9
```

## Handoff envelope

```yaml
handoff:
  schema_version: "1"
  contract: "sdd-delivery/v2"
  stage: initiative-feasibility
  outcome: findings
  initiative: INIT-GATEFLOW-007
  human_checkpoint: false
  external_action: false
  next_candidates:
    - spec-technical-review
  artifact:
    path: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-007.md
  signals:
    lane_counts:
      pm: 1
      pe: 8
      domain: 0
      auto_fix: 3
    new_adr: possible  # FF-05 — confirm in TDD
    source_freshness: STALE_WAIVED
    ripple_action: continue
  blockers:
    - FF-01
    - FF-04
  notes:
    - Buildable on pin Pass-2 + INIT-001…006 control plane
    - Closeout API + learning DB are greenfield gaps (expected)
    - Gate 2 label remains spec-pending
  forge:
    action: commit_workspace
    # same Draft PR #77 tip — do not open a second spec PR
```
