## Pre-implement — gateflow / W2 — Setup chosen repos (batch)

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-013-W2.md` |
| Initiative | INIT-GATEFLOW-013 |
| Wave | W2 |
| Date | 2026-08-09 |
| Outcome | `pass` |
| Outcome reason | W1 Ground Report + human_approved; board #202 seeded; WorkManifest pass; P15 live verify contracted; H1–H3 CURRENT |
| Wave head context | Bound by Forge/human context: `develop` @ `d6f623c9f3c9…` — recommended coding branch `feature/INIT-GATEFLOW-013-w2-repo-setup` (not opened by this skill) |

---

### Gate check (prior wave)

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | `develop` or `feature/INIT-*-w{N}-*` — not `chore/*-spec-*` | [x] ok — on `develop` |
| Spec PR merged | Implementation plan on integration | [x] yes — #198 merged |
| Coding-readiness at merge | `spec-lgtm` on merged spec PR | [x] verified — #198 label `spec-lgtm` |
| Board seed (read-only) | Wave issue + TASK ids | [x] seeded — W2 [#202](https://github.com/drivestream-lab/gateflow/issues/202) parent EPIC [#199](https://github.com/drivestream-lab/gateflow/issues/199); W0–W4 [#200](https://github.com/drivestream-lab/gateflow/issues/200)–[#204](https://github.com/drivestream-lab/gateflow/issues/204) |
| WorkManifest contract | `prayog/v1` §9 pass | [x] pass — `prayog-skills/scripts/workmanifest_contract.py` |
| TASK exit proof | Every W2 TASK has exit + proof | [x] complete — TASK-W2-01…03 |
| Live-verification contract | P15 live script under `tests/verify/` | [x] extend `verify_repo_selection.py` (setup assertions) |
| Plan / H1–H3 freshness | CURRENT | [x] current — H1 `sha256:c3653bdc…`; H2 `sha256:17921af2…`; H3 rev 1 |
| Impact-map repo scope | match | [x] match — rev 1; scope `sha256:17921af2…` |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live when P15 | [x] `.venv/bin/python -m tests.verify.verify_repo_selection` |
| `ground_command` | N/A reason | [x] N/A — Pass-2 `/ground-spec` |
| Co-shipped live verify (P15) | FILE path | [x] `tests/verify/verify_repo_selection.py` (TASK-W2-03 modify) |
| Prior wave as-built row | `human_approved` | [x] INIT-013 W1 = human_approved |
| Prior Ground Report exists | W1 report | [x] `Ground-Report-INIT-GATEFLOW-013-W1.md` |
| Plan PE sign-off (W0 only) | N/A for W2 | [x] N/A |

**Gate verdict:** PASS

**Forge readiness:** `handoff.forge` → `/commit-workspace` to publish this checklist (recommend cut/bind `feature/INIT-GATEFLOW-013-w2-repo-setup` before `/loop-spec` coding).

---

### Contracts consumed (from prior Ground Report)

> Source: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-013-W1.md` §Contracts produced — confirmed against `src/` on `develop` @ `d6f623c`.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Select active list | `POST …/programme/repos/select` → `select_repos` | bearer + `{repos:[{org,repo}]}` | `results[]` + `active_repos` | Ground-Report W1 | [x] yes — W2 wires setup into same request after admit |
| Per-repo admit result | selection models / select response | batch | `pending_setup` \| `already_selected` (422 for probe/catalogue) | Ground-Report W1 | [x] yes — replace `pending_setup` with real setup outcomes |
| Active-list writers | `add_tenant_repos` / `list_tenant_repos` | tenant_id + refs | membership | Ground-Report W1 | [x] yes — admit before/with setup; membership still required |
| Tenant workspace auth | `get_tenant_workspace_auth` | tenant_id | workspace_root + pat | W0/W1 live | [x] yes — credential for `resolve_workspace` |
| Git resolve + optional ref | `TenantGitWorkspaceClient.resolve_workspace` | `TenantWorkspaceCredential` + optional `ref` | path + clone\|fetch mode; `TenantGitWorkspaceError.reason` | Ground-Report W0 | [x] yes — ADR-010 layout `{root}/{org}/{repo}` |
| Programme connection | required before select | — | — | Ground-Report W0/W1 | [x] yes — unchanged prerequisite |
| Tenant bearer zone | `verify_tenant_bearer_token` | bearer + path tenant_id | resolved context | ADR-011 | [x] yes |

**Unconfirmed contracts:**
- Exact per-repo setup outcome enum names in OpenAPI — deferred to `/loop-spec` (TDD: `setup_failed` / ok-style; keep models in `src/models/programme_selection_models.py`).
- Launchpad status in same request (TDD) — **not W2 scope**; W3 owns status evaluator (ADR-013).
- Sibling script `verify_repo_setup.py` — plan allows modify `verify_repo_selection` **or** create sibling; prefer extend existing FILE unless isolation needs a second script.

---

### Must read

- [x] `AGENTS.md`
- [x] MDC (domain-filtered):
  - [x] `infra-services.mdc` — reuse `TenantGitWorkspaceClient`; no new git stack
  - [x] `fail-fast.mdc` / `logging-loguru.mdc` — per-repo named reasons; IDs as kwargs
  - [x] `pydantic-schemas.mdc` — extend selection models only in `src/models/`
  - [x] `architecture.mdc` / `repository-pattern.mdc` — business orchestrates; no ORM
  - [x] `testing-verify-flows.mdc` / `python-tooling.mdc` — extend live verify; `make check`/`test`
  - skipped: dual-evaluator / Launchpad status (W3)
- [x] ADRs:
  - [x] ADR-010 **Accepted** — workspace authority / clone-or-fetch path unchanged
  - [x] ADR-011 **Accepted** — tenant bearer on select (unchanged routes)
  - skipped: ADR-012 (catalogue unchanged); ADR-013 (W3)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` (REQ-14–16)
- [x] Plan / §9 W2: `Implementation-Plan-INIT-GATEFLOW-013.md`
- [x] Board wave: https://github.com/drivestream-lab/gateflow/issues/202 — TASK list:
  - [x] TASK-W2-01 — REQ-14, REQ-15, REQ-16 — wire `resolve_workspace` into select for newly admitted; isolate failures; per-repo setup results — proof: `make check`
  - [x] TASK-W2-02 — REQ-14–16 — unit setup isolation + result shape — proof: `make test`
  - [x] TASK-W2-03 — REQ-14–16 — live setup assertions on `verify_repo_selection` + README/as-built — proof: live FILE

---

### Governance alignment

- [x] Slice does not contradict ADR-010 / ADR-011
- [x] Plan TASK MDC/ADR notes for W2 reviewed — infra reuse client; workspace authority unchanged
- [x] Partial-success batch (D5 / REQ-15): one setup failure must not roll back other admits or block peers
- [x] Probe failures remain all-or-nothing before admit (W1); setup isolation applies **after** successful probe/admit path
- [x] Do not wire Launchpad status (W3)

---

### Must update (via `/loop-spec`)

- [ ] `ProgrammeOnboardingService.select_repos` — after successful probe/admit of **new** repos, call `resolve_workspace` per repo independently; catch `TenantGitWorkspaceError`; continue peers
- [ ] `programme_selection_models.py` — per-repo setup outcome/reason fields (retire bare `pending_setup` for newly admitted success/fail paths)
- [ ] `tests/unit/test_programme_selection.py` — mixed success/failure isolation
- [ ] `tests/verify/verify_repo_selection.py` — assert selected repo directory under tenant workspace
- [ ] `tests/README.md` + `as-built/implementation-status.md` — W2 row / feature-map notes

---

### Must not

- [ ] Require status/readiness success for setup (W3)
- [ ] Bundle setup as all-or-nothing across the batch (violates REQ-15)
- [ ] Invent a second workspace client or caller-supplied `workspace_path` (ADR-010)
- [ ] Change catalogue/select admission gates from W1
- [ ] Open branch / commit / PR / labels from this skill
- [ ] Ship setup HTTP behaviour without co-shipped live verify assertions (P15)

---

### Engineering contracts to produce (W2)

| Contract | Entry point | Input | Output / invariants |
|----------|-------------|-------|---------------------|
| Setup-on-select batch | `select_repos` (same HTTP select) | newly admitted `{org,repo}` after probe | per-repo setup ok / setup_failed + named reason; peers independent |
| Workspace layout | `resolve_workspace(credential)` | tenant PAT + workspace_root + org/repo | `{workspace_root}/{org}/{repo}` present on success |
| Select response shape | `ProgrammeSelectResponse` | batch | results include setup outcome; admitted membership retained even if setup fails (unless product says otherwise — default: membership kept, failure reported) |

> Confirm in `/loop-spec` against TDD §3.1: setup failure reporting vs membership — plan exit says “one setup fail does not block others”; prefer keep admit + report `setup_failed` (partial success).

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | format, lint, types, layers | `make check` |
| Unit | setup isolation + result shape | `make test` |
| Live verify | human @ wave-acceptance | `.venv/bin/python -m tests.verify.verify_repo_selection` |
| Ground check | Pass-2 | N/A — `/ground-spec` |

### Human wave-acceptance (after loop-spec + Draft PR)

- [ ] Run `.venv/bin/python -m tests.verify.verify_repo_selection`
- [ ] Confirm selected repo directory present under tenant workspace; mixed-fail covered by unit if unsafe live
- [ ] Label tip `wave-accepted` (human only)

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-013
- Issue: [#202](https://github.com/drivestream-lab/gateflow/issues/202) (EPIC [#199](https://github.com/drivestream-lab/gateflow/issues/199))
- Spec path: `docs/specification/product/INIT-GATEFLOW-013-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_repo_selection`
- ADRs in scope: ADR-010, ADR-011
- Wave head: `develop` @ `d6f623c…` (cut `feature/INIT-GATEFLOW-013-w2-repo-setup` before coding)

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

N/A — single-repo W2. Depends on W1 select + W0 `resolve_workspace` contracts (grounded).

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-013-W2.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-013
    wave: W2
    board_issue: https://github.com/drivestream-lab/gateflow/issues/202
    epic_issue: https://github.com/drivestream-lab/gateflow/issues/199
    tasks:
      - TASK-W2-01
      - TASK-W2-02
      - TASK-W2-03
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_repo_selection
    ground_command: null
    workmanifest_contract: pass
    prior_wave_ground_report: docs/specification/reports/Ground-Report-INIT-GATEFLOW-013-W1.md
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    head_ref: develop
    include_paths:
      - docs/specification/reports/Pre-Implement-INIT-GATEFLOW-013-W2.md
```
