## Pre-implement — drivestream-lab/gateflow / W1 — Ingest-only handoff_path + dual-run isolation

Produced by `/pre-implement` on 2026-07-28 for **INIT-GATEFLOW-005-BOUNDINPUT**.
**No product code in this stage.**

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.

| Item | Required | Status |
|------|----------|--------|
| Branch context | `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | **ok** — workspace on `develop` (ahead of open `chore/*-spec-*`); cut `feature/INIT-GATEFLOW-005-w1-ingest` for coding |
| Spec PR merged | Implementation plan on integration branch | **yes** — `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-005-BOUNDINPUT.md` on `develop` via [#53](https://github.com/drivestream-lab/gateflow/pull/53) (`3b5af15`); prior package [#52](https://github.com/drivestream-lab/gateflow/pull/52) |
| Gate 2 at merge | Merged spec PR had `spec-lgtm` on head | **verified** — [#52](https://github.com/drivestream-lab/gateflow/pull/52) label `spec-lgtm`, head `4acd609…`, merge `de39694…`; plan recovery [#53](https://github.com/drivestream-lab/gateflow/pull/53) Approved on tip `4952a7b…` then merged (label empty on #53 — recovery process; board-seed + W0 already shipped) |
| Board seed | Wave issue(s) from plan §9 exist; TASK ids present; sub-issues of EPIC | **seeded** — EPIC [#54](https://github.com/drivestream-lab/gateflow/issues/54); W0 [#55](https://github.com/drivestream-lab/gateflow/issues/55) CLOSED; W1 [#56](https://github.com/drivestream-lab/gateflow/issues/56) OPEN; W2 [#57](https://github.com/drivestream-lab/gateflow/issues/57) OPEN — all parented under #54; W1 body lists TASK-W1-01…03 |
| Plan source freshness | all upstream rows `CURRENT` | **current** — product `sha256:5a2bb496…`, feasibility `sha256:e34b9f54…`, TDD `sha256:4feaf597…` match plan § Source freshness |
| Impact-map repo scope | revision and scope digest match canonical handoff | **match** — plan records revision **1**, scope `sha256:2cc5e215…`, meta head `0b6b11e4…` (attested on #52 Approve); no local `prayog-meta/` clone |
| `check_command` | resolved | **`make check`** |
| `test_command` | resolved | **`make test`** |
| `verify_command` | resolved or N/A with reason | **resolved** — plan W1: `make check && make test`; **carry-forward live** (D-W0-V1 / REQ-10): `.venv/bin/python -m tests.verify.verify_implement_lane` (opt-in; not in `verify_all`) |
| `ground_command` | resolved or N/A with reason | **N/A** — no Makefile ground target; post-wave `/ground-spec` |
| Prior wave as-built row | `human_approved` | **INIT-005 W0 = human_approved** (2026-07-28) in `docs/specification/as-built/implementation-status.md` |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | **exists** — `docs/specification/reports/Ground-Report-INIT-GATEFLOW-005-BOUNDINPUT-W0.md` (**human_approved**) |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | **complete** (N/A as W1 gate — prior wave approval is the gate) |

**Gate verdict:** PASS — W0 Ground Report + as-built `human_approved`; plan on `develop`; board seeded; upstream digests CURRENT.

---

### Contracts consumed (from prior Ground Report)

> Source: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-005-BOUNDINPUT-W0.md` §Contracts produced.
> Confirmed against `src/` on `develop` (not spec alone).

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Handoff root settings | `OrchestrationSettings.get_instance` | env absolute `GATEFLOW_HANDOFF_ROOT` | typed settings; relative/blank rejected | Ground-Report-005-W0 | **yes** — settings module used by wave-start / orchestrator baton path |
| Prompt package models | `src.models.prompt_package_models` | schema.yaml + bind fields | typed package / bind / render | Ground-Report-005-W0 | **yes** — includes required `handoff_path` on bind inputs |
| PromptResolver | `PromptResolver.resolve` / `bind_and_render` | skill_id + bind map + pin tree | `prompt_id`, revision, rendered message | Ground-Report-005-W0 | **yes** — `src/business_services/prompt_resolver.py` |
| Run baton define/store | `WaveStartService` / `RunOrchestrator._ensure_run_handoff_path` | run id + handoff root | non-empty `runs.handoff_path`; empty baton file ensured | Ground-Report-005-W0 | **yes** — define/store live; injects bind `handoff_path` |
| Thin Cursor dispatch | `RunOrchestrator` → `CursorAgentRunner.run_skill` | rendered `message` + runner/model | stage with `prompt_id` / `prompt_revision` / runner / model | Ground-Report-005-W0 | **yes** — message-only packaged path |
| RunStore columns | ORM + DTO + Alembic `69de74666068` | nullable text/varchar | `runs.handoff_path`; `stages.prompt_*` | Ground-Report-005-W0 | **yes** — schema/models present |
| Wave-start ticket | `POST /api/v1/waves/start` | non-empty `ticket_id` | bind `ticket` | Ground-Report-005-W0 | **yes** — blank rejected |
| Implement-lane verify harness | `tests.verify.verify_implement_lane` | `gateflow:` + `features.implement_lane` | asserts prompt fields + chain | Ground-Report-005-W0 | **yes** — harness present; **live green deferred to W1** (D-W0-V1) |

**W1 dependency — ambient ingest still SSOT (must change):**

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Post-stage handoff ingest (pre-W1) | `RunOrchestrator._ingest_handoff_after_stage` | workspace path or payload override | `HandoffEnvelope` | Ground-Report-005-W0 D-W0-I1 | **yes — drift expected** — still calls `HandoffReader.find_latest_handoff(Path(workspace_path))` at `src/business_services/run_orchestrator.py` (~L577–595); **no `read_path` yet** (`handoff_reader.py` only has `find_latest_handoff` / `parse_handoff_yaml`) |

**Unconfirmed contracts** (none blocking start — these are *this* wave’s deliverables):

- `HandoffReader.read_path(path)` — **not in source** (TASK-W1-01)
- Packaged automate ingest SSOT = stored `run.handoff_path` only — **not yet** (TASK-W1-02)
- Dual-run isolation fixture — **not yet** (TASK-W1-03)
- Live implement-lane green with ingest-from-stored-path — **open** (D-W0-V1, D-W0-B1, REQ-10)

**Carry-forward discrepancies from W0:**

| ID | Severity | W1 action |
|----|----------|-----------|
| D-W0-V1 | Medium | Close with live `verify_implement_lane` after ingest SSOT switch |
| D-W0-I1 | Low→blocking for W1 | Replace ambient call on packaged path |
| D-W0-B1 | Medium | Empty baton + agent write-to-path; couple with ingest fail-closed + prompt packages |

---

### Must read

- [x] `AGENTS.md`
- [x] MDC rules (domain-filtered for W1 ingest / fail-closed / business / testing / SDD):
  - [x] `.cursor/rules/fail-fast.mdc` — no ambient fallback on missing path
  - [x] `.cursor/rules/architecture.mdc` — business owns handoff parse; layering
  - [x] `.cursor/rules/repository-pattern.mdc` — RunStore via repo only (no new ORM expected)
  - [x] `.cursor/rules/pydantic-schemas.mdc` — `HandoffEnvelope` / models in `src/models/`
  - [x] `.cursor/rules/testing-verify-flows.mdc` — dual-run unit + live verify separation
  - [x] `.cursor/rules/spec-driven-development.mdc` — as-built + same-PR docs
  - [x] `.cursor/rules/dependency-injection.mdc` — HandoffReader already `@inject` singleton
  - [x] `.cursor/rules/strong-typing.mdc` / `python-imports.mdc` — signatures + top-level imports
  - skipped: `http-api-conventions` (no route shape change), `database-migrations` (no new columns), `infra-services` (no runner change), `logging-loguru` (optional if new log lines), `code-guidelines-index` (index only)
- [x] ADRs (keyword-matched):
  - [x] ADR-008 — packaged-skill handoff ingest authority (automate SSOT = stored locator) — **Accepted**
  - [x] ADR-007 — brief ownership / message-only AgentRunner (retain; do not re-invent brief) — **Accepted**
  - [x] ADR-001 — RunStore SSOT for `handoff_path` locator durability — **Accepted** (cite)
  - [x] ADR-003 — handoff orchestration in business; AgentRunner in infra — **Accepted** (cite)
  - skipped deep-read: ADR-002/004/005/006 (auth / programme / token / dispatch allowlist — not W1 touch)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md` (W1 = REQ-8b + harden REQ-9)
- [x] Plan wave section: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-005-BOUNDINPUT.md` Phase W1
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/56 — TASK list:
  - [ ] TASK-W1-01 — implements REQ-8b, REQ-9 — done when `HandoffReader.read_path`; missing path fail closed
  - [ ] TASK-W1-02 — implements REQ-8b, REQ-9 — done when packaged automate ingest uses `read_path(run.handoff_path)` only — never ambient SSOT
  - [ ] TASK-W1-03 — implements REQ-8b — done when dual-run isolation fixture green; as-built W1 + `tests/README.md` updated

---

### Governance alignment

- [x] Slice spec does not contradict ADR-008 (Option B: stored locator only) or ADR-007
- [x] Plan TASK MDC notes / ADR notes for W1 reviewed (fail-fast; ADR-008)
- [x] ADR-007 / ADR-008 **Accepted** in `docs/specification/adr/` (digests match plan: `fd8f11f6…` / `cc940796…`)

---

### Must update (in the same change as the code)

- [ ] Product spec — `docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md` only if W1 changes contract wording (unlikely; prefer as-built)
- [ ] `docs/specification/as-built/implementation-status.md` — INIT-005 W1 verification row
- [ ] `tests/README.md` — BOUNDINPUT feature map: ingest-from-stored-path + dual-run isolation
- [ ] Unit — `tests/unit/test_handoff_workflow.py` (or sibling): `read_path`, missing path, ambient-not-called on packaged ingest, dual-run fixture
- [ ] Live verify — `.venv/bin/python -m tests.verify.verify_implement_lane` to close D-W0-V1 (plan W1 table is unit-only; Ground Report + as-built deferral make live an exit obligation for this wave)
- [ ] ADR — **do not** promote/edit Accepted ADR-007/008 unless PE supersedes

---

### Must not

- [ ] Implement ambient fallback “if stored path missing, glob workspace” on packaged automate (contradicts ADR-008 / REQ-8b)
- [ ] Call `find_latest_handoff` as SSOT from `_ingest_handoff_after_stage` on packaged path after W1
- [ ] Duplicate full live journey assertions inside unit tests
- [ ] Assume W0 live prove-it already green (it is **not** — D-W0-V1)
- [ ] Edit `postgres_migrations/versions/` (no new DDL expected for W1)
- [ ] Reintroduce invent-prose / Gateflow-authored brief in AgentRunner

---

### Engineering contracts (this wave)

| Concern | Entry point | Input | Output / invariant |
|---------|-------------|-------|--------------------|
| Path ingest | `HandoffReader.read_path` | absolute (or resolved) filesystem path to baton | `HandoffEnvelope` or fail closed (missing/unreadable/invalid YAML) |
| Orchestrator ingest | `RunOrchestrator._ingest_handoff_after_stage` (packaged automate) | run record with non-empty `handoff_path` | envelope from that path only; stage must match node; **no** `DEFAULT_ARTIFACT_GLOBS` / mtime discovery |
| Legacy ambient | `HandoffReader.find_latest_handoff` | workspace + optional globs | retained for legacy/debug **outside** packaged automate SSOT |
| Dual-run isolation | unit fixture under shared coding workspace root | two runs, distinct `{GATEFLOW_HANDOFF_ROOT}/{run_id}/handoff.md` | run A never ingests run B’s envelope |

**Files (plan §2 W1):**

| ID | Path | Action |
|----|------|--------|
| FILE-W1-01 | `src/business_services/handoff_reader.py` | edit — add `read_path` |
| FILE-W1-02 | `src/business_services/run_orchestrator.py` | edit — ingest SSOT switch |
| FILE-W1-03 | `tests/unit/test_handoff_workflow.py` (or sibling) | edit/create |
| FILE-W1-04 | `docs/specification/as-built/implementation-status.md`, `tests/README.md` | edit |

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | format, lint, types, layers | `make check` |
| Unit | `read_path` fail-closed; packaged ingest never ambient; dual-run isolation | `make test` |
| Live verify | Close D-W0-V1 / REQ-10 hop with stored-path ingest (opt-in) | `.venv/bin/python -m tests.verify.verify_implement_lane` |
| Ground check | All W1 REQs + carry-forward live; boundaries ADR-008 | `/ground-spec` (N/A Makefile) |

---

### Tracker / PR

- Initiative: **INIT-GATEFLOW-005-BOUNDINPUT**
- Issue: [#56](https://github.com/drivestream-lab/gateflow/issues/56)
- Spec path: `docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md`
- Plan: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-005-BOUNDINPUT.md` Phase W1
- Branch (plan): `feature/INIT-GATEFLOW-005-w1-ingest`
- Verify command: `make check && make test` ; live `.venv/bin/python -m tests.verify.verify_implement_lane`
- ADRs in scope: **ADR-008** (primary), ADR-007, ADR-001, ADR-003

---

### Merge order (if cross-module / cross-service)

N/A — gateflow-only. Depends on W0 already merged (`#59`). W2 blocked until this wave merges.

---

### Next step (human)

1. Review this checklist.
2. Open branch `feature/INIT-GATEFLOW-005-w1-ingest` from `develop`.
3. Move board [#56](https://github.com/drivestream-lab/gateflow/issues/56) to In Progress.
4. Run `/loop-spec` (or implement TASK-W1-01…03), then `/ground-spec` for W1.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-Checklist-INIT-GATEFLOW-005-BOUNDINPUT-W1.md
    digest: sha256:7834c671dc52a8c5f5a1175893839a44bacaae1e4110b5ee1dad2ac828447f07
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-005-BOUNDINPUT
    wave: W1
    board_issue: https://github.com/drivestream-lab/gateflow/issues/56
    epic_issue: https://github.com/drivestream-lab/gateflow/issues/54
    tasks:
      - TASK-W1-01
      - TASK-W1-02
      - TASK-W1-03
    implements_req: [REQ-8b, REQ-9]
    carry_forward: [D-W0-V1, D-W0-I1, D-W0-B1]
    check_command: make check
    test_command: make test
    verify_command: make check && make test ; .venv/bin/python -m tests.verify.verify_implement_lane
    ground_command: N/A
    prior_ground_report: docs/specification/reports/Ground-Report-INIT-GATEFLOW-005-BOUNDINPUT-W0.md
    branch_suggested: feature/INIT-GATEFLOW-005-w1-ingest
    adr_primary: docs/specification/adr/adr-008-packaged-skill-handoff-ingest-authority.md
  next_candidates:
    - loop-spec
  human_checkpoint: true
  external_action: false
```
