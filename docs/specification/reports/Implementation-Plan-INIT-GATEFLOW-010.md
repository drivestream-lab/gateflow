---
goal: INIT-GATEFLOW-010 — eng-lane pin tip executor parity
initiative: INIT-GATEFLOW-010
status: Planned
date_created: 2026-08-05
source_spec: docs/specification/product/INIT-GATEFLOW-010-gateflow.md
source_spec_digest: sha256:f98e101a508407dcebaa5fd0fc9033744dbed24a388c4e50c4303f687b4d91ea
feasibility_report: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-010.md
feasibility_digest: sha256:8c1b5fcd732fba05863931d9fd51334f64bb3f4263a7073d6b1f2dfbdb06bd7b
technical_review: docs/specification/reports/Technical-Review-INIT-GATEFLOW-010.md
technical_review_digest: sha256:894ac27f4532c8d62384b7200d4fc77e115570ffb742e4ee03aa401b3db9286c
prd_digest: sha256:457f19617113171c973abdbc15d1afaa00df2f6947ab4567b57d8440bd88b206
impact_map: prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-010.md
impact_map_revision: 1
repo_scope_digest: sha256:09c89c143c14401c8812738c162c05a2f5e504cabafd1818ee72eb4e9b781532
approved_meta_pr_head: df0f5a5c09b6c4f951463bb42f277305310aaa80
branch: feature/INIT-GATEFLOW-010-w0-spec-lane
review_deadline: 2026-08-12
deciders: PE @drivestream-lab/prayog-pe-team — spec-lgtm + Approve on exact head after full package
---

# Implementation plan — INIT-GATEFLOW-010

## Source freshness and command contract

