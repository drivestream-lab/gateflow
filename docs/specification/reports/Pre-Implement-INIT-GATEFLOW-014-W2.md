## Pre-implement — gateflow / W2 — Cut over repo lifecycle/twin under JWT; refuse old doors

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-014-W2.md` |
| Initiative | INIT-GATEFLOW-014 |
| Wave | W2 |
| Date | 2026-08-11 |
| Outcome | `pass` |
| Outcome reason | Prior W1 Ground Report + `human_approved`; WorkManifest contract clean after W1/W2 live.covers alignment; board #217 seeded under EPIC #214; P15 live scripts declared; W1 contracts confirmed in `source_roots`. |
| Wave head context | Bound by Forge/human context: `develop` @ `278de19` (W1 merge [#221](https://github.com/drivestream-lab/gateflow/pull/221)) — not opened by this skill. No `feature/INIT-GATEFLOW-014-w2-*` yet; cut from `develop` before `/loop-spec` (or bind `develop` for checklist publish only). |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — `develop` @ `278de19`; not on `chore/*-spec-*` |
| Spec PR merged | Implementation plan on integration branch | [x] yes — PR [#212](https://github.com/drivestream-lab/gateflow/pull/212) MERGED; plan on tree |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — `spec-lgtm` on [#212](https://github.com/drivestream-lab/gateflow/pull/212); head `4df184c…`; merge `ae77433…` ancestor of HEAD |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present; waves are **sub-issues of the EPIC** | [x] seeded — EPIC [#214](https://github.com/drivestream-lab/gateflow/issues/214); W2 [#217](https://github.com/drivestream-lab/gateflow/issues/217) `parent`=#214; body lists TASK-W2-01…06 |
| WorkManifest contract | `prayog/v1` §9 passes `workmanifest_contract.py` | [x] pass — re-verified after aligning W1/W2 `live.covers` with verify markers |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` | [x] complete — TASK-W2-01…06 |
| Live-verification contract | P15: `verification.live` applicable + script under `live_verify_dir` | [x] contract — `verify_jwt_cutover` (primary) + `verify_cross_programme_isolation` (steps / FILE-W2-28); scripts **not yet on disk** (co-ship in `/loop-spec`) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current |
| Impact-map repo scope | revision and scope digest match | [x] match — H3 `1`; H2 `sha256:53bb4c4f204888154afc40385c7e717f92d39f98463fcc6e97694e465a0ac9ef` |
| Product-spec H1–H3 spend freshness | live durable roots match citations | [x] current — H1 `sha256:e8c5103ea55a16823bf6a4e5c10bfc34be8e9f94efee12f6a3da69722fc3ea3e` |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script when P15 | [x] `.venv/bin/python -m tests.verify.verify_jwt_cutover` **and** `.venv/bin/python -m tests.verify.verify_cross_programme_isolation` |
| `ground_command` | resolved or N/A | [x] N/A — `/ground-spec` uses as-built + spec |
| Co-shipped live verify (P15) | FILE under `live_verify_dir` | [x] `tests/verify/verify_jwt_cutover.py` (FILE-W2-27); `tests/verify/verify_cross_programme_isolation.py` (FILE-W2-28) |
| Prior wave as-built row | `human_approved` (from prior `wave-acceptance`) | [x] W1 = **human_approved** — `Implementation-Status-INIT-GATEFLOW-014.md`; PR [#221](https://github.com/drivestream-lab/gateflow/pull/221) `wave-accepted` then MERGED `278de19` |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] exists — `Ground-Report-INIT-GATEFLOW-014-W1.md` (outcome pass; §Contracts produced) |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] N/A — W2 |

**Gate verdict:** PASS — ready for Forge `commit_workspace` (this checklist + plan cover fix onto bound head) then `/loop-spec`.

**Notes (non-blocking):**
- W2 board [#217](https://github.com/drivestream-lab/gateflow/issues/217) Status may still be Todo until optional in-progress action.
- `src/common/auth/dependencies.py` already exists with `require_role` (W1) — TASK-W2-01 is **modify** (+ `require_programme_scope`), not create-from-scratch.
- Human-owned Alembic for non-nullable `runs.tenant_id` (agents describe DDL; humans create/apply revisions).
- Plan §9 W1/W2 `live.covers` aligned this session so `verify_agent_catalogue` / future isolation markers are not disjoint from the wave live contract.

**Blocker registry:** none open.

---

### Contracts consumed (from prior Ground Report)

> Read `Ground-Report-INIT-GATEFLOW-014-W1.md` §Contracts produced.
> Confirmed against `source_roots` on W1-merged tip `278de19`.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Programme store | `ProgrammeRepository` / `ProgrammeSchema` — create / get_by_id / list / `get_pat` / update_lane_defaults | PAT, workspace, meta, lane_defaults | `ProgrammeReadModel` (no PAT on read model); PAT via `get_pat` | Ground-Report-W1 | [x] yes — W2 factory must use `get_pat`, not env/App install |
| Validate-then-create | `ProgrammeService.validate_then_create` | meta + workspace + PAT | `ProgrammeCreateResult` + child tenant | Ground-Report-W1 | [x] yes — fail-closed before TX; no agent_key |
| Attach tenant_admin | `ProgrammeService.attach_tenant_admin` | programme_id + credentials | TENANT_ADMIN identity + JWT with `tenant_id` | Ground-Report-W1 | [x] yes — live needs two Programmes + attached admins |
| Role gate | `require_role` in `src/common/auth/dependencies.py` | AuthContext | AuthContext or 403 `role_forbidden` | Ground-Report-W1 | [x] yes — expand with `require_programme_scope` |
| Agent catalogue | `PlatformAgentCatalogueService.resolve_effective_runner` | runner_id / lane + optional caller | `EffectiveRunner` | Ground-Report-W1 | [x] yes — SlotValidator/CursorAgentRunner catalogue-only |
| Meta-connection rename | `CatalogueConnectionService` / `catalogue_connection_routes` | existing `/tenants/{id}/programme/*` | unchanged wire | Ground-Report-W1 | [x] yes — still on tenant bearer; W2 auth swap target |

**W0 contracts still in force:** middleware JWT claim gate; login/seed — W2 shrinks product `public_paths` (today still allowlists Appendix-C prefixes in `src/app.py`).

**Unconfirmed contracts** (net-new this wave):
- `require_programme_scope` tenant/programme binding matrix
- Old-door refusal on every Appendix-C route after `public_paths` shrink
- `ForgeClientFactory.for_programme` / `ProgrammePatTokenProvider` (ADR-015 Option C)
- Non-nullable `RunSchema.tenant_id` + join-through-run_id scoping (ADR-016 Option C)
- Catalogue-only slot/cursor dispatch (remove `CursorAgentSettings.has_api_key()` from `slot_validator.py`)

---

### Must read

- [x] `AGENTS.md`
- [x] MDC (domain-filtered):
  - [x] `architecture.mdc` — JWT edge; `*_service` naming; no second verifier
  - [x] `http-api-conventions.mdc` — deps on routes; body models unchanged by auth swap
  - [x] `dependency-injection.mdc` — ForgeClient singleton → provider/factory; no `is_configured()` silent skip
  - [x] `infra-services.mdc` — ForgeClient / token provider lifecycle
  - [x] `repository-pattern.mdc` — RunSchema + RunRepository only touch ORM
  - [x] `database-migrations.mdc` — human Alembic for `runs.tenant_id`
  - [x] `fail-fast.mdc` — refuse wrong role / cross-programme before query
  - [x] `pydantic-schemas.mdc` / `strong-typing.mdc` — AuthContext / RoleType
  - [x] `testing-verify-flows.mdc` — co-ship P15 live scripts; human at wave-acceptance
  - [x] `logging-loguru.mdc`, `python-imports.mdc`
- [x] ADRs (keyword-matched):
  - [x] **ADR-014** (Accepted) — reuse AuthMiddleware; shrink `public_paths` to health/internal/webhooks (+ keep `/api/auth` for login); refuse old Bearers
  - [x] **ADR-015** (Accepted) — Option C `ForgeClientFactory` + Programme PAT provider; no App/env fallback
  - [x] **ADR-016** (Accepted) — Option C `RunSchema.tenant_id` non-nullable; dependents via `run_id`
  - [x] ADR-006 boundary preserved for SlotValidator (business-owned)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-014-gateflow.md` (REQ-04, REQ-23–26, REQ-28–33, REQ-41)
- [x] Plan wave section / §9: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-014.md` W2
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/217 — TASK projection:
  - [ ] TASK-W2-01 — REQ-23,24,29,30,31 — `dependencies.py` **modify** (+ `require_programme_scope`) — proof: `pytest tests/unit/test_auth_dependencies.py -v`
  - [ ] TASK-W2-02 — REQ-04,32,33 — depends TASK-W2-01 — swap programme-token/tenant-bearer on waves/runs/board/checkpoints/initiatives/metrics/forge/tenant/**catalogue_connection** routes; shrink `public_paths`; refuse old Bearers; co-ship `verify_jwt_cutover.py` — proof: flipped unit refusal cases + live cutover
  - [ ] TASK-W2-03 — REQ-25 — `ForgeClientFactory.for_programme` + `ProgrammePatTokenProvider`; DI singleton → provider — proof: `pytest tests/unit/test_forge_client_factory.py -v`
  - [ ] TASK-W2-04 — REQ-23,24,31 — depends TASK-W2-01 — `RunSchema.tenant_id` + scoped queries; co-ship `verify_cross_programme_isolation.py`; **human Alembic** — proof: tenant_scope unit + live isolation
  - [ ] TASK-W2-05 — REQ-26,41 — SlotValidator + CursorAgentRunner catalogue-only — proof: slot/cursor unit; zero `CursorAgentSettings.has_api_key()` in `slot_validator.py`
  - [ ] TASK-W2-06 — REQ-28 — depends TASK-W2-02 — inspect webhooks untouched; `/webhooks` stays public — proof: review

**DAG order for `/loop-spec`:**  
`(TASK-W2-01 → TASK-W2-02 → TASK-W2-06)` parallel with `(TASK-W2-01 → TASK-W2-04)` and independent `(TASK-W2-03)`, `(TASK-W2-05)` after W1 catalogue/PAT contracts.

---

### Governance alignment

- [x] Slice spec aligns with ADR-014 / ADR-015 / ADR-016 Accepted options
- [x] Plan TASK MDC notes and ADR notes for this wave reviewed
- [x] ADR-014, ADR-015, ADR-016 **Accepted** in `docs/specification/adr/`

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — only if contract wording drifts (prefer as-built + verify)
- [ ] `as-built/implementation-status.md` + `Implementation-Status-INIT-GATEFLOW-014.md` — W2 verification row
- [ ] `tests/README.md` — feature map rows for cutover + isolation verify
- [ ] Unit — auth deps matrix; old-door refusal flips; forge factory isolation; tenant_scope; slot/cursor catalogue path
- [ ] Live — co-ship `verify_jwt_cutover.py` + `verify_cross_programme_isolation.py` (human-run at `wave-acceptance`)
- [ ] DDL note for human Alembic — `runs.tenant_id` non-nullable (agents do not write `postgres_migrations/versions/`)
- [ ] ADR — no supersession expected this wave

---

### Must not

- [ ] Implement against ADR-014 with a second JWT verifier stack
- [ ] Leave dual-path acceptance (old Bearer **and** JWT) on product routes
- [ ] Fall back to App-installation / env PAT when Programme PAT missing (ADR-015)
- [ ] Keep `CursorAgentSettings.has_api_key()` in SlotValidator alongside catalogue (rewrite, not extend)
- [ ] Agent-authored Alembic under `postgres_migrations/versions/`
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | format/lint/types/layers | `make check` |
| Unit | role/tenant deps; old-door refusal; forge factory; tenant scope; catalogue-only dispatch | `make test` (+ task-scoped pytest from plan) |
| Live verify | Old doors refused; JWT happy path; cross-programme refused | `.venv/bin/python -m tests.verify.verify_jwt_cutover`; `.venv/bin/python -m tests.verify.verify_cross_programme_isolation` |
| Ground check | Assigned W2 REQs; boundaries | N/A — `/ground-spec` manual + as-built |

> P15 applies: both live FILEs must be co-shipped in `/loop-spec`. Agent does **not** run them as skill success. Human runs at `wave-acceptance`.

### Human wave-acceptance (after loop-spec + Draft PR)

- [ ] Run both `{verify_command}` scripts (API + worker up; two synthetic Programmes with distinct PATs from W1)
- [ ] Confirm old-door Bearer refused; JWT accepted; cross-programme read refused
- [ ] Signal accept with GitHub label `wave-accepted` on the tip
- [ ] Tip hygiene before Pass-2 Enter-at
- [ ] Cleanup synthetic Programmes/runs per plan live intent

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-014
- Issue: [#217](https://github.com/drivestream-lab/gateflow/issues/217)
- Spec path: `docs/specification/product/INIT-GATEFLOW-014-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_jwt_cutover` and `.venv/bin/python -m tests.verify.verify_cross_programme_isolation`
- ADRs in scope: ADR-014, ADR-015, ADR-016
- Wave head: bind `develop` @ `278de19` or cut `feature/INIT-GATEFLOW-014-w2-*` from it — not opened here

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — gates satisfied; W1 contracts confirmed; WorkManifest clean |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish `Pre-Implement-INIT-GATEFLOW-014-W2.md` + plan cover fix to bound `head_ref` |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR |

Recommend `/commit-workspace` after explicit authorization (bind `develop` or W2 feature branch first). Do not open the PR here.

---

### Merge order (if cross-module / cross-service)

N/A — single-repo wave. Soft dependency: W1 already merged to `develop` (`278de19`).

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-014-W2.md
  blockers: []
  signals:
    wave: W2
    initiative: INIT-GATEFLOW-014
    board_issue: "https://github.com/drivestream-lab/gateflow/issues/217"
    tasks:
      - TASK-W2-01
      - TASK-W2-02
      - TASK-W2-03
      - TASK-W2-04
      - TASK-W2-05
      - TASK-W2-06
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_jwt_cutover
    verify_command_secondary: .venv/bin/python -m tests.verify.verify_cross_programme_isolation
    ground_command: null
    prior_wave: W1
    prior_ground_report: docs/specification/reports/Ground-Report-INIT-GATEFLOW-014-W1.md
    prior_as_built: human_approved
    head_ref_hint: develop
    head_sha_hint: 278de19
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    head_ref: develop
```
