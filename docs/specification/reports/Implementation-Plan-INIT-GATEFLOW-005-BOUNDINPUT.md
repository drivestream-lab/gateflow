---
goal: INIT-GATEFLOW-005-BOUNDINPUT — implementation plan
initiative: INIT-GATEFLOW-005-BOUNDINPUT
status: Planned
date_created: 2026-07-27
source_spec: docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md
source_spec_digest: sha256:5a2bb4965b705911c8ffb0673ac1a8bf5cbe948f1b6376a4b29ea2a9e716a861
feasibility_report: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-005-BOUNDINPUT.md
feasibility_digest: sha256:e34b9f54fdb509cc4847f6300ae2c68546999485c68f781fca3a1c92499dd15a
technical_review: docs/specification/reports/Technical-Review-INIT-GATEFLOW-005-BOUNDINPUT.md
technical_review_digest: sha256:4feaf5973657ce72bca73cdbc1bcd892b2dd20fbfe6b700e5fdd7edafe83891a
prd_digest: sha256:40fb856dd5068290c1d14f010239e6206bee2625aaf6a6e3970d769e9bb5e970
impact_map: prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-005-BOUNDINPUT.md
impact_map_revision: 1
repo_scope_digest: sha256:2cc5e2151451c47b973fdc86dafe19d5cb2fadd651212a5a00f9d681f274039b
approved_meta_pr_head: 0b6b11e4470517842affb894d7ea581c3819ead3
branch: chore/INIT-GATEFLOW-005-BOUNDINPUT-plan-gateflow
review_deadline: 2026-07-30
deciders: PE — spec-lgtm + Approve on exact head after plan package (post-merge recovery)
recovery_note: Spec package (spec + feasibility + TDD + ADR-007/008) merged on PR #52 without this plan; this branch restores Gate 2 plan artifact on develop before /board-seed
---

# Implementation plan — INIT-GATEFLOW-005-BOUNDINPUT

## Source freshness and command contract

