---
goal: INIT-GATEFLOW-008 — implementation plan (006A forge authorization)
initiative: INIT-GATEFLOW-008
status: Planned
date_created: 2026-07-30
source_spec: docs/specification/product/INIT-GATEFLOW-008-gateflow.md
source_spec_digest: sha256:8e4333dcf72dcfdf03288fc64a3b5bf1c98bfc9070393b83ffadb3099d8ba980
feasibility_report: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-008.md
feasibility_digest: sha256:7289a8d299bbfdd9da0474e4ff72481230562e1aad9dee0607bd76305c89edb5
technical_review: docs/specification/reports/Technical-Review-INIT-GATEFLOW-008.md
technical_review_digest: sha256:f70c34808b0e8fb599602367d4ea799c2303178651fb5111dd5a2cc2c0aededf
prd_digest: waived — Gate 1 PE waive (Q-1, 2026-07-30)
impact_map: waived
impact_map_revision: waived
repo_scope_digest: waived — gateflow-only
approved_meta_pr_head: waived
branch: chore/INIT-GATEFLOW-008-spec-gateflow
review_deadline: 2026-08-06
deciders: PE @nikd10x / prayog-pe-team — spec-lgtm + Approve on exact head after full package
---

# Implementation plan — INIT-GATEFLOW-008

## Source freshness and command contract

| Item | Value | Status |
|------|-------|--------|
| Spec / digest | `docs/specification/product/INIT-GATEFLOW-008-gateflow.md` / `sha256:8e4333dcf72dcfdf03288fc64a3b5bf1c98bfc9070393b83ffadb3099d8ba980` | CURRENT (Gate 1 **WAIVED**) |
| Feasibility / digest | `…/Initiative-Feasibility-Report-INIT-GATEFLOW-008.md` / `sha256:7289a8d299bbfdd9da0474e4ff72481230562e1aad9dee0607bd76305c89edb5` | CURRENT |
| Technical review / digest | `…/Technical-Review-INIT-GATEFLOW-008.md` / `sha256:f70c34808b0e8fb599602367d4ea799c2303178651fb5111dd5a2cc2c0aededf` | CURRENT — Status **Accepted** |
| Impact map / revision | waived | **WAIVED** |
| Repo scope digest | waived | **WAIVED** |
| Approved meta PR head | waived | **WAIVED** |
| `check_command` | `make check` | RESOLVED |
| `test_command` | `make test` | RESOLVED |
| `verify_command` | Per wave under `tests/verify/` — W0: N/A (no new surface); W1: `.venv/bin/python -m tests.verify.verify_implement_lane`; W2: `.venv/bin/python -m tests.verify.verify_board` | RESOLVED |
| `ground_command` | N/A — `/ground-spec` is Pass-2 pin skill, not a Makefile target | N/A |

> Do not use `{test_command}` as live `verify_command`. Pin remount record already
> CURRENT (`v0.5.0-rc.2` ≡ `355f403`); W0 consumes fields in code + fixes red tests.

## 0. Technical design reference

