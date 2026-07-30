# Pre-implement — gateflow / W2 — WorkManifest prayog/v1 + docs

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-008-W2.md` |
| Initiative | INIT-GATEFLOW-008 (brand **006A**) |
| Wave | W2 |
| Date | 2026-07-30 |
| Outcome | `pass` |
| Outcome reason | W1 human_approved on `develop`; WorkManifest + P15 live contract clean; board seeded; commands resolved |
| Wave head context | Recommended bind: `feature/INIT-GATEFLOW-008-w2-workmanifest` from `develop` @ `e83dc20` — **not** opened by this skill; current checkout is `develop` |

---

### Gate check (prior wave)

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — on `develop` @ `e83dc20` |
| Spec PR merged | Implementation plan on integration branch | [x] yes — PR [#91](https://github.com/drivestream-lab/gateflow/pull/91) MERGED |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — `spec-lgtm`; merge `d7d974a` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids in body | [x] seeded — EPIC [#92](https://github.com/drivestream-lab/gateflow/issues/92); W2 [#95](https://github.com/drivestream-lab/gateflow/issues/95) parent=92 |
| WorkManifest contract | `prayog/v1` §9 passes validator | [x] pass — `prayog-skills/scripts/workmanifest_contract.py` → `WorkManifest contract passed.` |
| TASK exit proof | Every W2 `TASK-*` has exit criteria + proof | [x] complete — TASK-W2-01…04 |
| Live-verification contract | P15 applies | [x] contract — `verification.live.applicable: true`; `.venv/bin/python -m tests.verify.verify_board` |
| Plan source freshness | CURRENT / WAIVED Gate 1 | [x] current (waived digests) |
| Impact-map repo scope | waived Gate 1 | [x] match (waived) |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live under `live_verify_dir` | [x] `.venv/bin/python -m tests.verify.verify_board` |
| `ground_command` | resolved or N/A | [x] N/A — `/ground-spec` Pass-2 pin skill |
| Co-shipped live verify (P15) | FILE under `live_verify_dir` | [x] `tests/verify/verify_board.py` (extend in TASK-W2-03) |
| Prior wave as-built row | `human_approved` | [x] W1 = **human_approved** (2026-07-30; merge [#98](https://github.com/drivestream-lab/gateflow/pull/98) @ `e83dc20`) |
| Prior Ground Report exists | W1 | [x] `Ground-Report-INIT-GATEFLOW-008-W1.md` |
| Plan PE sign-off (W0 only) | N/A for W2 | [x] N/A |

**Gate verdict:** **PASS**

**Forge readiness:** `commit_workspace` **required** — publish this checklist onto bound wave `head_ref` (create/cut `feature/INIT-GATEFLOW-008-w2-workmanifest` outside this skill if unbound). Do **not** open Draft PR here.

---

### Contracts consumed (from prior Ground Report)

> Source: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-008-W1.md` §Contracts produced. Confirmed against `src/` on `develop` @ `e83dc20`.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| EA policy branch | `PolicyEngine._decision_for_external_action` | resolved EA + auth | STOP explicit / APPLY_FORGE automated / BLOCK missing | Ground-Report-W1 | [x] yes — board-tickets stays explicit STOP (`test_policy_explicit_external_action_stops`) |
| Shared forge apply | `ForgeActionService.apply_external_action` | pin + handoff + optional head/base | apply result or ValidationError | Ground-Report-W1 | [x] yes — authorize reuses apply; board create via authorize path |
| Automated walker apply | `run_orchestrator._apply_automated_forge` | run + workspace + automated EA | `pr_number` + re-resolve | Ground-Report-W1 | [x] yes — W2 must not regress open_draft_pr automation |
| Job-start branch only | `_ensure_run_branch` | initiative/wave/slug/base | branch; `pr_number` may be null | Ground-Report-W1 | [x] yes — verify_board must not assume PR-at-start |
| Forge head/base slots | `forge_models` merge / readiness | head_ref, base_ref | filled when required | Ground-Report-W1 | [x] yes — board create may omit PR slots |
| Pass-1 live timing docs | `verify_implement_lane` + README | running stack | PR after wave-pr | Ground-Report-W1 | [x] yes — W2 extends `verify_board` + README |

**Unconfirmed contracts:** none blocking.

**Known gap for W2 (this wave’s work):** `execute_create_board_tickets` does **not** yet invoke pinned `workmanifest_contract.py`; `work_manifest_models` still documents legacy launchpad parse and does not enforce `apiVersion: prayog/v1` fail-closed before BoardService — TASK-W2-01.

---

### Must read

- [x] `AGENTS.md`
- [x] MDC rules (domain-filtered):
  - [x] `fail-fast.mdc` — reject launchpad/v1 / bad kind fail closed
  - [x] `architecture.mdc` — forge apply in business services; BoardService projection only
  - [x] `testing-verify-flows.mdc` — unit vs live; co-ship `verify_board`
  - [x] `spec-driven-development.mdc` — as-built / README / feature map with code
  - [x] `pydantic-schemas.mdc` — WorkManifest models at parse boundary
