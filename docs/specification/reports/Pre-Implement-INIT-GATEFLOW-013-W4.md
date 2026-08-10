# Pre-implement — gateflow / W4 — Catalogue refresh

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-013-W4.md` |
| Initiative | INIT-GATEFLOW-013 |
| Wave | W4 |
| Date | 2026-08-10 |
| Outcome | `pass` |
| Outcome reason | W3 Ground Report + human_approved; board #204 seeded; WorkManifest pass; P15 `verify_catalogue_refresh` contracted; H1–H3 CURRENT |
| Wave head context | Bound by Forge/human context: `develop` @ `ec364db` (W3 merge #208) — recommended coding branch `feature/INIT-GATEFLOW-013-w4-catalogue-refresh` (not opened by this skill) |

---

### Gate check (prior wave)

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | `develop` or `feature/INIT-*-w{N}-*` — not `chore/*-spec-*` | [x] ok — on `develop` |
| Spec PR merged | Implementation plan on integration | [x] yes — #198 merged |
| Coding-readiness at merge | `spec-lgtm` on merged spec PR | [x] verified — #198 label `spec-lgtm` |
| Board seed (read-only) | Wave issue + TASK ids | [x] seeded — W4 [#204](https://github.com/drivestream-lab/gateflow/issues/204) parent EPIC [#199](https://github.com/drivestream-lab/gateflow/issues/199); W0–W4 [#200](https://github.com/drivestream-lab/gateflow/issues/200)–[#204](https://github.com/drivestream-lab/gateflow/issues/204). **Note:** #204 is currently `CLOSED` (closed 2026-08-10 before W4 coding) — reopen / set In Progress on the board before `/loop-spec` tracking; seed still present |
| WorkManifest contract | `prayog/v1` §9 pass | [x] pass — `prayog-skills/scripts/workmanifest_contract.py` |
| TASK exit proof | Every W4 TASK has exit + proof | [x] complete — TASK-W4-01…02 |
| Live-verification contract | P15 live script under `tests/verify/` | [x] create `verify_catalogue_refresh.py` |
| Plan / H1–H3 freshness | CURRENT | [x] current — H1 `sha256:c3653bdc…`; H2 `sha256:17921af2…`; H3 rev 1 |
| Impact-map repo scope | match | [x] match — rev 1; scope `sha256:17921af2…` |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live when P15 | [x] `.venv/bin/python -m tests.verify.verify_catalogue_refresh` |
| `ground_command` | N/A reason | [x] N/A — Pass-2 `/ground-spec` |
| Co-shipped live verify (P15) | FILE path | [x] `tests/verify/verify_catalogue_refresh.py` (TASK-W4-02 create) |
| Prior wave as-built row | `human_approved` | [x] INIT-013 W3 = human_approved |
| Prior Ground Report exists | W3 report | [x] `Ground-Report-INIT-GATEFLOW-013-W3.md` |
| Plan PE sign-off (W0 only) | N/A for W4 | [x] N/A |

**Gate verdict:** PASS

**Forge readiness:** `handoff.forge` → `/commit-workspace` to publish this checklist (recommend cut/bind `feature/INIT-GATEFLOW-013-w4-catalogue-refresh` before `/loop-spec` coding). Human: reopen board [#204](https://github.com/drivestream-lab/gateflow/issues/204) / In Progress if tracking requires an open wave ticket.

---

### Contracts consumed (from prior Ground Reports)

> Primary refresh surface builds on W0 connect/catalogue + W1 membership. W3 readiness contracts must remain untouched on the success path (REQ-25). Confirmed against `src/` on `develop` @ `ec364db`.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Programme connection row | upsert/get by tenant_id | tenant + org/repo/ref + `last_synced_at` | connection DTO (no PAT) | Ground-Report W0 | [x] yes — refresh must update sync timestamp / tree for existing connection |
| Programme connect git sync | `connect_programme` → `resolve_workspace` | credential + optional ref | synced meta checkout | Ground-Report W0 | [x] yes — refresh reuses same git client; **do not** require re-sending connect body if plan chooses dedicated refresh (decide in `/loop-spec`) |
| Catalogue parse | `parse_candidates(meta_root, org=)` | synced meta tree | candidates or named parse error | Ground-Report W0 / ADR-012 | [x] yes — GET catalogue after refresh must reflect latest tree (REQ-07) |
| Catalogue API | GET `…/programme/catalogue` | bearer + tenant_id | programme_org + candidates | Ground-Report W0 | [x] yes — live verify compares before/after refresh |
| Active-list writers | `list_tenant_repos` / select membership | tenant_id | membership DTOs | Ground-Report W1 | [x] yes — refresh **must not** add/remove rows (REQ-25) |
| Deselect / select membership | select/deselect routes | bearer + repos | membership changes only via those APIs | Ground-Report W1 | [x] yes — refresh is not a select path |
| Provenance / readiness_source | tenant_repos + status path | status-sourced admits | harness_verified / readiness | Ground-Report W3 | [x] yes — refresh must not rewrite readiness or call status/filesystem evaluators |
| Status / dual gate | LaunchpadStatusClient / wave-start | N/A for catalogue refresh | unchanged | Ground-Report W3 | [x] yes — out of W4 mutate scope |
| Tenant bearer zone | `verify_tenant_bearer_token` | bearer + path tenant_id | resolved context | ADR-011 | [x] yes |

**Unconfirmed contracts:**
- Exact HTTP shape for catalogue refresh (path/method/body) — deferred to `/loop-spec` (models in `src/models/programme_connection_models.py` per §9; OpenAPI body/query per http-api-conventions). Plan: dedicated refresh that re-syncs connection checkout without mutating selections.
- Whether refresh is distinct from calling `PUT …/connect` again with same org/repo — product REQ-24 is “refresh at any time”; prefer explicit refresh entry so operators need not re-post connect payload; confirm in `/loop-spec` against TDD/plan.
- §9 TASK-W4-01 `files[]` lists connection models + onboarding + routes only — if response DTO needs catalogue snapshot, stay under listed modules / existing catalogue models (do not invent TASK ids).
- Live fixture “catalogue that can grow” — verify script must arrange meta fixture growth (or documented synthetic steps); agent ships script, human runs at wave-acceptance.

---

### Must read

- [x] `AGENTS.md`
- [x] MDC (domain-filtered):
  - [x] `architecture.mdc` / `http-api-conventions.mdc` — refresh route body models; routes → business only
  - [x] `pydantic-schemas.mdc` — DTOs in `src/models/` only
  - [x] `fail-fast.mdc` / `logging-loguru.mdc` — git failure named reason; IDs as kwargs; fail-closed without wiping selections
  - [x] `infra-services.mdc` — reuse `TenantGitWorkspaceClient`; no new git stack
  - [x] `repository-pattern.mdc` — no ORM in business; membership/readiness untouched
  - [x] `testing-verify-flows.mdc` / `python-tooling.mdc` — co-ship live verify; `make check`/`test`
- [x] ADRs:
  - [x] ADR-012 **Accepted** — catalogue discovery from latest synced meta (not frozen at connect)
  - [x] ADR-010 **Accepted** — workspace path authority via existing git client
  - [x] ADR-011 **Accepted** — tenant bearer on programme routes
  - skipped: ADR-013 (status dual gate — do not mutate in W4)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` (REQ-07, REQ-24, REQ-25)
- [x] Plan / §9 W4: `Implementation-Plan-INIT-GATEFLOW-013.md`
- [x] Board wave: https://github.com/drivestream-lab/gateflow/issues/204 — TASK list:
  - [x] TASK-W4-01 — REQ-07,24,25 — refresh API: re-sync programme copy; selections/readiness untouched — proof: `make check`
  - [x] TASK-W4-02 — REQ-07,24,25 — unit + create `verify_catalogue_refresh` + README/as-built — proof: live FILE

---

### Governance alignment

- [x] Slice does not contradict ADR-012 (latest sync is catalogue authority)
- [x] Plan TASK MDC/ADR notes for W4 reviewed — discovery from latest sync; no selection mutation
- [x] On-demand only this INIT (spec Q-4) — no scheduler in W4
- [x] Git failure → named reason; existing selections and readiness untouched (spec failure table REQ-24)
- [x] Do not call Launchpad status / filesystem harness as part of catalogue refresh
- [x] No DDL / Alembic expected for W4

---

### Must update (via `/loop-spec`)

- [ ] `src/business_services/programme_onboarding_service.py` — catalogue refresh: re-sync connection checkout; bump `last_synced_at`; leave `tenant_repos` / readiness alone
- [ ] `src/api/v1/programme_routes.py` — refresh endpoint (tenant bearer)
- [ ] `src/models/programme_connection_models.py` — request/response DTOs for refresh
- [ ] `tests/unit/test_programme_onboarding.py` — refresh success + git-fail leaves selections; catalogue growth visibility
- [ ] `tests/verify/verify_catalogue_refresh.py` — create (P15)
- [ ] `tests/README.md` + `docs/specification/as-built/implementation-status.md` — W4 feature map / matrix

---

### Must not

- [ ] Mutate `tenant_repos` membership on refresh success or failure (REQ-25)
- [ ] Rewrite `harness_verified` / `readiness_source` / call status or `sync_harness` from refresh path
- [ ] Freeze catalogue at first connect — refresh must re-fetch meta then re-parse (REQ-07 / ADR-012)
- [ ] Introduce a second git client or caller-supplied workspace path (ADR-010)
- [ ] Schedule/cron refresh in this wave (Q-4 on-demand only)
- [ ] Open branch / commit / PR / labels from this skill
- [ ] Ship refresh HTTP without co-shipped `verify_catalogue_refresh` (P15)

---

### Engineering contracts to produce (W4)

| Contract | Entry point | Input | Output / invariants |
|----------|-------------|-------|---------------------|
| Catalogue refresh | onboarding service + programme route | tenant bearer + connected tenant (body per OpenAPI) | connection with updated `last_synced_at`; meta tree refreshed |
| Selections unchanged | same refresh path | before/after `list_tenant_repos` | identical membership set on success and on git failure |
| Catalogue reflects sync | GET catalogue after refresh | — | new candidates visible when meta grew; parse fail-closed |
| Fail-closed refresh | git / resolve error | named reason | no selection/readiness writes; prior sync state policy per fail-fast (do not wipe working tenant) |

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | format, lint, types, layers | `make check` |
| Unit | refresh sync; selections untouched; git fail closed | `make test` |
| Live verify | human @ wave-acceptance | `.venv/bin/python -m tests.verify.verify_catalogue_refresh` |
| Ground check | Pass-2 | N/A — `/ground-spec` |

### Human wave-acceptance (after loop-spec + Draft PR)

- [ ] Connected tenant; catalogue fixture that can grow (plan prerequisites)
- [ ] Run `.venv/bin/python -m tests.verify.verify_catalogue_refresh`
- [ ] Confirm new candidates after refresh; prior selection membership unchanged
- [ ] Label tip `wave-accepted` (human only)

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-013
- Issue: [#204](https://github.com/drivestream-lab/gateflow/issues/204) (EPIC [#199](https://github.com/drivestream-lab/gateflow/issues/199)) — currently CLOSED; reopen for In Progress if needed
- Spec path: `docs/specification/product/INIT-GATEFLOW-013-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_catalogue_refresh`
- ADRs in scope: ADR-012, ADR-010, ADR-011
- Wave head: `develop` @ `ec364db` (cut `feature/INIT-GATEFLOW-013-w4-catalogue-refresh` before coding)

---

### Checklist publish readiness (on `pass`)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — gates satisfied |
| Next | `loop-spec` |
| Forge (this hop) | `commit_workspace` **required** — publish this Pre-Implement file |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR |

Recommend `/commit-workspace` after authorization. Do not open the PR here.

---

### Merge order

N/A — single-repo W4 (last eng wave for INIT-013 gateflow). Depends on W0 connect/catalogue + W1 membership (grounded). W3 readiness must remain untouched.

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-013-W4.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-013
    wave: W4
    board_issue: https://github.com/drivestream-lab/gateflow/issues/204
    board_issue_state: CLOSED
    epic_issue: https://github.com/drivestream-lab/gateflow/issues/199
    tasks:
      - TASK-W4-01
      - TASK-W4-02
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_catalogue_refresh
    ground_command: null
    workmanifest_contract: pass
    recommended_branch: feature/INIT-GATEFLOW-013-w4-catalogue-refresh
    develop_sha: ec364db0ce2e458250bbae7c48774573e6ba1a87
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    head_ref: develop
    commit_workspace:
      required: true
      head_ref: develop
```