| Item | Value |
|------|-------|
| Technical review | [`Technical-Review-INIT-GATEFLOW-008.md`](Technical-Review-INIT-GATEFLOW-008.md) |
| PE sign-off | [x] complete — 2026-07-30 (Cursor chat on PR #91: amend ADR-009; ensure_branch-only; pin WorkManifest subprocess; W0 unit fix; Q-5 removed) |
| Resolved ADRs | [`adr-009-pin-forge-publish-mutate-authority.md`](../adr/adr-009-pin-forge-publish-mutate-authority.md) (**Accepted** dual-authorization amendment); ADR-003/005/010 **Accepted** — **no ADR-011** |
| Outstanding PM questions | none |
| Outstanding domain questions | none |

> Do not start W0 coding until this plan is on tip with `spec-lgtm` + Approve
> (coding-readiness), then merge + `/create-board-tickets`.

---

## 1. Requirements (REQ) — product ids

| ID | Summary | Spec path | Waves |
|----|---------|-----------|-------|
| REQ-1 | Harness pin record matches submodule tip consumed at runtime | `docs/specification/product/INIT-GATEFLOW-008-gateflow.md` | W0 |
| REQ-2 | Parse `authorization` on every external-action; omit/unknown fail closed | same | W0 |
| REQ-3 | Carry `authorization` on `ResolvedWorkflowNode` | same | W0 |
| REQ-4 | ADR-009 dual mode Accepted (amend; no ADR-011) | same | W0 |
| REQ-5 | Required `commit_workspace` on pre-implement / loop-spec via ForgeClient | same | W1 |
| REQ-6 | Do not treat all external-action as STOP | same | W1 |
| REQ-7 | `explicit` → STOP + authorize path retained | same | W1 |
| REQ-8 | `automated` → ForgeClient.apply without authorize when requires complete | same | W1 |
| REQ-9 | `head_ref` / `base_ref` from run context when required | same | W1 |
| REQ-10 | Retire PR-at-start create; ensure_branch-only allowed | same | W1 |
| REQ-11 | Pass-1: pre-implement → loop-spec → wave-pr-action → live-verify | same | W1 |
| REQ-12 | Automated `spec-pr-action` same apply rules | same | W1 |
| REQ-13 | Pin WorkManifest validator; `prayog/v1` only | same | W2 |
| REQ-14 | Board projects; manifest not second SSOT | same | W2 |
| REQ-15 | Board create remains `authorization: explicit` | same | W2 |
| REQ-16 | As-built + tests/README feature map | same | W0, W1, W2 |
| REQ-17 | Ordering vs INIT-007 dogfood (docs/plan state) | same | W2 |

---

## 2. Implementation phases

### Phase W0 — Pin consume parse + unit hygiene + ADR confirm

**GOAL-W0:** Fail-closed `authorization` on resolved EA nodes; fix unit suite for
remounted Pass-1 edges / required commit_workspace; confirm harness/ADR-009
Accepted. **No new HTTP surface** (P15 N/A).

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W0-01 | Confirm harness `agent_skills.ref` exact-matches submodule HEAD used at runtime; document in as-built if needed | REQ-1 | — | `.harness-pin.yaml` inspect; `docs/specification/as-built/implementation-status.md` modify | `git -C prayog-skills describe --exact-match` equals pin ref; as-built notes remount CURRENT | command / `git -C prayog-skills rev-parse HEAD && git -C prayog-skills describe --exact-match HEAD` | tip SHA matches pin | Wave-Execution-INIT-GATEFLOW-008-W0.md § TASK-W0-01 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-008-gateflow.md` | `N/A — P15 N/A (no new product surface)` | fail-fast.mdc | ADR-009 | `feature/INIT-GATEFLOW-008-w0-auth-parse` |
| TASK-W0-02 | Add `AuthorizationModeType`; parse EA `authorization` in WorkflowEngine; put on `ResolvedWorkflowNode`; omit/unknown → ValueError | REQ-2, REQ-3 | TASK-W0-01 | `src/models/forge_types.py` modify; `src/models/handoff_models.py` modify; `src/business_services/workflow_engine.py` modify | Unit: omit/unknown fail; day-one matrix automated vs explicit | command / `make check && make test` | exit 0; new tests pass | Wave-Execution-INIT-GATEFLOW-008-W0.md § TASK-W0-02 | drivestream-lab/gateflow | same | `N/A — P15 N/A` | strong-typing.mdc, fail-fast.mdc | ADR-009 | same |
| TASK-W0-03 | Fix obsolete Pass-1 unit assertions (`loop-spec`→`wave-pr-action`; pre-implement commit **required**) | REQ-2, REQ-11 | TASK-W0-02 | `tests/unit/test_handoff_workflow.py` modify; `tests/unit/test_forge_policy.py` modify | Formerly red tests green against remounted pin | command / `make test` | exit 0; no assert live-verify after loop-spec pass | Wave-Execution-INIT-GATEFLOW-008-W0.md § TASK-W0-03 | drivestream-lab/gateflow | same | `N/A — P15 N/A` | testing-verify-flows.mdc | ADR-009 | same |
| TASK-W0-04 | Confirm ADR-009 dual-authorization amendment remains Accepted on tip (no code change if already Accepted) | REQ-4 | — | `docs/specification/adr/adr-009-pin-forge-publish-mutate-authority.md` inspect | Header Status Accepted; amendment section present | review / file inspect | Status Accepted | Wave-Execution-INIT-GATEFLOW-008-W0.md § TASK-W0-04 | drivestream-lab/gateflow | same | `N/A — P15 N/A` | spec-driven-development.mdc | ADR-009 | same |
| TASK-W0-05 | As-built row: 008 W0 parse/consume started; INIT-006 REQ-7 superseded note for automated | REQ-16 | TASK-W0-02 | `docs/specification/as-built/implementation-status.md` modify | Rows match W0 code | review / as-built | W0 partial/complete accurate | Wave-Execution-INIT-GATEFLOW-008-W0.md § TASK-W0-05 | drivestream-lab/gateflow | same | `N/A — P15 N/A` | SDD | ADR-009 | same |

#### Files (W0)

| ID | Path | Action |
|----|------|--------|
| FILE-W0-01 | `.harness-pin.yaml` | inspect |
| FILE-W0-02 | `src/models/forge_types.py` | modify |
| FILE-W0-03 | `src/models/handoff_models.py` | modify |
| FILE-W0-04 | `src/business_services/workflow_engine.py` | modify |
| FILE-W0-05 | `tests/unit/test_handoff_workflow.py` | modify |
| FILE-W0-06 | `tests/unit/test_forge_policy.py` | modify |
| FILE-W0-07 | `docs/specification/adr/adr-009-pin-forge-publish-mutate-authority.md` | inspect |
| FILE-W0-08 | `docs/specification/as-built/implementation-status.md` | modify |

#### Tests (W0)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W0-U | unit | `make test` | REQ-2, REQ-3, REQ-11 / TASK-W0-02..03 |
| TEST-W0-I | integration/contract | N/A | — |
| TEST-W0-L | live | N/A — P15 N/A | — |

#### Verification Coverage (W0)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-1 | inspect | N/A | N/A | N/A | tip match |
| REQ-2, REQ-3 | TEST-W0-U | N/A | N/A | N/A | |
| REQ-4 | review | N/A | N/A | N/A | already Accepted |
| REQ-11 (pin edges in unit) | TEST-W0-U | N/A | N/A | N/A | full walker W1 |
| REQ-16 | review | N/A | N/A | N/A | |

#### Live-verification intent (W0)

| Field | Value |
|-------|-------|
| Applicable | **no** — W0 is pin-field parse + unit hygiene; no new/changed callable product surface (P15 N/A) |
| Mode | N/A |
| Runtime head binding | N/A |
| Prerequisites | N/A |
| Cleanup / Stop | N/A |

---

### Phase W1 — Automated / explicit forge apply + retire PR-at-start

**GOAL-W1:** Policy/orchestrator branch on `authorization`; shared Forge apply;
ensure_branch-only at job start; Pass-1 automated `wave-pr-action`; unit +
**co-ship** live `verify_implement_lane` asserts for new PR timing (P15).

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W1-01 | PolicyEngine: STOP EA only when `authorization=explicit`; automated not authorize-STOP | REQ-6, REQ-7 | — | `src/business_services/policy_engine.py` modify; `tests/unit/test_*policy*` modify | Unit: explicit STOP; automated not pending-authorize STOP | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-008-W1.md § TASK-W1-01 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-008-gateflow.md` | `.venv/bin/python -m tests.verify.verify_implement_lane` | fail-fast.mdc | ADR-009 | `feature/INIT-GATEFLOW-008-w1-automated-forge` |
| TASK-W1-02 | Shared `ForgeActionService.apply` (pin⋉handoff requires; head/base from run); authorize path calls apply | REQ-7, REQ-8, REQ-9, REQ-12 | TASK-W1-01 | `src/business_services/forge_action_service.py` modify; forge unit tests modify | Unit: incomplete requires fail; automated open without authorize mock | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-008-W1.md § TASK-W1-02 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_implement_lane` | architecture.mdc | ADR-009, ADR-003, ADR-005 | same |
| TASK-W1-03 | Orchestrator: after content hop + publish, automated EA → apply then continue; Pass-1 multi-hop unit to live-verify STOP | REQ-5, REQ-8, REQ-11, REQ-12 | TASK-W1-02 | `src/business_services/run_orchestrator.py` modify; orchestrator/handoff tests modify | Unit walker: loop-spec → wave-pr apply → live-verify STOP | command / `make test` | exit 0; authorize not called for automated | Wave-Execution-INIT-GATEFLOW-008-W1.md § TASK-W1-03 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_implement_lane` | logging-loguru.mdc | ADR-009 | same |
| TASK-W1-04 | Retire PR create at job start; ensure_branch-only; `pr_number` null until open_draft_pr | REQ-10, REQ-9 | TASK-W1-03 | `src/business_services/run_orchestrator.py` modify; `tests/unit/test_run_orchestrator.py` modify | Unit: no create_or_update_pull_request at start; ensure_branch may run | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-008-W1.md § TASK-W1-04 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_implement_lane` | fail-fast.mdc | ADR-009 | same |
| TASK-W1-05 | Extend `verify_implement_lane` (+ README): assert ensure-branch / no early Draft PR; PR appears after automated wave-pr when worker on | REQ-8, REQ-10, REQ-11, REQ-16 | TASK-W1-04 | `tests/verify/verify_implement_lane.py` modify; `tests/README.md` modify | Script documents/asserts new Pass-1 PR timing; feature map updated | command / `.venv/bin/python -m tests.verify.verify_implement_lane` | exit 0 under documented prereqs (or clear skip when worker off — fail closed if assert path claims pass without check) | Live-Verify-INIT-GATEFLOW-008-W1.md | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_implement_lane` | testing-verify-flows.mdc | ADR-009 | same |

#### Files (W1)

| ID | Path | Action |
|----|------|--------|
| FILE-W1-01 | `src/business_services/policy_engine.py` | modify |
| FILE-W1-02 | `src/business_services/forge_action_service.py` | modify |
| FILE-W1-03 | `src/business_services/run_orchestrator.py` | modify |
| FILE-W1-04 | `tests/unit/test_run_orchestrator.py` | modify |
| FILE-W1-05 | `tests/verify/verify_implement_lane.py` | modify |
| FILE-W1-06 | `tests/README.md` | modify |

#### Tests (W1)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W1-U | unit | `make test` | REQ-5…12 / TASK-W1-01…04 |
| TEST-W1-L | live smoke | `.venv/bin/python -m tests.verify.verify_implement_lane` | REQ-8, REQ-10, REQ-11 / TASK-W1-05 |

#### Verification Coverage (W1)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-5…7 | TEST-W1-U | N/A | secondary | N/A | |
| REQ-8, REQ-10, REQ-11 | TEST-W1-U | N/A | TEST-W1-L | N/A | P15 |
| REQ-9, REQ-12 | TEST-W1-U | N/A | TEST-W1-L | N/A | |
| REQ-16 | N/A | N/A | docs in TASK-W1-05 | N/A | |

#### Live-verification intent (W1)

| Field | Value |
|-------|-------|
| Applicable | **yes** — implement-lane PR timing / automated wave-pr is a material product surface (P15) |
| Environment class | local-compose (Gateflow + worker + forge creds per `tests/config.yaml`) |
| Mode | smoke |
| Runtime head binding | Bound at `live-verify` against wave PR head |
| Prerequisites | API up; `gateflow.require_worker: true` when asserting PR open; forge credentials |
| Safe test data | Ephemeral INIT / ticket per tests config — no prod |
| Steps / command | `.venv/bin/python -m tests.verify.verify_implement_lane` |
| Expected observations | Start has no Draft PR (or pr_number unset); after Pass-1 coding hops PR exists; pin edge includes wave-pr-action |
| Expected evidence | `Live-Verify-INIT-GATEFLOW-008-W1.md` |
| Cleanup | Close ephemeral run/PR per script notes |
| Stop conditions | Non-zero exit or unexpected 5xx → stop; do not start Pass-2 |

---

### Phase W2 — WorkManifest prayog/v1 + docs

**GOAL-W2:** Pin `workmanifest_contract.py` before board create; reject
`launchpad/v1`; keep board authorize explicit; as-built/README + REQ-17 note;
**co-ship** `verify_board` assertions (P15).

| Task | Description | Implements | Depends on | Files (path/action) | Exit criteria | Proof (kind / command\|review) | Expected | Evidence expected | Codebase | Spec path | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|------------|---------------------|---------------|--------------------------------|----------|-------------------|----------|-----------|----------------|-----------|-----------|--------|
| TASK-W2-01 | Invoke pin validator subprocess before BoardService; accept only prayog/v1; reject launchpad/v1 | REQ-13, REQ-14 | — | `src/business_services/forge_action_service.py` modify; `src/models/work_manifest_models.py` modify; unit tests create/modify | Unit: launchpad/v1 rejected; prayog/v1 fixture passes validator then projects | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-008-W2.md § TASK-W2-01 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-008-gateflow.md` | `.venv/bin/python -m tests.verify.verify_board` | fail-fast.mdc | ADR-009 | `feature/INIT-GATEFLOW-008-w2-workmanifest` |
| TASK-W2-02 | Board create remains explicit STOP+authorize; unit still requires authorize | REQ-15 | TASK-W2-01 | forge action / policy tests modify | Unit: board-tickets-action still explicit authorize | command / `make test` | exit 0 | Wave-Execution-INIT-GATEFLOW-008-W2.md § TASK-W2-02 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_board` | — | ADR-005, ADR-009 | same |
| TASK-W2-03 | Extend `verify_board` (+ README): bad apiVersion fails closed; prayog path documented | REQ-13, REQ-16 | TASK-W2-01 | `tests/verify/verify_board.py` modify; `tests/README.md` modify | Live/smoke script covers new validation or documents authorize+fixture path | command / `.venv/bin/python -m tests.verify.verify_board` | exit 0 under prereqs | Live-Verify-INIT-GATEFLOW-008-W2.md | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_board` | testing-verify-flows.mdc | — | same |
| TASK-W2-04 | As-built complete 008; feature map Pass-1 edges; REQ-17 ordering vs 007 dogfood | REQ-16, REQ-17 | TASK-W2-03 | `docs/specification/as-built/implementation-status.md` modify; `tests/README.md` modify; `docs/specification/README.md` modify | Docs match shipped behavior | review / docs | Pass-1 string includes wave-pr-action; 007 dogfood unblocked note after merge | Wave-Execution-INIT-GATEFLOW-008-W2.md § TASK-W2-04 | drivestream-lab/gateflow | same | `.venv/bin/python -m tests.verify.verify_board` | SDD | — | same |

#### Files (W2)

| ID | Path | Action |
|----|------|--------|
| FILE-W2-01 | `src/business_services/forge_action_service.py` | modify |
| FILE-W2-02 | `src/models/work_manifest_models.py` | modify |
| FILE-W2-03 | `tests/verify/verify_board.py` | modify |
| FILE-W2-04 | `tests/README.md` | modify |
| FILE-W2-05 | `docs/specification/as-built/implementation-status.md` | modify |
| FILE-W2-06 | `docs/specification/README.md` | modify |

#### Tests (W2)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W2-U | unit | `make test` | REQ-13…15 |
| TEST-W2-L | live smoke | `.venv/bin/python -m tests.verify.verify_board` | REQ-13 / TASK-W2-03 |

#### Verification Coverage (W2)

| REQ / criterion | unit | integration/contract | smoke | sandbox | Notes |
|-----------------|------|----------------------|-------|---------|-------|
| REQ-13, REQ-14 | TEST-W2-U | N/A | TEST-W2-L | N/A | P15 |
| REQ-15 | TEST-W2-U | N/A | TEST-W2-L | N/A | |
| REQ-16, REQ-17 | review | N/A | N/A | N/A | docs |

#### Live-verification intent (W2)

| Field | Value |
|-------|-------|
| Applicable | **yes** — board-create validation is a material forge/product surface (P15) |
| Environment class | local-compose |
| Mode | smoke |
| Runtime head binding | Bound at `live-verify` |
| Prerequisites | API up; programme token; forge creds when script creates issues (soft-skip only if documented) |
| Safe test data | Ephemeral board fixtures per config |
| Steps / command | `.venv/bin/python -m tests.verify.verify_board` |
| Expected observations | Invalid apiVersion rejected; valid path documents prayog/v1 |
| Expected evidence | `Live-Verify-INIT-GATEFLOW-008-W2.md` |
| Cleanup | Delete ephemeral issues if created |
| Stop conditions | Unexpected mutate on fail path → stop |

---

## 3. Dependencies (DEP)

| ID | Dependency | Blocks |
|----|------------|--------|
| DEP-1 | W0 before W1 | Automated apply needs authorization on ResolvedWorkflowNode |
| DEP-2 | W1 before W2 | Board create uses shared apply / pin SSOT posture |
| DEP-3 | Pin tip with authorization already remounted | REQ-1 confirm only |
| DEP-4 | INIT-007 dogfood after 008 W0–W1 on `develop` | Product REQ-17 (docs in W2) |

---

## 4. Risks (RISK)

| ID | Risk | Mitigation |
|----|------|------------|
| RISK-1 | Live implement_lane needs Cursor worker + forge | Document skip vs fail; P15 script must not claim pass without asserts |
| RISK-2 | Subprocess validator path missing in deploy layout | Resolve via workspace `prayog-skills/scripts/…`; fail closed |
| RISK-3 | verify_pr_thread still assumes PR-at-start | Update or retire asserts in W1 with TASK-W1-04/05 |
| RISK-4 | Gate 1 waived package | PE `spec-lgtm` still required on exact plan head |

---

## 5. Out of scope

- INIT-007 closeout/learning implementation
- C2 probes / auto-merge / merge Forge action
- Env flags overriding pin `authorization`
- Skill-local `git commit` / `gh` as success
- New ADR-011

---

## 6. As-built and docs tasks

| Task | File | Action |
|------|------|--------|
| W0 as-built | `docs/specification/as-built/implementation-status.md` | TASK-W0-05 |
| W1 feature map | `tests/README.md` | TASK-W1-05 |
| W2 complete + REQ-17 | as-built + README + spec README | TASK-W2-04 |

---

## 7. Plan check summary

| Check | Status |
|-------|--------|
| P1 REQ coverage | PASS |
| P2 TASK ↔ REQ | PASS |
| P3 FILE paths | PASS |
| P4 Exit evidence | PASS |
| P5 Verification layers | PASS |
| P6 Scope | PASS |
| P7 Risks | PASS |
| P8 Wave order | PASS |
| P9 Docs same PR | PASS |
| P10 Self-contained + commands | PASS |
| P11 MDC notes | PASS |
| P12 ADR Accepted | PASS — ADR-009 Accepted |
| P13 TDD Accepted | PASS — 2026-07-30 |
| P14 WorkManifest seed | PASS — see §9 |
| P15 Co-ship live | PASS — W0 N/A; W1 verify_implement_lane; W2 verify_board |
| P16 Contract | PASS — `prayog-skills/scripts/workmanifest_contract.py` → ok |

---

## 8. Forge / PR instructions

> Persist locally; publish via `/commit-workspace` to Draft PR
> [#91](https://github.com/drivestream-lab/gateflow/pull/91). Do **not** commit
> inside this skill. Label stays **`spec-pending`** until §10.

```
Branch:   chore/INIT-GATEFLOW-008-spec-gateflow
PR:       https://github.com/drivestream-lab/gateflow/pull/91
Reviewers: @drivestream-lab/prayog-pe-team

After spec-lgtm + Approve + merge → /create-board-tickets from §9
Then Pass-1 implement waves; live-verify runs co-shipped scripts
```

---

## 10. Coding-readiness unlock (PE — after plan on head)

| Item | Value |
|------|-------|
| Workflow outcome | `pass` — P1–P16 intended PASS; sources CURRENT/WAIVED |
| Verdict | GATE OPEN REQUEST |
| Spec PR | https://github.com/drivestream-lab/gateflow/pull/91 |
| Spec PR head SHA | *(fill after `/commit-workspace` of this plan)* |
| Gate label (current) | `spec-pending` |
| Gate label (target) | `spec-lgtm` |
| Local plan path | `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-008.md` |
| Forge readiness | `/commit-workspace` — do not commit inside this skill |
| Blocking items | none for engineering package (Gate 1 waived) |

### Approve attestation body

```text
Spec package approved
initiative: INIT-GATEFLOW-008
spec_pr_head_sha: {SHA}
meta_pr_head_sha: WAIVED
impact_map_revision: WAIVED
prd_digest: WAIVED
scope_digest: WAIVED
plan_digest: sha256:{plan file digest}
artifacts:
  - docs/specification/product/INIT-GATEFLOW-008-gateflow.md
  - docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-008.md
  - docs/specification/reports/Technical-Review-INIT-GATEFLOW-008.md
  - docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-008.md
  - docs/specification/adr/adr-009-pin-forge-publish-mutate-authority.md
```

---

## 9. WorkManifest seed

```yaml
# Generated by /spec-implementation-plan — 2026-07-30
# LOCAL — do not commit to prayog-skills upstream
apiVersion: prayog/v1
kind: WorkManifest

initiative: INIT-GATEFLOW-008

metadata:
  title: INIT-GATEFLOW-008 — 006A forge authorization + wave-pr after loop-spec
  summary: |
    Consume pin dual authorization (explicit|automated), retire implement PR-at-start,
    automate wave/spec Draft PR open after coding, validate WorkManifest via pin prayog/v1.
  playbook:
    - docs/specification/product/INIT-GATEFLOW-008-gateflow.md
    - docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-008.md

target:
  org: drivestream-lab
  project: "drivestream-lab Board"

defaults:
  initiative: INIT-GATEFLOW-008
  parent: EPIC
  labels:
    - INIT-GATEFLOW-008

epic:
  id: EPIC
  repo: drivestream-lab/gateflow
  title: "[feature] INIT-GATEFLOW-008 — 006A forge authorization + wave-pr placement"
  codebase: drivestream-lab/gateflow
  spec_path: docs/specification/product/INIT-GATEFLOW-008-gateflow.md
  verify_command: .venv/bin/python -m tests.verify.verify_implement_lane
  body: |
    ## Objective

    Gateflow consumes pin authorization dual mode and Pass-1 wave-pr-after-loop-spec;
    retires PR-at-start; WorkManifest prayog/v1 before board seed.

    ## Waves

    | Wave | Goal |
    |------|------|
    | W0 | Auth parse + unit hygiene + ADR confirm |
    | W1 | Automated forge apply + retire PR-at-start + live implement_lane |
    | W2 | WorkManifest prayog/v1 + verify_board + docs |

    ## References

    - Spec: docs/specification/product/INIT-GATEFLOW-008-gateflow.md
    - Plan: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-008.md
    - TDD: docs/specification/reports/Technical-Review-INIT-GATEFLOW-008.md
    - ADR-009 (dual authorization amendment)

work:
  - id: W0
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-008 W0] Authorization parse + Pass-1 unit hygiene"
    depends_on: []
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-008-gateflow.md
    verify_command: "N/A — P15 N/A (no new product surface; unit + inspect only)"
    tasks:
      - id: TASK-W0-01
        implements: [REQ-1]
        depends_on: []
        files:
          - path: .harness-pin.yaml
            action: inspect
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "Harness pin ref exact-matches prayog-skills HEAD"
          proof:
            kind: command
            command: "git -C prayog-skills describe --exact-match HEAD"
            expected: "tag/ref equals .harness-pin.yaml agent_skills.ref"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-008-W0.md § TASK-W0-01"
      - id: TASK-W0-02
        implements: [REQ-2, REQ-3]
        depends_on: [TASK-W0-01]
        files:
          - path: src/models/forge_types.py
            action: modify
          - path: src/models/handoff_models.py
            action: modify
          - path: src/business_services/workflow_engine.py
            action: modify
        exit:
          criteria:
            - "EA omit/unknown authorization fails closed; ResolvedWorkflowNode carries enum"
          proof:
            kind: command
            command: "make check && make test"
            expected: "exit 0; new auth parse tests pass"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-008-W0.md § TASK-W0-02"
      - id: TASK-W0-03
        implements: [REQ-2, REQ-11]
        depends_on: [TASK-W0-02]
        files:
          - path: tests/unit/test_handoff_workflow.py
            action: modify
          - path: tests/unit/test_forge_policy.py
            action: modify
        exit:
          criteria:
            - "Pass-1 unit tests assert loop-spec→wave-pr-action and required pre-implement commit"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; formerly red pin-edge tests green"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-008-W0.md § TASK-W0-03"
      - id: TASK-W0-04
        implements: [REQ-4]
        depends_on: []
        files:
          - path: docs/specification/adr/adr-009-pin-forge-publish-mutate-authority.md
            action: inspect
        exit:
          criteria:
            - "ADR-009 Status Accepted with dual-authorization amendment"
          proof:
            kind: review
            review: "PE/dev inspects adr-009 header Status and Amendment fields on tip"
            expected: "Status Accepted; amendment Accepted"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-008-W0.md § TASK-W0-04"
      - id: TASK-W0-05
        implements: [REQ-16]
        depends_on: [TASK-W0-02]
        files:
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "As-built records W0 parse/consume and INIT-006 REQ-7 supersession note"
          proof:
            kind: review
            review: "Inspect implementation-status.md INIT-008 / 006 rows after W0"
            expected: "rows match W0 delivery"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-008-W0.md § TASK-W0-05"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: false
        reason: "W0 is pin-field parse + unit hygiene only — no new callable product surface (P15 N/A)"
    body: |
      ## Wave goal

      Parse pin authorization on EA nodes; fix remounted Pass-1 unit suite; confirm ADR-009 Accepted.

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W0-01 | REQ-1 | — | harness≡submodule | command/git describe |
      | TASK-W0-02 | REQ-2, REQ-3 | TASK-W0-01 | auth parse fail-closed | command/make test |
      | TASK-W0-03 | REQ-2, REQ-11 | TASK-W0-02 | Pass-1 unit edges green | command/make test |
      | TASK-W0-04 | REQ-4 | — | ADR-009 Accepted | review |
      | TASK-W0-05 | REQ-16 | TASK-W0-02 | as-built W0 | review |

      ## Done when

      - [ ] All W0 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-008-gateflow.md

  - id: W1
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-008 W1] Automated forge apply + retire PR-at-start"
    depends_on:
      - W0
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-008-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_implement_lane
    tasks:
      - id: TASK-W1-01
        implements: [REQ-6, REQ-7]
        depends_on: []
        files:
          - path: src/business_services/policy_engine.py
            action: modify
        exit:
          criteria:
            - "Policy STOP for explicit EA only; automated EA not authorize-STOP"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; policy unit covers both modes"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-008-W1.md § TASK-W1-01"
      - id: TASK-W1-02
        implements: [REQ-7, REQ-8, REQ-9, REQ-12]
        depends_on: [TASK-W1-01]
        files:
          - path: src/business_services/forge_action_service.py
            action: modify
        exit:
          criteria:
            - "Shared apply merges pin⋉handoff; incomplete requires fail; authorize reuses apply"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-008-W1.md § TASK-W1-02"
      - id: TASK-W1-03
        implements: [REQ-5, REQ-8, REQ-11, REQ-12]
        depends_on: [TASK-W1-02]
        files:
          - path: src/business_services/run_orchestrator.py
            action: modify
        exit:
          criteria:
            - "Unit walker: loop-spec publish → automated wave-pr apply → live-verify STOP"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; authorize not invoked for automated hop"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-008-W1.md § TASK-W1-03"
      - id: TASK-W1-04
        implements: [REQ-9, REQ-10]
        depends_on: [TASK-W1-03]
        files:
          - path: src/business_services/run_orchestrator.py
            action: modify
          - path: tests/unit/test_run_orchestrator.py
            action: modify
        exit:
          criteria:
            - "Job start never create_or_update_pull_request; ensure_branch-only allowed; pr_number null until open"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-008-W1.md § TASK-W1-04"
      - id: TASK-W1-05
        implements: [REQ-8, REQ-10, REQ-11, REQ-16]
        depends_on: [TASK-W1-04]
        files:
          - path: tests/verify/verify_implement_lane.py
            action: modify
          - path: tests/README.md
            action: modify
        exit:
          criteria:
            - "Live script asserts new Pass-1 PR timing / feature map updated"
          proof:
            kind: command
            command: ".venv/bin/python -m tests.verify.verify_implement_lane"
            expected: "exit 0 under documented prereqs"
            evidence_expected: "Live-Verify-INIT-GATEFLOW-008-W1.md"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_implement_lane
        covers: [REQ-8, REQ-10, REQ-11]
        prerequisites:
          - "Gateflow API up; tests/config.yaml; worker+forge when asserting PR open"
        safe_test_data:
          - "Ephemeral initiative/ticket per tests config — no production mutation"
        steps:
          - "Run verify_implement_lane against local stack"
        expected_observations:
          - "No Draft PR at implement start; PR present after automated wave-pr when worker enabled"
        evidence_expected: "Live-Verify-INIT-GATEFLOW-008-W1.md"
        cleanup:
          - "Close ephemeral run/PR per script notes"
        stop_conditions:
          - "Non-zero exit or unexpected 5xx → stop; do not start Pass-2"
    body: |
      ## Wave goal

      Automated/explicit forge apply; retire PR-at-start; co-ship verify_implement_lane (P15).

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W1-01 | REQ-6, REQ-7 | — | policy branch | command/make test |
      | TASK-W1-02 | REQ-7, REQ-8, REQ-9, REQ-12 | TASK-W1-01 | shared apply | command/make test |
      | TASK-W1-03 | REQ-5, REQ-8, REQ-11, REQ-12 | TASK-W1-02 | walker automated | command/make test |
      | TASK-W1-04 | REQ-9, REQ-10 | TASK-W1-03 | no PR-at-start | command/make test |
      | TASK-W1-05 | REQ-8, REQ-10, REQ-11, REQ-16 | TASK-W1-04 | live implement_lane | command/verify_implement_lane |

      ## Done when

      - [ ] All W1 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-008-gateflow.md

  - id: W2
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-008 W2] WorkManifest prayog/v1 + docs"
    depends_on:
      - W1
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-008-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_board
    tasks:
      - id: TASK-W2-01
        implements: [REQ-13, REQ-14]
        depends_on: []
        files:
          - path: src/business_services/forge_action_service.py
            action: modify
          - path: src/models/work_manifest_models.py
            action: modify
        exit:
          criteria:
            - "Pin workmanifest_contract subprocess runs; launchpad/v1 rejected; prayog/v1 accepted"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-008-W2.md § TASK-W2-01"
      - id: TASK-W2-02
        implements: [REQ-15]
        depends_on: [TASK-W2-01]
        files:
          - path: src/business_services/forge_action_service.py
            action: modify
        exit:
          criteria:
            - "board-tickets-action still requires explicit authorize"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-008-W2.md § TASK-W2-02"
      - id: TASK-W2-03
        implements: [REQ-13, REQ-16]
        depends_on: [TASK-W2-01]
        files:
          - path: tests/verify/verify_board.py
            action: modify
          - path: tests/README.md
            action: modify
        exit:
          criteria:
            - "verify_board covers prayog/v1 validation posture"
          proof:
            kind: command
            command: ".venv/bin/python -m tests.verify.verify_board"
            expected: "exit 0 under documented prereqs"
            evidence_expected: "Live-Verify-INIT-GATEFLOW-008-W2.md"
      - id: TASK-W2-04
        implements: [REQ-16, REQ-17]
        depends_on: [TASK-W2-03]
        files:
          - path: docs/specification/as-built/implementation-status.md
            action: modify
          - path: tests/README.md
            action: modify
          - path: docs/specification/README.md
            action: modify
        exit:
          criteria:
            - "Docs show Pass-1 wave-pr edges; 007 dogfood unblocked after 008 on develop"
          proof:
            kind: review
            review: "Inspect as-built + tests/README Pass-1 chain + docs/specification/README active initiative"
            expected: "docs match shipped 008 behavior"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-008-W2.md § TASK-W2-04"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_board
        covers: [REQ-13, REQ-15]
        prerequisites:
          - "Gateflow API up; programme token; forge creds when creating issues"
        safe_test_data:
          - "Ephemeral board fixtures per tests/config.yaml"
        steps:
          - "Run verify_board"
        expected_observations:
          - "Invalid WorkManifest apiVersion rejected; prayog/v1 path documented/green"
        evidence_expected: "Live-Verify-INIT-GATEFLOW-008-W2.md"
        cleanup:
          - "Delete ephemeral board issues if created"
        stop_conditions:
          - "Unexpected mutate on failure path → stop"
    body: |
      ## Wave goal

      Pin WorkManifest prayog/v1 before board create; docs + REQ-17; co-ship verify_board (P15).

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W2-01 | REQ-13, REQ-14 | — | pin validator | command/make test |
      | TASK-W2-02 | REQ-15 | TASK-W2-01 | explicit board | command/make test |
      | TASK-W2-03 | REQ-13, REQ-16 | TASK-W2-01 | verify_board | command/verify_board |
      | TASK-W2-04 | REQ-16, REQ-17 | TASK-W2-03 | docs | review |

      ## Done when

      - [ ] All W2 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-008-gateflow.md
```

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-implementation-plan
  outcome: pass
  artifact:
    path: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-008.md
    digest: sha256:85721284092e63955391f8e14d60f73272657bd732c64e611e8eb95cce0d5287
  blockers: []
  signals:
    ready_for_coding_readiness: true
    workmanifest_api: prayog/v1
    draft_pr: "91"
    brand: 006A
    waves: "W0,W1,W2"
    p15_w1: verify_implement_lane
    p15_w2: verify_board
  next_candidates:
    - coding-readiness
  human_checkpoint: true
  external_action: false
  forge:
    action: commit_workspace
    # Pin: spec-implementation-plan commit_workspace = required.
```
