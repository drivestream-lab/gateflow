---
goal: INIT-GATEFLOW-009 — implementation plan
initiative: INIT-GATEFLOW-009
status: Planned
date_created: 2026-08-03
source_spec: docs/specification/product/INIT-GATEFLOW-009-gateflow.md
source_spec_digest: sha256:f4c93f4a13bb72617555fe320b3926130a0885ede45f9574c4ff1a09e2cad642
feasibility_report: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-009.md
feasibility_digest: sha256:36d16d9c31d43ebbed356f36efc415f30978c29821755cc328aa7b41f12ce0ca
technical_review: docs/specification/reports/Technical-Review-INIT-GATEFLOW-009.md
technical_review_digest: sha256:b314173e7e35104bbb62730816c9d94947057b6ae56eb3b45be82046af079562
prd_digest: sha256:76ab22b3c197b9d0cb6b08e6cea377c4e07b3a471b8a88203fddca6014c1c012
impact_map: prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-009.md
impact_map_revision: 1
repo_scope_digest: sha256:d0a2b62632113db0fa64cb7d7e63dc393fa5a8217092dda242a99b3392978e9b
approved_meta_pr_head: 6660aa4fefbcd80324cb970aa5bab642d3e5e0a1
branch: feature/INIT-GATEFLOW-009-w0-spec-lane
review_deadline: 2026-08-06
deciders: PE @drivestream-lab/prayog-pe-team
---

# Implementation plan — INIT-GATEFLOW-009

## Source freshness and command contract

