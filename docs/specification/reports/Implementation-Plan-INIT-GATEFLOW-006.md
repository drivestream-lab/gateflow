---
goal: INIT-GATEFLOW-006 — implementation plan
initiative: INIT-GATEFLOW-006
status: Draft — PE review
date_created: 2026-07-29
source_spec: docs/specification/product/INIT-GATEFLOW-006-gateflow.md
source_spec_digest: TBD — recompute after PE edits
feasibility_report: N/A — interactive / PE-directed backfill (Gate 1 open)
technical_review: N/A — ADR-009 Accepted; Draft ADR-010 before W3
prd_digest: TBD
impact_map: TBD
impact_map_revision: TBD
repo_scope_digest: TBD — gateflow-only
approved_meta_pr_head: TBD
branch: chore/INIT-GATEFLOW-006-plan-gateflow
review_deadline: 2026-08-05
deciders: PE @nikd10x / prayog-pe-team
mode: Interactive build — forge unit already on develop (#70); plan productizes + schedules lane APIs
---

# Implementation plan — INIT-GATEFLOW-006

## Source freshness and command contract

| Item | Value | Status |
|------|-------|--------|
| Spec | `docs/specification/product/INIT-GATEFLOW-006-gateflow.md` | DRAFT |
| Feasibility / TDD digests | Deferred — interactive PE track; ADR-009 Accepted | WAIVED / catch-up |
| Meta Gate 1 | No PRD / Impact-Map yet (spec Q-1) | OPEN |
| Architecture | ADR-009 **Accepted**; **ADR-010** Draft required before W3 code | PARTIAL |
| `check_command` | `make check` | RESOLVED |
| `test_command` | `make test` | RESOLVED |
| `verify_command` | W0/W1: `.venv/bin/python -m tests.verify.verify_implement_lane` (forge/`stage_commit`); W1 authorize: programme `POST …/forge/authorize` + inspection; W4: `.venv/bin/python -m tests.verify.verify_spec_lane` (to implement); smoke: `verify_all` / `verify_wave_start` | RESOLVED |
| `ground_command` | N/A — `/ground-spec` per wave | N/A |

> **As-built fact:** Forge publish / authorize / sparse-notify **unit-complete** on
> `develop` (#70). W0–W2 tasks below are primarily **live evidence, docs, and
> gap-fill** — not greenfield rewrites. W3–W4 are the primary new build.

## 0. Technical design reference

| Item | Value |
|------|-------|
| Product INIT | [`docs/specification/product/INIT-GATEFLOW-006-gateflow.md`](../product/INIT-GATEFLOW-006-gateflow.md) |
| ADR-009 (forge) | [`adr-009-pin-forge-publish-mutate-authority.md`](../adr/adr-009-pin-forge-publish-mutate-authority.md) — **Accepted** — do not catalogue features here |
| ADR-010 (lane intake) | **To draft** before W3 — Spec vs implement wave intake (separate start contracts + dual workspace + meta PR accept authority) |
| Reuse | ADR-001…008 (RunStore, programme mutate token, pin dispatch, brief/bind, baton, ForgeClient infra) |
| Outstanding PE | Spec Q-1 (Gate 1), Q-2 (paths), Q-3–Q-4 (accept evidence / initiative), Q-5 (ADR-010), Q-6 (pin), Q-7 (bind names) — defaults in INIT |

**Defaults locked for this plan (change only via PE edit):**

| Topic | Default |
|-------|---------|
| Implement start path | `POST /api/v1/waves/implement/start` |
| Spec start path | `POST /api/v1/waves/spec/start` |
| Legacy | **Delete** undifferentiated `POST /api/v1/waves/start` at W3 cutover (no long deprecation alias — see Execution-Plan dead-code policy) |
| Bind keys | `workspace`, `meta_workspace`, `meta_pr_url` (when schema requires) |
| Initiative on spec start | Required; derive from meta PR and **fail closed on mismatch** |
| Accept evidence | APPROVED on meta head when available; labels projection-only |
| Pin | Spec-draft → feasibility → technical-review `dispatch: orchestrated` before W4 live (pin-owned) |
| Out of scope | INIT-005 W2; authorize-resume walker; invented labels |

---

## 1. Requirements (REQ) — product ids

| ID | Summary | Waves |
|----|---------|-------|
| REQ-1…REQ-5 | Pin forge parse, path filter, commit to run head, publish-before-ingest, policy class | W0 |
| REQ-6 | Live `stage_commit` prove-it for required publish nodes | W0 |
| REQ-7…REQ-11 | External-action STOP + authorize; Launchpad labels; board seed; dual executor; FR-24 | W1 |
| REQ-12…REQ-13 | Sparse PR milestone comments + `stage_started` timeline | W2 |
| REQ-14…REQ-16 | Separate implement vs spec start APIs | W3 |
| REQ-17…REQ-21 | Meta PR accept-gate; dual bind; app write / meta read; pin orchestrate dep; live spec prove-it | W4 |

---

## 2. Implementation phases

### Phase W0 — Workspace publish (catch-up + live)

**GOAL-W0:** Confirm ADR-009 publish path is product-complete: unit green (already),
live implement-lane (or equivalent) leaves `stage_commit` for pin-required nodes;
as-built W0 row honest.

| Task | Description | Implements | Done when | Verify | ADR | Branch |
|------|-------------|------------|-----------|--------|-----|--------|
| TASK-W0-01 | Audit as-built vs code: `forge_models`, `workspace_commit_paths`, `ForgeClient.commit_paths_to_branch`, orchestrator publish-before-ingest; close any unit gaps | REQ-1…5 | `make check && make test` green; gap list empty or filed | `make check && make test` | ADR-009 | `feature/INIT-GATEFLOW-006-w0-forge-publish` |
| TASK-W0-02 | Live dogfood: `verify_implement_lane` with forge creds + dirty workspace; assert `stage_commit` for required nodes (`loop-spec`, `ground-spec`) | REQ-6 | Live exit 0; run id recorded in as-built / ground | `verify_implement_lane` | ADR-009 | same |
| TASK-W0-03 | As-built + `tests/README.md`: W0 live row; note 005 W2 still out of track | REQ-6 | Docs match live evidence | inspection | — | same |

#### Files (W0)

| ID | Path | Action |
|----|------|--------|
| FILE-W0-01 | `src/business_services/workspace_commit_paths.py`, `run_orchestrator.py`, `infra_services/forge_client.py`, `models/forge_*` | edit only if gaps |
| FILE-W0-02 | `tests/unit/test_forge_*`, `test_workspace_commit_paths.py`, `test_run_orchestrator.py` | edit if gaps |
| FILE-W0-03 | `tests/verify/verify_implement_lane.py`, `tests/README.md`, as-built | edit |

#### Tests (W0)

| ID | Layer | Command |
|----|-------|---------|
| TEST-W0-U | unit | `make test` |
| TEST-W0-V | live | `verify_implement_lane` |

---

### Phase W1 — External-action authorize (catch-up + live)

**GOAL-W1:** Authorize path proven live for at least one pin action
(`open_draft_pr` **or** `create_board_tickets`); labels Launchpad-only; worker
never board-mutates.

| Task | Description | Implements | Done when | Verify | ADR | Branch |
|------|-------------|------------|-----------|--------|-----|--------|
| TASK-W1-01 | Audit `ForgeActionService` + `POST /api/v1/runs/{id}/forge/authorize`; unit coverage complete | REQ-7…11 | Unit green; FR-24 test present | `make check && make test` | ADR-009 | `feature/INIT-GATEFLOW-006-w1-forge-authorize` |
| TASK-W1-02 | Live authorize dogfood: STOP at external-action → authorize with programme token → forge mutation observed; document run id | REQ-8, REQ-9, REQ-10 | Live note + as-built | manual + `debug_forge_client` / API | ADR-009 | same |
| TASK-W1-03 | As-built W1 matrix + README authorize row | REQ-7…11 | Docs updated | inspection | — | same |

#### Files (W1)

| ID | Path | Action |
|----|------|--------|
| FILE-W1-01 | `src/business_services/forge_action_service.py`, `api/v1/forge_routes.py` | edit if gaps |
| FILE-W1-02 | `tests/unit/test_forge_action_service.py`, `test_forge_merge.py` | edit if gaps |
| FILE-W1-03 | as-built, `tests/README.md` | edit |

---

### Phase W2 — Sparse PR comments (catch-up)

**GOAL-W2:** Milestone-only PR notify + `stage_started` timeline documented complete
(unit already on #70).

| Task | Description | Implements | Done when | Verify | ADR | Branch |
|------|-------------|------------|-----------|--------|-----|--------|
| TASK-W2-01 | Confirm `Notifier.posts_run_event_to_pr` allowlist + orchestrator `stage_started`; fill any unit gap | REQ-12, REQ-13 | Unit green | `make test` | — (UX; not ADR-009 catalogue) | `feature/INIT-GATEFLOW-006-w2-sparse-notify` |
| TASK-W2-02 | As-built W2/W3 sparse matrix → complete | REQ-12, REQ-13 | Docs | inspection | — | same |

---

### Phase W2.5 — ADR-010 (architecture gate before lane APIs)

**GOAL-ADR:** Accept **ADR-010** — Spec vs implement wave intake authority
(separate start contracts; meta PR accept; dual workspace). Architecture-only
(same hygiene as ADR-007/008/009).

| Task | Description | Implements | Done when | Verify | ADR | Branch |
|------|-------------|------------|-----------|--------|-----|--------|
| TASK-ADR-01 | Draft `docs/specification/adr/adr-010-lane-intake-and-dual-workspace-authority.md` | Enables REQ-14…21 | PE Accept + approved head recorded | inspection | **NEW ADR-010** | `feature/INIT-GATEFLOW-006-adr-010` |
| TASK-ADR-02 | Point INIT Spec Q-5 → Accepted; update as-built truth split | — | Docs linked | inspection | ADR-010 | same |

**Do not start W3 coding until ADR-010 Status = Accepted** (interactive PE can Accept in-chat then record head).

---

### Phase W3 — Separate lane start APIs

**GOAL-W3:** Distinct programme-token start surfaces; shared enqueue/run core;
fail-closed validators per lane.

| Task | Description | Implements | Done when | Verify | ADR | Branch |
|------|-------------|------------|-----------|--------|-----|--------|
| TASK-W3-01 | Models: `ImplementWaveStartRequest`, `SpecWaveStartRequest` (extra=forbid); shared response; **remove** undifferentiated `WaveStartRequest` when callers moved | REQ-14…16 | pyright clean; unit validate shapes | `make check && make test` | ADR-010, ADR-005 | `feature/INIT-GATEFLOW-006-w3-lane-starts` |
| TASK-W3-02 | Routes: `POST /api/v1/waves/implement/start`, `POST /api/v1/waves/spec/start`; **delete** legacy `POST /waves/start` in same PR after callers moved (Execution-Plan E5) | REQ-14 | OpenAPI distinct; old route gone; unit route tests | `make test` | ADR-005 | same |
| TASK-W3-03 | Refactor `WaveStartService` (or split `ImplementWaveStartService` / `SpecWaveStartService` with shared helper): implement path = today’s ticket/Enter-at logic **without** meta fields | REQ-15 | Implement start works; meta fields rejected | `make test`; `verify_wave_start` | ADR-006, ADR-010 | same |
| TASK-W3-04 | Spec start stub accept: require `meta_pr_url` + `meta_workspace_path` + app workspace; **fail closed** if `start_node` not orchestrated; do **not** yet call full meta Gate-1 resolve (W4) — validate paths exist / absolute | REQ-16 | 4xx on missing; 4xx on manual start_node | `make test` | ADR-006, ADR-010 | same |
| TASK-W3-05 | Unit + verify helpers + README feature map for two starts | REQ-14…16 | Docs + tests | `make test` | — | same |

#### Files (W3)

| ID | Path | Action |
|----|------|--------|
| FILE-W3-01 | `src/models/adapter_models.py` (or `wave_start_models.py`) | edit/create |
| FILE-W3-02 | `src/api/v1/waves_routes.py` | edit |
| FILE-W3-03 | `src/business_services/wave_start_service.py` (+ optional split) | edit |
| FILE-W3-04 | `src/di/modules/business_services_module.py` | edit if new services |
| FILE-W3-05 | `tests/unit/test_wave_start.py`, verify helpers, `tests/README.md`, as-built | edit |

#### Tests (W3)

| ID | Layer | Command |
|----|-------|---------|
| TEST-W3-U | unit | `make test` |
| TEST-W3-V | live | `verify_wave_start` via implement path |

---

### Phase W4 — Meta accept-gate + dual bind + spec prove-it

**GOAL-W4:** Spec start resolves meta PR, binds dual workspaces, dispatches
orchestrated spec chain (pin-dependent), live prove-it stops at ADR human gate.

| Task | Description | Implements | Done when | Verify | ADR | Branch |
|------|-------------|------------|-----------|--------|-----|--------|
| TASK-W4-01 | ForgeClient (or thin helper): parse `meta_pr_url`; fetch PR; initiative mismatch fail closed; persist `meta_pr_url` / `meta_head_sha` on run (ORM + human Alembic if new columns) | REQ-17 | Unit with mocked forge; schema mapped | `make test` | ADR-010, ADR-001, ADR-003 | `feature/INIT-GATEFLOW-006-w4-spec-intake` |
| TASK-W4-02 | Orchestrator / PromptResolver bind: inject `meta_workspace` + `meta_pr_url` when present; fail closed if schema requires and missing | REQ-18, REQ-19 | Unit bind/render | `make test` | ADR-007, ADR-010 | same |
| TASK-W4-03 | Spec start wires accept-gate before enqueue; app `org`/`repo` for PR targeting | REQ-17, REQ-19 | Integration unit | `make test` | ADR-010 | same |
| TASK-W4-04 | **Pin dependency (document + consume):** prayog-skills orchestrate spec-draft → feasibility → technical-review; schema declares `meta_workspace` — Gateflow PR notes pin ref; no invent labels | REQ-20 | Spec start accepts `spec-draft` when pin orchestrated | pin promote + `make test` | ADR-006 | pin repo / remount |
| TASK-W4-05 | Implement `verify_spec_lane` (replace stub): opt-in config; assert prompt ids + stop at human ADR gate; document evidence | REQ-21 | Live exit 0 when enabled | `verify_spec_lane` | ADR-010 | same |
| TASK-W4-06 | As-built W4 complete; INIT README; ground-ready | REQ-21 | Docs | inspection | — | same |

#### Files (W4)

| ID | Path | Action |
|----|------|--------|
| FILE-W4-01 | `src/infra_services/forge_client.py` (+ optional `meta_pr_resolver.py` business) | edit/create |
| FILE-W4-02 | `src/database/postgres/schema/run_store_schema.py`, models, repo, `postgres_migrations/env.py` | edit — meta audit fields |
| FILE-W4-03 | `postgres_migrations/versions/` | **human** Alembic |
| FILE-W4-04 | `src/business_services/prompt_resolver.py`, `run_orchestrator.py`, `wave_start_service.py` | edit |
| FILE-W4-05 | `tests/verify/verify_spec_lane.py`, `tests/config.yaml.example`, README, as-built | edit |
| FILE-W4-06 | pin `workflow.yaml` + skill `schema.yaml` | **prayog-skills** (dependency) |

#### Tests (W4)

| ID | Layer | Command |
|----|-------|---------|
| TEST-W4-U | unit | `make test` |
| TEST-W4-V | live | `verify_spec_lane` |

---

## 3. Dependencies (DEP)

| ID | Dependency | Blocks |
|----|------------|--------|
| DEP-01 | ADR-009 Accepted + forge unit on `develop` (#70) | W0 start |
| DEP-02 | `GATEFLOW_HANDOFF_ROOT` + Cursor + forge creds for live | W0/W1/W4 live |
| DEP-03 | ADR-010 Accepted | W3 code |
| DEP-04 | W3 merged | W4 |
| DEP-05 | Pin orchestrate + `meta_workspace` in schemas | W4 live (REQ-20/21) |
| DEP-06 | Human Alembic if new run columns | W4 store tasks |
| DEP-07 | INIT-005 W2 | **Not a dependency** — out of track |

---

## 4. Risks (RISK)

| ID | Risk | Mitigation |
|----|------|------------|
| RISK-01 | Live forge dogfood blocked by empty baton / agent quality | Pin dual-write already landed (#65); treat W0 live as forge evidence, not 005 W2 |
| RISK-02 | Spec start before pin orchestrate | Fail closed at accept (REQ-20); pin first |
| RISK-03 | Dual checkout ops burden | Document `meta_workspace_path` absolute; fail closed if missing |
| RISK-04 | Callers of legacy `/waves/start` break at W3 | Same-PR update verify helpers + README; **delete** old route (no multi-release alias) |
| RISK-05 | ADR-010 delayed | No W3 coding until Accept (interactive PE can fast-track) |
| RISK-06 | Gate 1 missing | Interactive waive for build; retrospective PRD before formal board-seed if required |

---

## 5. Out of scope

- INIT-GATEFLOW-005 W2 multi-skill dogfood (#57)
- Authorize → resume walker
- Invented PE labels / writing `*-lgtm`
- prayog-skills package authoring (schema/dispatch consume only)
- gateflow-ops UI; second AgentRunner
- Allowlist-first publish (ADR-009 revisit)

---

## 6. As-built and docs tasks

| Task | File | Action |
|------|------|--------|
| Per-wave as-built | `docs/specification/as-built/implementation-status.md` | W0→W4 rows |
| Feature map | `tests/README.md` | Lane starts + authorize + spec_lane verify |
| Env / runbook | `.env.example`, README, optional runbook | meta checkout + dual paths |
| ADR-010 | `docs/specification/adr/adr-010-…md` | Draft → Accepted before W3 |
| Spec Q updates | INIT-006 product file | Resolve Q-5 when ADR-010 Accepted |

---

## 7. Plan check summary

| Check | Status |
|-------|--------|
| P1 REQs in §1 | PASS — REQ-1…21 |
| P2 every REQ ≥1 TASK | PASS |
| P3 FILE paths | PASS |
| P4 done when | PASS |
| P5 verify commands | PASS |
| P6 scope gateflow (+ pin dep noted) | PASS |
| P7 ADR | PASS — 009 Accepted; 010 before W3 |
| P8 wave order | PASS — W0→W1→W2→ADR→W3→W4 |
| P9 as-built/docs | PASS — §6 |
| P10 interactive / Gate 1 waived for build | NOTED |
| P11 005 W2 excluded | PASS |
| P14 WorkManifest | PASS — §9 |

---

## 8. PR instructions (plan artifact)

```
Branch:   chore/INIT-GATEFLOW-006-plan-gateflow
Base:     develop
PR title: [INIT-GATEFLOW-006] Implementation plan — gateflow
Reviewers: @drivestream-lab/prayog-pe-team
```

PE review focus: wave order, ADR-010 gate before W3, pin dependency, exclusion of 005 W2, path defaults.

Interactive track may implement W0–W2 on feature branches **before** plan merge if PE agrees (forge already shipped).

---

## 9. WorkManifest (board seed)

```yaml
apiVersion: gateflow/v1
kind: WorkManifest
initiative: INIT-GATEFLOW-006
epic:
  title: "[INIT-GATEFLOW-006] Forge publish/mutate + lane starts + dual meta intake"
  repo: drivestream-lab/gateflow
waves:
  - id: W0
    title: "[INIT-GATEFLOW-006 W0] Workspace publish catch-up + live stage_commit"
    tasks:
      - id: TASK-W0-01
        implements: [REQ-1, REQ-2, REQ-3, REQ-4, REQ-5]
        done_when: "Unit audit green; gaps closed"
      - id: TASK-W0-02
        implements: [REQ-6]
        done_when: "Live stage_commit evidence"
      - id: TASK-W0-03
        implements: [REQ-6]
        done_when: "as-built W0"
  - id: W1
    title: "[INIT-GATEFLOW-006 W1] Forge authorize catch-up + live"
    depends_on: [W0]
    tasks:
      - id: TASK-W1-01
        implements: [REQ-7, REQ-8, REQ-9, REQ-10, REQ-11]
        done_when: "Authorize unit complete"
      - id: TASK-W1-02
        implements: [REQ-8, REQ-9, REQ-10]
        done_when: "Live authorize evidence"
      - id: TASK-W1-03
        implements: [REQ-7, REQ-8, REQ-9, REQ-10, REQ-11]
        done_when: "as-built W1"
  - id: W2
    title: "[INIT-GATEFLOW-006 W2] Sparse PR notify catch-up"
    depends_on: [W1]
    tasks:
      - id: TASK-W2-01
        implements: [REQ-12, REQ-13]
        done_when: "Unit confirm sparse notify"
      - id: TASK-W2-02
        implements: [REQ-12, REQ-13]
        done_when: "as-built W2"
  - id: W-ADR
    title: "[INIT-GATEFLOW-006] Accept ADR-010 lane intake + dual workspace"
    depends_on: [W2]
    tasks:
      - id: TASK-ADR-01
        implements: []
        done_when: "ADR-010 Accepted"
      - id: TASK-ADR-02
        implements: []
        done_when: "INIT Q-5 + as-built linked"
  - id: W3
    title: "[INIT-GATEFLOW-006 W3] Separate implement/spec wave-start APIs"
    depends_on: [W-ADR]
    tasks:
      - id: TASK-W3-01
        implements: [REQ-14, REQ-15, REQ-16]
        done_when: "Lane request models"
      - id: TASK-W3-02
        implements: [REQ-14]
        done_when: "Routes mounted"
      - id: TASK-W3-03
        implements: [REQ-15]
        done_when: "Implement start service"
      - id: TASK-W3-04
        implements: [REQ-16]
        done_when: "Spec start path validation"
      - id: TASK-W3-05
        implements: [REQ-14, REQ-15, REQ-16]
        done_when: "Tests + README"
  - id: W4
    title: "[INIT-GATEFLOW-006 W4] Meta accept-gate + dual bind + spec prove-it"
    depends_on: [W3]
    tasks:
      - id: TASK-W4-01
        implements: [REQ-17]
        done_when: "Meta PR resolve + persist"
      - id: TASK-W4-02
        implements: [REQ-18, REQ-19]
        done_when: "Dual bind"
      - id: TASK-W4-03
        implements: [REQ-17, REQ-19]
        done_when: "Spec start accept-gate wired"
      - id: TASK-W4-04
        implements: [REQ-20]
        done_when: "Pin orchestrate consumed"
      - id: TASK-W4-05
        implements: [REQ-21]
        done_when: "verify_spec_lane live"
      - id: TASK-W4-06
        implements: [REQ-21]
        done_when: "as-built W4 ground-ready"
```

---

## 10. Review checklist (for PE)

- [ ] W0–W2 correctly treated as catch-up / live (not rebuild)
- [ ] ADR-010 hard gate before W3 agreed
- [ ] Path defaults (`/waves/implement/start`, `/waves/spec/start`) OK
- [ ] Dual bind key names OK (`meta_workspace`, `meta_pr_url`)
- [ ] Pin dependency ownership clear (prayog-skills)
- [ ] INIT-005 W2 excluded
- [ ] Authorize-resume still out of scope
- [ ] Interactive build may proceed W0 without meta Gate 1
