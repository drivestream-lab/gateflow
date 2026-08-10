# Pre-implement — gateflow / W3 — Launchpad status readiness + dual evaluators

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-013-W3.md` |
| Initiative | INIT-GATEFLOW-013 |
| Wave | W3 |
| Date | 2026-08-10 |
| Outcome | `pass` |
| Outcome reason | W2 Ground Report + human_approved; board #203 seeded; WorkManifest pass; P15 `verify_harness_status` contracted; H1–H3 CURRENT |
| Wave head context | Bound by Forge/human context: `develop` @ `3346e86…` — recommended coding branch `feature/INIT-GATEFLOW-013-w3-status-readiness` (not opened by this skill) |

---

### Gate check (prior wave)

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | `develop` or `feature/INIT-*-w{N}-*` — not `chore/*-spec-*` | [x] ok — on `develop` |
| Spec PR merged | Implementation plan on integration | [x] yes — #198 merged |
| Coding-readiness at merge | `spec-lgtm` on merged spec PR | [x] verified — #198 label `spec-lgtm` |
| Board seed (read-only) | Wave issue + TASK ids | [x] seeded — W3 [#203](https://github.com/drivestream-lab/gateflow/issues/203) parent EPIC [#199](https://github.com/drivestream-lab/gateflow/issues/199); W0–W4 [#200](https://github.com/drivestream-lab/gateflow/issues/200)–[#204](https://github.com/drivestream-lab/gateflow/issues/204) |
| WorkManifest contract | `prayog/v1` §9 pass | [x] pass — `prayog-skills/scripts/workmanifest_contract.py` |
| TASK exit proof | Every W3 TASK has exit + proof | [x] complete — TASK-W3-01…05 |
| Live-verification contract | P15 live script under `tests/verify/` | [x] create `verify_harness_status.py` |
| Plan / H1–H3 freshness | CURRENT | [x] current — H1 `sha256:c3653bdc…`; H2 `sha256:17921af2…`; H3 rev 1 |
| Impact-map repo scope | match | [x] match — rev 1; scope `sha256:17921af2…` |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live when P15 | [x] `.venv/bin/python -m tests.verify.verify_harness_status` |
| `ground_command` | N/A reason | [x] N/A — Pass-2 `/ground-spec` |
| Co-shipped live verify (P15) | FILE path | [x] `tests/verify/verify_harness_status.py` (TASK-W3-05 create) |
| Prior wave as-built row | `human_approved` | [x] INIT-013 W2 = human_approved |
| Prior Ground Report exists | W2 report | [x] `Ground-Report-INIT-GATEFLOW-013-W2.md` |
| Plan PE sign-off (W0 only) | N/A for W3 | [x] N/A |

**Gate verdict:** PASS

**Forge readiness:** `handoff.forge` → `/commit-workspace` to publish this checklist (recommend cut/bind `feature/INIT-GATEFLOW-013-w3-status-readiness` before `/loop-spec` coding).

---

### Contracts consumed (from prior Ground Report)

> Source: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-013-W2.md` §Contracts produced — confirmed against `src/` on `develop` @ `3346e86`.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Setup-on-select batch | `select_repos` after admit | newly admitted `{org,repo}` | per-repo `ok` / `setup_failed` + reason | Ground-Report W2 | [x] yes — W3 wires status **after** successful setup (or skip status when setup failed) |
| Workspace layout on success | `TenantGitWorkspaceClient.resolve_workspace` | credential | `{root}/{org}/{repo}` present | Ground-Report W2 / ADR-010 | [x] yes — status inspect targets that checkout |
| Select response setup outcomes | `ProgrammeSelectResponse.results[]` | batch | `ok` \| `already_selected` \| `setup_failed` | Ground-Report W2 | [x] yes — extend with status outcomes (`ok` / `status_failed` per TDD) |
| Admit retained on setup fail | select + `tenant_repos` | setup error | membership kept | Ground-Report W2 | [x] yes — **do not** run status / write status readiness for failed setup; D5 partial success |
| Select admit + probe | same select path | catalogue + PAT | 422 before admit on probe/catalogue fail | Ground-Report W1 | [x] yes — unchanged |
| Active-list writers | `add_tenant_repos` / `list_tenant_repos` | tenant_id + refs | membership | Ground-Report W1 | [x] yes |
| Filesystem harness evaluator | `LaunchpadClient.sync_harness` | workspace_path | ready / HarnessReadinessError | as-built INIT-012; wave_start / orchestrator | [x] yes — **retain** for pre-INIT / filesystem provenance (ADR-013 Option B) |
| Harness cache writers | `TenantService.mark_harness_verified` / `is_harness_verified` | org, repo | bool cache | tenant_service / repository | [x] yes — status path may write only for status-sourced admits (REQ-21/22) |
| Tenant bearer zone | `verify_tenant_bearer_token` | bearer + path tenant_id | resolved context | ADR-011 | [x] yes |

**Unconfirmed contracts:**
- Exact `readiness_source` column vs inferred provenance — TDD §8 recommends optional column (`filesystem` \| `launchpad_status`); plan TASK-W3-02 creates DDL-NOTE + schema modify — decide in `/loop-spec` (prefer explicit column for gate clarity).
- Exact status/refresh OpenAPI field names — deferred to `/loop-spec` (models in `src/models/` only).
- §9 TASK-W3-02 `files[]` omits `src/models/` while plan §2 Files table lists `src/models/ modify` — architecture requires DTOs/enums under `src/models/`; `/loop-spec` must add those modules as part of the listed route/service contracts (do not invent TASK ids).
- Launchpad CLI binary presence in live env (Q-2 / FF-06) — ops prerequisite; OPS-NOTE + settings path; unit covers `tool_unavailable`; live verify needs CLI on PATH/settings.
- Wave-start never-checked fail-closed (spec Q-3 default) — implement in TASK-W3-03 per plan.

---

### Must read

- [x] `AGENTS.md`
- [x] MDC (domain-filtered):
  - [x] `infra-services.mdc` — new `LaunchpadStatusClient` as `BaseInfraService`; DI + `_INFRA_SERVICE_TYPES`
  - [x] `dependency-injection.mdc` — `@inject`; settings via `get_instance()` not ConfigModule
  - [x] `fail-fast.mdc` / `logging-loguru.mdc` — `tool_unavailable` distinct; IDs as kwargs
  - [x] `pydantic-schemas.mdc` — readiness/status DTOs + enums in `src/models/` only
  - [x] `repository-pattern.mdc` / `database-migrations.mdc` — schema + `env.py` only; human owns `versions/` + DDL-NOTE
  - [x] `architecture.mdc` / `http-api-conventions.mdc` — refresh body models; routes → business only
  - [x] `testing-verify-flows.mdc` / `python-tooling.mdc` — co-ship live verify; `make check`/`test`
- [x] ADRs:
  - [x] ADR-013 **Accepted** — dual evaluators; separate inspect-only status client (Option B)
  - [x] ADR-010 **Accepted** — workspace path authority unchanged
  - [x] ADR-011 **Accepted** — tenant bearer on programme routes
  - skipped: ADR-012 (catalogue unchanged this wave)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-013-gateflow.md` (REQ-17–23)
- [x] Plan / §9 W3: `Implementation-Plan-INIT-GATEFLOW-013.md`
- [x] Board wave: https://github.com/drivestream-lab/gateflow/issues/203 — TASK list:
  - [x] TASK-W3-01 — REQ-17,18,20 — `LaunchpadStatusClient` + settings + DI + OPS-NOTE — proof: `make test`
  - [x] TASK-W3-02 — REQ-17,19,21–23 — readiness_source + status in select batch + refresh; schema/DDL-NOTE — proof: `make check`
  - [x] TASK-W3-03 — REQ-21,22 — dual gate wave-start/orchestrator; never-checked fail-closed — proof: `make test`
  - [x] TASK-W3-04 — REQ-18–23 — unit dual/status/argv/tool_unavailable/legacy — proof: `make test`
  - [x] TASK-W3-05 — REQ-17,18,20,21,23 — create `verify_harness_status` + README/as-built — proof: live FILE

---

### Governance alignment

- [x] Slice does not contradict ADR-013 Option B (separate client; retain filesystem evaluator)
- [x] Plan TASK MDC/ADR notes for W3 reviewed — inspect-only argv; no apply; settings `get_instance()`
- [x] Status path must not rewrite pre-INIT / filesystem-provenance rows (REQ-22)
- [x] Partial-success for status batch (REQ-19) matches setup D5 pattern from W2
- [x] Do not evolve `LaunchpadClient.sync_harness` into status (ADR-013 rejects Option A)
- [x] Human Alembic for `readiness_source` (or equivalent) — agent ships schema + DDL-NOTE only

---

### Must update (via `/loop-spec`)

- [ ] `src/infra_services/launchpad_status_client.py` — create inspect-only client
- [ ] `src/configs/app_settings.py` — CLI path / related settings
- [ ] `src/di/modules/infra_module.py` + `dependency_container.py` — bind + `_INFRA_SERVICE_TYPES`
- [ ] `docs/specification/reports/OPS-NOTE-INIT-GATEFLOW-013-launchpad-cli.md` — preinstall / PATH note
- [ ] `src/database/postgres/schema/tenant_schema.py` + `postgres_migrations/env.py` if needed — provenance column
- [ ] `docs/specification/reports/DDL-NOTE-INIT-GATEFLOW-013-readiness-source.md` — human migration note
- [ ] `programme_onboarding_service.py` / `tenant_service.py` / `programme_routes.py` — status batch + refresh; `mark_harness_verified` only on status path for status-sourced repos
- [ ] `src/models/*` — readiness_source enum, status/refresh DTOs, select outcome extensions (see §9 gap note above)
- [ ] `wave_start_service.py` / `run_orchestrator.py` — provenance switch; never-checked fail-closed
- [ ] `tests/unit/test_launchpad_status_client.py` + `test_harness_dual_gate.py`
- [ ] `tests/verify/verify_harness_status.py` + `tests/README.md` + as-built W3 row

---

### Must not

- [ ] Invoke Launchpad apply / install / mutate from status client (REQ-18)
- [ ] Call status evaluator for filesystem-provenance / pre-INIT rows on force-recheck (REQ-22 / ADR-013)
- [ ] Assume checkout exists after `setup_failed` — skip status for that repo (Ground-Report W2)
- [ ] Treat `tool_unavailable` as repo-not-ready (REQ-20)
- [ ] Write agent-owned files under `postgres_migrations/versions/`
- [ ] Open branch / commit / PR / labels from this skill
- [ ] Ship status HTTP behaviour without co-shipped `verify_harness_status` (P15)

---

### Engineering contracts to produce (W3)

| Contract | Entry point | Input | Output / invariants |
|----------|-------------|-------|---------------------|
| Inspect-only status client | `LaunchpadStatusClient` (infra) | workspace path + programme meta config dir (CTR-02) | status verdict; never apply; missing binary → `tool_unavailable` |
| Status-on-select batch | `select_repos` after setup ok | newly admitted with successful setup | per-repo status ok / `status_failed` + reason; peers independent |
| Provenance / readiness_source | tenant_repos row | set at admission for selection-admitted | `launchpad_status` vs `filesystem` (or equivalent); gates switch on this |
| On-demand refresh | programme refresh-check route (path per OpenAPI in loop-spec) | tenant bearer + org/repo (status-sourced only) | replaces stored readiness in place; legacy rows rejected/untouched |
| Dual harness gate | wave-start + orchestrator | registered org/repo | status vs `sync_harness` by provenance; never-checked selected → fail closed |

> Confirm in `/loop-spec`: status only after setup `ok` (or already-selected with checkout); setup_failed keeps membership without status write.

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | format, lint, types, layers | `make check` |
| Unit | argv guard, tool_unavailable, dual gate, legacy untouched | `make test` |
| Live verify | human @ wave-acceptance | `.venv/bin/python -m tests.verify.verify_harness_status` |
| Ground check | Pass-2 | N/A — `/ground-spec` |

### Human wave-acceptance (after loop-spec + Draft PR)

- [ ] Ensure Launchpad CLI available per OPS-NOTE / settings
- [ ] Run `.venv/bin/python -m tests.verify.verify_harness_status`
- [ ] Confirm selection-admitted repo gets status-sourced readiness; legacy filesystem path still works (or unit-covered)
- [ ] Label tip `wave-accepted` (human only)

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-013
- Issue: [#203](https://github.com/drivestream-lab/gateflow/issues/203) (EPIC [#199](https://github.com/drivestream-lab/gateflow/issues/199))
- Spec path: `docs/specification/product/INIT-GATEFLOW-013-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_harness_status`
- ADRs in scope: ADR-013, ADR-010, ADR-011
- Wave head: `develop` @ `3346e86…` (cut `feature/INIT-GATEFLOW-013-w3-status-readiness` before coding)

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

N/A — single-repo W3. Depends on W2 setup-on-select + W0/W1 select/admit contracts (grounded). Ops: Launchpad CLI preinstalled before live verify.

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-013-W3.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-013
    wave: W3
    board_issue: https://github.com/drivestream-lab/gateflow/issues/203
    epic_issue: https://github.com/drivestream-lab/gateflow/issues/199
    tasks:
      - TASK-W3-01
      - TASK-W3-02
      - TASK-W3-03
      - TASK-W3-04
      - TASK-W3-05
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_harness_status
    ground_command: null
    workmanifest_contract: pass
    prior_wave_ground_report: docs/specification/reports/Ground-Report-INIT-GATEFLOW-013-W2.md
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    head_ref: develop
    include_paths:
      - docs/specification/reports/Pre-Implement-INIT-GATEFLOW-013-W3.md
```
