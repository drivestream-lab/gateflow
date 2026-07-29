## Pre-implement — drivestream-lab/gateflow / W2 — Multi-skill packaged dogfood

Produced by `/pre-implement` on 2026-07-29 for **INIT-GATEFLOW-005-BOUNDINPUT** (board [#57](https://github.com/drivestream-lab/gateflow/issues/57)).
**No product code in this stage.**

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.

| Item | Required | Status |
|------|----------|--------|
| Branch context | `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | **ok** — workspace on `develop`; cut `feature/INIT-GATEFLOW-005-w2-dogfood` for coding |
| Spec PR merged | Implementation plan on integration branch | **yes** — `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-005-BOUNDINPUT.md` on `develop` (package [#52](https://github.com/drivestream-lab/gateflow/pull/52); plan recovery [#53](https://github.com/drivestream-lab/gateflow/pull/53); digest backfill `113a7f2`) |
| Gate 2 at merge | Merged spec PR had `spec-lgtm` on head | **verified** — [#52](https://github.com/drivestream-lab/gateflow/pull/52) label `spec-lgtm`, merge `de396948…` |
| Board seed | Wave issue(s) from plan §9 exist; TASK ids present; sub-issues of EPIC | **seeded** — EPIC [#54](https://github.com/drivestream-lab/gateflow/issues/54); W0 [#55](https://github.com/drivestream-lab/gateflow/issues/55) CLOSED; W1 [#56](https://github.com/drivestream-lab/gateflow/issues/56) CLOSED; W2 [#57](https://github.com/drivestream-lab/gateflow/issues/57) OPEN — #57 parent = #54; body lists TASK-W2-01…02 |
| Plan source freshness | all upstream rows `CURRENT` | **current** — product `sha256:5a2bb496…`, feasibility `sha256:4aa8038c…`, TDD `sha256:1493c3f7…` match plan § Source freshness (verified `shasum -a 256` on `develop`) |
| Impact-map repo scope | revision and scope digest match canonical handoff | **match** — plan records revision **1**, scope `sha256:2cc5e215…`, meta head `0b6b11e4…`; no local `prayog-meta/` clone |
| `check_command` | resolved | **`make check`** |
| `test_command` | resolved | **`make test`** |
| `verify_command` | resolved or N/A with reason | **resolved** — plan W2: `make check && make test` ; live multi-skill: `.venv/bin/python -m tests.verify.verify_implement_lane` (opt-in; not in `verify_all`) |
| `ground_command` | resolved or N/A with reason | **N/A** — no Makefile ground target; post-wave `/ground-spec` |
| Prior wave as-built row | `human_approved` | **INIT-005 W1 = human_approved** (2026-07-28) in `docs/specification/as-built/implementation-status.md` |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | **exists** — `docs/specification/reports/Ground-Report-INIT-GATEFLOW-005-BOUNDINPUT-W1.md` (**human_approved**) |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | **complete** (N/A as W2 gate — prior wave approval is the gate) |

**Gate verdict:** PASS — W1 Ground Report + as-built `human_approved`; plan on `develop` with CURRENT digests; board seeded; commands resolved.

---

### Contracts consumed (from prior Ground Report)

> Source: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-005-BOUNDINPUT-W1.md` §Contracts produced.
> Confirmed against `src/` on `develop` (not spec alone).

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Stored-path handoff ingest | `HandoffReader.read_path` | filesystem path string | `HandoffEnvelope` or fail closed | Ground-Report-005-W1 | **yes** — `src/business_services/handoff_reader.py` |
| Packaged automate ingest SSOT | `RunOrchestrator._ingest_handoff_after_stage` | stored `handoff_path` + expected stage id | envelope; stage must match node | Ground-Report-005-W1 | **yes** — calls `read_path` only; no ambient fallback (`run_orchestrator.py` ~L680–699) |
| Dual-run baton isolation | path formula `{GATEFLOW_HANDOFF_ROOT}/{run_id}/handoff.md` | two run ids, shared coding workspace | each `read_path` returns own envelope | Ground-Report-005-W1 | **yes** — `tests/unit/test_handoff_workflow.py::test_dual_run_isolation_distinct_handoff_paths` |
| W0 — PromptResolver + thin Cursor | `PromptResolver.bind_and_render` → `CursorAgentRunner.run_skill` | skill_id + bind map | rendered message; stage `prompt_id` / `prompt_revision` | Ground-Report-005-W0 (retained) | **yes** — unchanged substrate |
| W0 — baton define/store | `RunOrchestrator._ensure_run_handoff_path` | run id + `GATEFLOW_HANDOFF_ROOT` | non-empty `runs.handoff_path` | Ground-Report-005-W0 (retained) | **yes** |
| W0 — wave-start ticket | `WaveStartService` / implement start | non-empty `ticket_id` | bind `ticket` | Ground-Report-005-W0 (retained) | **yes** |
| Implement-lane verify harness | `tests.verify.verify_implement_lane` | `features.implement_lane` opt-in | asserts four lane nodes + prompt fields | Ground-Report-005-W1 | **yes** — harness present; **full chain not green** (D-W1-V1) |

**Legacy ambient scan:** Ground Report W1 documents `HandoffReader.find_latest_handoff` as debug-only. **Not present** in current `handoff_reader.py` on `develop` (removed during INIT-006 cleanup) — packaged automate path never depended on it post-W1; **no drift risk for W2**.

**Unconfirmed contracts** (carry-forward — not blocking W2 unit/docs start):

| ID | Risk | W2 action |
|----|------|-----------|
| D-W1-V1 / D-W0-V1 | Live implement-lane stops after hop-1 on empty baton | Close with multi-skill live verify + pin baton dual-write (see below) |
| D-W0-B1 | Agent did not write envelope to `{{handoff_path}}` after Cursor success | Pin `pre-implement` template **now** includes baton write instructions (`prayog-skills/skills/development/pre-implement/prompts/template.md` §Handoff baton); W2 dogfood must prove ≥2 hops write durable envelopes |

**Pin orchestrated skills (implement lane — SSOT for W2 scope, no Gateflow allowlist):**

| Node id | Pin location | `dispatch` |
|---------|--------------|------------|
| `pre-implement` | `prayog-skills/workflow.yaml` | orchestrated |
| `loop-spec` | same | orchestrated |
| `verify` | same | orchestrated |
| `ground-spec` | same | orchestrated |

W2 requires evidence for **≥2** of these with non-null `prompt_id` / `prompt_revision` matching pin packages (TASK-W2-01).

---

### Must read

- [x] `AGENTS.md`
- [x] MDC rules (domain-filtered for W2 verify extension / dogfood / SDD — no new API or DDL expected):
  - [x] `.cursor/rules/testing-verify-flows.mdc` — live verify vs unit separation; implement-lane opt-in
  - [x] `.cursor/rules/spec-driven-development.mdc` — as-built + same-PR docs (TASK-W2-02)
  - [x] `.cursor/rules/fail-fast.mdc` — no Gateflow skill allowlist; pin is SSOT
  - [x] `.cursor/rules/architecture.mdc` — W2 touches verify + docs primarily; retain layering
  - [x] `.cursor/rules/dependency-injection.mdc` — no new services expected
  - skipped: `http-api-conventions`, `database-migrations`, `infra-services`, `repository-pattern`, `pydantic-schemas`, `logging-loguru`, `python-tooling`, `python-imports`, `strong-typing`, `code-guidelines-index` (index only — not in W2 touch set)
- [x] ADRs (keyword-matched):
  - [x] **ADR-006** — adapter/dispatch selection; pin walker SSOT; **no PolicyEngine skill allowlist in Gateflow** — **Accepted**
  - [x] **ADR-007** — message-only Cursor; persist `prompt_id` / `prompt_revision` — **Accepted**
  - [x] **ADR-008** — stored-path ingest; baton dual-write prerequisite for multi-hop — **Accepted**
  - [x] ADR-001 — RunStore SSOT for locators — **Accepted** (cite)
  - [x] ADR-003 — business owns handoff orchestration — **Accepted** (cite)
  - skipped deep-read: ADR-002/004/005/009/010 (auth/token/forge/lane-intake — not W2 primary touch)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md` (W2 = REQ-10 multi-skill dogfood)
- [x] Plan wave section: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-005-BOUNDINPUT.md` Phase W2
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/57 — TASK list:
  - [ ] TASK-W2-01 — implements REQ-10 — done when evidence lists ≥2 orchestrated packaged skill ids with `prompt_id`/`prompt_revision`; pin remains SSOT; no Gateflow allowlist
  - [ ] TASK-W2-02 — implements REQ-10 — done when as-built W2 complete + `tests/README.md` BOUNDINPUT row final; ground-ready

---

### Governance alignment

- [x] Slice spec does not contradict ADR-006 (pin dispatch SSOT), ADR-007, or ADR-008
- [x] Plan TASK MDC notes / ADR notes for W2 reviewed (no allowlist; ADR-006)
- [x] ADR-007 / ADR-008 **Accepted** in `docs/specification/adr/` (digests match plan)

---

### Must update (in the same change as the code)

- [ ] `tests/verify/verify_implement_lane.py` and/or documented multi-skill verify mode — extend asserts for ≥2 lane skill ids (TASK-W2-01)
- [ ] `tests/README.md` — BOUNDINPUT feature map: multi-skill prompt-id evidence + live prerequisites
- [ ] `docs/specification/as-built/implementation-status.md` — INIT-005 W2 row → complete; close or document D-W1-V1 / D-W0-B1 status
- [ ] Product spec — only if W2 changes contract wording (unlikely; prefer as-built)
- [ ] ADR — **do not** edit Accepted ADR-006/007/008 unless PE supersedes

---

### Must not

- [ ] Add a Gateflow PolicyEngine allowlist of packaged skill ids (contradicts ADR-006 / plan W2)
- [ ] Reintroduce ambient `find_latest_handoff` as automate SSOT on packaged path
- [ ] Duplicate full live journey assertions inside unit tests
- [ ] Re-run `/create-board-tickets` (board already seeded #54–#57)
- [ ] Edit `postgres_migrations/versions/` (no new DDL expected for W2)
- [ ] Reintroduce invent-prose / Gateflow-authored brief in AgentRunner

---

### Engineering contracts (this wave)

| Concern | Entry point | Input | Output / invariant |
|---------|-------------|-------|--------------------|
| Multi-skill prompt telemetry | `RunOrchestrator` packaged automate path | pin node id per hop | each orchestrated stage persists `prompt_id` == node id, non-null `prompt_revision` |
| Live verify evidence | `tests.verify.verify_implement_lane` | opt-in `features.implement_lane` | documents ≥2 skill ids with prompt fields; full chain when baton writes succeed |
| Pin package SSOT | `PromptResolver` + pin tree | skill_id from walker | no hardcoded skill set in Gateflow business code |
| As-built closure | `implementation-status.md` | W2 matrix | INIT-005 W0→W2 complete or explicit deferral ids |

**Files (plan §2 W2):**

| ID | Path | Action |
|----|------|--------|
| FILE-W2-01 | `tests/verify/verify_implement_lane.py` (and/or sibling verify) | edit — multi-skill / broaden asserts |
| FILE-W2-02 | `tests/README.md`, `docs/specification/as-built/implementation-status.md` | edit — close INIT-005 |

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | format, lint, types, layers | `make check` |
| Unit | no regression on W0/W1 substrate | `make test` |
| Live verify | REQ-10 multi-skill dogfood; close D-W1-V1 if baton writes succeed | `.venv/bin/python -m tests.verify.verify_implement_lane` |
| Ground check | All W2 REQs; boundaries ADR-006/007/008 | `/ground-spec` (N/A Makefile) |

**Live prerequisites:** `make run` (API + worker), migrated Postgres, `PROGRAMME_SERVICE_TOKEN`, Gateflow runtime `CURSOR_API_KEY`, `GATEFLOW_HANDOFF_ROOT`, `tests/config.yaml` with `gateflow.require_worker: true` and `features.implement_lane.enabled: true`.

---

### Tracker / PR

- Initiative: **INIT-GATEFLOW-005-BOUNDINPUT**
- Issue: [#57](https://github.com/drivestream-lab/gateflow/issues/57)
- Epic: [#54](https://github.com/drivestream-lab/gateflow/issues/54)
- Spec path: `docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md`
- Plan: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-005-BOUNDINPUT.md` Phase W2
- Branch (plan): `feature/INIT-GATEFLOW-005-w2-dogfood`
- Verify command: `make check && make test` ; live `.venv/bin/python -m tests.verify.verify_implement_lane`
- ADRs in scope: **ADR-006** (primary), ADR-007, ADR-008, ADR-001, ADR-003

---

### Merge order (if cross-module / cross-service)

N/A — gateflow-only. Depends on W1 merged to `develop` (**done** — W1 human_approved). No cross-service calls in W2 slice.

---

### Next step (human)

1. Review this checklist.
2. Open branch `feature/INIT-GATEFLOW-005-w2-dogfood` from `develop`.
3. Move board [#57](https://github.com/drivestream-lab/gateflow/issues/57) to In Progress.
4. Run `/loop-spec` (or implement TASK-W2-01…02), then `/ground-spec` for W2.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-Checklist-INIT-GATEFLOW-005-BOUNDINPUT-W2.md
    digest: sha256:dd4f2918841e81632a3243a452214132637fee8b4521f39ef3603256f2d422e0
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-005-BOUNDINPUT
    wave: W2
    board_issue: https://github.com/drivestream-lab/gateflow/issues/57
    epic_issue: https://github.com/drivestream-lab/gateflow/issues/54
    tasks:
      - TASK-W2-01
      - TASK-W2-02
    implements_req: [REQ-10]
    carry_forward: [D-W1-V1, D-W0-B1, D-W0-V1]
    orchestrated_skills: [pre-implement, loop-spec, verify, ground-spec]
    check_command: make check
    test_command: make test
    verify_command: make check && make test ; .venv/bin/python -m tests.verify.verify_implement_lane
    ground_command: N/A
    prior_ground_report: docs/specification/reports/Ground-Report-INIT-GATEFLOW-005-BOUNDINPUT-W1.md
    branch_suggested: feature/INIT-GATEFLOW-005-w2-dogfood
    adr_primary: docs/specification/adr/adr-006-adapter-registry-fail-closed.md
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
```
