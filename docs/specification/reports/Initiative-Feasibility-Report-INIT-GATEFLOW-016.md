# Feasibility report — INIT-GATEFLOW-016

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-016 |
| Spec | `docs/specification/product/INIT-GATEFLOW-016-gateflow.md` |
| PRD digest | `sha256:2ee19c297b4f948c9f3fbb29d5b45e1e5db9e32fce4a21780915872b3640947a` (live meta tip; **not cited in spec header**) |
| Impact map / revision | `prd/reports/Impact-Map-INIT-GATEFLOW-016.md` / `1` |
| Repo scope digest | **none for gateflow** — map §2 affected repo is `gateflow-ops` only (`sha256:4daa0360b2c895fca619c93bc2bf765c6cca1a0c05d12e0cae9331bead47df08`). Gateflow is §4 transitive **monitor**, not a spec-to-create target |
| Approved meta PR head | label `impact-map-lgtm` on [prayog-meta#41](https://github.com/drivestream-lab/prayog-meta/pull/41); current head `5422e0f28ce8cb6b0b9f936b5df87afe280d4957`. Review body cites `meta_pr_head_sha: 003e4228d2a66ccb5305305c7103bef95824bc70` (first commit; second commit is harness pin, not PRD) |
| Impact-map approval | [@0xbeefdead APPROVED](https://github.com/drivestream-lab/prayog-meta/pull/41) 2026-08-12T10:57:35Z, `map_revision: 1`, `prd_digest: sha256:2ee19c297b4f948c9f3fbb29d5b45e1e5db9e32fce4a21780915872b3640947a`, label `impact-map-lgtm` |
| Source freshness | **STALE** — spec H1–H3 / G1 are `pending`; live Gate 1 exists and assigns a **different product and a different primary repo**. Map ripple for this repo: **hold** (not a build target) |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-13 |
| Branch | `chore/INIT-GATEFLOW-016-spec-gateflow` — spec PR [#242](https://github.com/drivestream-lab/gateflow/pull/242) **MERGED** to `develop` @ `d5c59ef` as a pre-Gate-1 outline (plus unrelated catalogue JSONB) |
| Initiative segment | `INIT-GATEFLOW-016` |
| Status | Draft |
| Review deadline | 2026-08-18 |
| Deciders | PM: programme PM (meta PR #41) · Domain SME: @drivestream-lab/prayog-pe-team |

## Summary

This repo **must not implement** the local `INIT-GATEFLOW-016-gateflow.md` slice as INIT-GATEFLOW-016. Gate 1 (meta PR #41, `impact-map-lgtm`) approved **Gateflow Mission Control** for **`gateflow-ops`**, CAP-A–G / REQ-01–REQ-31, with **zero gateflow backend work**. The in-repo spec is a **person directory + N:N programme membership + session select** product (CAP-01–04 / REQ-01–REQ-29) written before that PRD, with H1–H3 / G1 still `pending`. Feasibility stops on authority drift. Next is `/spec-draft` to withdraw or replace the gateflow file so it does not claim this initiative.

**Findings:** 4 total (2 Critical, 1 Should fix, 0 Verify, 1 Gap)

### Derived counts (lane × severity)

| Lane | Blocking open | Non-blocking open | Resolved |
|------|---------------|-------------------|----------|
| PM | 1 | 1 | 0 |
| PE / ADR | 0 | 1 | 0 |
| Domain | 0 | 0 | 0 |
| Auto-fix | 1 | 0 | 0 |

| Severity | Unresolved count |
|----------|------------------|
| Critical | 2 |
| Should fix | 1 |
| Verify / Gap (informational) | 1 |

### Selected workflow outcome

| Field | Value |
|-------|-------|
| Outcome | `stale` |
| Rationale | First matching lane-to-outcome rule: product-spec H1–H3 / G1 / tip authority drift vs live approved PRD + impact map (and this repo is not an affected build target). |
| Next (from workflow) | `spec-draft` |

Informational observations alone do **not** select `findings`. Unresolved blocking PE/ADR → `findings`; blocking PM/domain → `needs-input`. Stale takes precedence over those rows.

**Impact-map revision handling:** **hold** for `drivestream-lab/gateflow` as a delivery target. Map §2 `Spec to create` is `INIT-GATEFLOW-016-gateflow-ops.md`. Map §4 disposition for gateflow is **monitor — not a build target**. Do not fill this spec’s header with Mission Control H1–H3 and keep the person-directory REQs.

## ADR pass (before T2)

| ADR id | Domain matched | Status | Read? |
|--------|----------------|--------|-------|
| ADR-014 | JWT / product edge / programme bind | Accepted | yes — revisit trigger matches the **local unauthorized** N:N spec, not the approved Mission Control PRD |
| ADR-002 | Edge trust model | Accepted (superseded by 014) | title only |
| ADR-011 | Tenant-scoped bearer | Accepted (superseded by 014) | title only |
| ADR-016 | Tenant-scoped product authorization | Accepted | title — programme-scoped routes stay 1:1 JWT `tenant_id` |
| ADR-004 | Programme config authority | Accepted | skipped body — not touched by approved 016 |
| ADR-012 | Catalogue discovery | Accepted | skipped — catalogue connect is consumed by ops, unchanged |
| ADR-001, 003, 005–010, 013, 015, 017, 018 | runtime, slots, forge, waves, metrics | Accepted | skipped — approved 016 requests no gateflow change |

## MDC pass (before T2)

| MDC file | Domain | Read / skipped |
|----------|--------|----------------|
| `spec-driven-development.mdc` | truth hierarchy / as-built | read |
| `architecture.mdc` | layers, JWT edge, `src/models` | read |
| `http-api-conventions.mdc` | body vs query | read |
| `pydantic-schemas.mdc` | models / enums | read |
| `repository-pattern.mdc` | ORM isolation | read |
| `dependency-injection.mdc` | services | skipped — no implementation this hop |
| `database-migrations.mdc` | Alembic | skipped — no schema work this hop |
| `testing-verify-flows.mdc` | verify vs unit | read |
| `fail-fast.mdc` | no silent fallback | skipped — no impl |
| `logging-loguru.mdc` | logs | skipped — no impl |
| `infra-services.mdc` | outbound HTTP | skipped — approved 016 does not add clients here |
| `python-imports.mdc`, `python-tooling.mdc`, `strong-typing.mdc`, `code-guidelines-index.mdc` | tooling / index | skipped — no impl |

## Baseline snapshot (F1)

| Area | Current state | Evidence |
|------|---------------|----------|
| Unit tests | `tests/unit/` — 70+ modules; identity/programme: `test_user_identity_repository`, `test_auth_identity_service`, `test_programme_service`, `test_programme_admin_routes`, `test_programme_onboarding` | `tests/unit/*.py`; `make test` |
| Live verify | `tests/verify/` — 40+ scripts; attach/login: `verify_jwt_login`, `verify_programme_onboarding`, `verify_auth_bootstrap`, `verify_cross_programme_isolation` | `tests/verify/*.py`; `tests/README.md` |
| As-built | Attach is 1:1 create+JWT; login is token-only; no person `display_name`/`status`; no `/me`; no select-programme | `implementation-status.md` rows “Attach tenant_admin”, “Login API”, “User identity persist” |
| Toolchain | `make check` (black, ruff, pyright, import-linter); CI placeholder | as-built Testing harness |
| Codegraph | MCP `user-prayog-fleet-cbm` project `data-repos-prayog-gateflow` | `ProgrammeService.attach_tenant_admin` L177; route L90 |

## Traceability matrix

Approved Gate 1 slice (this repo): **no CAP/REQ to implement**. Local file REQs are recorded only to prove collision, not as a build map.

| Spec REQ / wave | Spec claim | Code evidence | Unit | Verify | Status |
|-----------------|------------|---------------|------|--------|--------|
| **Map §2 / §4** | gateflow-ops builds Mission Control; gateflow **unchanged** (D2) | Live APIs already exist for ops consumption (`tenant_routes`, catalogue, waves, runs, forge, checkpoints, board, initiatives, metrics) | existing | existing | **approved scope: no work** |
| Local REQ-01–05 / W0–W1 | Person directory create/list/patch/password/status | `UserIdentitySchema` has identifier, hash, role, optional `tenant_id` only — no `display_name`/`status` | `test_user_identity_repository` (014 shape) | none for directory | **not in approved scope** / gap vs local file |
| Local REQ-06–13 / W1 | N:N attach of existing `user_id`; no JWT on map; delete combined door | `POST /programmes/{id}/tenant-admins` + `AttachTenantAdminRequest` (identifier+password) + `AttachTenantAdminResponse.access_token`; `credential_conflict` on second programme | `test_programme_service` | `verify_programme_onboarding` | **not in approved scope** / would **break** live 014 attach |
| Local REQ-14–20 / W2 | Login snapshot, `/me`, 0/1/N session, select-programme | `LoginResponse` is `{access_token, token_type}`; JWT `tenant_id` 1:1; no select route | `test_auth_identity_service` | `verify_jwt_login` | **not in approved scope** |
| Local REQ-21–29 / W0–W3 | Role split, backfill, wipe memberships, verify rewrite | Wipe exists (`wipe_programme`); membership table does not | `test_programme_wipe_service` | `verify_wipe_cutover` | **not in approved scope** |
| PRD CAP-A–G / REQ-01–31 | Ops UI/BFF against **existing** gateflow routes | This repo is provider, not consumer | n/a here | n/a here | **belongs in gateflow-ops spec** |

## ADR traceability (F13)

| Spec REQ / wave | Relevant ADR(s) | Status | Code evidence | Finding |
|-----------------|-----------------|--------|----------------|---------|
| Approved map D2 / CTR-01–07 | ADR-014, ADR-016 | aligned | `src/api/v1/programme_admin_routes.py`, `src/common/auth/` — no change requested | N/A — freeze existing JWT + tenant scope |
| Local REQ-08 / REQ-18 / W1–W2 (unauthorized file) | ADR-014 revisit: “finer-grained than role + programme binding”; NEW-ADR if a **future** INIT owns this product | missing ADR **if that product is later approved** | `ProgrammeService.attach_tenant_admin`; `AuthIdentityService.login`; `LoginResponse` | `ALTERNATIVE: keep JWT as a single tenant_id bind reminted at select-programme vs encode a membership list on the token vs snapshot-only memberships with no programme claim until bind` |

> The ALTERNATIVE row is **not** a blocking PE finding for INIT-GATEFLOW-016. The approved slice does not introduce N:N session bind. Do not send this hop to `/spec-technical-review`.

## Governance findings (F13–F14)

| ID | Check | Spec quote | Governing doc | Finding |
|----|-------|------------|---------------|---------|
| FF-01 | F1 freshness | "PRD digest (H1) \| **pending** — Gate 1 not run" | `artifact-write-contract.md` H1–H3 / G1 | Spec header does not cite live PRD digest / map revision 1 / G1 head |
| FF-02 | F5 / F10 | "This INIT, **gateflow only**, replaces that attach contract" | Impact map §2–§4; PRD “Zero new gateflow backend work” | Local product and primary repo contradict Gate 1 |
| FF-04 | F13 | "which ADR supersedes ADR-014 are **deferred to feasibility / technical review** (Q-2, Q-3)" | ADR-014 revisit triggers | `ALTERNATIVE: keep JWT as a single tenant_id bind reminted at select-programme vs encode a membership list on the token vs snapshot-only memberships with no programme claim until bind` — Gap only; future INIT |

## Findings by severity

### Critical

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-01 | F1 | Spec H1–H3 / G1 are `pending` while Gate 1 is live (`impact-map-lgtm`, map revision 1, PRD digest `sha256:2ee19c297b4f948c9f3fbb29d5b45e1e5db9e32fce4a21780915872b3640947a`). | Spec header rows PRD / H1 / G1 / H2 / H3; [prayog-meta#41](https://github.com/drivestream-lab/prayog-meta/pull/41); impact map frontmatter |
| FF-02 | F2 / F5 / F9 / F10 | Local spec is person-directory N:N membership for **gateflow**. Approved PRD is Mission Control for **gateflow-ops**, CAP-A–G / REQ-01–31, **zero gateflow diff**. Same INIT id, incompatible products. CAP/REQ numbers collide. | Spec overview + REQ table; PRD document control “Primary repo: gateflow-ops”; map §2 spec-to-create `INIT-GATEFLOW-016-gateflow-ops.md`; map §4 “No code or contract change is requested of `gateflow`” |

### Should fix

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-03 | F6 | Pre-Gate-1 outline (and catalogue JSONB) already merged to `develop` via PR #242 under this INIT id. `docs/specification/README.md` still calls 016 a local Gate-1-pending draft. | [gateflow#242](https://github.com/drivestream-lab/gateflow/pull/242) MERGED; `docs/specification/README.md` line “Local spec draft (016, Gate 1 pending)” |

## Impact surface

| Wave / area | Likely files/modules | Test touch |
|-------------|----------------------|------------|
| **Approved 016 (this repo)** | **none** — freeze existing public API for ops | none new |
| Local unauthorized W0–W3 (do **not** build under this INIT) | Would have been `user_identity_schema`, membership persistence, `programme_admin_routes.attach_tenant_admin`, `auth_identity_service`, login/`/me`/select | `test_programme_*`, `verify_jwt_login`, `verify_programme_onboarding` rewrite |

## Risks & assumptions

| ID | Risk / assumption | Mitigation |
|----|-------------------|------------|
| R-1 | Walking `/spec-technical-review` on the local file would design N:N JWT against the wrong PRD | Outcome `stale` → `spec-draft` only |
| R-2 | Copying Mission Control H1–H3 into the person-directory spec would fake freshness | Spec-draft must **not** bind those digests to the current REQ table |
| R-3 | Person-directory chat decisions (2026-08-13) are real product intent **without** an INIT id | PM files a **new** initiative; do not reuse 016 |
| A-1 | Map IM-01 (freeze gateflow APIs during ops delivery) remains a monitoring commitment | No backend work in this repo for 016 |
| A-2 | Meta review body SHA `003e4228` ≠ current head `5422e0f` (harness commit). Label still `impact-map-lgtm`. Recorded; not used to invent a new G1 | Meta hygiene; does not restore this spec’s citations |

## Recommended spec edits

- **Do not** fill H1–H3 / G1 on `INIT-GATEFLOW-016-gateflow.md` from meta #41 while the body remains person-directory / N:N attach.
- `/spec-draft` should **withdraw** this file as a gateflow delivery spec (replace with a short “not in map — monitor only / see gateflow-ops” pointer, or delete and drop the README row).
- Person-directory + N:N membership + session select needs a **new initiative id** and its own PRD + impact map (gateflow **affected**, not transitive).
- Do not mix that product into INIT-GATEFLOW-016 waves in this repo.

---

## Open items by lane

| ID | Lane | Question / item | Blocking | Owner | Status | Required by | Default if deferred | Evidence | Resolution reference |
|----|------|-----------------|----------|-------|--------|-------------|---------------------|----------|----------------------|
| FF-01 | PE | Spec H1–H3 / G1 pending vs live Gate 1 | yes | spec-draft | open | spec-draft | none — cannot defer freshness | spec header; meta #41 | pending |
| FF-02 | PM | INIT-GATEFLOW-016 id collision: Mission Control (approved) vs person directory (local file) | yes | PM | open | spec merge | none — cannot implement both under one id | PRD primary repo gateflow-ops vs spec “gateflow only” | pending |
| FF-03 | auto-fix | Withdraw/replace merged pre-Gate-1 `INIT-GATEFLOW-016-gateflow.md` + README pointer | yes | spec-draft | open | spec-draft | none if 016 stays Mission Control | PR #242; README | pending |
| FF-04 | PE | If a **future** INIT owns N:N membership, ADR-014 successor (JWT bind vs remint vs snapshot-only) | no | PE | open | that INIT’s technical review | keep 014 1:1 `tenant_id` until a new INIT is approved | ADR-014 revisit; local Q-2 | pending |
| IM-01 | PM | Confirm gateflow consumed APIs stay frozen during gateflow-ops 016 delivery | no | PE/PM | open | ops W0 | Proceed — no gateflow change planned (map default) | Impact map §10 IM-01 | pending |

### PM questions (product scope, UX, priority)

#### Blocking — must resolve before spec merge

1. **FF-02:** INIT-GATEFLOW-016 on meta is Gateflow Mission Control for `gateflow-ops` (zero gateflow backend). The gateflow spec file describes a breaking person-directory / N:N membership / session-select API. Which product keeps id 016? (Gate 1 already chose Mission Control.) File a **new** PRD for the directory work if it is still wanted.

#### Defer — can proceed with documented assumption

1. **IM-01:** Treat gateflow’s existing route groups as frozen for the duration of `gateflow-ops` Mission Control delivery (map default).

### PE questions (engineering decisions — resolved by `/spec-technical-review`)

> Not for this hop. Do **not** run `/spec-technical-review` until spec-draft aligns this repo with Gate 1 (likely: no TDD in gateflow for 016).

#### Blocking for implementation plan

1. None for approved INIT-GATEFLOW-016 in this repo.

#### Defer with default

1. **FF-04:** JWT representation of zero / one / N memberships — only if a future INIT owns that product. Default until then: ADR-014 single `tenant_id` bind.

### Domain clarifications (business source-of-truth)

| # | Question | Suggested SME | Blocks |
|---|----------|---------------|--------|
| — | None. ID collision is a PM/programme numbering issue, not a business-rule SME gap. | — | — |

### Auto-fixable (agent resolves later — not inside this skill)

| # | Item | Fix |
|---|------|-----|
| AF-1 | `INIT-GATEFLOW-016-gateflow.md` + README “Gate 1 pending” pointer | spec-draft: withdraw or replace with monitor-only pointer; do not bind Mission Control digests to the current REQ table |

---

## Check summary

| Check | Status | Findings |
|-------|--------|----------|
| F1 Baseline snapshot | PASS | Inventory captured; **source freshness STALE** (header) |
| F2 Spec → code map | FAIL | FF-02 — local CAP/REQ are not the approved slice; approved slice maps to **no** new modules here |
| F3 Spec → verify map | SKIPPED | `scripts/verify_coverage_query.py` absent; approved 016 has no new verify claims in this repo |
| F4 Spec → unit map | SKIPPED | Approved 016 has no new unit work here; local directory tests do not exist |
| F5 As-built drift | FAIL | FF-02 — local spec would replace 014 attach; as-built attach is still create+JWT; map forbids gateflow change |
| F6 Docs drift | FAIL | FF-03 — #242 merged a pre-Gate-1 outline onto `develop` |
| F7 Overlap risk | SKIPPED | No approved new capability in this repo to dual-test |
| F8 CI vs live boundary | PASS | Unchanged: `make check`/`make test` in CI; `tests/verify` live-only |
| F9 Cross-service touch | FAIL | FF-02 — local CTR-01 (breaking attach/login) vs map CTR-01–07 **unchanged** |
| F10 Assumptions | FAIL | FF-02 — spec A-6 / Q-1 assumed a forthcoming PRD with CAP-01–04; live PRD is CAP-A–G Mission Control |
| F11 Effort drivers | PASS | Approved: **zero** in this repo. Local unauthorized slice would be high (schema, membership, breaking auth, verify rewrite) — not scheduled |
| F12 PM questions | PASS | FF-02 numbered; IM-01 deferred with map default |
| F13 ADR conformance | PASS | Approved slice aligned (no ADR change). FF-04 Gap only for unauthorized local Q-2 |
| F14 MDC conformance | PASS | No MDC conflict for “do not change gateflow”. Local file defers paths to TDD — moot until withdrawn |

**Check PASS** = zero unresolved blocking findings (informational OK). Overall checks: **FAIL** on authority (FF-01, FF-02). Workflow outcome remains **`stale`**, not `findings`.

---

## Next steps

> Persist this report locally alongside the spec draft. Fill `handoff.forge` for
> `/commit-workspace` (or Gateflow ForgeClient) onto the Draft spec PR —
> **do not** commit, push, open PRs, or apply labels inside this skill.
> The spec PR is the engineering review surface; product Q&A uses the meta PRD PR.

**PM questions** → post as numbered comments on the **meta PRD PR** (plain English).
  Link from a spec PR comment if helpful. PM answers on meta PRD PR.
  Unresolved blocking PM items → outcome `needs-input` **after** freshness is restored; this hop is `stale` first.

**PE questions** → discuss on the **Draft spec PR**; run `/spec-technical-review` next
  **only after** spec-draft produces a Gate-1-aligned spec. For this repo that is likely N/A / no TDD.

**Domain clarifications** → none.

**Auto-fixable items** → leave in report; resolve in `/spec-draft` — not during this read-only feasibility run.

### Forge readiness

| Item | Value |
|------|-------|
| Local report path | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-016.md` |
| Target branch | `chore/INIT-GATEFLOW-016-spec-gateflow` (PR #242 already **merged**; Forge may need a fresh spec branch from `develop`) |
| Recommended forge | `/commit-workspace` (Gate 2 stays `spec-pending` if a Draft spec PR is reopened) |
| Mutations performed by this skill | **none** |

```
Draft spec PR: chore/INIT-GATEFLOW-016-spec-gateflow  (spec-pending)
When ready:
  [ ] Source freshness is CURRENT
  [ ] All blocking PM questions answered on meta PRD PR
  [ ] All blocking Domain clarifications answered and published via Forge
  [ ] Spec updated to reflect answers (same branch, via Forge)
  [ ] Incremental re-run of /initiative-feasibility on updated spec is clean
  [ ] Proceed: /spec-technical-review (always — pin routes pass and findings here)
  [ ] After spec + feasibility + TDD (if any) + plan on branch (Forge publish):
      PE sets spec-lgtm + Approve on exact head → Ready for review → merge
  [ ] After merge: `/create-board-tickets` from plan §9 — then /pre-implement → /loop-spec
```

Note: after `stale`, the pin next node is **`spec-draft`**, not technical review. The checklist above applies only once a Gate-1-aligned spec exists.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: initiative-feasibility
  outcome: stale
  artifact:
    path: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-016.md
  blockers:
    - FF-01
    - FF-02
  signals:
    new_adr: false
    ripple_action: hold
    map_revision: 1
    source_prd_digest: sha256:2ee19c297b4f948c9f3fbb29d5b45e1e5db9e32fce4a21780915872b3640947a
    approved_primary_repo: drivestream-lab/gateflow-ops
    this_repo_disposition: monitor
    spec_pr_merged: true
    spec_pr: https://github.com/drivestream-lab/gateflow/pull/242
    meta_pr: https://github.com/drivestream-lab/prayog-meta/pull/41
    lane_blocking_open:
      pm: 1
      pe: 0
      domain: 0
      auto_fix: 1
    selected_outcome_rationale: "H1-H3/G1 pending vs live Gate 1; local spec product != approved Mission Control; gateflow not a build target"
    codegraph_provider: mcp-user-prayog-fleet-cbm
    grounding_depth: deep
  next_candidates:
    - spec-draft
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    title: "[INIT-GATEFLOW-016] Feasibility — STALE vs Mission Control Gate 1"
    body_path: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-016.md
```