| Item | Value | Status |
|------|-------|--------|
| Spec / digest | `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` / `sha256:f98e101a508407dcebaa5fd0fc9033744dbed24a388c4e50c4303f687b4d91ea` | CURRENT |
| Feasibility / digest | `…/Initiative-Feasibility-Report-INIT-GATEFLOW-010.md` / `sha256:8c1b5fcd732fba05863931d9fd51334f64bb3f4263a7073d6b1f2dfbdb06bd7b` | CURRENT — **Accepted** |
| Technical review / digest | `…/Technical-Review-INIT-GATEFLOW-010.md` / `sha256:894ac27f4532c8d62384b7200d4fc77e115570ffb742e4ee03aa401b3db9286c` | CURRENT — **Accepted** |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-010.md` / `1` | CURRENT |
| Repo scope digest | `sha256:09c89c143c14401c8812738c162c05a2f5e504cabafd1818ee72eb4e9b781532` | CURRENT |
| Approved meta PR head | `df0f5a5c09b6c4f951463bb42f277305310aaa80` | CURRENT (G1) |
| `check_command` | `make check` | RESOLVED |
| `test_command` | `make test` | RESOLVED |
| `verify_command` | Per wave under `tests/verify/` — W0: N/A (P15 N/A); W1: `.venv/bin/python -m tests.verify.verify_implement_lane`; W2: `.venv/bin/python -m tests.verify.verify_wave_start` (+ board asserts); W3: `.venv/bin/python -m tests.verify.verify_wave_closeout` + `verify_spec_lane`; W4: `.venv/bin/python -m tests.verify.verify_closure` | RESOLVED |
| `ground_command` | N/A — `/ground-spec` is Pass-2 pin skill, not a Makefile target | N/A |

> W0 is unit-only per PRD §5 / Q-3. W1–W4 co-ship live verify when product surfaces change (P15).

## 0. Technical design reference

| Item | Value |
|------|-------|
| Technical review | [`Technical-Review-INIT-GATEFLOW-010.md`](Technical-Review-INIT-GATEFLOW-010.md) |
| PE sign-off | [x] complete — 2026-08-05 (Cursor chat: accept package docs; ADR hygiene; proceed to `/spec-implementation-plan`) |
| Resolved ADRs | [`adr-009-pin-forge-publish-mutate-authority.md`](../adr/adr-009-pin-forge-publish-mutate-authority.md) (**Accepted**, hygiene strip); [`adr-010-lane-intake-and-dual-workspace-authority.md`](../adr/adr-010-lane-intake-and-dual-workspace-authority.md) (**Accepted**, closeout §6 + **closure §7**); ADR-001/003/005 **Accepted** — **ADR_REQUIRED=0; no ADR-011** |
| Outstanding PM questions | Q-2 (non-blocking — parallel meta PRs; default proceed) |
| Outstanding domain questions | none |

> Do not start W0 coding until this plan is on tip with `spec-lgtm` + Approve
> (coding-readiness), then merge + `/create-board-tickets`.

---

## 1. Requirements (REQ) — product ids

| ID | Summary | Spec path | Waves |
|----|---------|-----------|-------|
| REQ-01 | Consume pin `v0.5.0-rc.2`; harness ref == submodule tip | `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` | W0 |
| REQ-02 | Parse `update_board_status` + status + ticket requires; 0 BROKEN nodes | same | W0 |
| REQ-03 | APPLY_FORGE board-status hop updates board ticket | same | W1 |
| REQ-04 | Implement-start applies In Progress before pre-implement (idempotent) | same | W1 |
| REQ-05 | Closeout applies Done after ground-spec.pass; purpose at wave-signoff | same | W3 |
| REQ-06 | Create-tickets hard-fails unless triple predicates pass | same | W2 |
| REQ-07 | Create success returns `epic_ticket_id` + non-empty `wave_ticket_ids[]` | same | W2 |
| REQ-08 | Implement-start board-resolved ticket gate (400/422; 0 enqueue) | same | W2 |
| REQ-09 | No Forge merge | same | W3 |
| REQ-10 | Stop payload includes pin `purpose` / `owner` when present | same | W0 |
| REQ-11 | Create-tickets does not resume into implement on same run | same | W1 |
| REQ-12 | `POST /api/v1/initiatives/closure/start` → 202 + run_id | same | W4 |
| REQ-13 | Closure Done-gate on all wave tickets | same | W4 |
| REQ-14 | EPIC → Done before purge-app dispatch | same | W4 |
| REQ-15 | Closure walk purge-app → closure PR → signoff-app; never purge-meta | same | W4 |
| REQ-16 | Never auto-apply `*-lgtm` | same | W3 |
| REQ-17 | Verify suite covers lanes (partial W2–W4) | same | W2, W3, W4 |
| REQ-18 | Feature-readiness freeze doc | same | W4 |
| REQ-19 | No auto-chain after wave-signoff to next wave/closure | same | W3 |
| REQ-20 | Partial closure failure recorded; no success claim | same | W4 |

---

## 2. Implementation phases

### Phase W0 — Pin parse parity + purpose/owner on stops

**GOAL-W0:** Remounted pin nodes including board-status hops `get_node` without
error; `ResolvedWorkflowNode` + `run_stopped` carry pin `purpose`/`owner` when
present. **No new HTTP surface** (P15 N/A — unit only per Q-3).

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W0-01 | Confirm harness `agent_skills.ref` exact-matches submodule tip; note in as-built | REQ-01 | — | `.harness-pin.yaml` inspect; `docs/specification/as-built/implementation-status.md` modify | `git -C prayog-skills describe --exact-match` equals pin ref | command / `git -C prayog-skills rev-parse HEAD && git -C prayog-skills describe --exact-match HEAD` | tip matches `v0.5.0-rc.2` / SHA | Wave-Execution-INIT-GATEFLOW-010-W0.md § TASK-W0-01 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` | `N/A — P15 N/A` | fail-fast.mdc | ADR-009 | `feature/INIT-GATEFLOW-010-w0-pin-parse` |
| TASK-W0-02 | Assert remounted pin board-status nodes parse (action, status, ticket requires); 0 BROKEN `get_node` | REQ-02 | TASK-W0-01 | `tests/unit/test_forge_policy.py` modify | Unit matrix green for `update_board_status` nodes; invalid status fails closed | command / `make check && make test` | exit 0; parse tests pass | Wave-Execution-INIT-GATEFLOW-010-W0.md § TASK-W0-02 | drivestream-lab/gateflow | same | `N/A — P15 N/A` | fail-fast.mdc | ADR-009 | same |
| TASK-W0-03 | Add optional `purpose`/`owner` on `ResolvedWorkflowNode`; parse in WorkflowEngine | REQ-10 | TASK-W0-01 | `src/models/handoff_models.py` modify; `src/business_services/workflow_engine.py` modify | Fields present when pin sets them; absent → None | command / `make check && make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-010-W0.md § TASK-W0-03 | drivestream-lab/gateflow | same | `N/A — P15 N/A` | pydantic-schemas.mdc, strong-typing.mdc | ADR-009 | same |
| TASK-W0-04 | Emit `purpose`/`owner` on `run_stopped` from resolved stop node | REQ-10 | TASK-W0-03 | `src/business_services/run_orchestrator.py` modify; unit tests modify/create | Stop at human-checkpoint / gate with pin purpose includes keys | command / `make test` | exit 0; REQ-10 assertions pass | Wave-Execution-INIT-GATEFLOW-010-W0.md § TASK-W0-04 | drivestream-lab/gateflow | same | `N/A — P15 N/A` | logging-loguru.mdc | — | same |
| TASK-W0-05 | As-built INIT-010 W0 row (FF-02) | REQ-01, REQ-02, REQ-10 | TASK-W0-04 | `docs/specification/as-built/implementation-status.md` modify | Row reflects W0 unit-proven state | review / as-built | accurate W0 status | Wave-Execution-INIT-GATEFLOW-010-W0.md § TASK-W0-05 | drivestream-lab/gateflow | same | `N/A — P15 N/A` | SDD | — | same |

#### Files (W0)

| ID | Path | Action |
|----|------|--------|
| FILE-W0-01 | `.harness-pin.yaml` | inspect |
| FILE-W0-02 | `src/models/handoff_models.py` | modify |
| FILE-W0-03 | `src/business_services/workflow_engine.py` | modify |
| FILE-W0-04 | `src/business_services/run_orchestrator.py` | modify |
| FILE-W0-05 | `tests/unit/test_forge_policy.py` | modify |
| FILE-W0-06 | `tests/unit/test_run_orchestrator.py` (or new REQ-10 module) | modify/create |
| FILE-W0-07 | `docs/specification/as-built/implementation-status.md` | modify |

#### Tests (W0)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W0-U | unit | `make test` | REQ-02, REQ-10 / TASK-W0-02..04 |
| TEST-W0-I | integration/contract | N/A | — |
| TEST-W0-L | live | N/A — P15 N/A | — |

#### Verification Coverage (W0)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-01 | inspect | N/A | N/A | N/A | tip match |
| REQ-02 | TEST-W0-U | N/A | N/A | N/A | |
| REQ-10 | TEST-W0-U | N/A | N/A | N/A | |

#### Live-verification intent (W0)

| Field | Value |
|-------|-------|
| Applicable | **no** — parse + stop payload only; no new callable product surface (P15 N/A; Q-3) |
| Mode | N/A |
| Cleanup / Stop | N/A |

---

### Phase W1 — Board-status apply + implement In Progress

**GOAL-W1:** APPLY_FORGE `update_board_status`; implement-start sets In Progress
before pre-implement (idempotent); create-tickets still does not resume
implement. **P15:** extend live implement-lane / wave-start asserts.

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W1-01 | `ForgeActionService` apply branch for `update_board_status` via BoardService; missing ticket fail closed | REQ-03 | — | `src/business_services/forge_action_service.py` modify; unit tests modify | Unit: status applied; missing ticket → hop fail | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-010-W1.md § TASK-W1-01 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` | `.venv/bin/python -m tests.verify.verify_implement_lane` | architecture.mdc, fail-fast.mdc | ADR-009, ADR-003 | `feature/INIT-GATEFLOW-010-w1-board-status` |
| TASK-W1-02 | Implement-start: In Progress for `ticket_id` before enqueue; idempotent if already in_progress | REQ-04 | TASK-W1-01 | wave start routes/service modify; `tests/unit/test_wave_start.py` modify | Unit: board update called; already in_progress OK | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-010-W1.md § TASK-W1-02 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_implement_lane` | http-api-conventions.mdc | ADR-010 | same |
| TASK-W1-03 | Guard: create-tickets success does not dispatch pre-implement on same run | REQ-11 | — | policy/orchestrator tests modify | Unit: no same-run resume | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-010-W1.md § TASK-W1-03 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_implement_lane` | fail-fast.mdc | ADR-010 | same |
| TASK-W1-04 | Co-ship live asserts: board In Progress on implement path when worker on; README feature map | REQ-03, REQ-04, REQ-17 | TASK-W1-02 | `tests/verify/verify_implement_lane.py` modify; `tests/README.md` modify | Script asserts In Progress / board-status hop evidence under knobs | command / `.venv/bin/python -m tests.verify.verify_implement_lane` | exit 0 or documented skip (fail closed if claiming pass without check) | Live-Verify-INIT-GATEFLOW-010-W1.md | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_implement_lane` | testing-verify-flows.mdc | ADR-009 | same |
| TASK-W1-05 | As-built W1 row | REQ-03, REQ-04, REQ-11 | TASK-W1-04 | `docs/specification/as-built/implementation-status.md` modify | Accurate W1 status | review | rows updated | Wave-Execution-INIT-GATEFLOW-010-W1.md § TASK-W1-05 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_implement_lane` | SDD | — | same |

#### Files (W1)

| ID | Path | Action |
|----|------|--------|
| FILE-W1-01 | `src/business_services/forge_action_service.py` | modify |
| FILE-W1-02 | `src/api/v1/` wave start module(s) | modify |
| FILE-W1-03 | `tests/unit/test_forge_action_service.py` | modify |
| FILE-W1-04 | `tests/unit/test_wave_start.py` | modify |
| FILE-W1-05 | `tests/verify/verify_implement_lane.py` | modify |
| FILE-W1-06 | `tests/README.md` | modify |
| FILE-W1-07 | `docs/specification/as-built/implementation-status.md` | modify |

#### Tests (W1)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W1-U | unit | `make test` | REQ-03, REQ-04, REQ-11 |
| TEST-W1-L | live smoke | `.venv/bin/python -m tests.verify.verify_implement_lane` | REQ-03, REQ-04 / TASK-W1-04 |

