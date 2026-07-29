---
goal: INIT-GATEFLOW-007 — implementation plan
initiative: INIT-GATEFLOW-007
status: Planned
date_created: 2026-07-29
source_spec: docs/specification/product/INIT-GATEFLOW-007-gateflow.md
source_spec_digest: sha256:1c613846f4b0ea5c9c2db3deab982ddf791bd93bba81dfdc2fdc175aa3051793
feasibility_report: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-007.md
feasibility_digest: sha256:ca40b9e2a77926a75569306a272e280fad086ddaf97d3bf7a37c3fecce3f6f64
technical_review: docs/specification/reports/Technical-Review-INIT-GATEFLOW-007.md
technical_review_digest: sha256:573b02ec81926ab71d6f6a0cfb7db73a05192e7bf350e7675e60a7167b09ddc7
prd_digest: TBD — Gate 1 open (Q-1 waived for engineering package)
impact_map: TBD
impact_map_revision: TBD
repo_scope_digest: TBD — gateflow-only
approved_meta_pr_head: TBD
branch: chore/INIT-GATEFLOW-007-spec-gateflow
review_deadline: 2026-08-05
deciders: PE @nikd10x / prayog-pe-team — spec-lgtm + Approve on exact head after full package
---

# Implementation plan — INIT-GATEFLOW-007

## Source freshness and command contract

| Item | Value | Status |
|------|-------|--------|
| Spec / digest | `docs/specification/product/INIT-GATEFLOW-007-gateflow.md` / `sha256:1c613846f4b0ea5c9c2db3deab982ddf791bd93bba81dfdc2fdc175aa3051793` | CURRENT on branch (Gate 1 digests WAIVED) |
| Feasibility / digest | `…/Initiative-Feasibility-Report-INIT-GATEFLOW-007.md` / `sha256:ca40b9e2…` | CURRENT |
| Technical review / digest | `…/Technical-Review-INIT-GATEFLOW-007.md` | CURRENT after acceptance commit |
| Impact map / revision | TBD | **WAIVED** — Q-1 |
| Repo scope digest | TBD | **WAIVED** — Q-1 |
| Approved meta PR head | TBD | **WAIVED** — Q-1 |
| `check_command` | `make check` | RESOLVED |
| `test_command` | `make test` | RESOLVED |
| `verify_command` | W0: unit + `verify_wave_start` smoke; W2: `.venv/bin/python -m tests.verify.verify_wave_closeout` (new); Pass-1 prerequisite: `verify_implement_lane` | RESOLVED |
| `ground_command` | N/A — `/ground-spec` is Pass-2 pin skill (orchestrated), not a Makefile target | N/A |

> Gate 1 STALE/WAIVED matches feasibility + TDD. Engineering plan proceeds; formal
> CURRENT / board-seed still needs Q-1 before claiming Gate 1 complete.

## 0. Technical design reference

