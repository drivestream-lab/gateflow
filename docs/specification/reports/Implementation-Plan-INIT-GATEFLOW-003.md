---
goal: INIT-GATEFLOW-003 — implementation plan
initiative: INIT-GATEFLOW-003
status: Planned
date_created: 2026-07-24
source_spec: docs/specification/product/INIT-GATEFLOW-003-gateflow.md
source_spec_digest: sha256:4d0fd484deb7eaad6dca3632355547604644a570140bf70d03e60ee642d41f18
feasibility_report: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-003.md
feasibility_digest: sha256:7fa2b2b011e5079b689c15c09071ffa5cc56f5bc7e85bea8687db3f577fd1c59
technical_review: docs/specification/reports/Technical-Review-INIT-GATEFLOW-003.md
technical_review_digest: sha256:047e899c921b0ee4126e03b02062ceada55c78ea0052ed8cf91397ee691b33ea
prd_digest: sha256:6062fa11d136e9a49dd6546377ec5d907789ef388108b477b846f6299673f9ad
impact_map: prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-003.md
impact_map_revision: 2
repo_scope_digest: sha256:aaf398dc53a4606b34e9e24fa7513cd3a3b7e64ea677047faf5d2e90c64eba85
approved_meta_pr_head: 4c9cacb8b7aa5aeac50ef902c9d8fc400bb2ece5
branch: chore/INIT-GATEFLOW-003-spec-gateflow
review_deadline: 2026-07-29
deciders: PE — spec-lgtm + Approve on exact head after full package
---

# Implementation plan — INIT-GATEFLOW-003

## Source freshness and command contract