#### Verification Coverage (W1)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-03 | TEST-W1-U | N/A | TEST-W1-L | N/A | P15 |
| REQ-04 | TEST-W1-U | N/A | TEST-W1-L | N/A | P15 |
| REQ-11 | TEST-W1-U | N/A | secondary | N/A | |
| REQ-17 (partial) | N/A | N/A | TEST-W1-L | N/A | |

#### Live-verification intent (W1)

| Field | Value |
|-------|-------|
| Applicable | **yes** — board-status apply + implement In Progress are product surfaces (P15) |
| Environment class | local-compose (API + worker + forge/board creds per `tests/config.yaml`) |
| Mode | smoke |
| Runtime head binding | Bound at `live-verify` against wave PR head |
| Prerequisites | API up; forge/board credentials; `require_worker` when asserting hops |
| Safe test data | Ephemeral initiative/ticket — no prod |
| Steps / command | `.venv/bin/python -m tests.verify.verify_implement_lane` |
| Expected observations | Bound ticket reaches In Progress before coding; board-status hop when exercised |
| Expected evidence | `Live-Verify-INIT-GATEFLOW-010-W1.md` |
| Cleanup | Close ephemeral run/PR per script |
| Stop conditions | Non-zero exit or unexpected 5xx → stop |

---

### Phase W2 — Ticket gates + create predicates

**GOAL-W2:** Create-tickets triple predicate gate; implement-start board ticket
validation (400/422); create returns epic + wave ids. **P15:** extend
`verify_wave_start` / `verify_board` (+ README).

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W2-01 | Authorize/apply create-tickets: require `spec-pr-merged`, `implementation-plan-current`, `workmanifest-contract-pass`; else 422 + 0 creates | REQ-06 | — | forge authorize / `forge_action_service` / policy modify; unit tests | Unit negatives: any predicate fail → 422; 0 tickets | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-010-W2.md § TASK-W2-01 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` | `.venv/bin/python -m tests.verify.verify_board` | fail-fast.mdc | ADR-009 | `feature/INIT-GATEFLOW-010-w2-ticket-gates` |
| TASK-W2-02 | Create success response includes `epic_ticket_id` + non-empty `wave_ticket_ids[]` | REQ-07 | TASK-W2-01 | forge action / response models modify; unit tests | Unit: fields present on success | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-010-W2.md § TASK-W2-02 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_board` | pydantic-schemas.mdc | ADR-009 | same |
| TASK-W2-03 | Implement-start ticket gate: missing/malformed → 400; unresolvable/mismatch/Done → 422; 0 enqueue | REQ-08 | — | wave start validators modify; unit tests | Unit matrix matches PRD error table | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-010-W2.md § TASK-W2-03 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_wave_start` | http-api-conventions.mdc | ADR-010 | same |
| TASK-W2-04 | Co-ship live: negative ticket / create predicate cases (or documented authorize path) + README | REQ-06, REQ-08, REQ-17 | TASK-W2-03 | `tests/verify/verify_wave_start.py` and/or `verify_board.py` modify; `tests/README.md` modify | Live script asserts 400/422 side-effect table under knobs | command / `.venv/bin/python -m tests.verify.verify_wave_start` | exit 0 under prereqs | Live-Verify-INIT-GATEFLOW-010-W2.md | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_wave_start` | testing-verify-flows.mdc | ADR-010 | same |
| TASK-W2-05 | As-built W2 row | REQ-06–08, REQ-17 | TASK-W2-04 | `docs/specification/as-built/implementation-status.md` modify | Accurate W2 status | review | rows updated | Wave-Execution-INIT-GATEFLOW-010-W2.md § TASK-W2-05 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_wave_start` | SDD | — | same |

#### Files (W2)

| ID | Path | Action |
|----|------|--------|
| FILE-W2-01 | `src/business_services/forge_action_service.py` (and/or authorize path) | modify |
| FILE-W2-02 | wave start validators / routes | modify |
| FILE-W2-03 | `tests/unit/test_forge_action_service.py` | modify |
| FILE-W2-04 | `tests/unit/test_wave_start.py` | modify |
| FILE-W2-05 | `tests/verify/verify_wave_start.py` | modify |
| FILE-W2-06 | `tests/verify/verify_board.py` | modify |
| FILE-W2-07 | `tests/README.md` | modify |
| FILE-W2-08 | `docs/specification/as-built/implementation-status.md` | modify |

#### Tests (W2)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W2-U | unit | `make test` | REQ-06–08 |
| TEST-W2-L | live smoke | `.venv/bin/python -m tests.verify.verify_wave_start` | REQ-08, REQ-17; board script for REQ-06/07 |

#### Verification Coverage (W2)

| REQ / criterion | unit | smoke | Notes |
|-----------------|------|-------|-------|
| REQ-06, REQ-07 | TEST-W2-U | verify_board (TASK-W2-04) | P15 |
| REQ-08 | TEST-W2-U | TEST-W2-L | P15 |
| REQ-17 (partial) | N/A | TEST-W2-L | |

#### Live-verification intent (W2)

| Field | Value |
|-------|-------|
| Applicable | **yes** — ticket/create gates are API product surfaces (P15) |
| Environment class | local-compose |
| Mode | smoke |
| Steps / command | `.venv/bin/python -m tests.verify.verify_wave_start` (+ `verify_board` as needed) |
| Expected evidence | `Live-Verify-INIT-GATEFLOW-010-W2.md` |
| Cleanup | Ephemeral tickets/runs per script |
| Stop conditions | Non-zero / unexpected 5xx → stop |

---

### Phase W3 — Closeout Done + no merge/lgtm + no auto-chain

**GOAL-W3:** Closeout applies Done after ground-spec.pass; terminal purpose;
never merge; never `*-lgtm`; no auto-start next wave/closure. **P15:**
`verify_wave_closeout` + `verify_spec_lane`.

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W3-01 | Closeout walk applies Done hop after ground-spec.pass; stop at wave-signoff with purpose | REQ-05 | — | orchestrator / closeout path modify; unit tests | Unit timeline includes Done; purpose on terminal stop | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-010-W3.md § TASK-W3-01 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` | `.venv/bin/python -m tests.verify.verify_wave_closeout` | fail-fast.mdc | ADR-009, ADR-010 | `feature/INIT-GATEFLOW-010-w3-closeout-done` |
| TASK-W3-02 | Code guards: no Forge merge action; refuse `*-lgtm` apply_labels | REQ-09, REQ-16 | — | forge_action_service / parse guards; unit tests | Unit: merge absent; lgtm rejected | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-010-W3.md § TASK-W3-02 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_wave_closeout` | fail-fast.mdc | ADR-009 | same |
| TASK-W3-03 | After wave-signoff / wave-complete: no auto enqueue next wave or closure | REQ-19 | TASK-W3-01 | orchestrator / policy modify; unit tests | Unit: terminal stop does not chain | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-010-W3.md § TASK-W3-03 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_wave_closeout` | fail-fast.mdc | ADR-010 | same |
| TASK-W3-04 | Co-ship live closeout Done + purpose; spec Pass-1 verify green under knobs; README | REQ-05, REQ-17, REQ-19 | TASK-W3-03 | `tests/verify/verify_wave_closeout.py` modify; `verify_spec_lane.py` as needed; `tests/README.md` modify | Live asserts Done hop / terminal purpose / no auto-chain | command / `.venv/bin/python -m tests.verify.verify_wave_closeout` | exit 0 under dogfood knobs | Live-Verify-INIT-GATEFLOW-010-W3.md | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_wave_closeout` | testing-verify-flows.mdc | ADR-010 | same |
| TASK-W3-05 | As-built W3 row | REQ-05, REQ-09, REQ-16, REQ-19 | TASK-W3-04 | `docs/specification/as-built/implementation-status.md` modify | Accurate W3 status | review | rows updated | Wave-Execution-INIT-GATEFLOW-010-W3.md § TASK-W3-05 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_wave_closeout` | SDD | — | same |

