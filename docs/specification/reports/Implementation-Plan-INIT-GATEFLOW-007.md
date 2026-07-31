---
goal: INIT-GATEFLOW-007 — implementation plan (prayog/v1 WorkManifest backfill)
initiative: INIT-GATEFLOW-007
status: Planned
date_created: 2026-07-30
date_updated: 2026-07-31
source_spec: docs/specification/product/INIT-GATEFLOW-007-gateflow.md
source_spec_digest: sha256:4cfec83c18e6e1653baf0876383c8bab6fdc5b511c19254d45adb4156b0cf017
feasibility_report: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-007.md
feasibility_digest: sha256:651cc16583fcc56fa76009b0f5ec628f3a26e022356de59224f33c653fdfd0ce
technical_review: docs/specification/reports/Technical-Review-INIT-GATEFLOW-007.md
technical_review_digest: sha256:b490d9cdfbffbafe459d79320e43106151d8fdd3ea6cca835714dfa0e7e161d0
prd_digest: TBD — Gate 1 open (Q-1 waived for engineering package)
impact_map: TBD
impact_map_revision: TBD
repo_scope_digest: TBD — gateflow-only
approved_meta_pr_head: TBD
branch: chore/INIT-GATEFLOW-007-plan-prayog-v1-backfill
review_deadline: 2026-08-05
deciders: PE @nikd10x / prayog-pe-team — spec-lgtm + Approve on exact head after plan package
---

# Implementation plan — INIT-GATEFLOW-007

