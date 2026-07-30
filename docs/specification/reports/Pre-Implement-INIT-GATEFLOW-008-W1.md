# Pre-implement — gateflow / W1 — Automated forge apply + retire PR-at-start

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-008-W1.md` |
| Initiative | INIT-GATEFLOW-008 (brand **006A**) |
| Wave | W1 |
| Date | 2026-07-30 |
| Outcome | `pass` |
| Outcome reason | W0 human_approved; WorkManifest + P15 live contract clean; board seeded; commands resolved |
| Wave head context | Recommended bind: `feature/INIT-GATEFLOW-008-w1-automated-forge` from `develop` @ `64db0ee` — **not** opened by this skill; current checkout is `develop` |

---

### Gate check (prior wave)

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — on `develop` @ `64db0ee` |
| Spec PR merged | Implementation plan on integration branch | [x] yes — PR [#91](https://github.com/drivestream-lab/gateflow/pull/91) MERGED |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — `spec-lgtm`; merge `d7d974a` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids in body | [x] seeded — EPIC [#92](https://github.com/drivestream-lab/gateflow/issues/92); W1 [#94](https://github.com/drivestream-lab/gateflow/issues/94) parent=92 |
| WorkManifest contract | `prayog/v1` §9 passes validator | [x] pass — `prayog-skills/scripts/workmanifest_contract.py` |
| TASK exit proof | Every W1 `TASK-*` has exit criteria + proof | [x] complete — TASK-W1-01…05 |
| Live-verification contract | P15 applies | [x] contract — `verification.live.applicable: true`; `.venv/bin/python -m tests.verify.verify_implement_lane` |
| Plan source freshness | CURRENT / WAIVED Gate 1 | [x] current (waived digests) |
| Impact-map repo scope | waived Gate 1 | [x] match (waived) |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live under `live_verify_dir` | [x] `.venv/bin/python -m tests.verify.verify_implement_lane` |
| `ground_command` | resolved or N/A | [x] N/A — `/ground-spec` Pass-2 pin skill |
| Co-shipped live verify (P15) | FILE under `live_verify_dir` | [x] `tests/verify/verify_implement_lane.py` (extend in TASK-W1-05) |
| Prior wave as-built row | `human_approved` | [x] W0 = **human_approved** (2026-07-30; chore [#97](https://github.com/drivestream-lab/gateflow/pull/97)) |
| Prior Ground Report exists | W0 | [x] `Ground-Report-INIT-GATEFLOW-008-W0.md` |
| Plan PE sign-off (W0 only) | N/A for W1 | [x] N/A |

**Gate verdict:** **PASS**

**Forge readiness:** `commit_workspace` **required** — publish this checklist onto bound wave `head_ref` (create/cut `feature/INIT-GATEFLOW-008-w1-automated-forge` outside this skill if unbound). Do **not** open Draft PR here.

---

### Contracts consumed (from prior Ground Report)

> Source: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-008-W0.md` §Contracts produced. Confirmed against `src/` on `develop` @ `64db0ee`.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Authorization enum | `AuthorizationModeType` | wire `explicit` \| `automated` | enum | Ground-Report-W0 | [x] yes — `src/models/forge_types.py` |
| Resolved node auth | `ResolvedWorkflowNode.authorization` | optional enum | enum on EA; null else | Ground-Report-W0 | [x] yes — `src/models/handoff_models.py` |
| Fail-closed EA parse | `WorkflowEngine.get_node` / `_parse_authorization` | pin node map | node or ValueError | Ground-Report-W0 | [x] yes — `workflow_engine.py` |
| Day-one pin matrix | `get_node(<ea-id>)` | node id | authorization enum | Ground-Report-W0 | [x] yes — pin load via engine |
| Pass-1 resolve edge | `resolve_next(loop-spec/pass)` | stage+outcome | `wave-pr-action` automated | Ground-Report-W0 | [x] yes |
| Pre-implement publish policy | `get_node("pre-implement").forge.commit_workspace` | — | `required` | Ground-Report-W0 | [x] yes |

**Unconfirmed contracts:** none blocking. W1 must **change** current behaviour that still STOPs all `external-action` (`policy_engine._STOP_NODE_TYPES`) and still creates Draft PR at job start (`run_orchestrator` + `create_or_update_pull_request`) — those are this wave’s work, not missing W0 contracts.

**Known gap for W1 apply path:** pin `wave-pr-action` requires `head_ref`/`base_ref`; merge slots today lack those fields — REQ-9 says fill from **run context** (TASK-W1-02).

---

### Must read

- [x] `AGENTS.md`
- [x] MDC rules (domain-filtered):
  - [x] `fail-fast.mdc` — incomplete requires / wrong authorize fail closed
  - [x] `architecture.mdc` — business services own policy/orchestrator; ForgeClient infra
  - [x] `logging-loguru.mdc` — orchestrator structured logs (TASK-W1-03)
  - [x] `testing-verify-flows.mdc` — unit vs live; co-ship `verify_implement_lane`
  - [x] `spec-driven-development.mdc` — as-built / README with code