#### Files (W3)

| ID | Path | Action |
|----|------|--------|
| FILE-W3-01 | `src/business_services/run_orchestrator.py` | modify |
| FILE-W3-02 | closeout / forge guards | modify |
| FILE-W3-03 | `tests/unit/test_wave_closeout.py` | modify |
| FILE-W3-04 | `tests/verify/verify_wave_closeout.py` | modify |
| FILE-W3-05 | `tests/verify/verify_spec_lane.py` | modify |
| FILE-W3-06 | `tests/README.md` | modify |
| FILE-W3-07 | `docs/specification/as-built/implementation-status.md` | modify |

#### Tests (W3)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W3-U | unit | `make test` | REQ-05, REQ-09, REQ-16, REQ-19 |
| TEST-W3-L | live smoke | `.venv/bin/python -m tests.verify.verify_wave_closeout` | REQ-05, REQ-17, REQ-19 |

#### Verification Coverage (W3)

| REQ / criterion | unit | smoke | Notes |
|-----------------|------|-------|-------|
| REQ-05, REQ-19 | TEST-W3-U | TEST-W3-L | P15 |
| REQ-09, REQ-16 | TEST-W3-U | secondary | |
| REQ-17 | N/A | TEST-W3-L + spec_lane | |

#### Live-verification intent (W3)

| Field | Value |
|-------|-------|
| Applicable | **yes** — closeout Done / terminal stop behavior (P15) |
| Mode | smoke (dogfood when asserting full Pass-2) |
| Steps / command | `.venv/bin/python -m tests.verify.verify_wave_closeout` |
| Expected evidence | `Live-Verify-INIT-GATEFLOW-010-W3.md` |
| Stop conditions | Non-zero / unexpected 5xx → stop |

---

### Phase W4 — Initiative closure Enter-at + freeze

**GOAL-W4:** Closure start route (ADR-010 §7); Done-gate; EPIC Done before
purge-app; purge walk; partial-failure hygiene; freeze doc; **co-ship**
`verify_closure` (P15).

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W4-01 | Add `POST …/initiatives/closure/start` (programme token); Pydantic body; 400 malformed; 202 + run_id | REQ-12 | — | `src/api/` closure routes create; `src/models/` body create; DI wiring | Unit: 400/202 matrix; OpenAPI lists route | command / `make check && make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-010-W4.md § TASK-W4-01 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` | `.venv/bin/python -m tests.verify.verify_closure` | http-api-conventions.mdc, pydantic-schemas.mdc | ADR-010 §7, ADR-005 | `feature/INIT-GATEFLOW-010-w4-closure` |
| TASK-W4-02 | Done-gate validator: any wave not Done → 422; 0 enqueue; EPIC untouched | REQ-13 | TASK-W4-01 | closure service/validator create; unit negatives | Unit: 422 + no side effects | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-010-W4.md § TASK-W4-02 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_closure` | fail-fast.mdc | ADR-010 §7 | same |
| TASK-W4-03 | After Done-gate: EPIC → Done then enqueue fixed Enter-at; walk purge-app → closure PR → signoff; never purge-meta | REQ-14, REQ-15 | TASK-W4-02 | board_service + orchestrator enqueue; unit/integration tests | Unit/timeline: EPIC Done before purge; no meta purge | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-010-W4.md § TASK-W4-03 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_closure` | architecture.mdc | ADR-010 §7, ADR-009 | same |
| TASK-W4-04 | Partial failure after EPIC Done: record failure; no closure-complete claim | REQ-20 | TASK-W4-03 | orchestrator failure path; unit test | Unit: failure recorded; success claim absent | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-010-W4.md § TASK-W4-04 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_closure` | fail-fast.mdc, logging-loguru.mdc | ADR-001 | same |
| TASK-W4-05 | Create `tests/verify/verify_closure.py` + README feature map; live 400/422/202 + Done-gate | REQ-12, REQ-13, REQ-17 | TASK-W4-04 | `tests/verify/verify_closure.py` create; `tests/README.md` modify | Script exits 0 under knobs; negatives covered | command / `.venv/bin/python -m tests.verify.verify_closure` | exit 0 under prereqs | Live-Verify-INIT-GATEFLOW-010-W4.md | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_closure` | testing-verify-flows.mdc | ADR-010 §7 | same |
| TASK-W4-06 | Feature-readiness freeze doc (proven vs deferred) | REQ-18 | TASK-W4-05 | `docs/specification/reports/Feature-Readiness-INIT-GATEFLOW-010.md` create | Lists proven vs deferred (PM Enter-at, meta purge, ops UI, C2, authorize→resume) | review / file inspect | freeze doc present | Wave-Execution-INIT-GATEFLOW-010-W4.md § TASK-W4-06 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_closure` | SDD | — | same |
| TASK-W4-07 | As-built W4 + initiative freeze row | REQ-12–15, REQ-17–20 | TASK-W4-06 | `docs/specification/as-built/implementation-status.md` modify | Accurate W4 / freeze status | review | rows updated | Wave-Execution-INIT-GATEFLOW-010-W4.md § TASK-W4-07 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_closure` | SDD | — | same |

#### Files (W4)

| ID | Path | Action |
|----|------|--------|
| FILE-W4-01 | `src/api/v1/` closure routes (new module) | create |
| FILE-W4-02 | `src/models/` closure request/response | create |
| FILE-W4-03 | closure business service / validators | create |
| FILE-W4-04 | `src/app.py` / DI modules | modify |
| FILE-W4-05 | `tests/unit/` closure tests | create |
| FILE-W4-06 | `tests/verify/verify_closure.py` | create |
| FILE-W4-07 | `tests/README.md` | modify |
| FILE-W4-08 | `docs/specification/reports/Feature-Readiness-INIT-GATEFLOW-010.md` | create |
| FILE-W4-09 | `docs/specification/as-built/implementation-status.md` | modify |

#### Tests (W4)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W4-U | unit | `make test` | REQ-12–15, REQ-20 |
| TEST-W4-L | live smoke | `.venv/bin/python -m tests.verify.verify_closure` | REQ-12, REQ-13, REQ-17 |

#### Verification Coverage (W4)

| REQ / criterion | unit | smoke | Notes |
|-----------------|------|-------|-------|
| REQ-12–15, REQ-20 | TEST-W4-U | TEST-W4-L | P15 new route |
| REQ-17 | N/A | TEST-W4-L | |
| REQ-18 | review | N/A | freeze doc |