| Item | Value |
|------|-------|
| Technical review | [`Technical-Review-INIT-GATEFLOW-007.md`](Technical-Review-INIT-GATEFLOW-007.md) |
| PE sign-off | [x] complete — 2026-07-29 (Cursor chat: fold into ADR-010; run `/spec-implementation-plan` on #77) |
| Resolved ADRs | [`adr-010-lane-intake-and-dual-workspace-authority.md`](../adr/adr-010-lane-intake-and-dual-workspace-authority.md) (**Accepted**, closeout §6); ADR-001/005/007/008/009 **Accepted** (cited, unchanged files) — **no ADR-011** |
| Outstanding PM questions | Q-1 Gate 1 meta PRD / waive — blocks formal CURRENT only |
| Outstanding domain questions | none |

**Defaults locked (from TDD §9):**

| Topic | Default |
|-------|---------|
| Closeout path | `POST /api/v1/waves/closeout/start` |
| Enter-at | Fixed `learning-extract` (no client `start_node`) |
| Run model | New `run_id`; required `pr_number`; optional `prior_run_id` audit-only |
| Park-ack API | None — closeout after Pass-1 `stopped@live-verify` |
| Learning ingest | After `learning-extract` hop; publish-before-ingest then learning ingest before `ground-spec` |
| Learning HTTP read | None in 007 |
| Live prove-it | Implement-first; spec live or PE-waived as-built deferral |

---

## 1. Requirements (REQ) — product ids

| ID | Summary | Spec path | Waves |
|----|---------|-----------|-------|
| REQ-1 | Closeout start route + programme token | `INIT-GATEFLOW-007-gateflow.md` | W0 |
| REQ-2 | Fixed Enter-at `learning-extract`; pin orchestrated fail-closed | same | W0 |
| REQ-3 | New run + PR bind; ACTIVE concurrent 409 | same | W0 |
| REQ-4 | Closeout body fields; `extra=forbid` | same | W0 |
| REQ-5 | Bind to pin `learning-extract` schema | same | W0 |
| REQ-6 | Both lanes; meta fields not required | same | W0 |
| REQ-7 | Walker Pass-2 → `wave-signoff`; forge rules | same | W0 |
| REQ-8 | Handoff + baton dual-write (reuse ADR-008) | same | W0 |
| REQ-9 | Postgres learning ingest from Learning-Extract artifact | same | W1 |
| REQ-10 | L-* taxonomy / item model | same | W1 |
| REQ-11 | No skill→HTTP; worker ingest | same | W1 |
| REQ-12 | Ground Report cites L-* (pin-owned; Gateflow tip evidence) | same | W1, W2 |
| REQ-13 | Optional `prior_run_id` | same | W0 |
| REQ-14 | Live implement closeout prove-it | same | W2 |
| REQ-15 | Spec-lane closeout parity / deferral | same | W2 |
| REQ-16 | Checkpoint id hygiene (`src/` + unit mocks) | same | W0, W2 |
| REQ-17 | As-built + feature map | same | W0, W1, W2 |

---

## 2. Implementation phases

### Phase W0 — Closeout start API + Pass-2 walker

**GOAL-W0:** Programme-token `POST /api/v1/waves/closeout/start` creates a new run
bound to an existing PR, Enter-ats `learning-extract`, walks to `wave-signoff`
(unit + pin fixtures); no learning DB yet.

| Task | Description | Implements | Codebase | Spec path | Done when | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|----------|-----------|-----------|----------------|-----------|-----------|--------|
| TASK-W0-01 | Add `CloseoutWaveStartRequest` (+ response reuse); forbid `start_node` / meta fields; require absolute `workspace_path` + `pr_number` | REQ-4, REQ-6, REQ-13 | gateflow | `docs/specification/product/INIT-GATEFLOW-007-gateflow.md` | Model validates; undeclared keys rejected | `make check && make test` | `pydantic-schemas.mdc`, `http-api-conventions.mdc` | ADR-010 §6 | `feature/INIT-GATEFLOW-007-w0-closeout-start` |
| TASK-W0-02 | Mount `POST /api/v1/waves/closeout/start`; programme token; `public_paths` | REQ-1 | gateflow | same | OpenAPI + 401 without token | `make test` | `architecture.mdc` | ADR-005 | same |
| TASK-W0-03 | `WaveStartService.start_closeout_wave`: fixed Enter-at; pin orchestrated check; ACTIVE 409; new run + baton; enqueue | REQ-2, REQ-3, REQ-5, REQ-8, REQ-13 | gateflow | same | Unit: happy + 400/409; baton path set; `start_node=learning-extract` | `make test` | `fail-fast.mdc` | ADR-010, ADR-007, ADR-008 | same |
| TASK-W0-04 | Unit walker Pass-2: learning-extract → ground-spec → stop `wave-signoff`; no verify dispatch | REQ-7, REQ-8 | gateflow | same | Orchestrator/handoff tests green | `make test` | — | ADR-009 forge reuse | same |
| TASK-W0-05 | Checkpoint mock hygiene: retarget `wave-human-decision` → `wave-signoff` / `live-verify` in unit mocks | REQ-16 | gateflow | same | `rg` clean in `tests/unit` for retired ids (allow historical docs) | `make test` | — | pin rename | same |
| TASK-W0-06 | As-built W0 row + README closeout API note (unit-complete; live deferred W2) | REQ-17 | gateflow | same | Docs match | inspection | `testing-verify-flows.mdc` | — | same |

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
| FILE-W0-08 | `docs/specification/as-built/implementation-status.md`, `tests/README.md` | edit |

#### Tests (W0)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W0-U | unit | `make check && make test` | REQ-1…8, REQ-13, REQ-16 |
| TEST-W0-V | live | N/A this wave — W2 | — |

---

### Phase W1 — Learning Postgres ingest

**GOAL-W1:** After `learning-extract` hop, parse Learning-Extract YAML into
`learning_extracts` / `learning_items` (TDD §8.1); no skill HTTP; human Alembic.

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

---

### Phase W2 — Live prove-it + docs closeout

**GOAL-W2:** Live implement-lane Pass-1 stop → closeout start → `wave-signoff`;
Learning-Extract + DB rows; feature map; spec-lane parity or PE-waived deferral.

| Task | Description | Implements | Codebase | Spec path | Done when | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|----------|-----------|-----------|----------------|-----------|-----------|--------|
| TASK-W2-01 | Add `tests/verify/verify_wave_closeout.py` + config.example opt-in | REQ-14 | gateflow | same | Script exits 0 against live stack (implement path) | `.venv/bin/python -m tests.verify.verify_wave_closeout` | `testing-verify-flows.mdc` | — | `feature/INIT-GATEFLOW-007-w2-closeout-prove` |
| TASK-W2-02 | Feature map + as-built live row (run id, tip, L-* cite evidence) | REQ-12, REQ-14, REQ-17 | gateflow | same | Docs match live | inspection | SDD | — | same |
| TASK-W2-03 | Spec-lane closeout live **or** as-built PE-waived deferral row | REQ-15 | gateflow | same | Live pass or explicit deferral documented | `verify_wave_closeout` (spec) or inspection | — | — | same |
| TASK-W2-04 | Final `src/` grep: no live transition constants on `gate-1`/`gate-2`/`wave-human-decision` | REQ-16 | gateflow | same | Grep clean in `src/` | `make test` + rg | — | pin | same |

#### Files (W2)

| ID | Path | Action |
|----|------|--------|
| FILE-W2-01 | `tests/verify/verify_wave_closeout.py` | create |
| FILE-W2-02 | `tests/config.yaml.example`, `tests/README.md` | edit |
| FILE-W2-03 | `docs/specification/as-built/implementation-status.md` | edit |
| FILE-W2-04 | Ground report for wave (human/skill) | create at wave close |

#### Tests (W2)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W2-V | live | `.venv/bin/python -m tests.verify.verify_wave_closeout` | REQ-14…17 |

---

## 3. Dependencies (DEP)

| ID | Dependency | Blocks |
|----|------------|--------|
| DEP-1 | Pass-1 pin remounted (`learning-extract` orchestrated) — **done** (#76) | W0 Enter-at |
| DEP-2 | W0 closeout enqueue | W1 ingest hook on hop |
| DEP-3 | W1 human Alembic applied | W1/W2 live ingest |
| DEP-4 | Pass-1 implement PR tip available | W2 live |
| DEP-5 | Q-1 Gate 1 | Formal CURRENT / board-seed claim only |

---

## 4. Risks (RISK)

| ID | Risk | Mitigation |
|----|------|------------|
| RISK-1 | Learning YAML drifts from pin template | Cite pin template; fail closed unknown class |
| RISK-2 | Spec-lane Pass-1 still pin-manual | REQ-15 deferral path |
| RISK-3 | Agent commits Alembic versions | MDC: human-only `versions/` |
| RISK-4 | Accidental resume of Pass-1 run | Fixed new-run + tests |
| RISK-5 | Gate 1 never lands | Q-1 waive recorded; do not fake CURRENT |

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

| Task | File | Action |
|------|------|--------|
| W0/W1/W2 matrix rows | `docs/specification/as-built/implementation-status.md` | unit → live columns |
| Feature map closeout | `tests/README.md` | `verify_wave_closeout` + API row |
| Spec README active INIT | `docs/specification/README.md` | already points at 007 — keep current |

> ADR lifecycle: ADR-010 amendment **Accepted** before this plan; do not add ADR
> promotion tasks.

---

## 7. Plan check summary

| Check | Status |
|-------|--------|
| P1 REQ coverage | PASS — REQ-1…17 in §1 |
| P2 TASK Implements | PASS |
| P3 FILE paths | PASS |
| P4 done when | PASS |
| P5 test/verify commands | PASS |
| P6 scope | PASS — within INIT-007 |
| P7 feasibility blockers | PASS — FF-04/05 resolved in TDD; Q-1 deferred |
| P8 wave order | PASS — W0→W1→W2 |
| P9 as-built/README | PASS — §6 |
| P10 self-contained + commands | PASS — Gate 1 WAIVED documented |
| P11 MDC notes | PASS — in TASK table |
| P12 ADR Accepted | PASS — ADR-010 Accepted; ADR_REQUIRED=0 |
| P13 TDD Accepted | PASS — PE sign-off 2026-07-29 |
| P14 WorkManifest | PASS — §9 |

---

## 8. PR instructions

```
Branch:   chore/INIT-GATEFLOW-007-spec-gateflow
PR:       https://github.com/drivestream-lab/gateflow/pull/77
Label:    spec-pending until PE §10 unlock

After merge — /create-board-tickets from §9 (not before)
Then: /pre-implement → /loop-spec → live-verify → /waves/closeout/start (Pass-2)
```

---

## 10. Gate 2 unlock (PE — after plan on head)

| Item | Value |
|------|-------|
| Verdict | GATE OPEN REQUEST (engineering package; Gate 1 WAIVED) |
| Spec PR | https://github.com/drivestream-lab/gateflow/pull/77 |
| Spec PR head SHA | *(fill after plan commit)* |
| Gate label (current) | `spec-pending` |
| Gate label (target) | `spec-lgtm` |
| Blocking items | Q-1 if PE requires CURRENT Gate 1 before merge; else none for engineering |

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
# Generated by /spec-implementation-plan — 2026-07-29
# LOCAL — do not commit to prayog-skills upstream
apiVersion: launchpad/v1
kind: WorkManifest

initiative: INIT-GATEFLOW-007

metadata:
  title: INIT-GATEFLOW-007 — wave closeout + learning DB
  summary: |
    Pass-2 closeout start (fixed Enter-at learning-extract, new run + PR bind),
    Postgres learning ingest from Learning-Extract YAML, live prove-it to wave-signoff.
    Closeout intake folded into ADR-010 (no ADR-011).
  playbook:
    - docs/specification/product/INIT-GATEFLOW-007-gateflow.md
    - docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-007.md

target:
  org: drivestream-lab
  project: "drivestream-lab Board"

defaults:
  initiative: INIT-GATEFLOW-007
  parent: EPIC
  status: Backlog
  labels:
    - INIT-GATEFLOW-007

epic:
  id: EPIC
  repo: drivestream-lab/gateflow
  title: "[feature] INIT-GATEFLOW-007 — wave closeout + learning DB"
  codebase: drivestream-lab/gateflow
  spec_path: docs/specification/product/INIT-GATEFLOW-007-gateflow.md
  verify_command: make check && make test
  body: |
    ## Objective

    Finish waves after Pass-1 live-verify via closeout start + learning DB ingest.

    ## Waves

    | Wave | Goal |
    |------|------|
    | W0 | Closeout API + Pass-2 walker to wave-signoff |
    | W1 | Learning Postgres ingest |
    | W2 | Live prove-it + docs |

    ## References

    - Spec: docs/specification/product/INIT-GATEFLOW-007-gateflow.md
    - Plan: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-007.md
    - TDD: docs/specification/reports/Technical-Review-INIT-GATEFLOW-007.md
    - ADR-010 (closeout §6)

work:
  - id: W0
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-007 W0] Closeout start API + Pass-2 walker"
    depends_on: []
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-007-gateflow.md
    verify_command: make check && make test
    status: Backlog
    tasks:
      - id: TASK-W0-01
        implements: [REQ-4, REQ-6, REQ-13]
        done_when: "CloseoutWaveStartRequest validates; forbid start_node/meta"
      - id: TASK-W0-02
        implements: [REQ-1]
        done_when: "POST /waves/closeout/start mounted; programme token"
      - id: TASK-W0-03
        implements: [REQ-2, REQ-3, REQ-5, REQ-8, REQ-13]
        done_when: "start_closeout_wave enqueue; 409 ACTIVE; fixed Enter-at"
      - id: TASK-W0-04
        implements: [REQ-7, REQ-8]
        done_when: "Unit walker learning-extract → ground-spec → wave-signoff"
      - id: TASK-W0-05
        implements: [REQ-16]
        done_when: "Unit mocks retargeted off wave-human-decision"
      - id: TASK-W0-06
        implements: [REQ-17]
        done_when: "as-built W0 + README closeout API note"
    body: |
      ## Wave goal

      Closeout start API + Pass-2 walker (unit) to wave-signoff.

      ## Tasks

      | Task | Implements | Done when |
      |------|------------|-----------|
      | TASK-W0-01 | REQ-4, REQ-6, REQ-13 | Closeout body model |
      | TASK-W0-02 | REQ-1 | Route + token |
      | TASK-W0-03 | REQ-2, REQ-3, REQ-5, REQ-8, REQ-13 | Service enqueue |
      | TASK-W0-04 | REQ-7, REQ-8 | Walker unit |
      | TASK-W0-05 | REQ-16 | Mock hygiene |
      | TASK-W0-06 | REQ-17 | Docs |

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
    verify_command: make check && make test
    status: Backlog
    tasks:
      - id: TASK-W1-01
        implements: [REQ-9, REQ-10]
        done_when: "ORM + Pydantic learning models; env.py import"
      - id: TASK-W1-02
        implements: [REQ-9]
        done_when: "Human Alembic applied"
      - id: TASK-W1-03
        implements: [REQ-9, REQ-10, REQ-11]
        done_when: "Repository + LearningIngestService unit green"
      - id: TASK-W1-04
        implements: [REQ-9, REQ-11, REQ-12]
        done_when: "Orchestrator ingest hook after learning-extract hop"
      - id: TASK-W1-05
        implements: [REQ-17]
        done_when: "as-built W1 + README"
    body: |
      ## Wave goal

      Persist Learning-Extract YAML into Postgres (TDD §8.1).

      ## Tasks

      | Task | Implements | Done when |
      |------|------------|-----------|
      | TASK-W1-01 | REQ-9, REQ-10 | Schema + models |
      | TASK-W1-02 | REQ-9 | Human migration |
      | TASK-W1-03 | REQ-9, REQ-10, REQ-11 | Ingest service |
      | TASK-W1-04 | REQ-9, REQ-11, REQ-12 | Orchestrator hook |
      | TASK-W1-05 | REQ-17 | Docs |

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-007-gateflow.md

  - id: W2
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-007 W2] Live closeout prove-it + docs"
    depends_on:
      - W1
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-007-gateflow.md
    verify_command: .venv/bin/python -m tests.verify.verify_wave_closeout
    status: Backlog
    tasks:
      - id: TASK-W2-01
        implements: [REQ-14]
        done_when: "verify_wave_closeout live exit 0 (implement)"
      - id: TASK-W2-02
        implements: [REQ-12, REQ-14, REQ-17]
        done_when: "Feature map + as-built live row"
      - id: TASK-W2-03
        implements: [REQ-15]
        done_when: "Spec live or PE-waived deferral documented"
      - id: TASK-W2-04
        implements: [REQ-16]
        done_when: "src/ grep clean for retired checkpoint ids"
    body: |
      ## Wave goal

      Live Pass-2 prove-it to wave-signoff + docs closeout.

      ## Tasks

      | Task | Implements | Done when |
      |------|------------|-----------|
      | TASK-W2-01 | REQ-14 | Live verify script |
      | TASK-W2-02 | REQ-12, REQ-14, REQ-17 | Docs evidence |
      | TASK-W2-03 | REQ-15 | Spec parity / deferral |
      | TASK-W2-04 | REQ-16 | Checkpoint hygiene |

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-007-gateflow.md
```

## Handoff envelope

```yaml
handoff:
  schema_version: "1"
  contract: "sdd-delivery/v2"
  stage: spec-implementation-plan
  outcome: pass
  initiative: INIT-GATEFLOW-007
  human_checkpoint: true
  external_action: false
  next_candidates:
    - coding-readiness
  artifact:
    path: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-007.md
  signals:
    waves: [W0, W1, W2]
    adr_011: false
    gate2: spec-pending
  notes:
    - Plan committed to Draft PR #77
    - PE sets spec-lgtm + Approve on exact head after review
    - Board seed only after merge via /create-board-tickets
  forge:
    action: commit_workspace
```
