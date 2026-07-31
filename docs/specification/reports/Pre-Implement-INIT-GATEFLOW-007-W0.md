## Pre-implement — gateflow / W0 — Closeout start API + Pass-2 walker + smoke verify

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-007-W0.md` |
| Initiative | INIT-GATEFLOW-007 |
| Wave | W0 |
| Date | 2026-07-31 |
| Outcome | `blocked` |
| Outcome reason | Plan §9 WorkManifest fails `prayog/v1` contract (40 errors: `launchpad/v1`, missing `exit`/`files`/`verification` on all waves); P15 W0 live-verify contract absent in manifest |
| Wave head context | Recommended bind: `feature/INIT-GATEFLOW-007-w0-closeout-start` from `develop` @ `9642434` — **not** opened by this skill; current checkout is `develop` |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — on `develop` @ `9642434` |
| Spec PR merged | Implementation plan on integration branch | [x] yes — PR [#83](https://github.com/drivestream-lab/gateflow/pull/83) MERGED to `develop` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — label `spec-lgtm`; merge `560f11f` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — EPIC [#84](https://github.com/drivestream-lab/gateflow/issues/84); W0 [#85](https://github.com/drivestream-lab/gateflow/issues/85) parent=84; W1 [#86](https://github.com/drivestream-lab/gateflow/issues/86); W2 [#87](https://github.com/drivestream-lab/gateflow/issues/87) |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [ ] **fail** — 40 errors (see below) |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` | [ ] **missing** — all 16 tasks lack `exit` mapping |
| Live-verification contract | When P15 applies: `verification.live` applicable + script under `live_verify_dir` | [ ] **missing** — W0 `verification` mapping absent; P15 applies (new HTTP closeout surface) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current — Gate 1 digests **WAIVED** (Q-1); feasibility + TDD CURRENT |
| Impact-map repo scope | revision and scope digest match canonical handoff | [x] match — **WAIVED** (Q-1) per plan §Source freshness |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script under `live_verify_dir` when P15 applies | [x] `.venv/bin/python -m tests.verify.verify_wave_closeout` (plan §Source freshness; co-ship in `/loop-spec`) |
| `ground_command` | resolved or N/A with reason | [x] N/A — `/ground-spec` is Pass-2 pin skill (orchestrated) |
| Co-shipped live verify (P15) | FILE path under `live_verify_dir` listed | [ ] **missing on tip** — `tests/verify/verify_wave_closeout.py` not present (expected co-ship TASK-W0-06) |
| Prior wave as-built row | `human_approved` | [x] N/A — first wave of INIT-007 |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] N/A — W0 |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] complete — 2026-07-29; regen PE re-`spec-lgtm` on #83 |

**WorkManifest validator output (fail closed):**

```
WorkManifest contract FAILED (40 error(s))
  [identity] apiVersion must be 'prayog/v1'; got 'launchpad/v1'
  [mutable_field] defaults.status / work[*].status forbidden
  [exit] work[W0..W2].tasks[*].exit: exit mapping is required (16 tasks)
  [files] work[W0..W2].tasks[*].files: files is required (16 tasks)
  [verification] work[0..2].verification: verification mapping is required (3 waves)
```