- [x] ADRs:
  - [x] ADR-009 — pin SSOT; explicit board authorize; dual executor
  - [x] ADR-005 — programme-token control-plane mutations (board APIs)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-008-gateflow.md` (REQ-13…17)
- [x] Plan / §9: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-008.md` W2
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/95 — TASK list (projection):
  - [x] **TASK-W2-01** — REQ-13, REQ-14 — depends_on: [] — `forge_action_service.py`, `work_manifest_models.py` — exit: pin validator; launchpad/v1 rejected; prayog/v1 accepted — proof: `make test`
  - [x] **TASK-W2-02** — REQ-15 — depends_on: TASK-W2-01 — forge/policy tests — exit: board-tickets-action still explicit authorize — proof: `make test`
  - [x] **TASK-W2-03** — REQ-13, REQ-16 — depends_on: TASK-W2-01 — `verify_board.py`, `tests/README.md` — exit: live covers prayog/v1 posture — proof: `.venv/bin/python -m tests.verify.verify_board`
  - [x] **TASK-W2-04** — REQ-16, REQ-17 — depends_on: TASK-W2-03 — as-built, `tests/README.md`, `docs/specification/README.md` — exit: Pass-1 wave-pr edges + 007 dogfood unblocked note — proof: review

---

### Governance alignment

- [x] Slice does not contradict Accepted ADR-009 (board remains `authorization: explicit`)
- [x] Plan TASK MDC / ADR notes reviewed for W2
- [x] ADR-009, ADR-005 **Accepted**

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — only if contract drifts (prefer no drift)
- [ ] `as-built/implementation-status.md` — W2 complete + REQ-17 / 007 dogfood note
- [ ] `tests/README.md` — WorkManifest validator + verify_board feature map
- [ ] `docs/specification/README.md` — active initiative / 007 ordering note
- [ ] Unit — reject launchpad/v1; accept prayog/v1; board still explicit authorize
- [ ] Live — extend `tests/verify/verify_board.py` (human at `live-verify`)
- [ ] ADR — no new ADR; do not weaken ADR-009 / ADR-005

---

### Must not

- [ ] Treat board issue bodies as a second WorkManifest SSOT
- [ ] Automate `board-tickets-action` (must stay explicit STOP + authorize)
- [ ] Regress W1 automated `wave-pr-action` / ensure_branch-only start
- [ ] Use `make test` as live verify success
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill
- [ ] Soft-fallback to launchpad/v1 when pin validator fails

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | format/lint/types/layers | `make check` |
| Unit | pin WorkManifest validator; prayog/v1 only; board explicit authorize | `make test` |
| Live verify | board create validation posture on running stack (human at `live-verify`) | `.venv/bin/python -m tests.verify.verify_board` |
| Ground check | assigned W2 REQs | N/A — `/ground-spec` Pass-2 |

> P15 applies: live verify is required; unit-only is not sufficient for wave exit.

### Human live-verify (after loop-spec)

- [ ] Run `.venv/bin/python -m tests.verify.verify_board` with API + programme token (+ forge creds when script creates issues) per `tests/README.md` / config
- [ ] Confirm invalid `apiVersion` rejected; prayog/v1 path documented/green
- [ ] Capture evidence for `Live-Verify-INIT-GATEFLOW-008-W2.md`
- [ ] Tip hygiene before Pass-2 `/learning-extract`

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-008
- Issue: [#95](https://github.com/drivestream-lab/gateflow/issues/95)
- Spec path: `docs/specification/product/INIT-GATEFLOW-008-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_board`
- ADRs in scope: ADR-009, ADR-005
- Wave head: bind `feature/INIT-GATEFLOW-008-w2-workmanifest` outside this skill

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — W2 ready for `/loop-spec` |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish this Pre-Implement to bound `head_ref` |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR |

Recommend `/commit-workspace` after wave head exists. Do not open the PR here.

---

### Merge order (if cross-module / cross-service)

N/A — gateflow-only. W2 after W1 (on `develop` @ `e83dc20`). After W2 merges, INIT-007 dogfood is the first live prove-it priority (REQ-17).

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-008-W2.md
  blockers: []
  signals:
    wave: W2
    initiative: INIT-GATEFLOW-008
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/95"
    epic_issue: "https://github.com/drivestream-lab/gateflow/issues/92"
    recommended_head_ref: feature/INIT-GATEFLOW-008-w2-workmanifest
    base_ref: develop
    check_command: make check
    test_command: make test
    verify_command: ".venv/bin/python -m tests.verify.verify_board"
    tasks:
      - TASK-W2-01
      - TASK-W2-02
      - TASK-W2-03
      - TASK-W2-04
    implements:
      - REQ-13
      - REQ-14
      - REQ-15
      - REQ-16
      - REQ-17
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    # Pin pre-implement commit_workspace: required
    recommend: commit_workspace
    head_ref: feature/INIT-GATEFLOW-008-w2-workmanifest
    base_ref: develop
```