| Item | Value | Status |
|------|-------|--------|
| Spec / digest | `docs/specification/product/INIT-GATEFLOW-009-gateflow.md` / `sha256:f4c93f4a…` | CURRENT |
| Feasibility / digest | `…/Initiative-Feasibility-Report-INIT-GATEFLOW-009.md` / `sha256:36d16d9c…` | CURRENT |
| Technical review / digest | `…/Technical-Review-INIT-GATEFLOW-009.md` / `sha256:b314173e…` | CURRENT — **Accepted** |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-009.md` / `1` | CURRENT |
| Repo scope digest | `sha256:d0a2b626…` | CURRENT |
| Approved meta PR head | `6660aa4fefbcd80324cb970aa5bab642d3e5e0a1` | CURRENT |
| `check_command` | `make check` | RESOLVED |
| `test_command` | `make test` | RESOLVED |
| `verify_command` | W1: `verify_spec_lane`; W2: `verify_wave_closeout`; W3: `verify_authorize` (create) | RESOLVED |
| `ground_command` | N/A — Pass-2 pin skill | N/A |

## 0. Technical design reference

| Item | Value |
|------|-------|
| Technical review | `Technical-Review-INIT-GATEFLOW-009.md` — Status: **Accepted** |
| PE sign-off | [x] complete — 2026-08-03 |
| Resolved ADRs | ADR-009, ADR-010, ADR-003, ADR-005, ADR-008 (all Accepted) |
| Outstanding questions | none — Q-1…Q-4 resolved in TDD §9 |

---

## 1. Requirements (REQ)

| ID | Summary | Waves |
|----|---------|-------|
| REQ-1 | Consume pin `v0.5.0-rc.2`; pin == submodule | W0 |
| REQ-2 | W0 prove-out checklist | W0 |
| REQ-3 | `POST /waves/spec/start` meta accept-gate | W1 |
| REQ-4 | Publish after content hops | W1 |
| REQ-5 | Automated `spec-pr-action` opens Draft Spec PR | W1 |
| REQ-6 | Later hops commit to same PR tip | W1 |
| REQ-7 | Walker stops at manual/human boundary | W1 |
| REQ-8 | W1 evidence: run id, PR URL, attestation | W1 |
| REQ-9 | `verify_spec_lane.py` W1 prove-out | W1 |
| REQ-10 | Spec-lane wrap-up via closeout to `wave-signoff` | W2 |
| REQ-11 | W2 lifts INIT-007 REQ-15 deferral | W2 |
| REQ-12 | W2 evidence: closeout run id, Pass-2 stages | W2 |
| REQ-13 | Explicit EA → STOP with pending forge | W3 |
| REQ-14 | Authorize → side effect | W3 |
| REQ-15 | W3 live: stop → authorize → side effect | W3 |
| REQ-16 | Feature readiness freeze record | W3 |
| REQ-17 | Freeze checklist includes planning note update | W3 |
| REQ-18 | As-built updated to match freeze | W3 |
| REQ-19 | Replace placeholder CI with `make check` + `make test` | W3 |
| REQ-20 | Prove-out PRs subject to same CI | W3 |

---

## 2. Implementation phases

### Phase W0 — Pin consume + prove-out checklist

**GOAL-W0:** Confirm pin consume-only; publish W0 prove-out checklist.

| Task | Implements | Depends | Files | Exit criteria | Proof | Branch |
|------|------------|---------|-------|---------------|-------|--------|
| TASK-W0-01 | REQ-1 | — | `.harness-pin.yaml` inspect | Pin resolves `spec-draft` orchestrated; pin == submodule | command / `make check` → exit 0 | `feature/INIT-GATEFLOW-009-w0-pin-checklist` |
| TASK-W0-02 | REQ-2 | TASK-W0-01 | `docs/specification/reports/W0-Prove-Out-Checklist-INIT-GATEFLOW-009.md` create | Checklist exists; PE can execute | review / inspection | same |

#### Files (W0)

| ID | Path | Action |
|----|------|--------|
| FILE-W0-01 | `docs/specification/reports/W0-Prove-Out-Checklist-INIT-GATEFLOW-009.md` | create |

#### Tests (W0)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W0-U | unit | `make test` | REQ-1 |
| TEST-W0-L | live | N/A — docs-only; P15 N/A | — |

#### Verification Coverage (W0)

| REQ | unit | smoke | Notes |
|-----|------|-------|-------|
| REQ-1 | TEST-W0-U | N/A | Pin load |
| REQ-2 | N/A | N/A | Inspection only |

#### Live-verification intent (W0)

Not applicable — docs-only wave; no new product surface (P15 N/A).

---

### Phase W1 — Spec Pass-1 live prove-out

**GOAL-W1:** Live Draft Spec PR tip deliverable; reviewer attestation.

| Task | Implements | Depends | Files | Exit criteria | Proof | Branch |
|------|------------|---------|-------|---------------|-------|--------|
| TASK-W1-01 | REQ-3,4,5,7,9 | TASK-W0-02 | `tests/verify/verify_spec_lane.py` inspect, `tests/config.yaml` modify | Script exit 0; 3 Cursor stages success; Draft Spec PR open; stopped at `technical-review-approval` | command / `verify_spec_lane` → exit 0 | `feature/INIT-GATEFLOW-009-w1-spec-prove` |
| TASK-W1-02 | REQ-6,8 | TASK-W1-01 | `docs/specification/reports/Live-Verify-INIT-GATEFLOW-009-W1.md` create | Live-Verify with run id, PR URL, reviewer sign-off | review / inspection | same |

#### Files (W1)

| ID | Path | Action |
|----|------|--------|
| FILE-W1-01 | `tests/verify/verify_spec_lane.py` | inspect |
| FILE-W1-02 | `tests/config.yaml` | modify |
| FILE-W1-03 | `docs/specification/reports/Live-Verify-INIT-GATEFLOW-009-W1.md` | create |

#### Tests (W1)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W1-U | unit | `make test` | REQ-3/5/7 regression |
| TEST-W1-L | live | `verify_spec_lane` | REQ-3…9 (Pass-1) |

#### Verification Coverage (W1)

| REQ | unit | smoke | Notes |
|-----|------|-------|-------|
| REQ-3 | TEST-W1-U | TEST-W1-L | Meta accept + start |
| REQ-4 | TEST-W1-U | TEST-W1-L | Publish after hops |
| REQ-5 | TEST-W1-U | TEST-W1-L | Automated spec-pr-action |
| REQ-7 | TEST-W1-U | TEST-W1-L | Stop at gate |
| REQ-9 | — | TEST-W1-L | Verify script exit 0 |

#### Live-verification intent (W1)

| Field | Value |
|-------|-------|
| Applicable | yes |
| Mode | smoke |
| Command | `.venv/bin/python -m tests.verify.verify_spec_lane` |
| Prerequisites | API + worker + Postgres + forge creds + meta PR #23 |
| Safe test data | Ephemeral `INIT-SPECLANE-*` |
| Expected | 3 Cursor stages success; Draft Spec PR; stopped at `technical-review-approval` |
| Evidence | `Live-Verify-INIT-GATEFLOW-009-W1.md` |
| Stop conditions | Non-zero exit or 5xx → stop |

---

### Phase W2 — Spec-lane wrap-up live prove-out

**GOAL-W2:** Spec closeout on W1 PR → Pass-2 to `wave-signoff`; lifts REQ-15 deferral.

| Task | Implements | Depends | Files | Exit criteria | Proof | Branch |
|------|------------|---------|-------|---------------|-------|--------|
| TASK-W2-01 | REQ-10,11,12 | TASK-W1-02 | `tests/verify/verify_wave_closeout.py` inspect, `tests/config.yaml` modify | Script exit 0; Pass-2 success; stopped at `wave-signoff` | command / `verify_wave_closeout` → exit 0 | `feature/INIT-GATEFLOW-009-w2-closeout-prove` |
| TASK-W2-02 | REQ-11,12 | TASK-W2-01 | `docs/specification/reports/Live-Verify-INIT-GATEFLOW-009-W2.md` create, `docs/specification/as-built/implementation-status.md` modify | Live-Verify; as-built REQ-15 deferral lifted | review / inspection | same |

#### Files (W2)

| ID | Path | Action |
|----|------|--------|
| FILE-W2-01 | `tests/verify/verify_wave_closeout.py` | inspect |
| FILE-W2-02 | `tests/config.yaml` | modify |
| FILE-W2-03 | `docs/specification/reports/Live-Verify-INIT-GATEFLOW-009-W2.md` | create |
| FILE-W2-04 | `docs/specification/as-built/implementation-status.md` | modify |

#### Tests (W2)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W2-U | unit | `make test` | REQ-10 regression |
| TEST-W2-L | live | `verify_wave_closeout` | REQ-10…12 (Pass-2) |

#### Verification Coverage (W2)

| REQ | unit | smoke | Notes |
|-----|------|-------|-------|
| REQ-10 | TEST-W2-U | TEST-W2-L | Closeout to wave-signoff |
| REQ-11 | — | TEST-W2-L | Deferral lifted |
| REQ-12 | — | TEST-W2-L | Evidence recorded |

#### Live-verification intent (W2)

| Field | Value |
|-------|-------|
| Applicable | yes |
| Mode | smoke |
| Command | `.venv/bin/python -m tests.verify.verify_wave_closeout` |
| Prerequisites | W1 Draft Spec PR merged; API + worker + Postgres |
| Expected | Pass-2 success; stopped at wave-signoff |
| Evidence | `Live-Verify-INIT-GATEFLOW-009-W2.md` |
| Stop conditions | Non-zero exit → stop |

---

### Phase W3 — Authorize live + freeze + CI

**GOAL-W3:** Live authorize prove-out; feature readiness freeze; replace placeholder CI.

| Task | Implements | Depends | Files | Exit criteria | Proof | Branch |
|------|------------|---------|-------|---------------|-------|--------|
| TASK-W3-01 | REQ-13,14,15 | TASK-W2-02 | `tests/verify/verify_authorize.py` create, `tests/config.yaml` modify | Script exit 0; run stops at EA; authorize → tickets visible; deny → no side effect | command / `verify_authorize` → exit 0 | `feature/INIT-GATEFLOW-009-w3-authorize-freeze` |
| TASK-W3-02 | REQ-16,17 | TASK-W3-01 | `docs/specification/reports/Feature-Readiness-INIT-GATEFLOW-009.md` create | Freeze record with proven/deferred tables | review / inspection | same |
| TASK-W3-03 | REQ-18 | TASK-W3-02 | `docs/specification/as-built/implementation-status.md` modify | As-built W1–W3 rows match freeze | review / inspection | same |
| TASK-W3-04 | REQ-19,20 | TASK-W3-01 | `.github/workflows/ci.yml` modify | CI runs `make check` + `make test`; placeholder replaced | command / CI run on PR | same |

#### Files (W3)

| ID | Path | Action |
|----|------|--------|
| FILE-W3-01 | `tests/verify/verify_authorize.py` | create |
| FILE-W3-02 | `tests/config.yaml` | modify |
| FILE-W3-03 | `docs/specification/reports/Feature-Readiness-INIT-GATEFLOW-009.md` | create |
| FILE-W3-04 | `docs/specification/as-built/implementation-status.md` | modify |
| FILE-W3-05 | `.github/workflows/ci.yml` | modify |

#### Tests (W3)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W3-U | unit | `make test` | REQ-13/14 regression |
| TEST-W3-L | live | `verify_authorize` | REQ-13…15 (authorize) |
| TEST-W3-C | CI | GitHub Actions on PR | REQ-19/20 |

#### Verification Coverage (W3)

| REQ | unit | smoke | CI | Notes |
|-----|------|-------|----|-------|
| REQ-13 | TEST-W3-U | TEST-W3-L | — | STOP at explicit EA |
| REQ-14 | TEST-W3-U | TEST-W3-L | — | Authorize → side effect |
| REQ-15 | — | TEST-W3-L | — | Live evidence |
| REQ-16 | — | — | — | Inspection (freeze) |
| REQ-19 | — | — | TEST-W3-C | CI job |
| REQ-20 | — | — | TEST-W3-C | CI on PRs |

#### Live-verification intent (W3)

| Field | Value |
|-------|-------|
| Applicable | yes |
| Mode | smoke |
| Command | `.venv/bin/python -m tests.verify.verify_authorize` |
| Prerequisites | API + worker + Postgres + forge creds + plan on develop |
| Safe test data | Ephemeral initiative for authorize |
| Expected | Stop at board-tickets-action; authorize → tickets; deny → no side effect |
| Evidence | `Live-Verify-INIT-GATEFLOW-009-W3.md` |
| Stop conditions | Non-zero exit or unexpected mutate → stop |

---

## 3. Dependencies (DEP)

| ID | Dependency | Blocks |
|----|------------|--------|
| DEP-1 | Pin `v0.5.0-rc.2` remounted (done) | W0 |
| DEP-2 | Meta PR #23 Gate 1 approved (done) | W1 |
| DEP-3 | W1 Draft Spec PR merged | W2 |
| DEP-4 | Implementation plan on develop | W3 authorize |
| DEP-5 | Forge creds (GitHub App) configured | W1, W3 |

---

## 4. Risks (RISK)

| ID | Risk | Mitigation |
|----|------|------------|
| RISK-1 | W1 publish edge case (remote-only SHA) | Fixed in chore #112; re-run verify_spec_lane |
| RISK-2 | W3 authorize target (Q-2) | Default `board-tickets-action` per TDD §9 |
| RISK-3 | W2 lifts REQ-15 deferral — on critical path | Plan W2 before W3; no PE waiver |

---

## 5. Out of scope

- Ops portal / gateflow-ops UI (next initiative)
- Second coding agent (OpenCode/Claude) going live
- Slack/Teams alerts
- Rebuilding implement-lane walker or metrics
- Auto-merge or authorize→resume Pass-1
- Skills pin redesign or new RC

---

## 6. As-built and docs tasks

| Task | File | Action |
|------|------|--------|
| Update implementation-status.md | `docs/specification/as-built/implementation-status.md` | mark wave in_progress → complete per wave |
| Update tests/README.md | `tests/README.md` | add verify_authorize to feature map (W3) |

---

## 7. Plan check summary

| Check | Status |
|-------|--------|
| P1 REQ coverage | PASS — REQ-1…20 all in §1; every TASK implements ≥1 REQ |
| P2 TASK→REQ | PASS — every TASK has Implements; no shadow REQ-W* |
| P3 FILE paths | PASS — every TASK has files or docs-only |
| P4 Exit evidence | PASS — every TASK has criteria + proof + expected + evidence_expected |
| P5 Verification layers | PASS — unit + live per wave; P15 co-ship for W1/W2/W3 |
| P6 Scope | PASS — prove-out only; no new product APIs |
| P7 Risks | PASS — RISK-1…3 with mitigations |
| P8 Wave order | PASS — W0→W1→W2→W3 |
| P9 As-built/README | PASS — listed in §6 |
| P10 Self-contained | PASS — commands + digests resolved |
| P11 MDC conformance | PASS — testing-verify-flows, spec-driven-development |
| P12 ADR conformance | PASS — ADR-009/010 Accepted; no NEW-ADR |
| P13 TDD Accepted | PASS — Status: Accepted; ready_for_plan: true |
| P14 WorkManifest seed | PASS — §9 present; wave IDs match |
| P15 Co-ship live verify | PASS — W1/W2/W3 each have live_verify_dir FILE |
| P16 WorkManifest contract | PASS — prayog/v1 (validate after §9 complete) |

---

## 8. Forge / PR instructions

> Persist this plan locally and publish via `/commit-workspace` to the Draft spec PR branch. Label remains `spec-pending` until PE completes §10.

---

## 10. Coding-readiness unlock (PE — after plan on head)

| Item | Value |
|------|-------|
| Workflow outcome | `pass` — P1–P16 PASS; TDD Accepted; sources CURRENT |
| Verdict | GATE OPEN REQUEST |
| Spec PR | https://github.com/drivestream-lab/gateflow/pull/119 |
| Gate label (current) | `spec-pending` |
| Gate label (target) | `spec-lgtm` |
| Local plan path | `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-009.md` |
| Forge readiness | fill `handoff.forge` for `commit_workspace` |
| Blocking items | none |

PE actions (all on exact current head):
1. Remove `spec-pending`; add `spec-lgtm`
2. Submit GitHub Approve with attestation body
3. Mark Draft PR Ready for review
4. Authorize merge; then `/create-board-tickets` from §9

---

## 9. WorkManifest seed

```yaml
# Generated by /spec-implementation-plan — 2026-08-03
# LOCAL — do not commit to prayog-skills upstream
apiVersion: prayog/v1
kind: WorkManifest

