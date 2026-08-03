# Feasibility report — INIT-GATEFLOW-009

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-009 |
| Spec | `docs/specification/product/INIT-GATEFLOW-009-gateflow.md` |
| Spec digest | `sha256:f4c93f4a13bb72617555fe320b3926130a0885ede45f9574c4ff1a09e2cad642` |
| PRD digest | `sha256:76ab22b3c197b9d0cb6b08e6cea379c4e07b3a471b8a88203fddca6014c1c012` |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-009.md` / `1` |
| Repo scope digest | `sha256:d0a2b62632113db0fa64cb7d7e63dc393fa5a8217092dda242a99b3392978e9b` |
| Approved meta PR head | `6660aa4fefbcd80324cb970aa5bab642d3e5e0a1` |
| Impact-map approval | @0xbeefdead APPROVED 2026-08-03T10:47:39Z on `6660aa4…` — [meta PR #23](https://github.com/drivestream-lab/prayog-meta/pull/23) |
| Source freshness | **CURRENT** — PRD digest, map revision 1, scope digest, and approved head match spec header and prior `spec-draft` handoff |
| Prior stage | `/spec-draft` → `pass` → `/spec-pr-action` (Draft spec PR baton) |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-03 |
| Branch | `chore/INIT-GATEFLOW-009-spec-gateflow` — Draft spec PR (single review surface) |
| Initiative segment | `INIT-GATEFLOW-009` |
| Status | Draft |
| Review deadline | 2026-08-06 |
| Deciders | PM: programme / PE · Domain SME: N/A (factory prove-out) |

## Summary

INIT-GATEFLOW-009 is **buildable in this repo today** as a prove-out programme on
the INIT-006…008 control plane. Harness pin **`v0.5.0-rc.2`** exact-matches the
`prayog-skills` submodule (`72ad383`); `spec-draft` and `initiative-feasibility`
are **`dispatch: orchestrated`** on the active pin; spec start, workspace publish,
automated `spec-pr-action`, closeout, and authorize APIs are **unit-complete**
(217 pytest green, observed 2026-08-03). Remaining work is intentional W0–W3
deliverables (checklist, live dogfood, freeze record, real CI) — not missing
foundation or ADR conflicts.

**Findings:** 6 total (0 Critical, 0 Should fix, 4 Verify, 2 Gap)

### Derived counts (lane × severity)

| Lane | Blocking open | Non-blocking open | Resolved |
|------|---------------|-------------------|----------|
| PM | 0 | 0 | 0 |
| PE / ADR | 0 | 4 | 0 |
| Domain | 0 | 0 | 0 |
| Auto-fix | 0 | 1 | 0 |

| Severity | Unresolved count |
|----------|------------------|
| Critical | 0 |
| Should fix | 0 |
| Verify / Gap (informational) | 6 |

### Selected workflow outcome

| Field | Value |
|-------|-------|
| Outcome | `pass` |
| Rationale | Source freshness CURRENT; zero unresolved blocking PE/ADR findings; gaps are scoped W0–W3 prove-out deliverables |
| Next (from workflow) | `spec-technical-review` |

Informational observations do **not** block pass. Proceed to `/spec-technical-review`
before `/spec-implementation-plan`.

---

## Baseline snapshot (F1)

| Area | Current state | Evidence |
|------|---------------|----------|
| Unit tests | `tests/unit/` — 217 passed (2026-08-03) | `make test` |
| Toolchain | `make check` (black, ruff, pyright, import-linter) | `Makefile`, `tests/README.md` |
| Live verify | `verify_spec_lane.py` (opt-in W1 scaffold); `verify_wave_closeout.py`; `verify_all` smoke | `tests/verify/`, `tests/README.md` |
| As-built | Implement + 008 **human_approved**; spec wrap-up + authorize live **deferred**; CI **placeholder** | `docs/specification/as-built/implementation-status.md` |
| Pin / submodule | `.harness-pin.yaml` `agent_skills.ref: v0.5.0-rc.2` ≡ submodule `72ad383` | `.harness-pin.yaml`; `git -C prayog-skills describe --exact-match` |
| CI | Placeholder echo job | `.github/workflows/ci.yml` |

## Traceability matrix

| Spec REQ / wave | Spec claim | Code evidence | Unit | Verify | Status |
|-----------------|------------|---------------|------|--------|--------|
| REQ-1 / W0 | Consume `v0.5.0-rc.2` family; harness pin == submodule | `.harness-pin.yaml`; `prayog-skills/` @ `v0.5.0-rc.2` | `test_handoff_workflow` | — | **exists** |
| REQ-2 / W0 | W0 prove-out checklist artifact | No `*009*` checklist under `docs/specification/reports/` | — | — | **gap** (W0 deliverable) |
| REQ-3 / W1 | `POST /api/v1/waves/spec/start` meta accept-gate | `waves_routes.py`, `wave_start_service.py`, `meta_pr_intake.py` | `test_wave_start`, `test_meta_pr_intake` | `verify_spec_lane` | **exists** (unit); live W1 pending |
| REQ-4 / W1 | Publish after orchestrated content hops | `run_orchestrator._publish_stage_workspace_if_needed` | `test_publish_stage_workspace_*` in `test_run_orchestrator.py` | deferred | **exists** (unit); live W1 pending |
| REQ-5 / W1 | Automated `spec-pr-action` Draft PR | `run_orchestrator._apply_automated_forge`; pin `spec-pr-action` `authorization: automated` | `test_forge_action_service`, `test_forge_policy` | `verify_spec_lane` | **exists** (unit); live W1 pending |
| REQ-6 / W1 | Later hops commit to same PR tip | Same publish + run-head binding in orchestrator | publish unit tests | inspection + live | **partial** — needs W1 live attestation |
| REQ-7 / W1 | Honest stop at manual/human gate | Pin: `spec-implementation-plan` `dispatch: manual`; walker STOP logic | `test_run_orchestrator`, `test_trigger_policy` | `verify_spec_lane` | **exists** |
| REQ-8 / W1 | Reviewer attestation + non-empty tip | Not yet recorded for 009 | — | — | **gap** (W1 exit) |
| REQ-9 / W1 | `verify_spec_lane.py` W1 prove-out | `tests/verify/verify_spec_lane.py` (394 lines; happy + findings paths) | — | opt-in live | **exists** (scaffold) |
| REQ-10–12 / W2 | Spec closeout Pass-2 to `wave-signoff` | `POST /api/v1/waves/closeout/start`; pin Pass-2 graph | `test_wave_closeout`, `test_handoff_workflow` | `verify_wave_closeout` | **exists** (unit); live W2 pending |
| REQ-13–15 / W3 | Stop → authorize → side effect | `forge_routes.py`, `forge_action_service.py`; pin `board-tickets-action` explicit | `test_forge_action_service` | deferred | **exists** (unit); live W3 pending |
| REQ-16–18 / W3 | Feature readiness freeze + as-built | No `Feature-Readiness-INIT-GATEFLOW-009.md` yet | — | — | **gap** (W3 deliverable) |
| REQ-19–20 / W3 | Real CI on PRs | `.github/workflows/ci.yml` placeholder | — | — | **gap** (W3 deliverable; baseline acknowledged) |

## ADR pass (pre-T2)

| ADR | Domain matched | Status |
|-----|----------------|--------|
| ADR-009 | pin forge publish/mutate, automated vs explicit EA | **Accepted** — aligned (008 dual-authorization amendment) |
| ADR-010 | spec/meta intake, dual workspace, closeout | **Accepted** — aligned |
| ADR-003 | ForgeClient infra | Accepted — aligned |
| ADR-005 | programme token on starts/authorize | Accepted — aligned |
| ADR-008 | handoff baton ingest | Accepted — aligned with orchestrated baton |

## MDC pass (pre-T2)

| MDC | Domain | Read / skipped |
|-----|--------|----------------|
| `testing-verify-flows.mdc` | unit vs verify boundary, CI vs live | read |
| `spec-driven-development.mdc` | same-PR as-built discipline | read |
| `architecture.mdc` | layered src/, forge in infra | read |
| `fail-fast.mdc` | fail-closed preconditions | read |
| `http-api-conventions.mdc` | wave start routes | skipped (no new route shapes) |
| `database-migrations.mdc` | Alembic | skipped (no new DDL in prove-out spec) |

## ADR traceability (F13)

| Spec REQ / wave | Relevant ADR(s) | Status | Finding |
|-----------------|-----------------|--------|---------|
| REQ-3, REQ-4, CTR-04 | ADR-010 | aligned | — |
| REQ-4, REQ-5, REQ-13, CTR-02/03 | ADR-009 | aligned | — |
| REQ-10, CTR-05 | ADR-010 §6 closeout | aligned | — |
| REQ-19 CI | N/A | N/A | no ADR gap |

No **NEW-ADR** required — prove-out consumes existing Accepted ADRs and pin SSOT.

## Governance findings (F13–F14)

| ID | Check | Spec quote | Governing doc | Finding |
|----|-------|------------|---------------|---------|
| — | F13 | (none) | ADR-009, ADR-010 | No conflicts |
| — | F14 | REQ-19 "make check and/or make test" | `testing-verify-flows.mdc` | Aligned — CI should mirror local toolchain |

## Findings by severity

### Critical

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| — | — | None | — |

### Should fix

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| — | — | None | — |

### Verify / Gap (informational)

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-01 | F2 | REQ-2 W0 prove-out checklist not yet present | Spec REQ-2; no checklist under `docs/specification/reports/` for 009 |
| FF-02 | F5/F6 | As-built drift: §006 gap still says spec-draft pin `manual` and meta columns need human Alembic; pin is orchestrated and migration `1cd9a83a94a2` declares `meta_pr_url`/`meta_head_sha` | `implementation-status.md` L185–184; `postgres_migrations/versions/1cd9a83a94a2_first_version.py`; `workflow.yaml` `spec-draft.dispatch: orchestrated` |
| FF-03 | F2/F8 | REQ-19 CI still placeholder echo — W3 deliverable | `.github/workflows/ci.yml` |
| FF-04 | F1/F5 | Live prove-outs (W1 tip, W2 spec closeout, W3 authorize) deferred — matches spec as-built baseline | `implementation-status.md`; spec §As-built baseline |
| FF-05 | F2 | REQ-16 feature readiness freeze doc absent | No `Feature-Readiness-INIT-GATEFLOW-009.md` |
| FF-06 | F7 | Low overlap risk: spec lane journey in `verify_spec_lane` only; unit covers APIs/orchestrator separately | `tests/README.md`; `verify_spec_lane.py` vs `tests/unit/test_*` |

## Impact surface

| Wave / area | Likely files/modules | Test touch |
|-------------|----------------------|------------|
| W0 checklist | `docs/specification/reports/` runbook | inspection |
| W1 spec Pass-1 live | `run_orchestrator.py`, `forge_action_service.py`, `verify_spec_lane.py` | live verify + unit regression |
| W2 closeout | `wave_start_service.py`, closeout route | `verify_wave_closeout` dogfood |
| W3 authorize + freeze + CI | `forge_routes.py`, `.github/workflows/ci.yml`, reports | live verify + CI run |
| As-built hygiene | `implementation-status.md`, `tests/README.md` | inspection |

## Risks & assumptions

| ID | Risk / assumption | Mitigation |
|----|-------------------|------------|
| R-1 | W1 dogfood may hit publish/ingest edge cases (prior 009 chore PRs note publish crash on blocked handoff) | Harden publish fail-closed + stop context; re-run `verify_spec_lane` |
| R-2 | A-8 open — W3 authorize target node | Default `board-tickets-action` per pin; resolve in TDD (Q-2) |
| R-3 | REQ-15 lifts INIT-007 spec closeout deferral — W2 is on critical path | Plan W2 before W3; no PE waiver for 009 exit |

## Recommended spec edits

- None blocking. Optional: reference existing Alembic revision for meta columns when updating as-built during W3 (FF-02).
- Confirm Q-1…Q-4 defaults in TDD (`/spec-technical-review`).

---

## Open items by lane

| ID | Lane | Question / item | Blocking | Owner | Status | Required by | Default if deferred | Evidence | Resolution reference |
|----|------|-----------------|----------|-------|--------|-------------|---------------------|----------|----------------------|
| Q-1 | PE | W1 minimum path: feasibility → technical-review vs stop at plan | no | PE | open | W1 verify | Follow `verify_spec_lane` happy chain | `verify_spec_lane.py` L1–12 | TDD |
| Q-2 | PE | W3 authorize side-effect target | no | PE | open | W3 live | `board-tickets-action` / `create_board_tickets` | Spec A-8; pin `board-tickets-action` | TDD |
| Q-3 | PE | Freeze record location | no | PE | open | W3 | `docs/specification/reports/Feature-Readiness-INIT-GATEFLOW-009.md` | Spec REQ-16 | TDD |
| Q-4 | PE | CI minimum bar | no | PE | open | W3 | `make check` && `make test` on ubuntu-latest | Spec REQ-19 | TDD / CI PR |
| AF-1 | auto-fix | As-built §006 gaps stale (orchestrated spec-draft; meta Alembic) | no | PE | open | W0/W3 as-built update | Align rows to pin + `1cd9a83a94a2` | FF-02 | Forge publish during prove-out |

### PM questions (product scope, UX, priority)

#### Blocking — must resolve before spec merge

None.

#### Defer — can proceed with documented assumption

None.

### PE questions (engineering decisions — resolved by `/spec-technical-review`)

#### Blocking for implementation plan

None.

#### Defer with default

1. **Q-1** — W1 stop depth: default happy chain through `spec-technical-review` per `verify_spec_lane.py`.
2. **Q-2** — W3 authorize target: default `board-tickets-action`.
3. **Q-3** — Freeze doc path: default standalone report + as-built row.
4. **Q-4** — CI bar: default `make check` + `make test`.

### Domain clarifications (business source-of-truth)

None — factory prove-out; no SME source-of-truth gaps.

### Auto-fixable (agent resolves later — not inside this skill)

| # | Item | Fix |
|---|------|-----|
| AF-1 | As-built §006 open gaps contradict current pin/migration | Update `implementation-status.md` during W0/W3 prove-out |

---

## Check summary

| Check | Status | Findings |
|-------|--------|----------|
| F1 Baseline snapshot | PASS | FF-04 Verify |
| F2 Spec → code map | PASS | FF-01, FF-03, FF-05 Gap |
| F3 Spec → verify map | PASS | `verify_spec_lane`, `verify_wave_closeout` named |
| F4 Spec → unit map | PASS | meta intake, forge, closeout, orchestrator covered |
| F5 As-built drift | PASS | FF-02 Verify (doc lag, not code gap) |
| F6 Docs drift | PASS | FF-02 Verify |
| F7 Overlap risk | PASS | FF-06 Verify |
| F8 CI vs live boundary | PASS | placeholder CI documented |
| F9 Cross-service touch | PASS | CTR-01…05 files/pin exist |
| F10 Assumptions | PASS | A-1…A-8 evidenced or defaulted |
| F11 Effort drivers | PASS | W0 checklist → W1 live → W2 closeout → W3 authorize/CI/freeze |
| F12 PM questions | PASS | Q-1…Q-4 non-blocking with defaults |
| F13 ADR conformance | PASS | ADR-009/010 aligned; no NEW-ADR |
| F14 MDC conformance | PASS | testing/SDD aligned |

**Check PASS (severity-aware):** **PASS** — zero unresolved blocking findings.

---

## Next steps

> Persist this report locally alongside the spec draft. Fill `handoff.forge` for
> `/commit-workspace` (or Gateflow ForgeClient) onto the Draft spec PR —
> **do not** commit, push, open PRs, or apply labels inside this skill.
> Gate 2 label stays **`spec-pending`**.

1. **`/commit-workspace`** — publish this report onto `chore/INIT-GATEFLOW-009-spec-gateflow`.
2. **`/spec-technical-review`** — resolve Q-1…Q-4 in TDD; no blocking ADR work expected.
3. Then **`/spec-implementation-plan`** — after Accepted TDD on spec branch.
4. Execute W0→W3 prove-out per plan; PE sets **`spec-lgtm`** only after full package on head.

### Forge readiness

| Item | Value |
|------|-------|
| Local report path | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-009.md` |
| Target branch | `chore/INIT-GATEFLOW-009-spec-gateflow` |
| Recommended forge | `/commit-workspace` (Gate 2 stays `spec-pending`) |
| Mutations performed by this skill | **none** |