Reference shape: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-008.md` §9 (`apiVersion: prayog/v1` with per-task `files`, `exit`, wave `verification`).

**Gate verdict:** **BLOCKED** — §9 must be regenerated to `prayog/v1` before `/loop-spec`. Plan §7 P14 self-check is stale vs pin validator (INIT-008 W2 landed `run_workmanifest_contract`).

**Forge readiness (when seed / wave head absent):** Board seeded. Cut/bind `feature/INIT-GATEFLOW-007-w0-closeout-start` outside this skill before any `commit_workspace`. Do **not** open Draft PR here.

---

### Contracts consumed (from prior Ground Report)

> W0 of INIT-007 — no prior Ground Report for this initiative. Cross-programme
> contracts from INIT-008 W2 Ground Report §Contracts produced and as-built scan.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Implement lane start | `WaveStartService.start_implement_wave` | `ImplementWaveStartRequest` | `WaveStartResponse` + enqueue | `src/business_services/wave_start_service.py` | [x] yes |
| Spec lane start | `WaveStartService.start_spec_wave` | `SpecWaveStartRequest` | `WaveStartResponse` + enqueue | same | [x] yes |
| Programme token on wave mutations | `waves_routes` + `public_paths` | Bearer programme token | 401 without token | `src/api/v1/waves_routes.py`, `src/app.py` | [x] yes |
| Pass-1 pin Enter-at + stop @ live-verify | pin `workflow.yaml`; orchestrator walker | lane start → Pass-1 hops | `stopped` @ `live-verify` | Ground-Report INIT-008 W1; #76 | [x] yes |
| Pin WorkManifest contract gate | `run_workmanifest_contract` | plan §9 YAML | pass or ValueError | Ground-Report INIT-008 W2 §Contracts | [x] yes — **007 §9 currently fails** |
| Board create explicit authorize | pin `board-tickets-action` + `PolicyEngine` | EA + auth=explicit | STOP + authorize | Ground-Report INIT-008 W2 | [x] yes |
| Closeout intake authority (design) | ADR-010 §6 | third start contract; fixed Enter-at `learning-extract` | new run + PR bind | ADR-010 Accepted | [x] yes — **not implemented** |

**Unconfirmed contracts** (expected gap — W0 deliverable):

- `POST /api/v1/waves/closeout/start` — no route in `src/api/v1/waves_routes.py` (`rg closeout` empty)
- `WaveStartService.start_closeout_wave` — not present; pattern mirrors implement/spec starts
- `tests/verify/verify_wave_closeout.py` — not on tip; co-ship target for P15 smoke

---

### Must read

- [x] `AGENTS.md`
- [x] MDC rules (domain-filtered):
  - [x] `pydantic-schemas.mdc` — closeout request model `extra=forbid`
  - [x] `http-api-conventions.mdc` — route mount + programme token
  - [x] `architecture.mdc` — models vs routes vs services layering
  - [x] `fail-fast.mdc` — fixed Enter-at; ACTIVE 409; pin orchestrated check
  - [x] `testing-verify-flows.mdc` — co-ship live script under `tests/verify/`
  - [x] `spec-driven-development.mdc` — as-built + feature map same change
- [x] ADRs (keyword-matched):
  - [x] ADR-010 — lane intake + closeout §6 (Accepted)
  - [x] ADR-005 — programme-token mutations
  - [x] ADR-007 — bound prompt / workspace bind
  - [x] ADR-008 — handoff baton dual-write
  - [x] ADR-009 — forge publish ordering (learning-extract optional; ground-spec required)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-007-gateflow.md` (REQ-1…8, REQ-13, REQ-16, REQ-17 for W0)