> **Backfill (2026-07-31):** §9 regenerated to pin **`prayog/v1`** WorkManifest
> (`files` / `exit` / wave `verification`; no mutable `status`). Same product REQs /
> TDD / P15 co-ship smoke as the 2026-07-30 plan. Board EPIC [#84](https://github.com/drivestream-lab/gateflow/issues/84)
> + waves [#85](https://github.com/drivestream-lab/gateflow/issues/85)–[#87](https://github.com/drivestream-lab/gateflow/issues/87)
> already seeded — **do not** purge or re-seed; TASK ids unchanged.
>
> **Prior regen (2026-07-30):** Replaced the 2026-07-29 plan that deferred live verify
> to W2 (fails pin **P15**). W0 co-ships smoke `tests/verify/verify_wave_closeout.py`;
> full Pass-2 dogfood remains W2.

## Source freshness and command contract

| Item | Value | Status |
|------|-------|--------|
| Spec / digest | `docs/specification/product/INIT-GATEFLOW-007-gateflow.md` / `sha256:4cfec83c18e6e1653baf0876383c8bab6fdc5b511c19254d45adb4156b0cf017` | CURRENT on branch (Gate 1 digests **WAIVED**) |
| Feasibility / digest | `…/Initiative-Feasibility-Report-INIT-GATEFLOW-007.md` / `sha256:651cc16583fcc56fa76009b0f5ec628f3a26e022356de59224f33c653fdfd0ce` | CURRENT |
| Technical review / digest | `…/Technical-Review-INIT-GATEFLOW-007.md` / `sha256:b490d9cdfbffbafe459d79320e43106151d8fdd3ea6cca835714dfa0e7e161d0` | CURRENT — Status **Accepted** |
| Impact map / revision | TBD | **WAIVED** — Q-1 |
| Repo scope digest | TBD | **WAIVED** — Q-1 |
| Approved meta PR head | TBD | **WAIVED** — Q-1 |
| `check_command` | `make check` | RESOLVED |
| `test_command` | `make test` | RESOLVED |
| `verify_command` | Per wave live under `tests/verify/` — W0/W2: `.venv/bin/python -m tests.verify.verify_wave_closeout`; W1: N/A (no new HTTP surface — P15 N/A) | RESOLVED |
| `ground_command` | N/A — `/ground-spec` is Pass-2 pin skill (orchestrated), not a Makefile target | N/A |

> Gate 1 STALE/WAIVED matches feasibility + TDD. Engineering plan proceeds; formal
> CURRENT still needs Q-1. Do not use `{test_command}` as live `verify_command`.

## 0. Technical design reference

| Item | Value |
|------|-------|
| Technical review | [`Technical-Review-INIT-GATEFLOW-007.md`](Technical-Review-INIT-GATEFLOW-007.md) |
| PE sign-off | [x] complete — 2026-07-29 (fold into ADR-010; prior plan on #77). P15 regen #83 + this `prayog/v1` §9 backfill keep Accepted TDD/ADR; PE re-`spec-lgtm` on new plan head. |
| Resolved ADRs | [`adr-010-lane-intake-and-dual-workspace-authority.md`](../adr/adr-010-lane-intake-and-dual-workspace-authority.md) (**Accepted**, closeout §6); ADR-001/005/007/008/009 **Accepted** — **no ADR-011** (TDD §4 ADR_REQUIRED=0) |
| Outstanding PM questions | Q-1 Gate 1 meta PRD / waive — blocks formal CURRENT only |
| Outstanding domain questions | none |

> Do not start W0 implementation until this plan is merged with `spec-lgtm` on head
> (or PE explicitly authorizes engineering continue under Gate 1 waive).

---

## 1. Requirements (REQ) — product ids

| ID | Summary | Spec path | Waves |
|----|---------|-----------|-------|
| REQ-1 | `POST /api/v1/waves/closeout/start` + programme token | `docs/specification/product/INIT-GATEFLOW-007-gateflow.md` | W0 |
| REQ-2 | Fixed Enter-at `learning-extract`; reject client `start_node` | same | W0 |
| REQ-3 | New run + PR bind; ACTIVE concurrent 409 | same | W0 |
| REQ-4 | Closeout body fields; `extra=forbid` | same | W0 |
| REQ-5 | Bind to pin `learning-extract` schema | same | W0 |
| REQ-6 | Both lanes; meta fields not required on closeout | same | W0 |
| REQ-7 | Walker Pass-2 → `wave-signoff`; no auto `verify` | same | W0, W2 |
| REQ-8 | Handoff + baton dual-write (ADR-008) | same | W0 |
| REQ-9 | Postgres learning ingest from Learning-Extract YAML | same | W1, W2 |
| REQ-10 | Learning item taxonomy `L-*` / classes | same | W1 |
| REQ-11 | No skill→Gateflow HTTP as success (H6) | same | W1 |
| REQ-12 | Ground Report cites `L-*` (pin-owned; tip evidence) | same | W1, W2 |
| REQ-13 | Optional `prior_run_id` audit-only | same | W0 |
| REQ-14 | Live implement closeout prove-it (full Pass-2) | same | W2 |
| REQ-15 | Spec-lane closeout parity / PE deferral | same | W2 |
| REQ-16 | Checkpoint id hygiene (`src/` + mocks) | same | W0, W2 |
| REQ-17 | As-built + feature map | same | W0, W1, W2 |

---

## 2. Implementation phases

### Phase W0 — Closeout start API + Pass-2 walker + smoke verify

**GOAL-W0:** Programme-token `POST /api/v1/waves/closeout/start` creates a new run
bound to an existing PR, Enter-ats `learning-extract`, walks to `wave-signoff`
(unit + pin fixtures); **co-ship** smoke live script asserting the new HTTP
surface (P15). No learning DB yet. Full Pass-2 dogfood is W2.

| Task | Description | Implements | Codebase | Spec path | Done when | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|----------|-----------|-----------|----------------|-----------|-----------|--------|
| TASK-W0-01 | Add `CloseoutWaveStartRequest` (+ response reuse); forbid `start_node` / meta fields; require absolute `workspace_path` + `pr_number` | REQ-4, REQ-6, REQ-13 | gateflow | `docs/specification/product/INIT-GATEFLOW-007-gateflow.md` | Model validates; undeclared keys rejected | `make check && make test` | `pydantic-schemas.mdc`, `http-api-conventions.mdc` | ADR-010 §6 | `feature/INIT-GATEFLOW-007-w0-closeout-start` |
| TASK-W0-02 | Mount `POST /api/v1/waves/closeout/start`; programme token; `public_paths` | REQ-1 | gateflow | same | OpenAPI + 401 without token | `make test` | `architecture.mdc` | ADR-005 | same |
| TASK-W0-03 | `WaveStartService.start_closeout_wave`: fixed Enter-at; pin orchestrated check; ACTIVE 409; new run + baton; enqueue | REQ-2, REQ-3, REQ-5, REQ-8, REQ-13 | gateflow | same | Unit: happy + 400/409; baton path set; `start_node=learning-extract` | `make test` | `fail-fast.mdc` | ADR-010, ADR-007, ADR-008 | same |
| TASK-W0-04 | Unit walker Pass-2: learning-extract → ground-spec → stop `wave-signoff`; no verify dispatch | REQ-7, REQ-8 | gateflow | same | Orchestrator/handoff tests green | `make test` | — | ADR-009 forge reuse | same |
| TASK-W0-05 | Checkpoint mock hygiene: retarget `wave-human-decision` → `wave-signoff` / `live-verify` in unit mocks | REQ-16 | gateflow | same | `rg` clean in `tests/unit` for retired ids (allow historical docs) | `make test` | — | pin rename | same |
| TASK-W0-06 | Co-ship `tests/verify/verify_wave_closeout.py` **smoke**: 401; body validation; happy enqueue → `run_id` (+ soft-skip deeper Pass-2 without tip/worker); `config.yaml.example` knobs | REQ-1, REQ-7, REQ-17 | gateflow | same | Script exists; feature-map row; human can run command | `.venv/bin/python -m tests.verify.verify_wave_closeout` | `testing-verify-flows.mdc` | — | same |
| TASK-W0-07 | As-built W0 row + README: closeout API + smoke verify command (unit + script present; full dogfood W2) | REQ-17 | gateflow | same | Docs match tip | inspection | SDD | — | same |

#### Files (W0)

| ID | Path | Action |
|----|------|--------|
| FILE-W0-01 | `src/models/wave_start_models.py` (or `wave_closeout_models.py`) | create/edit |
| FILE-W0-02 | `src/api/v1/waves_routes.py` | edit |
| FILE-W0-03 | `src/app.py` (`public_paths`) | edit |
| FILE-W0-04 | `src/business_services/wave_start_service.py` | edit |
| FILE-W0-05 | `tests/unit/test_wave_closeout.py` | create |
| FILE-W0-06 | `tests/unit/test_run_orchestrator.py`, `test_handoff_workflow.py` | edit |
| FILE-W0-07 | `tests/unit/test_trigger_policy.py`, `test_notifier.py` | edit |
| FILE-W0-08 | `tests/verify/verify_wave_closeout.py` | create |
| FILE-W0-09 | `tests/config.yaml.example`, `tests/README.md` | edit |
| FILE-W0-10 | `docs/specification/as-built/implementation-status.md` | edit |

#### Tests (W0)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W0-U | unit | `make check && make test` | REQ-1…8, REQ-13, REQ-16 |
| TEST-W0-L | live | `.venv/bin/python -m tests.verify.verify_wave_closeout` | Closeout HTTP surface (P15); human-run at `live-verify` |

> **Smoke vs dogfood:** W0 script asserts accept path (auth, validation, enqueue /
> `run_id`). Optional deeper stages soft-skip without Pass-1 tip + worker.
> W2 extends the same module for full stop @ `wave-signoff` + learning evidence.

---

### Phase W1 — Learning Postgres ingest

**GOAL-W1:** After `learning-extract` hop, parse Learning-Extract YAML into
`learning_extracts` / `learning_items` (TDD §8.1); no skill HTTP; human Alembic.
**P15:** no new HTTP / lane-start surface — live `verify_command` N/A this wave;
ingest proven by unit; full live ingest evidence in W2 dogfood.

| Task | Description | Implements | Codebase | Spec path | Done when | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|----------|-----------|-----------|----------------|-----------|-----------|--------|
| TASK-W1-01 | ORM schema + Pydantic learning models/enums per TDD §8.1; env.py import | REQ-9, REQ-10 | gateflow | same | pyright clean; schema modules registered | `make check` | `repository-pattern.mdc`, `database-migrations.mdc` | ADR-001 | `feature/INIT-GATEFLOW-007-w1-learning-ingest` |
| TASK-W1-02 | **Human** Alembic revision for learning tables | REQ-9 | gateflow | same | Migration applied locally; upgrade/downgrade symmetric | `./scripts/run_postgres_migration.sh` (human) | human-owned versions | ADR-001 | same |
| TASK-W1-03 | `LearningRepository` + `LearningIngestService`; DI bind | REQ-9, REQ-10, REQ-11 | gateflow | same | Unit parse/upsert/idempotent; unknown class fails | `make test` | `pydantic-schemas.mdc`, `dependency-injection.mdc` | ADR-001, ADR-003 | same |
| TASK-W1-04 | Orchestrator hook: after learning-extract hop, publish-before-ingest then learning ingest before ground-spec | REQ-9, REQ-11, REQ-12 | gateflow | same | Unit order asserted; missing artifact fails closed | `make test` | `fail-fast.mdc` | ADR-009 ordering | same |
| TASK-W1-05 | As-built W1 + README learning note | REQ-17 | gateflow | same | Docs updated | inspection | — | — | same |

#### Files (W1)

| ID | Path | Action |
|----|------|--------|
| FILE-W1-01 | `src/models/learning_models.py` | create |
| FILE-W1-02 | `src/database/postgres/schema/learning_schema.py` | create |
| FILE-W1-03 | `src/database/postgres/repository/learning_repository.py` | create |
| FILE-W1-04 | `src/business_services/learning_ingest_service.py` | create |
| FILE-W1-05 | `src/business_services/run_orchestrator.py` | edit |
| FILE-W1-06 | `src/di/modules/*`, `dependency_container.py` | edit |
| FILE-W1-07 | `postgres_migrations/env.py` | edit (import) |
| FILE-W1-08 | `postgres_migrations/versions/*` | **human create** |
| FILE-W1-09 | `tests/unit/test_learning_ingest.py` | create |
| FILE-W1-10 | as-built, `tests/README.md` | edit |

#### Tests (W1)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W1-U | unit | `make check && make test` | REQ-9…12 |
| TEST-W1-M | migration | human script | REQ-9 DDL |
| TEST-W1-L | live | N/A — P15 does not apply (no new product HTTP/lane surface); dogfood in W2 | — |

---

### Phase W2 — Full Pass-2 dogfood + docs closeout

**GOAL-W2:** Live implement-lane Pass-1 stop → closeout start → `wave-signoff`;
Learning-Extract + DB rows; Ground cites `L-*`; extend W0 smoke script to full
dogfood; spec-lane parity or PE-waived deferral; final checkpoint hygiene.

| Task | Description | Implements | Codebase | Spec path | Done when | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|----------|-----------|-----------|----------------|-----------|-----------|--------|
| TASK-W2-01 | Extend `tests/verify/verify_wave_closeout.py` for full Pass-2 (implement): stop @ `wave-signoff`, learning artifact/rows when configured; config.example opt-in | REQ-7, REQ-9, REQ-14 | gateflow | same | Script exits 0 against live stack (implement path) | `.venv/bin/python -m tests.verify.verify_wave_closeout` | `testing-verify-flows.mdc` | — | `feature/INIT-GATEFLOW-007-w2-closeout-prove` |
| TASK-W2-02 | Feature map + as-built live row (run id, tip, L-* cite evidence) | REQ-12, REQ-14, REQ-17 | gateflow | same | Docs match live | inspection | SDD | — | same |
| TASK-W2-03 | Spec-lane closeout live **or** as-built PE-waived deferral row | REQ-15 | gateflow | same | Live pass or explicit deferral documented | `verify_wave_closeout` (spec) or inspection | — | — | same |
| TASK-W2-04 | Final `src/` grep: no live transition constants on `gate-1`/`gate-2`/`wave-human-decision` | REQ-16 | gateflow | same | Grep clean in `src/` | `make test` + rg | — | pin | same |

#### Files (W2)

| ID | Path | Action |
|----|------|--------|
| FILE-W2-01 | `tests/verify/verify_wave_closeout.py` | edit (dogfood depth) |
| FILE-W2-02 | `tests/config.yaml.example`, `tests/README.md` | edit |
| FILE-W2-03 | `docs/specification/as-built/implementation-status.md` | edit |
| FILE-W2-04 | Ground report for wave (human/skill) | create at wave close |

#### Tests (W2)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W2-L | live | `.venv/bin/python -m tests.verify.verify_wave_closeout` | REQ-14…17 (full Pass-2) |

---

## 3. Dependencies (DEP)

| ID | Dependency | Blocks |
|----|------------|--------|
| DEP-1 | Pass-1 pin remounted (`learning-extract` orchestrated) — **done** (#76) | W0 Enter-at |
| DEP-2 | W0 closeout enqueue + smoke script | W1 ingest hook; human live-verify |
| DEP-3 | W1 human Alembic applied | W1/W2 live ingest |
| DEP-4 | Pass-1 implement PR tip available | W2 dogfood |
| DEP-5 | Q-1 Gate 1 | Formal CURRENT claim only |
| DEP-6 | Board EPIC #84 + W0–W2 #85–#87 already seeded (stable TASK ids) | Pre-implement / loop-spec — no re-seed |

---

## 4. Risks (RISK)

| ID | Risk | Mitigation |
|----|------|------------|
| RISK-1 | Learning YAML drifts from pin template | Cite pin template; fail closed unknown class |
| RISK-2 | Spec-lane Pass-1 still pin-manual | REQ-15 deferral path |
| RISK-3 | Agent commits Alembic versions | MDC: human-only `versions/` |
| RISK-4 | Accidental resume of Pass-1 run | Fixed new-run + tests |
| RISK-5 | Gate 1 never lands | Q-1 waive recorded; do not fake CURRENT |
| RISK-6 | Smoke script mistaken for full dogfood | README + as-built distinguish W0 smoke vs W2 depth |

---

## 5. Out of scope

- Authorize→resume from `live-verify` into skills
- ADR-011 / new intake ADR (folded into ADR-010)
- Learning HTTP read API / Mission Control UI
- Pin package authoring (prayog-skills)
- Skill→Gateflow HTTP as success
- INIT-005 W2 dogfood

---

## 6. As-built and docs tasks

> Update these in the **same PR** as the code they describe.

| Task | File | Action |
|------|------|--------|
| W0/W1/W2 matrix rows | `docs/specification/as-built/implementation-status.md` | unit → live columns; W0 smoke vs W2 dogfood |
| Feature map closeout | `tests/README.md` | `verify_wave_closeout` + API row (W0 create; W2 deepen) |
| Spec README active INIT | `docs/specification/README.md` | keep pointing at 007 |

> ADR lifecycle: ADR-010 amendment **Accepted**; do not add ADR promotion tasks.

---

## 7. Plan check summary

| Check | Status |
|-------|--------|
| P1 REQ coverage | PASS — REQ-1…17 in §1 |
| P2 TASK Implements | PASS |
| P3 FILE paths | PASS |
| P4 done when | PASS |
| P5 test/verify | PASS — unit + live named |
| P6 scope | PASS — within INIT-007 |
| P7 feasibility blockers | PASS — FF resolved in TDD; Q-1 deferred |
| P8 wave order | PASS — W0→W1→W2 |
| P9 as-built/README | PASS — §6 |
| P10 self-contained + commands | PASS — Gate 1 WAIVED documented |
| P11 MDC notes | PASS — in TASK table |
| P12 ADR Accepted | PASS — ADR-010 Accepted; ADR_REQUIRED=0 |
| P13 TDD Accepted | PASS — PE sign-off 2026-07-29 |
| P14 WorkManifest | PASS — §9 `apiVersion: prayog/v1` with per-task `files`/`exit` + wave `verification` |
| P15 Co-ship live verify | PASS — W0 FILE-W0-08 + TEST-W0-L + live `verify_command`; W1 N/A (no new surface); W2 edits same script for dogfood |
| P16 Contract | PASS — `prayog-skills/scripts/workmanifest_contract.py` → ok on this plan |

---

## 8. PR instructions

```
Branch:   chore/INIT-GATEFLOW-007-plan-prayog-v1-backfill
PR title: "[INIT-GATEFLOW-007] Plan — prayog/v1 WorkManifest backfill"
Label:    spec-pending until PE §10 unlock

PE checklist (before spec-lgtm):
  [ ] This plan on current head with Accepted TDD/ADR-010
  [ ] P15: W0 co-ships verify_wave_closeout smoke
  [ ] §9 WorkManifest passes pin workmanifest_contract.py (prayog/v1)
  [ ] §9 TASK ids match board #85–#87 (no purge/re-seed)

After spec-lgtm + Approve + merge — do NOT re-run /create-board-tickets:
  Pass-1: /pre-implement → /loop-spec → live-verify (human runs co-shipped script)
  Pass-2 closeout: POST /waves/closeout/start → learning-extract → ground-spec → wave-signoff
```

---

## 10. Coding-readiness unlock (PE — after plan on head)

| Item | Value |
|------|-------|
| Verdict | GATE OPEN REQUEST (engineering package; Gate 1 WAIVED) |
| Spec PR | *(fill after Draft/Ready PR opened)* |
| Spec PR head SHA | *(fill after plan commit)* |
| Gate label (current) | `spec-pending` |
| Gate label (target) | `spec-lgtm` |
| Blocking items | Q-1 if PE requires CURRENT Gate 1 before merge; else none for engineering. Purge stale board tickets before re-seed. |

### Approve attestation body

```text
Spec package approved
initiative: INIT-GATEFLOW-007
spec_pr_head_sha: {SHA}
meta_pr_head_sha: TBD-WAIVED
impact_map_revision: TBD-WAIVED
prd_digest: TBD-WAIVED
scope_digest: TBD-WAIVED
plan_digest: sha256:{plan file digest}
artifacts:
  - docs/specification/product/INIT-GATEFLOW-007-gateflow.md
  - docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-007.md
  - docs/specification/reports/Technical-Review-INIT-GATEFLOW-007.md
  - docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-007.md
  - docs/specification/adr/adr-010-lane-intake-and-dual-workspace-authority.md
```

---

## 9. WorkManifest seed

```yaml
# Backfill 2026-07-31 — pin prayog/v1 (post INIT-008 W2 contract)
# LOCAL — do not commit to prayog-skills upstream
apiVersion: prayog/v1
kind: WorkManifest

initiative: INIT-GATEFLOW-007

metadata:
  title: INIT-GATEFLOW-007 — wave closeout + learning DB
  summary: |
    Pass-2 closeout start (fixed Enter-at learning-extract, new run + PR bind),
    W0 co-ships smoke verify_wave_closeout (P15); W1 learning Postgres ingest;
    W2 full Pass-2 dogfood to wave-signoff. Closeout intake in ADR-010 (no ADR-011).
  playbook:
    - docs/specification/product/INIT-GATEFLOW-007-gateflow.md
    - docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-007.md

target:
  org: drivestream-lab
  project: "drivestream-lab Board"

defaults:
  initiative: INIT-GATEFLOW-007
  parent: EPIC
  labels:
    - INIT-GATEFLOW-007

epic:
  id: EPIC
  repo: drivestream-lab/gateflow
  title: "[feature] INIT-GATEFLOW-007 — wave closeout + learning DB"
  codebase: drivestream-lab/gateflow
  spec_path: docs/specification/product/INIT-GATEFLOW-007-gateflow.md
  verify_command: .venv/bin/python -m tests.verify.verify_wave_closeout
  body: |
    ## Objective

    Finish waves after Pass-1 live-verify via closeout start + learning DB ingest.

    ## Waves

    | Wave | Goal |
    |------|------|
    | W0 | Closeout API + Pass-2 walker + smoke verify (P15) |
    | W1 | Learning Postgres ingest |
    | W2 | Full Pass-2 dogfood + docs |

    ## References

    - Spec: docs/specification/product/INIT-GATEFLOW-007-gateflow.md
    - Plan: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-007.md
    - TDD: docs/specification/reports/Technical-Review-INIT-GATEFLOW-007.md
    - ADR-010 (closeout §6)

    ## Board

    EPIC #84; W0 #85; W1 #86; W2 #87 — already seeded; do not re-create.

work:
  - id: W0
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-007 W0] Closeout start API + Pass-2 walker + smoke verify"
    depends_on: []
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-007-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_wave_closeout
    tasks:
      - id: TASK-W0-01
        implements: [REQ-4, REQ-6, REQ-13]
        depends_on: []
        files:
          - path: src/models/wave_start_models.py
            action: modify
        exit:
          criteria:
            - "CloseoutWaveStartRequest validates; forbid start_node/meta; absolute workspace_path + pr_number"
          proof:
            kind: command
            command: "make check && make test"
            expected: "exit 0; closeout model unit green"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-007-W0.md § TASK-W0-01"
      - id: TASK-W0-02
        implements: [REQ-1]
        depends_on: [TASK-W0-01]
        files:
          - path: src/api/v1/waves_routes.py
            action: modify
          - path: src/app.py
            action: modify
        exit:
          criteria:
            - "POST /api/v1/waves/closeout/start mounted; 401 without programme token"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; route/auth unit green"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-007-W0.md § TASK-W0-02"
      - id: TASK-W0-03
        implements: [REQ-2, REQ-3, REQ-5, REQ-8, REQ-13]
        depends_on: [TASK-W0-02]
        files:
          - path: src/business_services/wave_start_service.py
            action: modify
          - path: tests/unit/test_wave_closeout.py
            action: create
        exit:
          criteria:
            - "start_closeout_wave enqueues; fixed Enter-at learning-extract; ACTIVE 409; baton set"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; happy + 400/409 unit green"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-007-W0.md § TASK-W0-03"
      - id: TASK-W0-04
        implements: [REQ-7, REQ-8]
        depends_on: [TASK-W0-03]
        files:
          - path: tests/unit/test_run_orchestrator.py
            action: modify
          - path: tests/unit/test_handoff_workflow.py
            action: modify
        exit:
          criteria:
            - "Unit walker Pass-2: learning-extract → ground-spec → stop at wave-signoff; no verify dispatch"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; Pass-2 walker unit green"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-007-W0.md § TASK-W0-04"
      - id: TASK-W0-05
        implements: [REQ-16]
        depends_on: [TASK-W0-04]
        files:
          - path: tests/unit/test_trigger_policy.py
            action: modify
          - path: tests/unit/test_notifier.py
            action: modify
        exit:
          criteria:
            - "Unit mocks retargeted off wave-human-decision toward wave-signoff/live-verify"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; no retired checkpoint ids in tests/unit mocks"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-007-W0.md § TASK-W0-05"
      - id: TASK-W0-06
        implements: [REQ-1, REQ-7, REQ-17]
        depends_on: [TASK-W0-03]
        files:
          - path: tests/verify/verify_wave_closeout.py
            action: create
          - path: tests/config.yaml.example
            action: modify
          - path: tests/README.md
            action: modify
        exit:
          criteria:
            - "verify_wave_closeout smoke script exists with feature-map row"
          proof:
            kind: command
            command: ".venv/bin/python -m tests.verify.verify_wave_closeout"
            expected: "exit 0 under documented smoke prereqs (or soft-skip deeper stages)"
            evidence_expected: "Live-Verify-INIT-GATEFLOW-007-W0.md"
      - id: TASK-W0-07
        implements: [REQ-17]
        depends_on: [TASK-W0-06]
        files:
          - path: docs/specification/as-built/implementation-status.md
            action: modify
          - path: tests/README.md
            action: modify
        exit:
          criteria:
            - "As-built W0 + README distinguish smoke vs W2 dogfood"
          proof:
            kind: review
            review: "Inspect as-built INIT-007 W0 row and tests/README feature map"
            expected: "docs match tip smoke surface"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-007-W0.md § TASK-W0-07"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: smoke
        command: .venv/bin/python -m tests.verify.verify_wave_closeout
        covers: [REQ-1, REQ-7]
        prerequisites:
          - "Gateflow API up; programme token; tests/config.yaml closeout knobs"
        safe_test_data:
          - "Ephemeral PR/run per tests config — no production mutation"
        steps:
          - "Run verify_wave_closeout smoke against local stack"
        expected_observations:
          - "401 without token; body validation; happy enqueue returns run_id"
        evidence_expected: "Live-Verify-INIT-GATEFLOW-007-W0.md"
        cleanup:
          - "Close ephemeral closeout run per script notes"
        stop_conditions:
          - "Non-zero exit or unexpected 5xx → stop; do not start Pass-2 dogfood"
    body: |
      ## Wave goal

      Closeout start API + Pass-2 walker (unit) + co-shipped smoke verify (P15).

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W0-01 | REQ-4, REQ-6, REQ-13 | — | closeout model | command/make test |
      | TASK-W0-02 | REQ-1 | TASK-W0-01 | route + token | command/make test |
      | TASK-W0-03 | REQ-2, REQ-3, REQ-5, REQ-8, REQ-13 | TASK-W0-02 | enqueue Enter-at | command/make test |
      | TASK-W0-04 | REQ-7, REQ-8 | TASK-W0-03 | Pass-2 walker unit | command/make test |
      | TASK-W0-05 | REQ-16 | TASK-W0-04 | mock hygiene | command/make test |
      | TASK-W0-06 | REQ-1, REQ-7, REQ-17 | TASK-W0-03 | smoke verify script | command/verify_wave_closeout |
      | TASK-W0-07 | REQ-17 | TASK-W0-06 | as-built W0 | review |

      ## Done when

      - [ ] All W0 tasks complete per plan exit proof
      - [ ] Human ran `.venv/bin/python -m tests.verify.verify_wave_closeout` (smoke)

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-007-gateflow.md

  - id: W1
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-007 W1] Learning Postgres ingest"
    depends_on:
      - W0
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-007-gateflow.md
    verify_command: "N/A — P15 N/A (no new HTTP surface); unit + W2 dogfood"
    tasks:
      - id: TASK-W1-01
        implements: [REQ-9, REQ-10]
        depends_on: []
        files:
          - path: src/models/learning_models.py
            action: create
          - path: src/database/postgres/schema/learning_schema.py
            action: create
          - path: postgres_migrations/env.py
            action: modify
        exit:
          criteria:
            - "ORM + Pydantic learning models registered; pyright clean"
          proof:
            kind: command
            command: "make check"
            expected: "exit 0; schema modules imported in env.py"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-007-W1.md § TASK-W1-01"
      - id: TASK-W1-02
        implements: [REQ-9]
        depends_on: [TASK-W1-01]
        files:
          - path: postgres_migrations/env.py
            action: inspect
        exit:
          criteria:
            - "Human Alembic revision for learning tables applied; upgrade/downgrade symmetric"
          proof:
            kind: review
            review: "Human owns postgres_migrations/versions revision; run_postgres_migration.sh applied locally"
            expected: "migration applied; agent did not commit versions/"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-007-W1.md § TASK-W1-02"
      - id: TASK-W1-03
        implements: [REQ-9, REQ-10, REQ-11]
        depends_on: [TASK-W1-02]
        files:
          - path: src/database/postgres/repository/learning_repository.py
            action: create
          - path: src/business_services/learning_ingest_service.py
            action: create
          - path: src/di/dependency_container.py
            action: modify
          - path: tests/unit/test_learning_ingest.py
            action: create
        exit:
          criteria:
            - "LearningRepository + LearningIngestService unit green; unknown class fails closed"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; parse/upsert/idempotent unit green"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-007-W1.md § TASK-W1-03"
      - id: TASK-W1-04
        implements: [REQ-9, REQ-11, REQ-12]
        depends_on: [TASK-W1-03]
        files:
          - path: src/business_services/run_orchestrator.py
            action: modify
          - path: tests/unit/test_run_orchestrator.py
            action: modify
        exit:
          criteria:
            - "After learning-extract hop: publish-before-ingest then ingest before ground-spec"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; order asserted; missing artifact fails closed"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-007-W1.md § TASK-W1-04"
      - id: TASK-W1-05
        implements: [REQ-17]
        depends_on: [TASK-W1-04]
        files:
          - path: docs/specification/as-built/implementation-status.md
            action: modify
          - path: tests/README.md
            action: modify
        exit:
          criteria:
            - "As-built W1 + README learning ingest note"
          proof:
            kind: review
            review: "Inspect as-built INIT-007 W1 row and tests/README"
            expected: "docs match tip ingest path"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-007-W1.md § TASK-W1-05"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: false
        reason: "W1 adds Postgres ingest only — no new HTTP/lane-start surface (P15 N/A); live ingest proven in W2 dogfood"
    body: |
      ## Wave goal

      Learning Postgres ingest after learning-extract hop (no skill HTTP).

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W1-01 | REQ-9, REQ-10 | — | schema + models | command/make check |
      | TASK-W1-02 | REQ-9 | TASK-W1-01 | human Alembic | review |
      | TASK-W1-03 | REQ-9, REQ-10, REQ-11 | TASK-W1-02 | repo + service | command/make test |
      | TASK-W1-04 | REQ-9, REQ-11, REQ-12 | TASK-W1-03 | orchestrator hook | command/make test |
      | TASK-W1-05 | REQ-17 | TASK-W1-04 | as-built W1 | review |

      ## Done when

      - [ ] All W1 tasks complete per plan exit proof

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-007-gateflow.md

  - id: W2
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-007 W2] Full Pass-2 dogfood + docs"
    depends_on:
      - W1
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-007-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_wave_closeout
    tasks:
      - id: TASK-W2-01
        implements: [REQ-7, REQ-9, REQ-14]
        depends_on: []
        files:
          - path: tests/verify/verify_wave_closeout.py
            action: modify
          - path: tests/config.yaml.example
            action: modify
        exit:
          criteria:
            - "verify_wave_closeout full Pass-2 dogfood exits 0 (implement path to wave-signoff)"
          proof:
            kind: command
            command: ".venv/bin/python -m tests.verify.verify_wave_closeout"
            expected: "exit 0 against live stack (implement closeout path)"
            evidence_expected: "Live-Verify-INIT-GATEFLOW-007-W2.md"
      - id: TASK-W2-02
        implements: [REQ-12, REQ-14, REQ-17]
        depends_on: [TASK-W2-01]
        files:
          - path: docs/specification/as-built/implementation-status.md
            action: modify
          - path: tests/README.md
            action: modify
        exit:
          criteria:
            - "Feature map + as-built live row cite run id / tip / L-* evidence"
          proof:
            kind: review
            review: "Inspect as-built live row and tests/README after dogfood"
            expected: "docs match live Pass-2 evidence"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-007-W2.md § TASK-W2-02"
      - id: TASK-W2-03
        implements: [REQ-15]
        depends_on: [TASK-W2-02]
        files:
          - path: docs/specification/as-built/implementation-status.md
            action: modify
        exit:
          criteria:
            - "Spec-lane closeout live pass or PE-waived deferral documented in as-built"
          proof:
            kind: review
            review: "Inspect as-built REQ-15 row for live pass or explicit deferral"
            expected: "parity or PE waive recorded"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-007-W2.md § TASK-W2-03"
      - id: TASK-W2-04
        implements: [REQ-16]
        depends_on: [TASK-W2-01]
        files:
          - path: src/business_services/run_orchestrator.py
            action: inspect
          - path: tests/unit/test_run_orchestrator.py
            action: modify
        exit:
          criteria:
            - "src/ grep clean of live gate-1/gate-2/wave-human-decision transition constants"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0; rg clean in src/ for retired checkpoint ids"
            evidence_expected: "Wave-Execution-INIT-GATEFLOW-007-W2.md § TASK-W2-04"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: sandbox
        command: .venv/bin/python -m tests.verify.verify_wave_closeout
        covers: [REQ-7, REQ-9, REQ-14]
        prerequisites:
          - "Pass-1 tip available; API + worker; learning migration applied; tests/config.yaml dogfood knobs"
        safe_test_data:
          - "Ephemeral implement PR + closeout run per tests config"
        steps:
          - "Run verify_wave_closeout full dogfood (implement path)"
        expected_observations:
          - "Stop at wave-signoff; learning artifact/rows when configured"
        evidence_expected: "Live-Verify-INIT-GATEFLOW-007-W2.md"
        cleanup:
          - "Close ephemeral runs/PRs per script notes"
        stop_conditions:
          - "Non-zero exit or unexpected mutate → stop"
    body: |
      ## Wave goal

      Full Pass-2 live prove-it to wave-signoff + docs closeout.

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Depends on | Exit criteria | Proof |
      |------|------------|------------|---------------|-------|
      | TASK-W2-01 | REQ-7, REQ-9, REQ-14 | — | dogfood verify | command/verify_wave_closeout |
      | TASK-W2-02 | REQ-12, REQ-14, REQ-17 | TASK-W2-01 | as-built live | review |
      | TASK-W2-03 | REQ-15 | TASK-W2-02 | spec parity/deferral | review |
      | TASK-W2-04 | REQ-16 | TASK-W2-01 | checkpoint hygiene | command/make test |

      ## Done when

      - [ ] All W2 tasks complete per plan exit proof
      - [ ] Human/sandbox ran full verify_wave_closeout

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-007-gateflow.md
```

---

## Handoff envelope

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-implementation-plan
  outcome: pass
  artifact:
    path: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-007.md
    digest: sha256:0a9f8da82cc71c21dbefee7c963dea9be9066f58052d5dd60bb9f9cdf41eb4b7
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-007
    p15: co-ship_smoke_w0
    p16: workmanifest_prayog_v1
    gate1: WAIVED
    prior_plan: prayog_v1_backfill
    board: keep_seeded_84_through_87
  next_candidates:
    - coding-readiness
  human_checkpoint: true
  external_action: false
  forge:
    action: open_draft_pr
    draft: true
    apply_labels:
      - spec-pending
    title: "[INIT-GATEFLOW-007] Plan — prayog/v1 WorkManifest backfill"
    body_path: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-007.md
```