```
Draft spec PR: chore/INIT-GATEFLOW-009-spec-gateflow  (spec-pending)
When ready:
  [x] Source freshness is CURRENT
  [x] All blocking PM questions answered (none)
  [x] All blocking Domain clarifications answered (none)
  [ ] Spec + feasibility on branch tip (Forge `/commit-workspace` for this report)
  [ ] Proceed: /spec-technical-review (pass and findings both route here)
  [ ] After spec + feasibility + TDD + plan on branch (Forge publish):
      PE sets spec-lgtm + Approve on exact head → Ready for review → merge
  [ ] After merge: W0–W3 live prove-out per plan
```

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: initiative-feasibility
  outcome: pass
  artifact:
    path: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-009.md
    digest: sha256:99dec941857a7e8112d9ec6d4b3821feca2b34f9019495a20a6a6ae0020caa31
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-009
    ticket: "271562"
    meta_pr: "https://github.com/drivestream-lab/prayog-meta/pull/23"
    meta_pr_head: "6660aa4fefbcd80324cb970aa5bab642d3e5e0a1"
    map_revision: 1
    prd_digest: "sha256:76ab22b3c197b9d0cb6b08e6cea379c4e07b3a471b8a88203fddca6014c1c012"
    scope_digest: "sha256:d0a2b62632113db0fa64cb7d7e63dc393fa5a8217092dda242a99b3392978e9b"
    spec_digest: "sha256:f4c93f4a13bb72617555fe320b3926130a0885ede45f9574c4ff1a09e2cad642"
    source_freshness: CURRENT
    ripple_action: continue
    new_adr: false
    findings_critical: 0
    findings_should_fix: 0
    findings_verify_gap: 6
    nonblocking_questions: "Q-1,Q-2,Q-3,Q-4"
    pin_ref: v0.5.0-rc.2
    pin_sha: 72ad383a13499b7d4cc69ea5c44d30e9302d0685
    unit_tests_pass: 217
  next_candidates:
    - spec-technical-review
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    # Pin: initiative-feasibility forge.commit_workspace = required.
    # Publish this report onto Draft spec PR head — invoke /commit-workspace
    # (or Gateflow ForgeClient). This skill does not mutate.
```