#### Live-verification intent (W4)

| Field | Value |
|-------|-------|
| Applicable | **yes** — new closure Enter-at HTTP surface (P15) |
| Environment class | local-compose |
| Mode | smoke |
| Steps / command | `.venv/bin/python -m tests.verify.verify_closure` |
| Expected observations | 202 + run_id on valid binds; 400/422 per table; Done-gate; no meta purge |
| Expected evidence | `Live-Verify-INIT-GATEFLOW-010-W4.md` |
| Cleanup | Ephemeral closure run; no prod EPIC mutation outside test board |
| Stop conditions | Non-zero / unexpected 5xx → stop |

---

## 3. Dependencies (DEP)

| ID | Dependency | Blocks |
|----|------------|--------|
| DEP-1 | W0 before W1 (parse before apply) | W1 board-status apply |
| DEP-2 | W1 before W2 (In Progress path exists before ticket-gate live) | W2 verify |
| DEP-3 | W2 before W3 (ticket model stable for closeout Done) | W3 |
| DEP-4 | W3 before W4 (waves Done semantics before closure Done-gate) | W4 |
| DEP-5 | Pin tip `v0.5.0-rc.2` frozen (A-3) | all waves |
| DEP-6 | Q-1 OpenAPI field names deferred | W2/W4 OpenAPI polish only — HTTP semantics normative now |

---

## 4. Risks (RISK)

| ID | Risk | Mitigation |
|----|------|------------|
| R-1 | Pin tip retag mid-INIT | A-3 frozen; programme decision required |
| R-2 | Q-1 problem+json field names drift | Defer OpenAPI polish; 400/422 + side-effect table normative |
| R-3 | Product rules leaked into ADRs again | ADR-010 §7 authority-only; REQs SSOT; hygiene strip on 009/010 |
| R-4 | W4 EPIC Done then purge fail (REQ-20) | Explicit failure record; PE re-enter; verify negative path |
| R-5 | Live verify needs forge/board creds | Document knobs in tests/README; fail closed on false pass |

---

## 5. Out of scope

- gateflow-ops UI; prayog-skills pin redesign; `purge-initiative-artifacts-meta`
- PM Enter-at; Forge merge / `delete_branch`; auto `*-lgtm`
- authorize→resume Pass-1; discover waves via `list_tickets` alone
- ADR-011 (withdrawn — folded into ADR-010 §7)

---

## 6. As-built and docs tasks

| Task | File | Action |
|------|------|--------|
| INIT-010 matrix rows per wave | `docs/specification/as-built/implementation-status.md` | W0–W4 TASK-*-05/07 |
| Feature map + verify commands | `tests/README.md` | W1–W4 live tasks |
| Feature-readiness freeze | `docs/specification/reports/Feature-Readiness-INIT-GATEFLOW-010.md` | W4 TASK-W4-06 |

> ADR lifecycle complete — no ADR promotion tasks.

---

## 7. Plan check summary

| Check | Status |
|-------|--------|
| P1 REQ catalogue | PASS — REQ-01…20 in §1 |
| P2 REQ↔TASK | PASS — each REQ has ≥1 TASK |
| P3 FILE paths | PASS |
| P4 Exit evidence | PASS — criteria/proof/expected/evidence on TASK rows |
| P5 Verification layers | PASS — coverage tables per wave |
| P6 Scope | PASS — within spec |
| P7 Feasibility risks | PASS — R-1…R-5; Q-2 deferred |
| P8 Wave order | PASS — DEP-1…4 |
| P9 As-built/docs same PR | PASS — §6 |
| P10 Self-contained + commands | PASS |
| P11 MDC | PASS — notes on TASKs |
| P12 ADR | PASS — ADR_REQUIRED=0; cite Accepted 009/010; no Draft ADR-011 |
| P13 TDD Accepted | PASS — Status Accepted 2026-08-05 |
| P14 WorkManifest seed | PASS — §9 W0–W4 |
| P15 Co-ship live | PASS — W0 N/A; W1–W4 co-ship |
| P16 WorkManifest contract | PASS — validated via `prayog-skills/scripts/workmanifest_contract.py` |

---

## 8. Forge / PR instructions

> Persist this plan locally and publish via `/commit-workspace` to the **Draft
> spec PR** branch alongside spec, feasibility, TDD, and ADR hygiene. Do **not**
> commit inside this skill. Label remains **`spec-pending`** until PE completes §10.

```
Branch:   feature/INIT-GATEFLOW-010-w0-spec-lane  (Draft PR)
PR title: "[INIT-GATEFLOW-010] Spec — eng-lane pin tip executor parity (gateflow)"
Required reviewers: @drivestream-lab/prayog-pe-team
Review deadline: 2026-08-12

PE checklist (before spec-lgtm):
  [ ] Spec + feasibility + TDD (Accepted) + ADR-009/010 hygiene + this plan on current head
  [ ] §0 PE sign-off complete
  [ ] Wave order W0→W4 and P15 co-ship make sense
  [ ] WorkManifest §9 passes workmanifest-contract-pass
  [ ] P1–P16 pass

After spec-lgtm + Approve + merge — `/create-board-tickets` from §9 (post-merge only)
```

---

## 10. Coding-readiness unlock (PE — after plan on head)

| Item | Value |
|------|-------|
| Workflow outcome | `pass` — P1–P16 PASS; sources CURRENT; TDD/ADRs Accepted; plan ready |
| Verdict | GATE OPEN REQUEST |
| Spec PR | Draft on `feature/INIT-GATEFLOW-010-w0-spec-lane` (Forge pending if not yet opened) |
| Spec PR head SHA | Bound after `/commit-workspace` publish |
| Gate label (current) | `spec-pending` |
| Gate label (target) | `spec-lgtm` |
| Local plan path | `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-010.md` |
| Forge readiness | fill `handoff.forge` for `/commit-workspace` — do not commit inside this skill |
| Blocking items | none |

PE actions (all on **exact current head**):

1. Remove `spec-pending` / blocked / revised / stale; add **`spec-lgtm`**
2. Submit GitHub **Approve** with attestation body
3. Mark Draft PR **Ready for review**
4. Authorize merge; then **`/create-board-tickets`** from §9

### Approve attestation body

```text
Spec package approved
initiative: INIT-GATEFLOW-010
spec_pr_head_sha: {SHA after Forge publish}
meta_pr_head_sha: df0f5a5c09b6c4f951463bb42f277305310aaa80
impact_map_revision: 1
prd_digest: sha256:457f19617113171c973abdbc15d1afaa00df2f6947ab4567b57d8440bd88b206
scope_digest: sha256:09c89c143c14401c8812738c162c05a2f5e504cabafd1818ee72eb4e9b781532
plan_digest: sha256:{plan file digest after publish}
artifacts:
  - docs/specification/product/INIT-GATEFLOW-010-gateflow.md
  - docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-010.md
  - docs/specification/reports/Technical-Review-INIT-GATEFLOW-010.md
  - docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-010.md
  - docs/specification/adr/adr-009-pin-forge-publish-mutate-authority.md
  - docs/specification/adr/adr-010-lane-intake-and-dual-workspace-authority.md
```

---

