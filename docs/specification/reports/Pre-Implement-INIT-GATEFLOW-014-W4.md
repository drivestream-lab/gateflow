## Pre-implement — gateflow / W4 — Prove absence + rewrite teaching surfaces

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-014-W4.md` |
| Initiative | INIT-GATEFLOW-014 |
| Wave | W4 |
| Date | 2026-08-11 |
| Outcome | `pass` |
| Outcome reason | Prior W3 Ground Report + `human_approved`; WorkManifest contract clean; board #219 seeded under EPIC #214; P15 live scripts declared (`verify_all` + `verify_old_doors_refused`); W3 contracts confirmed on `develop`. |
| Wave head context | Bound by Forge/human context: `develop` @ `6794f21` (W3 merge [#224](https://github.com/drivestream-lab/gateflow/pull/224)) — not opened by this skill. No `feature/INIT-GATEFLOW-014-w4-*` yet; cut from `develop` before `/loop-spec` (or bind `develop` for checklist publish only). |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — `develop` @ `6794f21`; not on `chore/*-spec-*` |
| Spec PR merged | Implementation plan on integration branch | [x] yes — PR [#212](https://github.com/drivestream-lab/gateflow/pull/212) MERGED; plan on tree |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — `spec-lgtm` on [#212](https://github.com/drivestream-lab/gateflow/pull/212); merge ancestor of HEAD |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present; waves are **sub-issues of the EPIC** | [x] seeded — EPIC [#214](https://github.com/drivestream-lab/gateflow/issues/214); W4 [#219](https://github.com/drivestream-lab/gateflow/issues/219) `parent`=#214; body lists TASK-W4-01…03 |
| WorkManifest contract | `prayog/v1` §9 passes `workmanifest_contract.py` | [x] pass |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` | [x] complete — TASK-W4-01…03 |
| Live-verification contract | P15: `verification.live` applicable + script under `live_verify_dir` | [x] contract — primary `verify_all`; steps also `verify_old_doors_refused` (FILE-W4-07 — **not yet on disk**, co-ship in `/loop-spec`) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current |
| Impact-map repo scope | revision and scope digest match | [x] match — H3 `1`; H2 `sha256:53bb4c4f204888154afc40385c7e717f92d39f98463fcc6e97694e465a0ac9ef` |
| Product-spec H1–H3 spend freshness | live durable roots match citations | [x] current — H1 `sha256:e8c5103ea55a16823bf6a4e5c10bfc34be8e9f94efee12f6a3da69722fc3ea3e` |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script when P15 | [x] `.venv/bin/python -m tests.verify.verify_all` **and** `.venv/bin/python -m tests.verify.verify_old_doors_refused` |
| `ground_command` | resolved or N/A | [x] N/A — `/ground-spec` uses as-built + spec |
| Co-shipped live verify (P15) | FILE under `live_verify_dir` | [x] extend listed verify scripts (TASK-W4-01); create `tests/verify/verify_old_doors_refused.py` (FILE-W4-07) |
| Prior wave as-built row | `human_approved` (from prior `wave-acceptance`) | [x] W3 = **human_approved** — `Implementation-Status-INIT-GATEFLOW-014.md`; PR [#224](https://github.com/drivestream-lab/gateflow/pull/224) `wave-accepted` then MERGED `6794f21` |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] exists — `Ground-Report-INIT-GATEFLOW-014-W3.md` (outcome pass; §Contracts produced) |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] N/A — W4 |

**Gate verdict:** PASS — ready for Forge `commit_workspace` (this checklist onto bound head) then `/loop-spec`.

**Notes (non-blocking):**
- W4 board [#219](https://github.com/drivestream-lab/gateflow/issues/219) Status may still be Todo until optional in-progress action.
- TASK-W4-01 `files[]` lists six scripts, but exit proof requires **zero** `PROGRAMME_SERVICE_TOKEN` matches under **all** of `tests/verify/`. Inventory today still hits ~30 scripts (beyond the six). Plan prose says rewrite listed scripts **and remaining** consumers — treat remaining token/bearer consumers as **in-scope for exit**, even when not every path appears in §9 `files[]` (RISK-05: `verify_all` is the gate).
- FILE-W4-09 said *create* `Implementation-Status-INIT-GATEFLOW-014.md` — file **already exists** from W0–W3. TASK-W4-03 = complete/update matrix + JWT-only teaching examples, not greenfield create.
- Initiative exit gate (PRD Hard exit): JWT happy path via `verify_all` **and** old-door refusal via `verify_old_doors_refused` — both live at wave-acceptance.
- Stop condition: any script still succeeding with an old-door credential → fail wave.

**Blocker registry:** none open.

---

### Contracts consumed (from prior Ground Report)

> Read `Ground-Report-INIT-GATEFLOW-014-W3.md` §Contracts produced.
> Confirmed against `source_roots` / `tests/**` on W3-merged tip `6794f21`.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Dead doors removed | deleted token modules; no `POST /api/v1/tenants` | any caller | 404/405 with JWT; middleware 401 without | Ground-Report-W3 | [x] yes — modules absent; register route gone |
| Programme wipe | `POST /api/v1/programmes/{id}/wipe` | platform_admin JWT | wipe result or 409 | Ground-Report-W3 | [x] yes — available if teaching/smoke needs cutover; not primary W4 rewrite target |
| JWT product edge + role scope | middleware + `require_role` / programme scope | Gateflow JWT | AuthContext or 401/403 | Ground-Report-W2 (still in force) | [x] yes — all rewrite scripts must mint/login JWT |
| Per-programme ForgeClient + catalogue agents | factory / SlotValidator | programme PAT / catalogue credential | forge/agent ops | Ground-Report-W2 | [x] yes — teaching must not instruct env Cursor as product auth |
| Login / seed platform_admin | `POST /api/auth/login` + seed script | credentials | JWT | Ground-Report-W0 | [x] yes — verify helpers already used by W0–W3 scripts |

**Unconfirmed contracts** (net-new this wave):
- Consolidated `verify_old_doors_refused` covering programme token → 401, tenant bearer → 401, open register → 404/405 in one script
- Full `tests/verify/` grepped clean of `PROGRAMME_SERVICE_TOKEN` / old tenant-bearer client patterns after rewrite
- `tests/README.md` Appendix-C examples JWT-only (no old-door invocation copy)

---

### Must read

- [x] `AGENTS.md`
- [x] MDC (domain-filtered):
  - [x] `testing-verify-flows.mdc` — verify vs pytest; feature map; live smoke ownership
  - [x] `architecture.mdc` — teaching surfaces stay outside `src/` product edge
  - [x] `http-api-conventions.mdc` — scripts call frozen routes correctly under JWT
  - [x] `logging-loguru.mdc` — verify scripts print `[OK]`/`[ERROR]`; no secret logging
  - [x] `fail-fast.mdc` — negative-path scripts must fail closed on unexpected accept
  - [x] skipped: `repository-pattern.mdc`, `database-migrations.mdc`, `infra-services.mdc` — no product schema/infra change this wave
- [x] ADRs (keyword-matched):
  - [x] **ADR-014** (Accepted) — JWT-only product edge; teaching must not revive programme-token / tenant-bearer zones
  - [x] ADR-015 / ADR-016 — teaching should describe per-programme PAT + tenant-scoped runs (no App/env PAT product story)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-014-gateflow.md` (REQ-36, REQ-37, REQ-38)
- [x] Plan wave section / §9: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-014.md` W4
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/219 — TASK projection:
  - [ ] TASK-W4-01 — implements REQ-36, REQ-38 — depends_on: [] — rewrite listed verify scripts (+ remaining token consumers for exit grep) — proof: `verify_all` exit 0; zero `PROGRAMME_SERVICE_TOKEN` in `tests/verify/`
  - [ ] TASK-W4-02 — implements REQ-37 — depends_on: [TASK-W4-01] — create `verify_old_doors_refused.py` — proof: script exit 0
  - [ ] TASK-W4-03 — implements REQ-38 — depends_on: [TASK-W4-02] — update `tests/README.md` + as-built detail/index — proof: review (JWT-only teaching; no old-door examples)

**DAG order for `/loop-spec`:**  
`TASK-W4-01` → `TASK-W4-02` → `TASK-W4-03` (strict).

---

### Governance alignment

- [x] Slice spec aligns with ADR-014 (JWT-only teaching / prove absence)
- [x] Plan TASK MDC/ADR notes for this wave reviewed (N/A columns — teaching/verify only)
- [x] No new ADR expected; no supersession this wave

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — only if contract wording drifts (prefer as-built + verify)
- [ ] `as-built/Implementation-Status-INIT-GATEFLOW-014.md` — complete W4 capability matrix (TASK-W4-03)
- [ ] `as-built/implementation-status.md` — W4 index/status row
- [ ] `tests/README.md` — JWT-only invocation examples for Appendix-C / feature map
- [ ] Live — rewrite verify consumers; co-ship `verify_old_doors_refused.py` (human-run at `wave-acceptance`)
- [ ] Unit — typically light this wave (smoke-owned REQs); add only if rewrite introduces helper logic worth unit coverage
- [ ] ADR — no supersession expected

---

### Must not

- [ ] Leave any `tests/verify/` script authenticating with `PROGRAMME_SERVICE_TOKEN` or tenant shared-secret bearer
- [ ] Instruct env `CURSOR_API_KEY` as product-run auth in teaching docs/scripts
- [ ] Dual-path “JWT or old door” helpers
- [ ] Claim initiative exit without both `verify_all` (JWT happy) and `verify_old_doors_refused` (negative)
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | format/lint/types/layers | `make check` |
| Unit | helper logic if any; otherwise suite still green | `make test` |
| Live verify | JWT-only happy path across verify suite; consolidated old-door refusal | `.venv/bin/python -m tests.verify.verify_all`; `.venv/bin/python -m tests.verify.verify_old_doors_refused` |
| Ground check | Assigned W4 REQs; boundaries | N/A — `/ground-spec` manual + as-built |

> P15 applies: extend existing live FILEs + co-ship `verify_old_doors_refused.py`. Agent does **not** run smoke as skill success. Human runs at `wave-acceptance`.

### Human wave-acceptance (after loop-spec + Draft PR)

- [ ] Run `verify_all` (API + worker up; Accepted Programme + tenant_admin fixtures)
- [ ] Run `verify_old_doors_refused` (programme token → 401; tenant bearer → 401; `POST /tenants` → 404/405)
- [ ] Confirm `rg PROGRAMME_SERVICE_TOKEN tests/verify` is empty
- [ ] Signal accept with GitHub label `wave-accepted` on the tip
- [ ] Tip hygiene before Pass-2 Enter-at
- [ ] Cleanup synthetic fixtures per plan live intent

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-014
- Issue: [#219](https://github.com/drivestream-lab/gateflow/issues/219)
- Spec path: `docs/specification/product/INIT-GATEFLOW-014-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_all` and `.venv/bin/python -m tests.verify.verify_old_doors_refused`
- ADRs in scope: ADR-014 (primary); ADR-015/016 teaching alignment
- Wave head: bind `develop` @ `6794f21` or cut `feature/INIT-GATEFLOW-014-w4-*` from it — not opened here

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — gates satisfied; W3 contracts confirmed; WorkManifest clean |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish `Pre-Implement-INIT-GATEFLOW-014-W4.md` to bound `head_ref` |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR |

Recommend `/commit-workspace` after explicit authorization (bind `develop` or W4 feature branch first). Do not open the PR here.

---

### Merge order (if cross-module / cross-service)

N/A — single-repo wave. Soft dependency: W3 already merged to `develop` (`6794f21`). Last eng wave for INIT-GATEFLOW-014 on gateflow — after accept/closeout, initiative closure may follow.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-014-W4.md
  blockers: []
  signals:
    wave: W4
    initiative: INIT-GATEFLOW-014
    board_issue: "https://github.com/drivestream-lab/gateflow/issues/219"
    tasks:
      - TASK-W4-01
      - TASK-W4-02
      - TASK-W4-03
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_all
    verify_command_secondary: .venv/bin/python -m tests.verify.verify_old_doors_refused
    ground_command: null
    prior_wave: W3
    prior_ground_report: docs/specification/reports/Ground-Report-INIT-GATEFLOW-014-W3.md
    prior_as_built: human_approved
    head_ref_hint: develop
    head_sha_hint: 6794f21
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    head_ref: develop
```