| Item | Value | Status |
|------|-------|--------|
| Spec / digest | `docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md` / `sha256:5a2bb4965b705911c8ffb0673ac1a8bf5cbe948f1b6376a4b29ea2a9e716a861` | CURRENT |
| Feasibility / digest | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-005-BOUNDINPUT.md` / `sha256:e34b9f54fdb509cc4847f6300ae2c68546999485c68f781fca3a1c92499dd15a` | CURRENT |
| Technical review / digest | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-005-BOUNDINPUT.md` / `sha256:4feaf5973657ce72bca73cdbc1bcd892b2dd20fbfe6b700e5fdd7edafe83891a` | CURRENT |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-005-BOUNDINPUT.md` / `1` | CURRENT |
| Repo scope digest | `sha256:2cc5e2151451c47b973fdc86dafe19d5cb2fadd651212a5a00f9d681f274039b` | CURRENT |
| Approved meta PR head | `0b6b11e4470517842affb894d7ea581c3819ead3` | CURRENT |
| `check_command` | `make check` | RESOLVED |
| `test_command` | `make test` | RESOLVED |
| `verify_command` | W0/W2: `.venv/bin/python -m tests.verify.verify_implement_lane`; wave-start: `.venv/bin/python -m tests.verify.verify_wave_start`; aggregator `.venv/bin/python -m tests.verify.verify_all` (implement-lane opt-in, not in aggregator) | RESOLVED |
| `ground_command` | N/A — no Makefile ground target; post-wave use `/ground-spec` skill per workflow | N/A |

> TDD Status **Accepted** (PE @nikd10x 2026-07-27). ADR_REQUIRED: ADR-007 + ADR-008
> both **Accepted**. Product path/bind/columns remain TDD §3 / §9. Pin consumer
> `v0.5.0-rc.2` (packages present for implement-lane skills).

## 0. Technical design reference

| Item | Value |
|------|-------|
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-005-BOUNDINPUT.md` |
| PE sign-off | [x] complete — 2026-07-27 (@nikd10x via Cursor chat on https://github.com/drivestream-lab/gateflow/pull/52); architecture Option B; TDD_ONLY Q-3 `GATEFLOW_HANDOFF_ROOT` |
| Resolved ADRs | [`adr-007-invocation-brief-and-agent-message-contract.md`](../adr/adr-007-invocation-brief-and-agent-message-contract.md) (Accepted, `sha256:fd8f11f61be203db409e1dc23df12f78f26dfe5b75c819fce22e0723b0225d89`); [`adr-008-packaged-skill-handoff-ingest-authority.md`](../adr/adr-008-packaged-skill-handoff-ingest-authority.md) (Accepted, `sha256:cc94079602762d58622d321f4bdefacf2c54fcd0a6511da3415daacb48b52cad`). Reuse ADR-001…006 (topology / RunStore / AgentRunner infra / fail-closed). |
| Outstanding PM questions | none — all resolved |
| Outstanding domain questions | none — Q-1…Q-4 + FF-* resolved in TDD §9 |

> Do not start W0 implementation until this plan is merged to `develop` and
> `/board-seed` has created the wave issues (post Gate 2 on this recovery PR).

---

## 1. Requirements (REQ) — product ids

Cite **product** `REQ-*` from the spec. Do **not** invent wave-scoped `REQ-W*`.

| ID | Summary | Spec path | Waves |
|----|---------|-----------|-------|
| REQ-1 | Resolve pin prompt package (`template.md` + `schema.yaml`); fail closed if missing | `docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md` | W0 |
| REQ-2 | Bind `ticket`, `initiative`, `skill_id`, `workspace`, `handoff_path` from wave-start + run | same | W0 |
| REQ-3 | Validate bound map against pin `schema.yaml` | same | W0 |
| REQ-4 | Render simple `{{var}}` only; undeclared/engine features fail closed | same | W0 |
| REQ-5 | AgentRunner message == render; remove invent-prose on packaged path; anti-hardcode | same | W0 |
| REQ-6 | Persist `prompt_id` + `prompt_revision` on automated packaged stages | same | W0 |
| REQ-7 | Persist `runner` + `model_id` on automated packaged stages | same | W0 |
| REQ-8a | Define + persist `runs.handoff_path`; inject into bind map | same | W0 |
| REQ-8b | Ingest only from stored `handoff_path`; no ambient SSOT; dual-run isolation | same | W1 |
| REQ-9 | Fail closed before AgentRunner on package/schema/bind/`handoff_path` failures | same | W0, W1 |
| REQ-10 | Live Cursor prove-it with pin package (`pre-implement` default); W2 multi-skill dogfood | same | W0, W2 |

---

## 2. Implementation phases

### Phase W0 — Resolve + bind + render + thin Cursor + store handoff_path + prove-it

**GOAL-W0:** PromptResolver loads pin packages, binds known context (required
`ticket` ← `ticket_id`), validates/renders `{{var}}`, dispatches **only** the
rendered message through Cursor AgentRunner (no invent-prose), persists
`prompt_id` / `prompt_revision` / runner / model, defines and stores
`runs.handoff_path` as `{GATEFLOW_HANDOFF_ROOT}/{run_id}/handoff.md`, fail-closes
before AgentRunner on bind/package failures, and proves one live
`pre-implement` hop via extended `verify_implement_lane`.

| Task | Description | Implements | Codebase | Spec path | Done when | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|----------|-----------|-----------|----------------|-----------|-----------|--------|
| TASK-W0-01 | Add `GATEFLOW_HANDOFF_ROOT` settings (`get_instance()`); document in `.env.example` / README; fail closed when unset/non-absolute for packaged automate | REQ-8a, REQ-9 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md` | Settings load; missing root detectable; path not under workspace by default | `make check && make test` | settings not DI; fail-fast | ADR-008 (authority); TDD §3.4 path | `feature/INIT-GATEFLOW-005-w0-bound-input` |
| TASK-W0-02 | Create Pydantic models for pin `schema.yaml`, bind map, resolve/render result (`prompt_package_models.py`) | REQ-1, REQ-2, REQ-3, REQ-4 | drivestream-lab/gateflow | same | Models validate fixture schema; extra=forbid where internal | `make check && make test` | pydantic in `src/models/` only | — | same |
| TASK-W0-03 | Implement `PromptResolver` business service: search `prayog-skills/skills/{development,requirements}/{skill_id}/prompts/`; resolve + bind_and_render; DI bind singleton | REQ-1, REQ-2, REQ-3, REQ-4, REQ-9 | drivestream-lab/gateflow | same | Missing package / required miss / undeclared `{{var}}` → no render success; happy path matches pin fixture | `make check && make test` | business owns brief; no ORM | ADR-007 | same |
| TASK-W0-04 | ORM/DTO/repo: `runs.handoff_path`; `stages.prompt_id` + `stages.prompt_revision`; **human** Alembic for DDL | REQ-6, REQ-8a | drivestream-lab/gateflow | same | Schema modules + models/repo map fields; migration file owned by human | `make check && make test` | agent updates schema/env imports only; no `versions/` edits | ADR-001 | same |
| TASK-W0-05 | Wave-start: require non-empty `ticket_id` for packaged-skill automate; bind `ticket` ← `ticket_id`; blank → 4xx, no enqueue | REQ-2, REQ-9 | drivestream-lab/gateflow | same | Blank `ticket_id` rejected; unit + verify_wave_start can supply ticket | `make check && make test` | body model in `src/models/`; fail-fast | ADR-005 (programme token zone unchanged) | same |
| TASK-W0-06 | RunOrchestrator W0 path: on run create define `handoff_path`, ensure baton dir/file; bind → resolve → render → thin `run_skill(message=…)`; persist prompt ids + runner/model; fail closed before AgentRunner | REQ-2, REQ-5, REQ-6, REQ-7, REQ-8a, REQ-9 | drivestream-lab/gateflow | same | Packaged automate stages have prompt fields; 0 AgentRunner on bind/package fail; invent-prose not used | `make check && make test` | business orchestrates; infra message-only | ADR-007, ADR-008 | same |
| TASK-W0-07 | CursorAgentRunner: accept pre-rendered `message` on packaged path; remove/unused `_build_prompt` invent-prose for that path; anti-hardcode unit | REQ-5 | drivestream-lab/gateflow | same | Packaged success path message == render; anti-hardcode test fails if Gateflow brief reintroduced | `make check && make test` | infra SDK wrapper; business must not invent brief | ADR-007, ADR-003 | same |
| TASK-W0-08 | Unit tests: PromptResolver, wave-start ticket, orchestrator fail-closed, runner message-only, RunStore field mapping | REQ-1…REQ-7, REQ-8a, REQ-9 | drivestream-lab/gateflow | same | New/updated unit tests green | `make check && make test` | testing-verify-flows; unit under `tests/unit/` | — | same |
| TASK-W0-09 | Extend `verify_implement_lane` (Enter-at `pre-implement`): assert stage `prompt_id` + `prompt_revision` non-null matching pin package; update `tests/README.md` + as-built W0 | REQ-10, REQ-6 | drivestream-lab/gateflow | same | Live verify documents skill id + prompt fields; as-built W0 in_progress→complete | `make check && make test` ; `.venv/bin/python -m tests.verify.verify_implement_lane` | live verify not in pytest; GATEFLOW_HANDOFF_ROOT set in env | ADR-007 | `feature/INIT-GATEFLOW-005-w0-verify` |

#### Files (W0)

| ID | Path | Action |
|----|------|--------|
| FILE-W0-01 | `src/configs/orchestration_settings.py` (or sibling) | edit — `GATEFLOW_HANDOFF_ROOT` |
| FILE-W0-02 | `.env.example`, `README.md` | edit |
| FILE-W0-03 | `src/models/prompt_package_models.py` | create |
| FILE-W0-04 | `src/models/run_store_models.py`, `adapter_models.py` | edit |
| FILE-W0-05 | `src/business_services/prompt_resolver.py` | create |
| FILE-W0-06 | `src/di/modules/business_services_module.py`, `dependency_container.py` | edit — PromptResolver |
| FILE-W0-07 | `src/database/postgres/schema/run_store_schema.py`, `repository/run_store_repository.py`, `postgres_migrations/env.py` | edit ORM/imports |
| FILE-W0-08 | `postgres_migrations/versions/` | **human** creates revision |
| FILE-W0-09 | `src/business_services/wave_start_service.py` | edit |
| FILE-W0-10 | `src/business_services/run_orchestrator.py` | edit |
| FILE-W0-11 | `src/infra_services/cursor_agent_runner.py` | edit — message-only packaged path |
| FILE-W0-12 | `tests/unit/test_prompt_resolver.py`, `test_cursor_agent_runner.py`, `test_wave_start.py`, `test_run_orchestrator.py`, … | create/edit |
| FILE-W0-13 | `tests/verify/verify_implement_lane.py`, `tests/README.md`, as-built | edit |

#### Tests (W0)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W0-U | unit | `make test` | REQ-1…7, REQ-8a, REQ-9, REQ-5 anti-hardcode |
| TEST-W0-V | live verify | `.venv/bin/python -m tests.verify.verify_implement_lane` | REQ-10, REQ-6 |

---

### Phase W1 — Ingest-only from stored handoff_path + dual-run isolation

**GOAL-W1:** Packaged-skill automated ingest reads **only** `run.handoff_path` via
`HandoffReader.read_path`; ambient `find_latest_handoff` / `DEFAULT_ARTIFACT_GLOBS`
are not SSOT; missing/unreadable path fails closed; dual-run fixture proves
isolation.

| Task | Description | Implements | Codebase | Spec path | Done when | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|----------|-----------|-----------|----------------|-----------|-----------|--------|
| TASK-W1-01 | Add `HandoffReader.read_path(path)`; keep `find_latest_handoff` for legacy/debug only | REQ-8b, REQ-9 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md` | `read_path` parses envelope from given path; missing → fail closed | `make check && make test` | business handoff parse | ADR-008 | `feature/INIT-GATEFLOW-005-w1-ingest` |
| TASK-W1-02 | RunOrchestrator packaged automate: post-agent ingest uses `read_path(run.handoff_path)` only — never ambient for this path | REQ-8b, REQ-9 | drivestream-lab/gateflow | same | Unit proves ambient not called on packaged success/fail ingest | `make check && make test` | fail-fast; no silent ambient fallback | ADR-008 | same |
| TASK-W1-03 | Dual-run isolation fixture: two runs under same workspace coding root with distinct `handoff_path` under `GATEFLOW_HANDOFF_ROOT` never cross-ingest | REQ-8b | drivestream-lab/gateflow | same | Fixture green; as-built W1 + README updated | `make check && make test` | testing-verify-flows | ADR-008 | same |

#### Files (W1)

| ID | Path | Action |
|----|------|--------|
| FILE-W1-01 | `src/business_services/handoff_reader.py` | edit — `read_path` |
| FILE-W1-02 | `src/business_services/run_orchestrator.py` | edit — ingest SSOT |
| FILE-W1-03 | `tests/unit/test_handoff_workflow.py` (or sibling) | edit/create |
| FILE-W1-04 | as-built, `tests/README.md` | edit |

#### Tests (W1)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W1-U | unit | `make test` | REQ-8b isolation + fail-closed ingest |

---

### Phase W2 — Broaden orchestrated packaged skills / dogfood

**GOAL-W2:** Substrate works for any pin `dispatch: orchestrated` packaged skill
(not a hardcoded allowlist): dogfood evidence beyond the single W0
`pre-implement` hop (additional implement-lane and/or then-current orchestrated
skills under active pin), document skill ids in verify/ground evidence, as-built
complete.

| Task | Description | Implements | Codebase | Spec path | Done when | Verify command | MDC notes | ADR notes | Branch |
|------|-------------|------------|----------|-----------|-----------|----------------|-----------|-----------|--------|
| TASK-W2-01 | Multi-skill dogfood: extend verify or add documented second orchestrated hop asserting prompt ids for ≥1 additional packaged skill under pin (no PolicyEngine allowlist) | REQ-10 | drivestream-lab/gateflow | `docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md` | Evidence lists ≥2 skill ids with prompt_id/revision; pin remains SSOT | `make check && make test` ; `.venv/bin/python -m tests.verify.verify_implement_lane` (or documented multi-skill mode) | no skill allowlist in Gateflow | ADR-006 (dispatch SSOT = pin) | `feature/INIT-GATEFLOW-005-w2-dogfood` |
| TASK-W2-02 | As-built + tests README INIT-005 complete; ground-ready | REQ-10 | drivestream-lab/gateflow | same | as-built W2 complete; feature map BOUNDINPUT row final | inspection | SDD as-built | — | same |

#### Files (W2)

| ID | Path | Action |
|----|------|--------|
| FILE-W2-01 | `tests/verify/verify_implement_lane.py` and/or sibling verify | edit |
| FILE-W2-02 | `tests/README.md`, as-built | edit |

#### Tests (W2)

| ID | Layer | Command | Proves |
|----|-------|---------|--------|
| TEST-W2-V | live verify | implement-lane / multi-skill mode | REQ-10 broaden |
| TEST-W2-D | docs | inspection | as-built complete |

---

## 3. Dependencies (DEP)

| ID | Dependency | Blocks |
|----|------------|--------|
| DEP-01 | INIT-001…003 control plane + live Cursor (as-built human_approved) | W0 start |
| DEP-02 | Pin `v0.5.0-rc.2` (or later) with packages for target skills | W0 prove-it |
| DEP-03 | This plan merged to `develop` + `/board-seed` | W0 coding branch |
| DEP-04 | Human Alembic for `handoff_path` / prompt columns | W0 store tasks exit |
| DEP-05 | W0 merged | W1 |
| DEP-06 | W1 merged | W2 |
| DEP-07 | `GATEFLOW_HANDOFF_ROOT` + `CURSOR_API_KEY` for live verify | W0/W2 live |

---

## 4. Risks (RISK)

| ID | Risk | Mitigation |
|----|------|------------|
| RISK-01 | Premature merge of #52 without plan delayed board-seed | This recovery PR; Gate 2 on plan head before `/board-seed` |
| RISK-02 | Operators set `GATEFLOW_HANDOFF_ROOT` inside the git workspace | Document discourage; fail closed if unset; TDD path formula |
| RISK-03 | Residual invent-prose path reintroduced | Anti-hardcode unit (REQ-5); ADR-007 |
| RISK-04 | W0 still ambient-ingest until W1 (FF-03) confuses reviewers | Explicit W0/W1 split in plan + as-built; ADR-008 W1 switch |
| RISK-05 | Human Alembic lag blocks store fields | DEP-04; describe DDL in PR for owner |
| RISK-06 | Launchpad sync stub → pin search roots diverge later | TDD FF-09 search roots; revisit when sync lands |

---

## 5. Out of scope

- prayog-skills package authoring / `dispatch` eligibility changes
- gateflow-ops / Launchpad product features
- Second AgentRunner (OpenCode / Claude Code)
- Worktree-per-run as exit criterion
- Template engines beyond `{{var}}`
- Repo-relative handoff discovery as automate SSOT
- Formal INIT-001 PRD amendment
- SaaS prompt registry
- PolicyEngine / pin walker rewrite

---

## 6. As-built and docs tasks

> Update these in the **same PR** as the code they describe.

| Task | File | Action |
|------|------|--------|
| Update implementation-status.md | `docs/specification/as-built/implementation-status.md` | INIT-005 W0→W2 in_progress → complete |
| Update tests/README.md | `tests/README.md` | BOUNDINPUT feature map + `GATEFLOW_HANDOFF_ROOT` / prompt_id asserts |
| Document env | `.env.example`, `README.md` | `GATEFLOW_HANDOFF_ROOT` |

> **ADR lifecycle** — ADR-007 / ADR-008 already Accepted; do not add promotion tasks.

---

## 7. Plan check summary

| Check | Status |
|-------|--------|
| P1 REQs in §1 | PASS — REQ-1…10 (8a/8b) |
| P2 every REQ ≥1 TASK; every TASK Implements REQ-* | PASS |
| P3 FILE paths | PASS |
| P4 done when | PASS |
| P5 test/verify commands | PASS — `make test` + `verify_implement_lane` / `verify_wave_start` |
| P6 scope | PASS — gateflow only |
| P7 feasibility | PASS — FF-06 → ADR-007/008 Accepted; FF-* resolved in TDD |
| P8 wave order | PASS — W0→W1→W2 + DEP |
| P9 as-built/docs | PASS — §6 |
| P10 self-contained + commands | PASS |
| P11 MDC notes | PASS — TASK columns |
| P12 ADR conformance | PASS — ADR-007 + ADR-008 Accepted files; cite ADR-001…006 |
| P13 TDD Accepted | PASS — PE sign-off 2026-07-27 |
| P14 WorkManifest | PASS — §9 W0/W1/W2 + tasks[] |

---

## 8. PR instructions

> **Recovery:** Spec + feasibility + TDD + ADRs already merged on
> https://github.com/drivestream-lab/gateflow/pull/52 (`develop` @ `de39694`).
> Commit **this plan only** on branch
> `chore/INIT-GATEFLOW-005-BOUNDINPUT-plan-gateflow`. Open a **Draft** PR into
> `develop`. Label **`spec-pending`** until PE completes §10.

```
Branch:   chore/INIT-GATEFLOW-005-BOUNDINPUT-plan-gateflow
Base:     develop
PR title: "[INIT-GATEFLOW-005-BOUNDINPUT] Implementation plan — gateflow"
Required reviewers: @drivestream-lab/prayog-pe-team
Review deadline: 2026-07-30

PE checklist (before spec-lgtm on this plan PR):
  [ ] Plan on current head; digests match § Source freshness
  [ ] §0 PE sign-off on TDD already complete (historical #52)
  [ ] Wave order / done-when / WorkManifest §9 OK
  [ ] P1–P14 pass

After spec-lgtm + Approve + merge of this plan PR — **/board-seed** from §9
(post-merge only; do not seed from an open Draft branch)
```

---

## 10. Gate 2 unlock (PE — after plan on head)

| Item | Value |
|------|-------|
| Verdict | **GATE OPEN REQUEST** (plan recovery) |
| Spec PR (historical package) | https://github.com/drivestream-lab/gateflow/pull/52 (merged) |
| Plan recovery PR | *(fill after `gh pr create`)* |
| Plan PR head SHA | *(PE: `gh pr view <n> --json headRefOid -q .headRefOid`)* |
| Gate label (current) | `spec-pending` |
| Gate label (target) | `spec-lgtm` |
| Blocking items | none — plan complete; needs PE Approve on plan PR tip |

```bash
launchpad apply-gates --repo gateflow --apply
```

PE on **exact current plan-PR head**:

1. Remove `spec-pending` / `spec-blocked` / `spec-revised` / `spec-stale`; add **`spec-lgtm`**
2. GitHub **Approve** with attestation below
3. Mark Draft PR **Ready for review**
4. Authorize merge to `develop`; then **`/board-seed`** from §9

### Approve attestation body

```text
Spec package approved (plan recovery)
initiative: INIT-GATEFLOW-005-BOUNDINPUT
spec_pr_head_sha: <PE fills plan-PR tip OID at Approve>
meta_pr_head_sha: 0b6b11e4470517842affb894d7ea581c3819ead3
impact_map_revision: 1
prd_digest: sha256:40fb856dd5068290c1d14f010239e6206bee2625aaf6a6e3970d769e9bb5e970
scope_digest: sha256:2cc5e2151451c47b973fdc86dafe19d5cb2fadd651212a5a00f9d681f274039b
plan_digest: sha256:<PE: shasum -a 256 docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-005-BOUNDINPUT.md on tip>
artifacts:
  - docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md
  - docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-005-BOUNDINPUT.md
  - docs/specification/reports/Technical-Review-INIT-GATEFLOW-005-BOUNDINPUT.md
  - docs/specification/adr/adr-007-invocation-brief-and-agent-message-contract.md
  - docs/specification/adr/adr-008-packaged-skill-handoff-ingest-authority.md
  - docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-005-BOUNDINPUT.md
prior_merged_spec_pr: https://github.com/drivestream-lab/gateflow/pull/52
prior_merge_sha: de396948056f3d7fb7da1c7918adfb8ad9914f87
```

| PE action | Remove | Add |
|-----------|--------|-----|
| Pending/new revision | `spec-lgtm`, `spec-blocked` | `spec-pending` |
| Request changes/hold | `spec-pending`, `spec-lgtm` | `spec-blocked` |
| Approve full package | `spec-pending`, `spec-blocked`, `spec-revised`, `spec-stale` | `spec-lgtm` |

---

## 9. WorkManifest seed

> **Primary:** `/board-seed` after this plan merges to `develop`. Wave ids exactly
> `W0`, `W1`, `W2`. Board name from governance: **drivestream-lab Board**.

```yaml
# Generated by /spec-implementation-plan — 2026-07-27
# LOCAL — do not commit to prayog-skills upstream
apiVersion: launchpad/v1
kind: WorkManifest

initiative: INIT-GATEFLOW-005-BOUNDINPUT
# Branch naming: feature/INIT-GATEFLOW-005-w{N}-{slug}

metadata:
  title: INIT-GATEFLOW-005-BOUNDINPUT — Bound-input skill invocation
  summary: |
    Consume pinned skill prompt packages: bind wave-start context, validate/render
    {{var}}, thin Cursor message-only dispatch (no invent-prose), persist prompt
    ids, Gateflow-owned handoff_path define/store (W0) and ingest-only (W1), then
    multi-skill dogfood (W2).
  playbook:
    - docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md
    - docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-005-BOUNDINPUT.md

target:
  org: drivestream-lab
  project: drivestream-lab Board

defaults:
  initiative: INIT-GATEFLOW-005-BOUNDINPUT
  parent: EPIC
  status: Backlog
  labels:
    - INIT-GATEFLOW-005-BOUNDINPUT

epic:
  id: EPIC
  repo: drivestream-lab/gateflow
  title: "[feature] INIT-GATEFLOW-005-BOUNDINPUT — Bound-input skill invocation"
  codebase: drivestream-lab/gateflow
  spec_path: docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md
  verify_command: make check && make test
  body: |
    ## Objective

    Pin prompt resolve/bind/render, thin Cursor dispatch, prompt + runner
    telemetry, Gateflow-owned handoff_path define/store/ingest, fail closed,
    and live prove-it — gateflow only.

    ## Waves

    | Wave | Goal |
    |------|------|
    | W0 | Resolve + bind + render + thin Cursor + store handoff_path + prove-it |
    | W1 | Ingest only from stored handoff_path + dual-run isolation |
    | W2 | Broaden orchestrated packaged skills / dogfood |

    ## References

    - Spec: docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md
    - Implementation plan: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-005-BOUNDINPUT.md
    - Technical review: docs/specification/reports/Technical-Review-INIT-GATEFLOW-005-BOUNDINPUT.md
    - ADR-007 / ADR-008 (Accepted)

work:
  - id: W0
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-005-BOUNDINPUT W0] Resolve + bind + thin Cursor + handoff_path + prove-it"
    depends_on: []
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md
    verify_command: make check && make test ; .venv/bin/python -m tests.verify.verify_implement_lane
    status: Backlog
    tasks:
      - id: TASK-W0-01
        implements: [REQ-8a, REQ-9]
        done_when: "GATEFLOW_HANDOFF_ROOT settings + docs; fail closed when unset/non-absolute"
      - id: TASK-W0-02
        implements: [REQ-1, REQ-2, REQ-3, REQ-4]
        done_when: "prompt_package_models validate pin schema + bind map"
      - id: TASK-W0-03
        implements: [REQ-1, REQ-2, REQ-3, REQ-4, REQ-9]
        done_when: "PromptResolver resolve + bind_and_render; DI singleton; fail closed"
      - id: TASK-W0-04
        implements: [REQ-6, REQ-8a]
        done_when: "ORM/DTO/repo map handoff_path + prompt_id/revision; human Alembic DDL"
      - id: TASK-W0-05
        implements: [REQ-2, REQ-9]
        done_when: "Wave-start requires non-empty ticket_id for automate; bind ticket"
      - id: TASK-W0-06
        implements: [REQ-2, REQ-5, REQ-6, REQ-7, REQ-8a, REQ-9]
        done_when: "Orchestrator define path + render + thin dispatch + persist ids; fail closed"
      - id: TASK-W0-07
        implements: [REQ-5]
        done_when: "CursorAgentRunner message-only packaged path; anti-hardcode unit"
      - id: TASK-W0-08
        implements: [REQ-1, REQ-2, REQ-3, REQ-4, REQ-5, REQ-6, REQ-7, REQ-8a, REQ-9]
        done_when: "Unit tests green for resolver/orchestrator/runner/wave-start"
      - id: TASK-W0-09
        implements: [REQ-10, REQ-6]
        done_when: "verify_implement_lane asserts prompt_id/revision; as-built W0 + README"
    body: |
      ## Wave goal

      Pin package resolve/bind/render, thin Cursor message-only dispatch, persist
      prompt + runner fields, define/store GATEFLOW_HANDOFF_ROOT baton path, fail
      closed, and live pre-implement prove-it.

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Done when |
      |------|------------|-----------|
      | TASK-W0-01 | REQ-8a, REQ-9 | GATEFLOW_HANDOFF_ROOT settings |
      | TASK-W0-02 | REQ-1…4 | prompt_package_models |
      | TASK-W0-03 | REQ-1…4, REQ-9 | PromptResolver + DI |
      | TASK-W0-04 | REQ-6, REQ-8a | RunStore columns (+ human Alembic) |
      | TASK-W0-05 | REQ-2, REQ-9 | ticket_id required on automate |
      | TASK-W0-06 | REQ-2,5–7,8a,9 | Orchestrator bound-input path |
      | TASK-W0-07 | REQ-5 | Message-only Cursor + anti-hardcode |
      | TASK-W0-08 | REQ-1…7,8a,9 | Unit suite |
      | TASK-W0-09 | REQ-10, REQ-6 | Live verify + as-built W0 |

      ## Done when

      - [ ] All W0 tasks complete per plan

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md

  - id: W1
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-005-BOUNDINPUT W1] Ingest-only handoff_path + dual-run isolation"
    depends_on:
      - W0
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md
    verify_command: make check && make test
    status: Backlog
    tasks:
      - id: TASK-W1-01
        implements: [REQ-8b, REQ-9]
        done_when: "HandoffReader.read_path; missing path fail closed"
      - id: TASK-W1-02
        implements: [REQ-8b, REQ-9]
        done_when: "Packaged automate ingest uses read_path only — no ambient SSOT"
      - id: TASK-W1-03
        implements: [REQ-8b]
        done_when: "Dual-run isolation fixture green; as-built W1 + README"
    body: |
      ## Wave goal

      Packaged-skill automated ingest SSOT = stored run.handoff_path only;
      dual-run baton isolation; ambient glob/mtime not automate SSOT.

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Done when |
      |------|------------|-----------|
      | TASK-W1-01 | REQ-8b, REQ-9 | read_path |
      | TASK-W1-02 | REQ-8b, REQ-9 | Orchestrator ingest SSOT switch |
      | TASK-W1-03 | REQ-8b | Dual-run isolation + docs |

      ## Done when

      - [ ] All W1 tasks complete per plan

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md

  - id: W2
    kind: issue
    repo: drivestream-lab/gateflow
    title: "[INIT-GATEFLOW-005-BOUNDINPUT W2] Multi-skill packaged dogfood"
    depends_on:
      - W1
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md
    verify_command: make check && make test ; .venv/bin/python -m tests.verify.verify_implement_lane
    status: Backlog
    tasks:
      - id: TASK-W2-01
        implements: [REQ-10]
        done_when: "Evidence for ≥2 orchestrated packaged skills with prompt_id/revision; no Gateflow allowlist"
      - id: TASK-W2-02
        implements: [REQ-10]
        done_when: "as-built + tests README INIT-005 complete; ground-ready"
    body: |
      ## Wave goal

      Broaden dogfood under pin orchestrated packaged skills; document multi-skill
      evidence; close as-built.

      ## Tasks (from plan §2) — stable ids for loop-spec / board

      | Task | Implements | Done when |
      |------|------------|-----------|
      | TASK-W2-01 | REQ-10 | Multi-skill prompt-id evidence |
      | TASK-W2-02 | REQ-10 | As-built complete |

      ## Done when

      - [ ] All W2 tasks complete per plan

      ## Spec reference

      docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md
```

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-implementation-plan
  outcome: pass
  artifact:
    path: docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-005-BOUNDINPUT.md
    digest: sha256:eb95eeaf0c84f76aa8c2d5b7c689fb75c5a2d14f01e34dbdc87e0f5a9ea3301d
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-005-BOUNDINPUT
    recovery: true
    prior_spec_pr: https://github.com/drivestream-lab/gateflow/pull/52
    prior_merge_sha: de396948056f3d7fb7da1c7918adfb8ad9914f87
    branch: chore/INIT-GATEFLOW-005-BOUNDINPUT-plan-gateflow
    waves: [W0, W1, W2]
    adr_007: docs/specification/adr/adr-007-invocation-brief-and-agent-message-contract.md
    adr_008: docs/specification/adr/adr-008-packaged-skill-handoff-ingest-authority.md
    board_name: drivestream-lab Board
    p14: pass
  next_candidates:
    - gate-2
  human_checkpoint: true
  external_action: true
```