## 9. WorkManifest seed

```yaml
# Generated by /spec-implementation-plan — 2026-08-05
# LOCAL — do not commit to prayog-skills upstream
apiVersion: prayog/v1
kind: WorkManifest

initiative: INIT-GATEFLOW-010

metadata:
  title: INIT-GATEFLOW-010 — eng-lane pin tip executor parity
  summary: |
    Tip-faithful eng lifecycle on pin v0.5.0-rc.2: board-status parse/apply,
    ticket gates, closeout Done, initiative closure Enter-at (ADR-010 §7).
    W0 unit-only parse + purpose/owner; W1–W4 co-ship live verify.
  playbook:
    - docs/specification/product/INIT-GATEFLOW-010-gateflow.md
    - docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-010.md

target:
  org: drivestream-lab
  project: "drivestream-lab Board"

defaults:
  initiative: INIT-GATEFLOW-010
  parent: EPIC
  labels:
    - INIT-GATEFLOW-010

epic:
  id: EPIC
  repo: drivestream-lab/gateflow
  title: "[feature] INIT-GATEFLOW-010 — eng-lane pin tip executor parity"
  codebase: drivestream-lab/gateflow
  spec_path: docs/specification/product/INIT-GATEFLOW-010-gateflow.md
  verify_command: .venv/bin/python -m tests.verify.verify_closure
  body: |
    ## Objective

    Gateflow executes tip-faithful eng lanes: pin board-status, ticket gates,
    closeout Done, initiative closure Enter-at — without merge or meta purge.

    ## Waves

    | Wave | Goal |
    |------|------|
    | W0 | Pin parse + purpose/owner (unit) |
    | W1 | Board-status apply + implement In Progress |
    | W2 | Ticket gates + create predicates |
    | W3 | Closeout Done + no merge/lgtm/auto-chain |
    | W4 | Closure Enter-at + freeze |

    ## References

    - Spec: docs/specification/product/INIT-GATEFLOW-010-gateflow.md
    - Plan: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-010.md
    - TDD: docs/specification/reports/Technical-Review-INIT-GATEFLOW-010.md
    - ADR-009 / ADR-010 §7 (no ADR-011)

work:
  - id: W0
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-010 W0] Pin parse parity + purpose/owner on stops"
    depends_on: []
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-010-gateflow.md
    verify_command: "N/A — P15 N/A (no new product surface; unit + inspect only)"
    tasks:
      - id: TASK-W0-01
        implements: [REQ-01]
        depends_on: []
        files:
          - path: .harness-pin.yaml
            action: inspect
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "Harness pin ref exact-matches prayog-skills tip tag/SHA"
          proof:
            kind: command
            command: "git -C prayog-skills describe --exact-match HEAD"
            expected: "equals .harness-pin.yaml agent_skills.ref (v0.5.0-rc.2)"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-010-W0.md § TASK-W0-01"
      - id: TASK-W0-02
        implements: [REQ-02]
        depends_on: [TASK-W0-01]
        files:
          - path: tests/unit/test_forge_policy.py
            action: modify
        exit:
          criteria:
            - "Remounted update_board_status nodes parse; invalid status fails closed; 0 BROKEN get_node"
          proof:
            kind: command
            command: "make check && make test"
            expected: "exit 0; board-status parse tests pass"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-010-W0.md § TASK-W0-02"
      - id: TASK-W0-03
        implements: [REQ-10]
        depends_on: [TASK-W0-01]
        files:
          - path: src/models/handoff_models.py
            action: modify
          - path: src/business_services/workflow_engine.py
            action: modify
        exit:
          criteria:
            - "ResolvedWorkflowNode carries optional purpose and owner from pin"
          proof:
            kind: command
            command: "make check && make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-010-W0.md § TASK-W0-03"
      - id: TASK-W0-04
        implements: [REQ-10]
        depends_on: [TASK-W0-03]
        files:
          - path: src/business_services/run_orchestrator.py
            action: modify
          - path: tests/unit/test_run_orchestrator.py
            action: modify
        exit:
          criteria:
            - "run_stopped includes purpose/owner when stop node has pin values"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; REQ-10 assertions pass"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-010-W0.md § TASK-W0-04"
      - id: TASK-W0-05
        implements: [REQ-01, REQ-02, REQ-10]
        depends_on: [TASK-W0-04]
        files:
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "As-built INIT-010 W0 row reflects unit-proven state"
          proof:
            kind: review
            review: "Inspect as-built INIT-010 W0 row after unit exit"
            expected: "row present and accurate"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-010-W0.md § TASK-W0-05"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: false
        reason: "W0 parse + stop payload only — no new callable product surface (P15 N/A; Q-3)"
    body: |
      ## Wave goal

      Pin parse parity for board-status hops; purpose/owner on stops (unit only).

      ## Tasks (from plan §2)

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W0-01 | REQ-01 | — | Harness tip match | command |
      | TASK-W0-02 | REQ-02 | TASK-W0-01 | Board-status parse / 0 BROKEN | make test |
      | TASK-W0-03 | REQ-10 | TASK-W0-01 | purpose/owner on ResolvedWorkflowNode | make test |
      | TASK-W0-04 | REQ-10 | TASK-W0-03 | purpose/owner on run_stopped | make test |
      | TASK-W0-05 | REQ-01,02,10 | TASK-W0-04 | As-built W0 row | review |

      ## Done when

      - [ ] All W0 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-010-gateflow.md

  - id: W1
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-010 W1] Board-status apply + implement In Progress"
    depends_on: [W0]
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-010-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_implement_lane
    tasks:
      - id: TASK-W1-01
        implements: [REQ-03]
        depends_on: []
        files:
          - path: src/business_services/forge_action_service.py
            action: modify
          - path: tests/unit/test_forge_action_service.py
            action: modify
        exit:
          criteria:
            - "update_board_status apply updates board; missing ticket fails closed"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-010-W1.md § TASK-W1-01"
      - id: TASK-W1-02
        implements: [REQ-04]
        depends_on: [TASK-W1-01]
        files:
          - path: src/api/v1
            action: modify
          - path: tests/unit/test_wave_start.py
            action: modify
        exit:
          criteria:
            - "Implement-start applies In Progress before pre-implement; idempotent"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-010-W1.md § TASK-W1-02"
      - id: TASK-W1-03
        implements: [REQ-11]
        depends_on: []
        files:
          - path: tests/unit
            action: modify
        exit:
          criteria:
            - "Create-tickets success does not dispatch pre-implement on same run"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-010-W1.md § TASK-W1-03"
      - id: TASK-W1-04
        implements: [REQ-03, REQ-04, REQ-17]
        depends_on: [TASK-W1-02]
        files:
          - path: tests/verify/verify_implement_lane.py
            action: modify
          - path: tests/README.md
            action: modify
        exit:
          criteria:
            - "Live implement_lane asserts In Progress / board-status evidence under knobs"
          proof:
            kind: command
            command: ".venv/bin/python -m tests.verify.verify_implement_lane"
            expected: "exit 0 under documented prereqs"
            evidence_expected: "Live-Verify-INIT-GATEFLOW-010-W1.md"
      - id: TASK-W1-05
        implements: [REQ-03, REQ-04, REQ-11]
        depends_on: [TASK-W1-04]
        files:
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "As-built W1 row accurate"
          proof:
            kind: review
            review: "Inspect as-built INIT-010 W1 row"
            expected: "W1 row present"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-010-W1.md § TASK-W1-05"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_implement_lane
        covers: [REQ-03, REQ-04, REQ-17]
        prerequisites:
          - "API + worker up; forge/board credentials in tests/config.yaml"
        safe_test_data:
          - "Ephemeral initiative/ticket — no prod"
        steps:
          - "Run verify_implement_lane"
        expected_observations:
          - "Ticket In Progress before coding; board-status hop when exercised"
        evidence_expected: "Live-Verify-INIT-GATEFLOW-010-W1.md"
        cleanup:
          - "Close ephemeral run/PR per script"
        stop_conditions:
          - "Non-zero exit or unexpected 5xx → stop; do not start Pass-2"
    body: |
      ## Wave goal

      APPLY_FORGE board-status; implement-start In Progress; no same-run resume.

      ## Tasks

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W1-01 | REQ-03 | — | board-status apply | make test |
      | TASK-W1-02 | REQ-04 | TASK-W1-01 | In Progress pre-hop | make test |
      | TASK-W1-03 | REQ-11 | — | no same-run resume | make test |
      | TASK-W1-04 | REQ-03,04,17 | TASK-W1-02 | live implement_lane | verify_implement_lane |
      | TASK-W1-05 | REQ-03,04,11 | TASK-W1-04 | as-built | review |

      ## Done when

      - [ ] All W1 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-010-gateflow.md

  - id: W2
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-010 W2] Ticket gates + create predicates"
    depends_on: [W1]
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-010-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_wave_start
    tasks:
      - id: TASK-W2-01
        implements: [REQ-06]
        depends_on: []
        files:
          - path: src/business_services/forge_action_service.py
            action: modify
          - path: tests/unit/test_forge_action_service.py
            action: modify
        exit:
          criteria:
            - "Create-tickets fails closed unless all three predicates pass; 422 + 0 creates"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-010-W2.md § TASK-W2-01"
      - id: TASK-W2-02
        implements: [REQ-07]
        depends_on: [TASK-W2-01]
        files:
          - path: src/business_services/forge_action_service.py
            action: modify
          - path: tests/unit/test_forge_action_service.py
            action: modify
        exit:
          criteria:
            - "Create success returns epic_ticket_id and non-empty wave_ticket_ids"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-010-W2.md § TASK-W2-02"
      - id: TASK-W2-03
        implements: [REQ-08]
        depends_on: []
        files:
          - path: src/api/v1
            action: modify
          - path: tests/unit/test_wave_start.py
            action: modify
        exit:
          criteria:
            - "Implement-start ticket gate returns 400/422 per table; 0 enqueue"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-010-W2.md § TASK-W2-03"
      - id: TASK-W2-04
        implements: [REQ-06, REQ-08, REQ-17]
        depends_on: [TASK-W2-03]
        files:
          - path: tests/verify/verify_wave_start.py
            action: modify
          - path: tests/verify/verify_board.py
            action: modify
          - path: tests/README.md
            action: modify
        exit:
          criteria:
            - "Live scripts assert ticket/create gate side-effect table under knobs"
          proof:
            kind: command
            command: ".venv/bin/python -m tests.verify.verify_wave_start"
            expected: "exit 0 under documented prereqs"
            evidence_expected: "Live-Verify-INIT-GATEFLOW-010-W2.md"
      - id: TASK-W2-05
        implements: [REQ-06, REQ-07, REQ-08, REQ-17]
        depends_on: [TASK-W2-04]
        files:
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "As-built W2 row accurate"
          proof:
            kind: review
            review: "Inspect as-built INIT-010 W2 row"
            expected: "W2 row present"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-010-W2.md § TASK-W2-05"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_wave_start
        covers: [REQ-06, REQ-08, REQ-17]
        prerequisites:
          - "API up; programme token; board/forge knobs as documented"
        safe_test_data:
          - "Ephemeral tickets — no prod"
        steps:
          - "Run verify_wave_start; verify_board for create predicates as needed"
        expected_observations:
          - "400/422 side-effect table; create success fields when positive path run"
        evidence_expected: "Live-Verify-INIT-GATEFLOW-010-W2.md"
        cleanup:
          - "Remove ephemeral tickets/runs"
        stop_conditions:
          - "Non-zero exit or unexpected 5xx → stop"
    body: |
      ## Wave goal

      Create predicates + implement ticket gate; live verify co-shipped.

      ## Tasks

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W2-01 | REQ-06 | — | triple predicate gate | make test |
      | TASK-W2-02 | REQ-07 | TASK-W2-01 | epic + wave ids | make test |
      | TASK-W2-03 | REQ-08 | — | ticket 400/422 | make test |
      | TASK-W2-04 | REQ-06,08,17 | TASK-W2-03 | live gates | verify_wave_start |
      | TASK-W2-05 | REQ-06–08,17 | TASK-W2-04 | as-built | review |

      ## Done when

      - [ ] All W2 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-010-gateflow.md

  - id: W3
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-010 W3] Closeout Done + no merge/lgtm/auto-chain"
    depends_on: [W2]
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-010-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_wave_closeout
    tasks:
      - id: TASK-W3-01
        implements: [REQ-05]
        depends_on: []
        files:
          - path: src/business_services/run_orchestrator.py
            action: modify
          - path: tests/unit/test_wave_closeout.py
            action: modify
        exit:
          criteria:
            - "Closeout applies Done after ground-spec.pass; purpose at wave-signoff"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-010-W3.md § TASK-W3-01"
      - id: TASK-W3-02
        implements: [REQ-09, REQ-16]
        depends_on: []
        files:
          - path: src/business_services/forge_action_service.py
            action: modify
          - path: tests/unit
            action: modify
        exit:
          criteria:
            - "No Forge merge; *-lgtm apply_labels rejected"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-010-W3.md § TASK-W3-02"
      - id: TASK-W3-03
        implements: [REQ-19]
        depends_on: [TASK-W3-01]
        files:
          - path: src/business_services/run_orchestrator.py
            action: modify
          - path: tests/unit
            action: modify
        exit:
          criteria:
            - "No auto-chain to next wave or closure after wave-signoff"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-010-W3.md § TASK-W3-03"
      - id: TASK-W3-04
        implements: [REQ-05, REQ-17, REQ-19]
        depends_on: [TASK-W3-03]
        files:
          - path: tests/verify/verify_wave_closeout.py
            action: modify
          - path: tests/verify/verify_spec_lane.py
            action: modify
          - path: tests/README.md
            action: modify
        exit:
          criteria:
            - "Live closeout asserts Done/purpose/no auto-chain under knobs"
          proof:
            kind: command
            command: ".venv/bin/python -m tests.verify.verify_wave_closeout"
            expected: "exit 0 under documented prereqs"
            evidence_expected: "Live-Verify-INIT-GATEFLOW-010-W3.md"
      - id: TASK-W3-05
        implements: [REQ-05, REQ-09, REQ-16, REQ-19]
        depends_on: [TASK-W3-04]
        files:
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "As-built W3 row accurate"
          proof:
            kind: review
            review: "Inspect as-built INIT-010 W3 row"
            expected: "W3 row present"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-010-W3.md § TASK-W3-05"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_wave_closeout
        covers: [REQ-05, REQ-17, REQ-19]
        prerequisites:
          - "API + worker; closeout knobs / dogfood as documented"
        safe_test_data:
          - "Ephemeral wave PR / tickets"
        steps:
          - "Run verify_wave_closeout; verify_spec_lane as needed"
        expected_observations:
          - "Done hop; terminal purpose; no auto-chain"
        evidence_expected: "Live-Verify-INIT-GATEFLOW-010-W3.md"
        cleanup:
          - "Per script notes"
        stop_conditions:
          - "Non-zero exit or unexpected 5xx → stop"
    body: |
      ## Wave goal

      Closeout Done + purpose; no merge/lgtm; no auto-chain.

      ## Tasks

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W3-01 | REQ-05 | — | Done + purpose | make test |
      | TASK-W3-02 | REQ-09,16 | — | no merge/lgtm | make test |
      | TASK-W3-03 | REQ-19 | TASK-W3-01 | no auto-chain | make test |
      | TASK-W3-04 | REQ-05,17,19 | TASK-W3-03 | live closeout | verify_wave_closeout |
      | TASK-W3-05 | REQ-05,09,16,19 | TASK-W3-04 | as-built | review |

      ## Done when

      - [ ] All W3 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-010-gateflow.md

  - id: W4
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-010 W4] Initiative closure Enter-at + freeze"
    depends_on: [W3]
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-010-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_closure
    tasks:
      - id: TASK-W4-01
        implements: [REQ-12]
        depends_on: []
        files:
          - path: src/api/v1
            action: create
          - path: src/models
            action: create
          - path: src/app.py
            action: modify
        exit:
          criteria:
            - "POST initiatives/closure/start returns 202+run_id; malformed → 400"
          proof:
            kind: command
            command: "make check && make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-010-W4.md § TASK-W4-01"
      - id: TASK-W4-02
        implements: [REQ-13]
        depends_on: [TASK-W4-01]
        files:
          - path: src/business_services
            action: create
          - path: tests/unit
            action: create
        exit:
          criteria:
            - "Done-gate: any wave not Done → 422; 0 enqueue; EPIC untouched"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-010-W4.md § TASK-W4-02"
      - id: TASK-W4-03
        implements: [REQ-14, REQ-15]
        depends_on: [TASK-W4-02]
        files:
          - path: src/business_services
            action: modify
          - path: tests/unit
            action: modify
        exit:
          criteria:
            - "EPIC Done before purge-app; walk stops at signoff-app; never purge-meta"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-010-W4.md § TASK-W4-03"
      - id: TASK-W4-04
        implements: [REQ-20]
        depends_on: [TASK-W4-03]
        files:
          - path: src/business_services/run_orchestrator.py
            action: modify
          - path: tests/unit
            action: modify
        exit:
          criteria:
            - "Partial failure after EPIC Done recorded; no closure-complete claim"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-010-W4.md § TASK-W4-04"
      - id: TASK-W4-05
        implements: [REQ-12, REQ-13, REQ-17]
        depends_on: [TASK-W4-04]
        files:
          - path: tests/verify/verify_closure.py
            action: create
          - path: tests/README.md
            action: modify
        exit:
          criteria:
            - "verify_closure exits 0 under knobs; covers 400/422/202 + Done-gate"
          proof:
            kind: command
            command: ".venv/bin/python -m tests.verify.verify_closure"
            expected: "exit 0 under documented prereqs"
            evidence_expected: "Live-Verify-INIT-GATEFLOW-010-W4.md"
      - id: TASK-W4-06
        implements: [REQ-18]
        depends_on: [TASK-W4-05]
        files:
          - path: docs/specification/reports/Feature-Readiness-INIT-GATEFLOW-010.md
            action: create
        exit:
          criteria:
            - "Freeze doc lists proven vs deferred eng capabilities"
          proof:
            kind: review
            review: "Inspect Feature-Readiness-INIT-GATEFLOW-010.md proven vs deferred table"
            expected: "file present with proven/deferred table"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-010-W4.md § TASK-W4-06"
      - id: TASK-W4-07
        implements: [REQ-12, REQ-13, REQ-14, REQ-15, REQ-17, REQ-18, REQ-20]
        depends_on: [TASK-W4-06]
        files:
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "As-built W4 + freeze status accurate"
          proof:
            kind: review
            review: "Inspect as-built INIT-010 W4 + freeze status"
            expected: "W4 row present"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-010-W4.md § TASK-W4-07"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_closure
        covers: [REQ-12, REQ-13, REQ-17]
        prerequisites:
          - "API up; programme token; board tickets for Done-gate positives/negatives"
        safe_test_data:
          - "Ephemeral initiative/EPIC/wave tickets on test board"
        steps:
          - "Run verify_closure"
        expected_observations:
          - "202 on valid; 400/422 per table; no meta purge"
        evidence_expected: "Live-Verify-INIT-GATEFLOW-010-W4.md"
        cleanup:
          - "Do not leave prod EPICs Done; cleanup test board artifacts"
        stop_conditions:
          - "Non-zero exit or unexpected 5xx → stop"
    body: |
      ## Wave goal

      Closure Enter-at (ADR-010 §7) + Done-gate + EPIC hygiene + freeze.

      ## Tasks

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W4-01 | REQ-12 | — | closure route 202/400 | make test |
      | TASK-W4-02 | REQ-13 | TASK-W4-01 | Done-gate 422 | make test |
      | TASK-W4-03 | REQ-14,15 | TASK-W4-02 | EPIC Done + purge walk | make test |
      | TASK-W4-04 | REQ-20 | TASK-W4-03 | partial failure hygiene | make test |
      | TASK-W4-05 | REQ-12,13,17 | TASK-W4-04 | verify_closure | live |
      | TASK-W4-06 | REQ-18 | TASK-W4-05 | freeze doc | review |
      | TASK-W4-07 | REQ-12–15,17,18,20 | TASK-W4-06 | as-built | review |

      ## Done when

      - [ ] All W4 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-010-gateflow.md
```

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-implementation-plan
  outcome: pass
  artifact:
    path: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-010.md
    digest: sha256:68d70cfcf921eabc395fef57e96a78cb6a2f069929482f06e16281c8c9346f37
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-010
    delivery_wave: W0
    source_freshness: CURRENT
    meta_pr: "https://github.com/drivestream-lab/prayog-meta/pull/28"
    meta_pr_head: "df0f5a5c09b6c4f951463bb42f277305310aaa80"
    map_revision: 1
    prd_digest: "sha256:457f19617113171c973abdbc15d1afaa00df2f6947ab4567b57d8440bd88b206"
    scope_digest: "sha256:09c89c143c14401c8812738c162c05a2f5e504cabafd1818ee72eb4e9b781532"
    tdd_status: Accepted
    adr_required_count: 0
    ready_for_coding_readiness: true
    waves: "W0,W1,W2,W3,W4"
  next_candidates:
    - coding-readiness
  human_checkpoint: true
  external_action: false
  forge:
    action: commit_workspace
```
