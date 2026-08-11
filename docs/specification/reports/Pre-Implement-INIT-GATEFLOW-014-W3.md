## Pre-implement — gateflow / W3 — Dead-door deletion + wipe cutover

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-014-W3.md` |
| Initiative | INIT-GATEFLOW-014 |
| Wave | W3 |
| Date | 2026-08-11 |
| Outcome | `pass` |
| Outcome reason | Prior W2 Ground Report + `human_approved`; WorkManifest contract clean; board #218 seeded under EPIC #214; P15 live scripts declared; W2 contracts confirmed in `source_roots`. |
| Wave head context | Bound by Forge/human context: `develop` @ `ca81b46` (includes W2 merge [#222](https://github.com/drivestream-lab/gateflow/pull/222) `b3cd8c6`) — not opened by this skill. No `feature/INIT-GATEFLOW-014-w3-*` yet; cut from `develop` before `/loop-spec` (or bind `develop` for checklist publish only). |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — `develop` @ `ca81b46`; not on `chore/*-spec-*` |
| Spec PR merged | Implementation plan on integration branch | [x] yes — PR [#212](https://github.com/drivestream-lab/gateflow/pull/212) MERGED; plan on tree |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — `spec-lgtm` on [#212](https://github.com/drivestream-lab/gateflow/pull/212); head `4df184c…`; merge `ae77433…` ancestor of HEAD |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present; waves are **sub-issues of the EPIC** | [x] seeded — EPIC [#214](https://github.com/drivestream-lab/gateflow/issues/214); W3 [#218](https://github.com/drivestream-lab/gateflow/issues/218) `parent`=#214; body lists TASK-W3-01…02 |
| WorkManifest contract | `prayog/v1` §9 passes `workmanifest_contract.py` | [x] pass — `prayog-skills/scripts/workmanifest_contract.py` → `WorkManifest contract passed.` |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` | [x] complete — TASK-W3-01, TASK-W3-02 |
| Live-verification contract | P15: `verification.live` applicable + script under `live_verify_dir` | [x] contract — `verify_dead_doors_deleted` (primary / WorkManifest `verify_command`) + `verify_wipe_cutover` (steps / FILE-W3-09); scripts **not yet on disk** (co-ship in `/loop-spec`) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current |
| Impact-map repo scope | revision and scope digest match | [x] match — H3 `1`; H2 `sha256:53bb4c4f204888154afc40385c7e717f92d39f98463fcc6e97694e465a0ac9ef` |
| Product-spec H1–H3 spend freshness | live durable roots match citations | [x] current — H1 `sha256:e8c5103ea55a16823bf6a4e5c10bfc34be8e9f94efee12f6a3da69722fc3ea3e`; meta PR [#35](https://github.com/drivestream-lab/prayog-meta/pull/35) head `3120e4e…` / `impact-map-lgtm` |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script when P15 | [x] `.venv/bin/python -m tests.verify.verify_dead_doors_deleted` **and** `.venv/bin/python -m tests.verify.verify_wipe_cutover` |
| `ground_command` | resolved or N/A | [x] N/A — `/ground-spec` uses as-built + spec |
| Co-shipped live verify (P15) | FILE under `live_verify_dir` | [x] `tests/verify/verify_dead_doors_deleted.py` (FILE-W3-08); `tests/verify/verify_wipe_cutover.py` (FILE-W3-09) |
| Prior wave as-built row | `human_approved` (from prior `wave-acceptance`) | [x] W2 = **human_approved** — `Implementation-Status-INIT-GATEFLOW-014.md`; PR [#222](https://github.com/drivestream-lab/gateflow/pull/222) `wave-accepted` then MERGED `b3cd8c6` |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] exists — `Ground-Report-INIT-GATEFLOW-014-W2.md` (outcome pass; §Contracts produced) |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] N/A — W3 |

**Gate verdict:** PASS — ready for Forge `commit_workspace` (this checklist onto bound head) then `/loop-spec`.

**Notes (non-blocking):**
- W3 board [#218](https://github.com/drivestream-lab/gateflow/issues/218) Status is Todo until optional in-progress action.
- W2 already **refused** old doors and swapped route deps; modules `programme_token.py` / `tenant_token.py` remain on disk with **zero** `src/api` route imports — W3 is **structural delete**, not a second refuse pass.
- `POST /api/v1/tenants` still exists as `platform_admin` JWT register (`tenant_routes.register_tenant`). Plan exit is **404/405 gone**, not “still 200 under JWT” — delete the open-register route entirely; flip/remove `test_register_200_with_platform_admin_jwt`.
- TDD PM-1 recorded ops context that a **full greenfield DB reset** may accompany cutover (human-owned). Product still implements plan TASK-W3-02 wipe service + mid-run 409 (REQ-46); do not invent wipe scope beyond plan/REQ.
- Teaching verify scripts still consume `PROGRAMME_SERVICE_TOKEN` — **W4** scope (REQ-36–38), not this wave.
- Conflict path for mid-run wipe: existing `ConflictError` → HTTP 409 (`src/exceptions/app_exceptions.py`).

**Blocker registry:** none open.

---

### Contracts consumed (from prior Ground Report)

> Read `Ground-Report-INIT-GATEFLOW-014-W2.md` §Contracts produced.
> Confirmed against `source_roots` on W2-merged tip (`b3cd8c6` ancestor of `ca81b46`).

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| JWT product edge | `AuthMiddleware` + shrunk `public_paths` in `src/app.py` | Gateflow JWT Bearer | AuthContext or 401 | Ground-Report-W2 | [x] yes — allowlist is health/internal/webhooks + `/api/auth`; old modules still present until this wave deletes |
| Role + programme scope | `require_role` / `require_programme_scope` / `require_tenant_resolved` | AuthContext + path tenant | AuthContext / TenantResolvedContext or 403 | Ground-Report-W2 | [x] yes — wipe admin route must use `require_role(PLATFORM_ADMIN)` |
| Tenant-attributed runs | `RunSchema.tenant_id` + `RunRepository.get_run` / `list_runs` / ACTIVE lookup | tenant_id at create; optional scope filter | RunModel; ACTIVE concurrency query | Ground-Report-W2 | [x] yes — wipe mid-run guard queries ACTIVE runs for programme/tenant |
| Per-programme ForgeClient | `ForgeClientFactory.for_programme` | programme PAT | ForgeClient | Ground-Report-W2 | [x] yes — not mutated this wave; wipe must not leave orphan forge paths |
| Catalogue-only agents | `SlotValidator` + `CursorAgentRunner` | catalogue credential | ok/fail | Ground-Report-W2 | [x] yes — out of W3 file scope |
| Webhooks unchanged | `github_routes` signature verify | HMAC payload | enqueue | Ground-Report-W2 | [x] yes — do not touch |

**Unconfirmed contracts** (net-new this wave):
- Structural absence of `programme_token` / `tenant_token` modules and every import (unit helpers included)
- `POST /api/v1/tenants` removed → 404/405 (not 401 refuse, not 200 under JWT)
- `ProgrammeWipeService` wipe semantics (which rows; named 409 when any ACTIVE run for that programme)
- Wipe HTTP surface on `programme_admin_routes` (path/body not frozen in prior Ground Report — follow plan + Pydantic models in `src/models/`)

---

### Must read

- [x] `AGENTS.md`
- [x] MDC (domain-filtered):
  - [x] `architecture.mdc` — route/service naming; JWT edge; no second verifier
  - [x] `http-api-conventions.mdc` — wipe mutation body model in `src/models/`
  - [x] `dependency-injection.mdc` — bind new `ProgrammeWipeService` in BusinessServicesModule + `_BUSINESS_SERVICE_TYPES`
  - [x] `fail-fast.mdc` — mid-run wipe → named Conflict/409, 0 wipe
  - [x] `repository-pattern.mdc` — wipe via repositories; no ORM in business/API
  - [x] `pydantic-schemas.mdc` / `strong-typing.mdc` — wipe request/response models
  - [x] `testing-verify-flows.mdc` — co-ship P15 live scripts; human at wave-acceptance
  - [x] `python-imports.mdc` — delete modules must clear all imports (including tests)
  - [x] skipped: `infra-services.mdc`, `database-migrations.mdc`, `logging-loguru.mdc` — no new infra client / no agent Alembic this wave
- [x] ADRs (keyword-matched):
  - [x] **ADR-014** (Accepted) — Consequences: structural removal of programme-token / tenant-bearer deps (this wave)
  - [x] ADR-015 / ADR-016 — consumed as prior contracts; no supersession expected
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-014-gateflow.md` (REQ-34, REQ-35, REQ-46)
- [x] Plan wave section / §9: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-014.md` W3
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/218 — TASK projection:
  - [ ] TASK-W3-01 — implements REQ-34 — depends_on: [] (plan body: TASK-W2-02) — files: delete `programme_token.py` / `tenant_token.py`; modify `tenant_routes.py`; create `verify_dead_doors_deleted.py` — exit: `make check` zero refs; `POST /api/v1/tenants` → 404/405 — proof: `make check && pytest tests/unit/test_tenant_routes.py -k register -v`
  - [ ] TASK-W3-02 — implements REQ-35, REQ-46 — depends_on: [] (plan body: TASK-W2-04) — files: create `programme_wipe_service.py` + unit; modify `programme_admin_routes.py`; create `verify_wipe_cutover.py` — exit: ACTIVE run → 409 named, 0 wipe — proof: `pytest tests/unit/test_programme_wipe_service.py -v`

**DAG order for `/loop-spec`:**  
`TASK-W3-01` and `TASK-W3-02` are independent in §9 `depends_on: []`; prefer delete doors first so wipe live smoke runs against a tree with no dead modules. Both must co-ship their live FILEs.

---

### Governance alignment

- [x] Slice spec aligns with ADR-014 structural-removal Consequences
- [x] Plan TASK MDC notes (`fail-fast.mdc`) and ADR notes (ADR-014) reviewed
- [x] ADR-014 **Accepted** in `docs/specification/adr/`; ADR-015/016 Accepted and in force from W2

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — only if contract wording drifts (prefer as-built + verify)
- [ ] `as-built/implementation-status.md` + `Implementation-Status-INIT-GATEFLOW-014.md` — W3 verification row
- [ ] `tests/README.md` — feature map rows for dead-door deletion + wipe cutover
- [ ] Unit — register route gone; wipe idle success + ACTIVE 409; delete/adjust `test_tenant_token.py` / any module that imported deleted files
- [ ] Live — co-ship `verify_dead_doors_deleted.py` + `verify_wipe_cutover.py` (human-run at `wave-acceptance`)
- [ ] DI — register `ProgrammeWipeService` singleton
- [ ] ADR — no supersession expected this wave

---

### Must not

- [ ] Leave `programme_token.py` / `tenant_token.py` on disk “for later” after refuse already shipped
- [ ] Keep `POST /tenants` as a JWT-only register and call that “deleted” (exit requires 404/405)
- [ ] Wipe while ACTIVE run exists (must 409 named; 0 rows changed)
- [ ] Rewrite W4 teaching verify scripts in this wave (PROGRAMME_SERVICE_TOKEN inventory stays until W4)
- [ ] Agent-authored Alembic under `postgres_migrations/versions/`
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | format/lint/types/layers; zero refs to deleted modules | `make check` |
| Unit | register route gone; wipe idle + mid-run 409 | `make test` (+ task-scoped pytest from plan) |
| Live verify | Old-door routes 404/405; wipe succeeds when idle, rejects when ACTIVE | `.venv/bin/python -m tests.verify.verify_dead_doors_deleted`; `.venv/bin/python -m tests.verify.verify_wipe_cutover` |
| Ground check | Assigned W3 REQs; boundaries | N/A — `/ground-spec` manual + as-built |

> P15 applies: both live FILEs must be co-shipped in `/loop-spec`. Agent does **not** run them as skill success. Human runs at `wave-acceptance`.

### Human wave-acceptance (after loop-spec + Draft PR)

- [ ] Run both `{verify_command}` scripts (API up; synthetic 012/013-shaped lab tenant; synthetic ACTIVE run for mid-run reject)
- [ ] Confirm old-door surfaces return 404/405 (gone, not merely 401); wipe idle OK; wipe mid-run 409
- [ ] Signal accept with GitHub label `wave-accepted` on the tip
- [ ] Tip hygiene before Pass-2 Enter-at
- [ ] Cleanup: none beyond what wipe itself performs (per plan live intent)

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-014
- Issue: [#218](https://github.com/drivestream-lab/gateflow/issues/218)
- Spec path: `docs/specification/product/INIT-GATEFLOW-014-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_dead_doors_deleted` and `.venv/bin/python -m tests.verify.verify_wipe_cutover`
- ADRs in scope: ADR-014 (primary); ADR-015/016 consumed
- Wave head: bind `develop` @ `ca81b46` or cut `feature/INIT-GATEFLOW-014-w3-*` from it — not opened here

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — gates satisfied; W2 contracts confirmed; WorkManifest clean |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish `Pre-Implement-INIT-GATEFLOW-014-W3.md` to bound `head_ref` |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR |

Recommend `/commit-workspace` after explicit authorization (bind `develop` or W3 feature branch first). Do not open the PR here.

---

### Merge order (if cross-module / cross-service)

N/A — single-repo wave. Soft dependency: W2 already merged to `develop` (`b3cd8c6`).

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-014-W3.md
  blockers: []
  signals:
    wave: W3
    initiative: INIT-GATEFLOW-014
    board_issue: "https://github.com/drivestream-lab/gateflow/issues/218"
    tasks:
      - TASK-W3-01
      - TASK-W3-02
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_dead_doors_deleted
    verify_command_secondary: .venv/bin/python -m tests.verify.verify_wipe_cutover
    ground_command: null
    prior_wave: W2
    prior_ground_report: docs/specification/reports/Ground-Report-INIT-GATEFLOW-014-W2.md
    prior_as_built: human_approved
    head_ref_hint: develop
    head_sha_hint: ca81b46
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    head_ref: develop
```