- [x] ADRs:
  - [x] ADR-009 — dual `authorization`; automated apply without interactive STOP
  - [x] ADR-003 — ForgeClient transport (unchanged ownership)
  - [x] ADR-005 — board/API boundaries (authorize path reuse)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-008-gateflow.md` (REQ-5…12, REQ-16 slice)
- [x] Plan / §9: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-008.md` W1
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/94 — TASK list (projection):
  - [x] **TASK-W1-01** — REQ-6, REQ-7 — depends_on: [] — `policy_engine.py` — exit: explicit STOP only; automated not authorize-STOP — proof: `make test`
  - [x] **TASK-W1-02** — REQ-7, REQ-8, REQ-9, REQ-12 — depends_on: TASK-W1-01 — `forge_action_service.py` — exit: shared apply; incomplete requires fail — proof: `make test`
  - [x] **TASK-W1-03** — REQ-5, REQ-8, REQ-11, REQ-12 — depends_on: TASK-W1-02 — `run_orchestrator.py` — exit: walker loop-spec → wave-pr apply → live-verify STOP — proof: `make test`
  - [x] **TASK-W1-04** — REQ-9, REQ-10 — depends_on: TASK-W1-03 — `run_orchestrator.py` + `test_run_orchestrator.py` — exit: no PR-at-start create; ensure_branch-only — proof: `make test`
  - [x] **TASK-W1-05** — REQ-8, REQ-10, REQ-11, REQ-16 — depends_on: TASK-W1-04 — `verify_implement_lane.py` + `tests/README.md` — exit: live asserts new PR timing — proof: verify command / `Live-Verify-INIT-GATEFLOW-008-W1.md`

---

### Governance alignment

- [x] Slice does not contradict Accepted ADR-009 dual mode (implements it)
- [x] Plan TASK MDC / ADR notes reviewed for W1
- [x] ADR-009, ADR-003, ADR-005 **Accepted**

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — only if contract drifts (prefer no drift)
- [ ] `as-built/implementation-status.md` — W1 verification row
- [ ] `tests/README.md` — feature map Pass-1 / PR timing (TASK-W1-05)
- [ ] Unit — policy, forge apply, orchestrator walker, no PR-at-start
- [ ] Live — extend `tests/verify/verify_implement_lane.py` (human at `live-verify`)
- [ ] ADR — no new ADR; do not weaken ADR-009

---

### Must not

- [ ] Implement W2 WorkManifest validator scope in this wave
- [ ] Keep STOP-all-EA or PR-at-start after claiming REQ-6/REQ-10 done
- [ ] Use `make test` as live verify success
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill
- [ ] Bypass W0 fail-closed authorization parse

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | format/lint/types/layers | `make check` |
| Unit | policy branch; shared apply; walker automated wave-pr; no PR-at-start | `make test` |
| Live verify | implement-lane PR timing on running stack (human at `live-verify`) | `.venv/bin/python -m tests.verify.verify_implement_lane` |
| Ground check | assigned W1 REQs | N/A — `/ground-spec` Pass-2 |

> P15 applies: live verify is required; unit-only is not sufficient for wave exit.

### Human live-verify (after loop-spec)

- [ ] Run `.venv/bin/python -m tests.verify.verify_implement_lane` with API/worker/forge per `tests/config.yaml` / script docs
- [ ] Confirm no Draft PR at implement start; PR after automated wave-pr when worker on
- [ ] Capture evidence for `Live-Verify-INIT-GATEFLOW-008-W1.md`
- [ ] Tip hygiene before Pass-2 `/learning-extract`

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-008
- Issue: [#94](https://github.com/drivestream-lab/gateflow/issues/94)
- Spec path: `docs/specification/product/INIT-GATEFLOW-008-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_implement_lane`
- ADRs in scope: ADR-009, ADR-003, ADR-005
- Wave head: bind `feature/INIT-GATEFLOW-008-w1-automated-forge` outside this skill

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — W1 ready for `/loop-spec` |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish this Pre-Implement to bound `head_ref` |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR |

Recommend `/commit-workspace` after wave head exists. Do not open the PR here.

---

### Merge order (if cross-module / cross-service)

N/A — gateflow-only. W1 before W2; INIT-007 dogfood still waits on W0+W1 on `develop`.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-008-W1.md
  blockers: []
  signals:
    wave: W1
    initiative: INIT-GATEFLOW-008
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/94"
    epic_issue: "https://github.com/drivestream-lab/gateflow/issues/92"
    recommended_head_ref: feature/INIT-GATEFLOW-008-w1-automated-forge
    base_ref: develop
    check_command: make check
    test_command: make test
    verify_command: ".venv/bin/python -m tests.verify.verify_implement_lane"
    tasks:
      - TASK-W1-01
      - TASK-W1-02
      - TASK-W1-03
      - TASK-W1-04
      - TASK-W1-05
    implements:
      - REQ-5
      - REQ-6
      - REQ-7
      - REQ-8
      - REQ-9
      - REQ-10
      - REQ-11
      - REQ-12
      - REQ-16
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
```