initiative: INIT-GATEFLOW-009

metadata:
  title: INIT-GATEFLOW-009 — Both-lane delivery factory prove-out
  summary: |
    Prove the spec lane and authorize API path live; freeze H1.5; replace placeholder CI.
  playbook:
    - docs/specification/product/INIT-GATEFLOW-009-gateflow.md
    - docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-009.md

target:
  org: drivestream-lab
  project: "drivestream-lab Board"

defaults:
  initiative: INIT-GATEFLOW-009
  parent: EPIC
  labels:
    - INIT-GATEFLOW-009

epic:
  id: EPIC
  repo: drivestream-lab/gateflow
  title: "[feature] INIT-GATEFLOW-009 — Both-lane delivery factory prove-out"
  codebase: drivestream-lab/gateflow
  spec_path: docs/specification/product/INIT-GATEFLOW-009-gateflow.md
  verify_command: .venv/bin/python -m tests.verify.verify_spec_lane
  body: |
    ## Objective

    Prove the existing Gateflow factory for the spec lane and authorize API path;
    freeze H1.5; replace placeholder CI.

    ## Waves

    | Wave | Goal |
    |------|------|
    | W0 | Pin consume + prove-out checklist |
    | W1 | Spec Pass-1 live prove-out |
    | W2 | Spec-lane wrap-up live prove-out |
    | W3 | Authorize live + freeze + CI |

    ## References

    - Spec: docs/specification/product/INIT-GATEFLOW-009-gateflow.md
    - Plan: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-009.md
    - TDD: docs/specification/reports/Technical-Review-INIT-GATEFLOW-009.md