| Item | Value | Status |
|------|-------|--------|
| Spec / digest | `docs/specification/product/INIT-GATEFLOW-003-gateflow.md` / `sha256:4d0fd484deb7eaad6dca3632355547604644a570140bf70d03e60ee642d41f18` | CURRENT |
| Feasibility / digest | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-003.md` / `sha256:7fa2b2b011e5079b689c15c09071ffa5cc56f5bc7e85bea8687db3f577fd1c59` | CURRENT |
| Technical review / digest | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-003.md` / `sha256:047e899c921b0ee4126e03b02062ceada55c78ea0052ed8cf91397ee691b33ea` | CURRENT |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-003.md` / `2` | CURRENT |
| Repo scope digest | `sha256:aaf398dc53a4606b34e9e24fa7513cd3a3b7e64ea677047faf5d2e90c64eba85` | CURRENT |
| Approved meta PR head | `4c9cacb8b7aa5aeac50ef902c9d8fc400bb2ece5` | CURRENT |
| `check_command` | `make check` | RESOLVED |
| `test_command` | `make test` | RESOLVED |
| `verify_command` | Per-wave: `.venv/bin/python -m tests.verify.<script>`; aggregator `.venv/bin/python -m tests.verify.verify_all` | RESOLVED |
| `ground_command` | N/A — no Makefile ground target; post-merge use `/ground-spec` skill per workflow | N/A |

> TDD Status **Accepted** (PE @nikd10x 2026-07-24). ADR_REQUIRED for 003: **0**.
> Reuse Accepted ADR-001…006. Pin consumer remains `v0.5.0-rc.2` (Scenario A
> `dispatch: orchestrated` is prayog-skills supporting delivery — CTR-01).

## 0. Technical design reference

| Item | Value |
|------|-------|
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-003.md` |
| PE sign-off | [x] complete — 2026-07-24 (@nikd10x via Cursor chat on https://github.com/drivestream-lab/gateflow/pull/18); posture A1+B1+C1 |
| Resolved ADRs | **No new ADR for 003.** Reused: `adr-001-runtime-and-durable-store.md` (Accepted); `adr-002-edge-trust-model.md` (Accepted); `adr-003-slot-layer-ownership.md` (Accepted — retained; not Cursor Cloud); `adr-004-programme-config-authority.md` (Accepted); `adr-005-programme-token-control-plane-mutations.md` (Accepted); `adr-006-adapter-registry-fail-closed.md` (Accepted). Draft ADR-007 **withdrawn**. |
| Outstanding PM questions | none |
| Outstanding domain questions | none |
| Deferred PE (non-blocking) | Q-4 meta #10 reconcile — proceed on as-built 002 W2; FF-12 / CTR-01 Scenario A pin — W2 blocked until prayog-skills supporting delivery |

> Do not start W0 implementation until PE sign-off is marked complete above.

---

## 1. Requirements (REQ) — product ids

| ID | Summary | Spec path | Waves |
|----|---------|-----------|-------|
| REQ-27 | Live Cursor AgentRunner (local `cursor-sdk`); orchestrated ⇒ triggered; Scenario B then A prove-it; no node allowlist | `docs/specification/product/INIT-GATEFLOW-003-gateflow.md` | W0, W1, W2 |
| REQ-28 | Config-driven runner; fail-fast unsupported/not-live at start | same | W0 |
| REQ-29 | Fail-fast Cursor auth / start / crash; wave-run precondition #12 | same | W0, W1 |
| REQ-30 | Stage + wave cycle-time; `by_runner` cursor p50/p95; failure stages emit duration | same | W1, W2 |
| REQ-31 | Reuse 001/002 control plane; no Launchpad product work; no rebuild | same | W0–W2 |

---

## 2. Implementation phases

### Phase W0 — Live Cursor skeleton + start-gate honesty

**GOAL-W0:** In-process local `cursor-sdk` adapter skeleton in infra; `CURSOR_API_KEY`
settings; wave-start fail-closed when Cursor credentials missing or not-live
runner required; stub/`mock-*` quarantined from live success path; unit coverage
green. (Full Scenario prove-it is W1/W2.)

| Task | Description | Implements | Codebase | Spec path | Done when | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|----------|-----------|-----------|----------------|-----------|-----------|--------|
| TASK-W0-01 | Add `cursor-sdk` to Poetry; `CursorAgentSettings` (`CURSOR_API_KEY`); document in `.env.example` / README | REQ-29, REQ-27 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-003-gateflow.md` | Settings load; missing key detectable; no secret in programme.yaml | `make check && make test` | settings `get_instance()` not DI; fail-fast | ADR-004 | `feature/INIT-GATEFLOW-003-w0-cursor-skeleton` |
| TASK-W0-02 | Implement `CursorAgentRunner` live path: `Agent.create` + `LocalAgentOptions(cwd=workspace)`; map to `AgentRunResult`; cloud agents never used | REQ-27, REQ-31 | drivestream-lab/gateflow | same | Unit with mocked SDK returns SUCCESS/FAILED; real skill without key/SDK fails closed | `make check && make test` | infra SDK wrapper; business must not import `cursor_sdk` | ADR-003, ADR-001 | same |
| TASK-W0-03 | Start-gate: when required runner is `cursor`, require API key + ADR-006 `implemented`; quarantine `GATEFLOW_AGENT_STUB`/`mock-*` from production-like live success; wire into WaveStartService (+ worker defense-in-depth) | REQ-28, REQ-29 | drivestream-lab/gateflow | same | Missing key → 422/structured fail before enqueue; stub env cannot satisfy live exit assertions | `make check && make test` | fail-fast; business SlotValidator | ADR-006, ADR-004 | same |
| TASK-W0-04 | Laptop spike evidence (TDD §3.3): one local `send()` with key+cwd; record result in `docs/specification/reports/` spike note or runbook | REQ-27 | drivestream-lab/gateflow | same | Spike note committed; pass/fail + blockers listed | inspection | — | TDD §3.3 C1 | same |
| TASK-W0-05 | Unit tests: settings, start-gate, runner reject/mock paths; update `tests/README.md` W0 map | REQ-28, REQ-29 | drivestream-lab/gateflow | same | New/updated unit tests green | `make check && make test` | testing-verify-flows | — | `feature/INIT-GATEFLOW-003-w0-verify` |
| TASK-W0-06 | As-built: INIT-003 W0 rows in_progress→complete for skeleton + start-gate | REQ-31 | drivestream-lab/gateflow | same | as-built updated | inspection | SDD as-built | — | same PR as last W0 code |

#### Files (W0)

| ID | Path | Action |
|----|------|--------|
| FILE-W0-01 | `pyproject.toml`, `poetry.lock` | edit — add `cursor-sdk` |
| FILE-W0-02 | `src/configs/cursor_agent_settings.py` | create |
| FILE-W0-03 | `.env.example`, `README.md` | edit — `CURSOR_API_KEY` |
| FILE-W0-04 | `src/infra_services/cursor_agent_runner.py` | edit — live local SDK |
| FILE-W0-05 | `src/business_services/slot_validator.py`, `wave_start_service.py`, optionally `run_orchestrator.py` | edit — start-gate |
| FILE-W0-06 | `tests/unit/test_cursor_agent_runner.py`, `test_slot_validator.py`, `test_wave_start.py` | edit/create |
| FILE-W0-07 | `docs/specification/reports/*spike*` or `docs/runbooks/cursor-local-sdk-spike.md` | create |
| FILE-W0-08 | `docs/specification/as-built/implementation-status.md`, `tests/README.md` | edit |

#### Tests (W0)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W0-U | unit | `make test` | REQ-27/28/29 skeleton + start-gate |
| TEST-W0-SPIKE | inspection | spike note | TDD §3.3 local SDK evidence |

---

### Phase W1 — Scenario B prove-it + cycle-time + Docker spike

**GOAL-W1:** Live Cursor on Scenario B skill set (`pre-implement`, `loop-spec`,
`verify`, `ground-spec`) with live coding-work evidence; auth/start/crash
fail-fast; stage duration on success **and** failure; `runs.wave_duration_ms`;
Docker/bridge spike passed before live prove-it exit.

| Task | Description | Implements | Codebase | Spec path | Done when | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|----------|-----------|-----------|----------------|-----------|-----------|--------|
| TASK-W1-01 | Docker/image spike: `cursor-sdk` in Gateflow-like image + `CURSOR_API_KEY` + cwd; document bridge/Node needs | REQ-27 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-003-gateflow.md` | Spike pass recorded; blockers listed if fail | inspection | — | TDD §3.3 | `feature/INIT-GATEFLOW-003-w1-scenario-b` |
| TASK-W1-02 | Orchestrator: persist `StageCreate` + `record_stage_duration` on AgentRunner **failure**; timeouts/crash → `failed` no advance | REQ-29, REQ-30 | drivestream-lab/gateflow | same | Failure path has stage + duration_ms event; unit covers FF-05 | `make check && make test` | fail-fast; repository boundary | ADR-001 | same |
| TASK-W1-03 | Human Alembic + ORM/DTO/API: `runs.wave_duration_ms`; compute on finalize from accept→stop/fail; expose on run detail | REQ-30 | drivestream-lab/gateflow | same | Column present after human migration; run detail shows field | `make check && make test` | human migrations only; pydantic models | ADR-001 | same |
| TASK-W1-04 | Live Scenario B prove-it verify script (worker + key + stub unset); assert RunStore `runner=cursor` + workspace coding work | REQ-27, REQ-31 | drivestream-lab/gateflow | same | Documented verify green on local stack | `make check && make test` ; `.venv/bin/python -m tests.verify.verify_scenario_b` (name may vary) | testing-verify-flows; no stub env | ADR-003 | `feature/INIT-GATEFLOW-003-w1-verify` |
| TASK-W1-05 | Unit tests for wave_duration_ms + failure metrics; update verify_all/README/as-built W1 | REQ-30 | drivestream-lab/gateflow | same | Tests + docs updated | `make check && make test` | SDD as-built | — | same |

#### Files (W1)

| ID | Path | Action |
|----|------|--------|
| FILE-W1-01 | `docs/runbooks/` or reports spike Docker note | create/edit |
| FILE-W1-02 | `src/business_services/run_orchestrator.py`, `metrics_emitter.py` | edit |
| FILE-W1-03 | `src/database/postgres/schema/run_store_schema.py`, models, repo, runs routes | edit |
| FILE-W1-04 | `postgres_migrations/versions/` | **human** creates revision |
| FILE-W1-05 | `tests/verify/verify_scenario_b.py`, `verify_all.py` | create/edit |
| FILE-W1-06 | `tests/unit/test_run_orchestrator.py`, `test_metrics_emitter.py` | edit |
| FILE-W1-07 | `tests/README.md`, as-built | edit |

#### Tests (W1)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W1-U | unit | `make test` | REQ-29/30 failure path + wave duration |
| TEST-W1-V | live verify | `.venv/bin/python -m tests.verify.verify_scenario_b` | REQ-27 Scenario B |
| TEST-W1-SPIKE | inspection | Docker spike note | TDD §3.3 |

---

### Phase W2 — Scenario A prove-it + metrics honesty

**GOAL-W2:** After prayog-skills CTR-01 (Scenario A `dispatch: orchestrated`), live
Cursor prove-it on Scenario A set; post–Gate 2 Scenario A still runnable; metrics
`by_runner` cursor p50/p95 with samples; as-built complete.

| Task | Description | Implements | Codebase | Spec path | Done when | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|----------|-----------|-----------|----------------|-----------|-----------|--------|
| TASK-W2-01 | Confirm CTR-01 pin: Scenario A skills orchestrated (consume pin; no Gateflow allowlist) | REQ-27, REQ-31 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-003-gateflow.md` | Pin fixtures show orchestrated; PolicyEngine dispatches without hardcoded list | `make check && make test` | no allowlists | ADR-006 (dispatch SSOT = pin) | `feature/INIT-GATEFLOW-003-w2-scenario-a` |
| TASK-W2-02 | Live verify Scenario A set + post–Gate 2 one-node re-run; coding-work evidence | REQ-27 | drivestream-lab/gateflow | same | Verify green after supporting pin | `.venv/bin/python -m tests.verify.verify_scenario_a` (name may vary) | testing-verify-flows | — | same |
| TASK-W2-03 | Assert metrics `by_runner` includes cursor p50/p95 when samples exist (unit + verify_status_metrics) | REQ-30 | drivestream-lab/gateflow | same | Assertions green with ≥1 sample | `make check && make test` ; `.venv/bin/python -m tests.verify.verify_status_metrics` | — | TDD PE-3 | `feature/INIT-GATEFLOW-003-w2-verify` |
| TASK-W2-04 | As-built + tests README INIT-003 complete; ground-ready | REQ-31 | drivestream-lab/gateflow | same | as-built W2 complete | inspection | SDD | — | same |

#### Files (W2)

| ID | Path | Action |
|----|------|--------|
| FILE-W2-01 | pin fixtures / unit pin tests | edit |
| FILE-W2-02 | `tests/verify/verify_scenario_a.py`, `verify_all.py` | create/edit |
| FILE-W2-03 | `tests/unit/test_metrics_emitter.py`, verify_status_metrics | edit |
| FILE-W2-04 | as-built, `tests/README.md` | edit |

#### Tests (W2)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W2-U | unit | `make test` | REQ-27 pin consume; REQ-30 by_runner |
| TEST-W2-V | live verify | Scenario A + status/metrics | REQ-27, REQ-30 |

---

## 3. Dependencies (DEP)

| ID | Dependency | Blocks |
|----|------------|--------|
| DEP-01 | INIT-001/002 control plane human_approved (as-built) | W0 start |
| DEP-02 | W0 merged (SDK + start-gate) | W1 |
| DEP-03 | W0 laptop spike + W1 Docker spike | W1 Scenario B exit |
| DEP-04 | W1 merged | W2 |
| DEP-05 | prayog-skills CTR-01 Scenario A `dispatch: orchestrated` | W2 Scenario A prove-it |
| DEP-06 | Human Alembic for `wave_duration_ms` | W1 store/API tasks |
| DEP-07 | `CURSOR_API_KEY` + model entitlement for programme account | W1/W2 live verify |

---

## 4. Risks (RISK)

| ID | Risk | Mitigation |
|----|------|------------|
| RISK-01 | `cursor-sdk` bridge/Node bits break Docker worker | TASK-W1-01 spike before Scenario B exit; document image deps |
| RISK-02 | Stub env accidentally used as live exit evidence | Start-gate quarantine; verify scripts require stub unset |
| RISK-03 | Long agent turns exceed job timeouts | Explicit SDK/orchestrator timeouts; tune in W1 |
| RISK-04 | Scenario A blocked on skills pin | DEP-05; hold W2 prove-it; gateflow still ships W0/W1 |
| RISK-05 | Registry `implemented=True` honesty regression | TASK-W0-03 + unit tests; ADR-006 |
| RISK-06 | Human forgets Alembic for wave_duration_ms | DDL note in PR; database-migrations.mdc |

---

## 5. Out of scope

- gateflow-ops UI/BFF
- Cursor **cloud** agents / self-hosted cloud shape
- Live OpenCode / Claude Code / Slack / Teams
- Launchpad product features
- Rebuilding wave-start / PR-at-start / board / ForgeClient
- Pin version-bump as exit gate; prayog-skills pin edits (CTR-01 — other repo)
- New ADRs (A1); metrics `?runner=` query param (PE-3)
- Multi-runner DI factory routing (PE-2 deferred)

---

## 6. As-built and docs tasks

| Task | File | Action |
|------|------|--------|
| As-built per wave | `docs/specification/as-built/implementation-status.md` | W0/W1/W2 capability rows |
| Feature map | `tests/README.md` | Scenario B/A verify + CURSOR_API_KEY prereqs |
| Spike notes | `docs/runbooks/` or `docs/specification/reports/` | laptop + Docker local SDK |
| Env example | `.env.example` | `CURSOR_API_KEY` |

> **ADR lifecycle** — no ADR promotion tasks. ADR-001…006 already Accepted; ADR-007 withdrawn.

---

## 7. Plan check summary

| Check | Status |
|-------|--------|
| P1 REQ coverage | PASS — REQ-27…31 in §1 |
| P2 TASK Implements | PASS — every TASK cites ≥1 REQ-* |
| P3 FILE paths | PASS — per wave |
| P4 done when | PASS |
| P5 test/verify commands | PASS — make test + verify scripts |
| P6 scope | PASS — gateflow only; CTR-01 external |
| P7 feasibility | PASS — FF-* addressed or deferred (CTR-01, Q-4) |
| P8 wave order | PASS — W0→W1→W2 + DEP table |
| P9 as-built/docs | PASS — §6 |
| P10 self-contained + commands | PASS |
| P11 MDC notes | PASS — TASK columns |
| P12 ADR conformance | PASS — ADR_REQUIRED 0; cite Accepted ADR-001…006; no Draft ADRs |
| P13 TDD Accepted | PASS — PE sign-off 2026-07-24 |
| P14 WorkManifest | PASS — §9 W0/W1/W2 + tasks[] |

---

## 8. PR instructions

> Commit this plan to the **Draft spec PR** branch alongside spec, feasibility,
> and TDD. Label remains **`spec-pending`** until PE completes §10.

```
Branch:   chore/INIT-GATEFLOW-003-spec-gateflow  (Draft PR #18)
PR title: "[INIT-GATEFLOW-003] Spec — gateflow"
Required reviewers: @drivestream-lab/prayog-pe-team
Review deadline: 2026-07-29

PE checklist (before spec-lgtm):
  [ ] Spec + feasibility + Accepted TDD + this plan on current head
  [ ] §0 PE sign-off complete
  [ ] Wave order / done-when / WorkManifest §9 OK
  [ ] P1–P14 pass

After spec-lgtm + Approve + merge — /board-seed from §9 (post-merge only)
```

---

## 10. Gate 2 unlock (PE — after plan on head)

| Item | Value |
|------|-------|
| Verdict | **GATE OPEN REQUEST** |
| Spec PR | https://github.com/drivestream-lab/gateflow/pull/18 |
| Spec PR head SHA | `223068d81c2aaa41c34dd80034a37748e8436eb8` |
| Gate label (current) | `spec-pending` |
| Gate label (target) | `spec-lgtm` |
| Blocking items | none |

```bash
launchpad apply-gates --repo gateflow --apply
```

PE on **exact current head**:

1. Remove `spec-pending` / `spec-blocked` / `spec-revised` / `spec-stale`; add **`spec-lgtm`**
2. GitHub **Approve** with attestation below
3. Mark Draft PR **Ready for review**
4. Authorize merge; then **`/board-seed`** from §9

### Approve attestation body

```text
Spec package approved
initiative: INIT-GATEFLOW-003
spec_pr_head_sha: 223068d81c2aaa41c34dd80034a37748e8436eb8
meta_pr_head_sha: 4c9cacb8b7aa5aeac50ef902c9d8fc400bb2ece5
impact_map_revision: 2
prd_digest: sha256:6062fa11d136e9a49dd6546377ec5d907789ef388108b477b846f6299673f9ad
scope_digest: sha256:aaf398dc53a4606b34e9e24fa7513cd3a3b7e64ea677047faf5d2e90c64eba85
plan_digest: sha256:c230eaeeb68bff1354308a335d4d5897020ff23ff452ca82df4e167a5cb928af
artifacts:
  - docs/specification/product/INIT-GATEFLOW-003-gateflow.md
  - docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-003.md
  - docs/specification/reports/Technical-Review-INIT-GATEFLOW-003.md
  - docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-003.md
```

---

## 9. WorkManifest seed

> **Primary:** `/board-seed` after spec merge. Wave ids exactly `W0`, `W1`, `W2`.

```yaml
# Generated by /spec-implementation-plan — 2026-07-24
# LOCAL — do not commit to prayog-skills upstream
apiVersion: launchpad/v1
kind: WorkManifest

initiative: INIT-GATEFLOW-003
# Branch naming: feature/INIT-GATEFLOW-003-w{N}-{slug}

metadata:
  title: INIT-GATEFLOW-003 — Live Cursor AgentRunner
  summary: |
    Make Cursor AgentRunner live in the Gateflow worker via official local
    cursor-sdk (in-process), fail-fast credentials/not-live runners, and
    stage/wave cycle-time metrics. Prove Scenario B then Scenario A (after
    prayog-skills pin). No new ADRs; reuse ADR-001…006.
  playbook:
    - docs/specification/product/INIT-GATEFLOW-003-gateflow.md
    - docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-003.md

target:
  org: drivestream-lab
  project: drivestream-lab Board

defaults:
  initiative: INIT-GATEFLOW-003
  parent: EPIC
  status: Backlog
  labels:
    - INIT-GATEFLOW-003

epic:
  id: EPIC
  repo: drivestream-lab/gateflow
  title: "[feature] INIT-GATEFLOW-003 — Live Cursor AgentRunner"
  codebase: drivestream-lab/gateflow
  spec_path: docs/specification/product/INIT-GATEFLOW-003-gateflow.md
  verify_command: make check && make test
  body: |
    ## Objective

    Live local cursor-sdk AgentRunner in the Gateflow worker, honest start-gate
    for credentials/not-live runners, and stage/wave cycle-time metrics —
    proven on Scenario B then Scenario A (after skills pin).

    ## Waves

    | Wave | Goal |
    |------|------|
    | W0 | Cursor SDK skeleton + start-gate honesty |
    | W1 | Scenario B prove-it + cycle-time + Docker spike |
    | W2 | Scenario A prove-it + metrics by_runner cursor |

    ## References

    - Spec: docs/specification/product/INIT-GATEFLOW-003-gateflow.md
    - Implementation plan: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-003.md
    - Technical review: docs/specification/reports/Technical-Review-INIT-GATEFLOW-003.md

work:
  - id: W0
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-003 W0] Cursor SDK skeleton + start-gate honesty"
    depends_on: []
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-003-gateflow.md
    verify_command: make check && make test
    status: Backlog
    tasks:
      - id: TASK-W0-01
        implements: [REQ-29, REQ-27]
        done_when: "CursorAgentSettings + cursor-sdk dependency; CURSOR_API_KEY documented; no secret in programme.yaml"
      - id: TASK-W0-02
        implements: [REQ-27, REQ-31]
        done_when: "CursorAgentRunner local SDK path; unit mock SUCCESS/FAILED; no cloud agents"
      - id: TASK-W0-03
        implements: [REQ-28, REQ-29]
        done_when: "Missing key blocks enqueue; stub/mock quarantined from live exit"
      - id: TASK-W0-04
        implements: [REQ-27]
        done_when: "Laptop local SDK spike note committed"
      - id: TASK-W0-05
        implements: [REQ-28, REQ-29]
        done_when: "Unit tests green; tests/README W0 map updated"
      - id: TASK-W0-06
        implements: [REQ-31]
        done_when: "as-built W0 rows updated"
    body: |
      ## Wave goal

      In-process local cursor-sdk adapter skeleton; CURSOR_API_KEY settings;
      fail-closed start-gate; stub quarantine; unit + laptop spike.

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Done when |
      |------|------------|-----------|
      | TASK-W0-01 | REQ-29, REQ-27 | Settings + poetry cursor-sdk |
      | TASK-W0-02 | REQ-27, REQ-31 | Live local AgentRunner adapter |
      | TASK-W0-03 | REQ-28, REQ-29 | Start-gate + stub quarantine |
      | TASK-W0-04 | REQ-27 | Laptop spike note |
      | TASK-W0-05 | REQ-28, REQ-29 | Unit + README |
      | TASK-W0-06 | REQ-31 | As-built W0 |

      ## Done when

      - [ ] All W0 tasks complete per plan

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-003-gateflow.md

  - id: W1
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-003 W1] Scenario B prove-it + cycle-time"
    depends_on:
      - W0
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-003-gateflow.md
    verify_command: make check && make test
    status: Backlog
    tasks:
      - id: TASK-W1-01
        implements: [REQ-27]
        done_when: "Docker/image spike with CURSOR_API_KEY + cwd recorded"
      - id: TASK-W1-02
        implements: [REQ-29, REQ-30]
        done_when: "Failure path persists stage + duration_ms; crash → failed"
      - id: TASK-W1-03
        implements: [REQ-30]
        done_when: "runs.wave_duration_ms + run detail (human Alembic applied)"
      - id: TASK-W1-04
        implements: [REQ-27, REQ-31]
        done_when: "Live Scenario B verify green; stub env unset"
      - id: TASK-W1-05
        implements: [REQ-30]
        done_when: "Unit + README + as-built W1 updated"
    body: |
      ## Wave goal

      Scenario B live Cursor prove-it; failure-path stage metrics; wave_duration_ms;
      Docker spike before exit.

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Done when |
      |------|------------|-----------|
      | TASK-W1-01 | REQ-27 | Docker spike |
      | TASK-W1-02 | REQ-29, REQ-30 | Failure stage metrics |
      | TASK-W1-03 | REQ-30 | wave_duration_ms |
      | TASK-W1-04 | REQ-27, REQ-31 | Scenario B live verify |
      | TASK-W1-05 | REQ-30 | Docs/as-built W1 |

      ## Done when

      - [ ] All W1 tasks complete per plan

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-003-gateflow.md

  - id: W2
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-003 W2] Scenario A prove-it + metrics"
    depends_on:
      - W1
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-003-gateflow.md
    verify_command: make check && make test
    status: Backlog
    tasks:
      - id: TASK-W2-01
        implements: [REQ-27, REQ-31]
        done_when: "Pin fixtures show Scenario A orchestrated; no Gateflow allowlist"
      - id: TASK-W2-02
        implements: [REQ-27]
        done_when: "Scenario A + post–Gate 2 live verify green (after CTR-01)"
      - id: TASK-W2-03
        implements: [REQ-30]
        done_when: "by_runner cursor p50/p95 asserted with samples"
      - id: TASK-W2-04
        implements: [REQ-31]
        done_when: "as-built + README INIT-003 complete"
    body: |
      ## Wave goal

      Scenario A live Cursor prove-it (depends on prayog-skills pin); post–Gate 2
      still runnable; metrics by_runner cursor; as-built complete.

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Done when |
      |------|------------|-----------|
      | TASK-W2-01 | REQ-27, REQ-31 | Consume orchestrated Scenario A pin |
      | TASK-W2-02 | REQ-27 | Scenario A live verify |
      | TASK-W2-03 | REQ-30 | Metrics by_runner cursor |
      | TASK-W2-04 | REQ-31 | As-built complete |

      ## Done when

      - [ ] All W2 tasks complete per plan
      - [ ] CTR-01 prayog-skills supporting pin available

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-003-gateflow.md
```

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-implementation-plan
  outcome: pass
  artifact:
    path: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-003.md
    digest: sha256:c230eaeeb68bff1354308a335d4d5897020ff23ff452ca82df4e167a5cb928af
  blockers: []
  signals:
    gate2_label: spec-pending
    gate_open_request: true
    ready_for_plan: true
    tdd_accepted: true
    adr_required_count: 0
    waves: [W0, W1, W2]
    reqs: [REQ-27, REQ-28, REQ-29, REQ-30, REQ-31]
    meta_pr: https://github.com/drivestream-lab/prayog-meta/pull/11
    meta_pr_head_sha: 4c9cacb8b7aa5aeac50ef902c9d8fc400bb2ece5
    map_revision: 2
    prd_digest: sha256:6062fa11d136e9a49dd6546377ec5d907789ef388108b477b846f6299673f9ad
    scope_digest: sha256:aaf398dc53a4606b34e9e24fa7513cd3a3b7e64ea677047faf5d2e90c64eba85
    spec_pr: https://github.com/drivestream-lab/gateflow/pull/18
  next_candidates:
    - gate-2
  human_checkpoint: true
  external_action: false
```