- [x] Plan wave section / §9: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-007.md` W0
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/85 — TASK list (projection from plan §2; **not** SSOT until §9 prayog/v1):
  - [ ] **TASK-W0-01** — REQ-4, REQ-6, REQ-13 — closeout body model — exit proof: **missing in §9**
  - [ ] **TASK-W0-02** — REQ-1 — route + token — exit proof: **missing in §9**
  - [ ] **TASK-W0-03** — REQ-2, REQ-3, REQ-5, REQ-8, REQ-13 — `start_closeout_wave` — exit proof: **missing in §9**
  - [ ] **TASK-W0-04** — REQ-7, REQ-8 — Pass-2 walker unit — exit proof: **missing in §9**
  - [ ] **TASK-W0-05** — REQ-16 — mock hygiene — exit proof: **missing in §9**
  - [ ] **TASK-W0-06** — REQ-1, REQ-7, REQ-17 — smoke verify script — exit proof: **missing in §9**
  - [ ] **TASK-W0-07** — REQ-17 — as-built + README — exit proof: **missing in §9**

---

### Governance alignment

- [x] Slice spec does not contradict Accepted ADR-010 closeout amendment
- [x] Plan TASK MDC/ADR notes for W0 reviewed (`pydantic-schemas`, `http-api`, `fail-fast`, ADR-010/007/008/009)
- [x] Every cited ADR is **Accepted** in `docs/specification/adr/`
- [ ] §9 WorkManifest conforms to pin `prayog/v1` contract — **fail** (blocks coding)

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] `src/models/wave_start_models.py` (or `wave_closeout_models.py`) — `CloseoutWaveStartRequest`
- [ ] `src/api/v1/waves_routes.py` — `POST /api/v1/waves/closeout/start`
- [ ] `src/app.py` — `public_paths`
- [ ] `src/business_services/wave_start_service.py` — `start_closeout_wave`
- [ ] Unit tests — `tests/unit/test_wave_closeout.py`; orchestrator/handoff/trigger/notifier edits per plan FILE-W0-05…07
- [ ] `tests/verify/verify_wave_closeout.py` — **create** (P15 smoke)
- [ ] `tests/config.yaml.example`, `tests/README.md` — feature map row
- [ ] `docs/specification/as-built/implementation-status.md` — W0 row (smoke vs W2 dogfood)

---

### Must not

- [ ] Start `/loop-spec` until §9 passes `workmanifest_contract.py`
- [ ] Treat board issue #85 body as execution SSOT over canonical §9
- [ ] Use `{test_command}` / `make test` as live `verify_command` (P15)
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill
- [ ] Implement product code in this skill (gate-only)

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | format/lint/types/layers | `make check` |
| Unit | closeout model, route, service, Pass-2 walker, mock hygiene | `make test` |
| Live verify | closeout HTTP surface smoke (P15) — human @ `live-verify` | `.venv/bin/python -m tests.verify.verify_wave_closeout` |
| Ground check | Pass-2 `/ground-spec` after W2 dogfood | N/A this wave |

> Co-shipped script path: `tests/verify/verify_wave_closeout.py` (FILE-W0-08). Not on tip pre-coding.

### Human live-verify (after loop-spec)

- [ ] Run `.venv/bin/python -m tests.verify.verify_wave_closeout` against live stack (smoke: 401, validation, happy enqueue → `run_id`)
- [ ] Capture exit evidence for `Live-Verify-INIT-GATEFLOW-007-W0.md`
- [ ] Distinguish W0 smoke vs W2 full Pass-2 dogfood in README/as-built

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-007
- Issue: [#85](https://github.com/drivestream-lab/gateflow/issues/85)
- EPIC: [#84](https://github.com/drivestream-lab/gateflow/issues/84)
- Spec path: `docs/specification/product/INIT-GATEFLOW-007-gateflow.md`
- Plan: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-007.md`
- Spec merge PR: [#77](https://github.com/drivestream-lab/gateflow/pull/77) (product) + [#83](https://github.com/drivestream-lab/gateflow/pull/83) (P15 plan regen)
- Verify command (human): `.venv/bin/python -m tests.verify.verify_wave_closeout`
- ADRs in scope: ADR-010, ADR-005, ADR-007, ADR-008, ADR-009
- Wave head: bind `feature/INIT-GATEFLOW-007-w0-closeout-start` (plan §2 Branch) — closed PR #88 used wrong slug `…-w0-w0-…`

---

### Remediation (before re-run `/pre-implement`)

1. **`/spec-implementation-plan`** (or PE-directed §9 edit): regenerate §9 to `apiVersion: prayog/v1` mirroring INIT-008 shape — per-task `files`, `exit.criteria` + `exit.proof`, wave-level `verification` with W0 `verification.live.applicable: true`, script `tests/verify/verify_wave_closeout`, mode `smoke`; remove forbidden `status` fields.
2. Re-run `python prayog-skills/scripts/workmanifest_contract.py docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-007.md` — must exit 0.
3. Merge plan update with `spec-lgtm` if on a spec branch; re-run `/pre-implement` for W0.
4. Human/Forge: cut `feature/INIT-GATEFLOW-007-w0-closeout-start` from `develop` before `/commit-workspace` + `/loop-spec`.

---

### Checklist publish readiness (blocked — no commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `blocked` — WorkManifest contract fail + P15 verification mapping missing |
| Next | `wave-signoff` (`human-checkpoint`) — PE/engineering decision on §9 regen |
| Forge (this hop) | **disabled** — do not publish blocked checklist to wave head |
| After unblock | `pass` → `loop-spec` with `commit_workspace` required on checklist |

---

### Merge order (if cross-module / cross-service)

N/A — gateflow-only. Sequencing: INIT-008 W2 **human_approved** on `develop` (REQ-17); W0 closeout API before W1 learning ingest.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: blocked
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-007-W0.md
    digest: sha256:60bcc1026c17da09eea87a4c9c3e67d4f54ce68e31608fceeedce0cf19f5a894
  blockers:
    - TASK-W0-01
    - TASK-W0-02
    - TASK-W0-03
    - TASK-W0-04
    - TASK-W0-05
    - TASK-W0-06
    - TASK-W0-07
  signals:
    initiative: INIT-GATEFLOW-007
    wave: W0
    board_issue: "85"
    epic: "84"
    workmanifest_contract: fail
    workmanifest_errors: 40
    workmanifest_api_version: launchpad/v1
    required_api_version: prayog/v1
    p15: co-ship_smoke_w0
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_wave_closeout
    recommended_head_ref: feature/INIT-GATEFLOW-007-w0-closeout-start
    base_ref: develop
    integration_sha: 964243423e3eaaf59d716843bafa032e5d1b50c8
    remediation: spec-implementation-plan-regen-section-9
  next_candidates:
    - wave-signoff
  human_checkpoint: true
  external_action: false
```