work:
  - id: W0
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-009 W0] Pin consume + prove-out checklist"
    depends_on: []
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-009-gateflow.md
    verify_command: "N/A — docs-only; P15 N/A"
    tasks:
      - id: TASK-W0-01
        implements: [REQ-1]
        depends_on: []
        files:
          - path: .harness-pin.yaml
            action: inspect
        exit:
          criteria:
            - "Pin resolves spec-draft orchestrated; pin == submodule"
          proof:
            kind: command
            command: "make check"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-009-W0.md § TASK-W0-01"
      - id: TASK-W0-02
        implements: [REQ-2]
        depends_on: [TASK-W0-01]
        files:
          - path: docs/specification/reports/W0-Prove-Out-Checklist-INIT-GATEFLOW-009.md
            action: create
        exit:
          criteria:
            - "Checklist artifact exists; PE can execute"
          proof:
            kind: review
            review: "Inspect checklist sections"
            expected: "checklist present"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-009-W0.md § TASK-W0-02"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: false
        reason: "docs-only wave; no new product surface (P15 N/A)"
    body: |
      ## Wave goal

      Confirm pin consume-only; publish W0 prove-out checklist.

      ## Tasks (from plan §2)

      | Task | Implements | Exit criteria | Proof |
      |------|------------|---------------|-------|
      | TASK-W0-01 | REQ-1 | Pin resolves | command/make check |
      | TASK-W0-02 | REQ-2 | Checklist exists | review/inspection |

      ## Done when

      - [ ] All W0 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-009-gateflow.md

  - id: W1
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-009 W1] Spec Pass-1 live prove-out"
    depends_on:
      - W0
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-009-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_spec_lane
    tasks:
      - id: TASK-W1-01
        implements: [REQ-3, REQ-4, REQ-5, REQ-7, REQ-9]
        depends_on: []
        files:
          - path: tests/verify/verify_spec_lane.py
            action: inspect
          - path: tests/config.yaml
            action: modify
        exit:
          criteria:
            - "verify_spec_lane exit 0; 3 Cursor stages success; Draft Spec PR open"
          proof:
            kind: command
            command: ".venv/bin/python -m tests.verify.verify_spec_lane"
            expected: "exit 0"
            evidence_expected: "Live-Verify-INIT-GATEFLOW-009-W1.md"
      - id: TASK-W1-02
        implements: [REQ-6, REQ-8]
        depends_on: [TASK-W1-01]
        files:
          - path: docs/specification/reports/Live-Verify-INIT-GATEFLOW-009-W1.md
            action: create
        exit:
          criteria:
            - "Live-Verify report with run id, PR URL, reviewer sign-off"
          proof:
            kind: review
            review: "Inspect Live-Verify report"
            expected: "docs match live Pass-1 evidence"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-009-W1.md § TASK-W1-02"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_spec_lane
        covers: [REQ-3, REQ-4, REQ-5, REQ-7, REQ-9]
        prerequisites:
          - "API + worker + Postgres + forge creds + meta PR #23"
        safe_test_data:
          - "Ephemeral INIT-SPECLANE-* initiative per config"
        steps:
          - "Run verify_spec_lane with dogfood knobs"
        expected_observations:
          - "3 Cursor stages success; Draft Spec PR; stopped at technical-review-approval"
        evidence_expected: "Live-Verify-INIT-GATEFLOW-009-W1.md"
        cleanup:
          - "Close ephemeral runs/PRs per script notes"
        stop_conditions:
          - "Non-zero exit or unexpected 5xx → stop"
    body: |
      ## Wave goal

      Live Draft Spec PR tip deliverable; reviewer attestation.

      | Task | Implements | Exit criteria | Proof |
      |------|------------|---------------|-------|
      | TASK-W1-01 | REQ-3,4,5,7,9 | verify_spec_lane exit 0 | command |
      | TASK-W1-02 | REQ-6,8 | Live-Verify report | review |

      ## Done when

      - [ ] All W1 tasks complete per plan exit proof

  - id: W2
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-009 W2] Spec-lane wrap-up live prove-out"
    depends_on:
      - W1
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-009-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_wave_closeout
    tasks:
      - id: TASK-W2-01
        implements: [REQ-10, REQ-11, REQ-12]
        depends_on: []
        files:
          - path: tests/verify/verify_wave_closeout.py
            action: inspect
          - path: tests/config.yaml
            action: modify
        exit:
          criteria:
            - "verify_wave_closeout exit 0; Pass-2 success; stopped at wave-signoff"
          proof:
            kind: command
            command: ".venv/bin/python -m tests.verify.verify_wave_closeout"
            expected: "exit 0"
            evidence_expected: "Live-Verify-INIT-GATEFLOW-009-W2.md"
      - id: TASK-W2-02
        implements: [REQ-11, REQ-12]
        depends_on: [TASK-W2-01]
        files:
          - path: docs/specification/reports/Live-Verify-INIT-GATEFLOW-009-W2.md
            action: create
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "as-built REQ-15 deferral lifted"
          proof:
            kind: review
            review: "Inspect as-built and Live-Verify"
            expected: "deferral lifted"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-009-W2.md § TASK-W2-02"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_wave_closeout
        covers: [REQ-10, REQ-11, REQ-12]
        prerequisites:
          - "W1 Draft Spec PR merged; API + worker + Postgres"
        safe_test_data:
          - "Ephemeral closeout run on spec PR"
        steps:
          - "Run verify_wave_closeout with closeout knobs"
        expected_observations:
          - "Pass-2 success; stopped at wave-signoff"
        evidence_expected: "Live-Verify-INIT-GATEFLOW-009-W2.md"
        cleanup:
          - "Close ephemeral runs per script notes"
        stop_conditions:
          - "Non-zero exit → stop"
    body: |
      ## Wave goal

      Spec closeout on W1 PR → Pass-2 to wave-signoff; lifts REQ-15 deferral.

      | Task | Implements | Exit criteria | Proof |
      |------|------------|---------------|-------|
      | TASK-W2-01 | REQ-10,11,12 | verify_wave_closeout exit 0 | command |
      | TASK-W2-02 | REQ-11,12 | deferral lifted | review |

      ## Done when

      - [ ] All W2 tasks complete per plan exit proof

  - id: W3
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-009 W3] Authorize live + freeze + CI"
    depends_on:
      - W2
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-009-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_authorize
    tasks:
      - id: TASK-W3-01
        implements: [REQ-13, REQ-14, REQ-15]
        depends_on: []
        files:
          - path: tests/verify/verify_authorize.py
            action: create
          - path: tests/config.yaml
            action: modify
        exit:
          criteria:
            - "verify_authorize exit 0; stop → authorize → tickets visible; deny → no side effect"
          proof:
            kind: command
            command: ".venv/bin/python -m tests.verify.verify_authorize"
            expected: "exit 0"
            evidence_expected: "Live-Verify-INIT-GATEFLOW-009-W3.md"
      - id: TASK-W3-02
        implements: [REQ-16, REQ-17]
        depends_on: [TASK-W3-01]
        files:
          - path: docs/specification/reports/Feature-Readiness-INIT-GATEFLOW-009.md
            action: create
        exit:
          criteria:
            - "Freeze record with proven/deferred tables"
          proof:
            kind: review
            review: "Inspect freeze record"
            expected: "proven/deferred tables present"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-009-W3.md § TASK-W3-02"
      - id: TASK-W3-03
        implements: [REQ-18]
        depends_on: [TASK-W3-02]
        files:
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "As-built W1–W3 rows match freeze"
          proof:
            kind: review
            review: "Inspect as-built"
            expected: "rows match freeze"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-009-W3.md § TASK-W3-03"
      - id: TASK-W3-04
        implements: [REQ-19, REQ-20]
        depends_on: [TASK-W3-01]
        files:
          - path: .github/workflows/ci.yml
            action: modify
        exit:
          criteria:
            - "CI runs make check + make test; placeholder replaced"
          proof:
            kind: command
            command: "CI run on PR"
            expected: "job passes on green tree"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-009-W3.md § TASK-W3-04"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_authorize
        covers: [REQ-13, REQ-14, REQ-15]
        prerequisites:
          - "API + worker + Postgres + forge creds + plan on develop"
        safe_test_data:
          - "Ephemeral initiative for authorize dogfood"
        steps:
          - "Run verify_authorize with authorize knobs"
        expected_observations:
          - "Stop at board-tickets-action; authorize → tickets; deny → no side effect"
        evidence_expected: "Live-Verify-INIT-GATEFLOW-009-W3.md"
        cleanup:
          - "Close ephemeral runs/tickets per script notes"
        stop_conditions:
          - "Non-zero exit or unexpected mutate → stop"
    body: |
      ## Wave goal

      Live authorize prove-out; feature readiness freeze; replace placeholder CI.

      | Task | Implements | Exit criteria | Proof |
      |------|------------|---------------|-------|
      | TASK-W3-01 | REQ-13,14,15 | verify_authorize exit 0 | command |
      | TASK-W3-02 | REQ-16,17 | freeze record | review |
      | TASK-W3-03 | REQ-18 | as-built match | review |
      | TASK-W3-04 | REQ-19,20 | CI runs | command/CI |

      ## Done when

      - [ ] All W3 tasks complete per plan exit proof
```

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-implementation-plan
  outcome: pass
  artifact:
    path: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-009.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-009
    tdd_status: Accepted
    ready_for_plan: true
    prd_digest: "sha256:76ab22b3c197b9d0cb6b08e6cea377c4e07b3a471b8a88203fddca6014c1c012"
    scope_digest: "sha256:d0a2b62632113db0fa64cb7d7e63dc393fa5a8217092dda242a99b3392978e9b"
    impact_map_revision: 1
    approved_meta_pr_head: "6660aa4fefbcd80324cb970aa5bab642d3e5e0a1"
    check_command: "make check"
    test_command: "make test"
    verify_command_w1: ".venv/bin/python -m tests.verify.verify_spec_lane"
    verify_command_w2: ".venv/bin/python -m tests.verify.verify_wave_closeout"
    verify_command_w3: ".venv/bin/python -m tests.verify.verify_authorize"
  next_candidates:
    - coding-readiness
  human_checkpoint: true
  external_action: false
  forge:
    action: commit_workspace
```
