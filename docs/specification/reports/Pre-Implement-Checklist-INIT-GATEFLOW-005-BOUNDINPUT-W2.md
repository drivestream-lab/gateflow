## Pre-implement — drivestream-lab/gateflow / W2 — Multi-skill packaged dogfood

Produced by `/pre-implement` on 2026-07-29 for **INIT-GATEFLOW-005-BOUNDINPUT**.
**No product code in this stage.**

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.

| Item | Required | Status |
|------|----------|--------|
| Branch context | `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | **ok** — workspace on `develop` (`469d700`); cut `feature/INIT-GATEFLOW-005-w2-dogfood` for coding |
| Spec PR merged | Implementation plan on integration branch | **yes** — `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-005-BOUNDINPUT.md` on `develop` via [#53](https://github.com/drivestream-lab/gateflow/pull/53); spec package [#52](https://github.com/drivestream-lab/gateflow/pull/52) |
| Gate 2 at merge | Merged spec PR had `spec-lgtm` on head | **verified** — [#52](https://github.com/drivestream-lab/gateflow/pull/52) label `spec-lgtm`, head `4acd609…`, merge `de39694…` |
| Board seed | Wave issue(s) from plan §9 exist; TASK ids present; sub-issues of EPIC | **seeded** — EPIC [#54](https://github.com/drivestream-lab/gateflow/issues/54) OPEN; W0 [#55](https://github.com/drivestream-lab/gateflow/issues/55) CLOSED; W1 [#56](https://github.com/drivestream-lab/gateflow/issues/56) CLOSED; W2 [#57](https://github.com/drivestream-lab/gateflow/issues/57) OPEN (parent #54); W2 body lists TASK-W2-01…02 |
| Plan source freshness | all upstream rows `CURRENT` | **stale** — product spec digest matches; feasibility and TDD digests **drifted** after plan merge (see below) |
| Impact-map repo scope | revision and scope digest match canonical handoff | **match** — plan records revision **1**, scope `sha256:2cc5e215…`, meta head `0b6b11e4…`; no local `prayog-meta/` clone |
| `check_command` | resolved | **`make check`** |
| `test_command` | resolved | **`make test`** |
| `verify_command` | resolved or N/A with reason | **resolved** — plan W2: `make check && make test` ; `.venv/bin/python -m tests.verify.verify_implement_lane` (opt-in; not in `verify_all`) |
| `ground_command` | resolved or N/A with reason | **N/A** — no Makefile ground target; post-wave `/ground-spec` |
| Prior wave as-built row | `human_approved` | **INIT-005 W1 = human_approved** (2026-07-28) in `docs/specification/as-built/implementation-status.md` |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | **exists** — `docs/specification/reports/Ground-Report-INIT-GATEFLOW-005-BOUNDINPUT-W1.md` (**human_approved**) |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | **complete** (N/A as W2 gate — prior wave approval is the gate) |

**Source digest verification (on `develop` @ `469d700`):**

| Upstream | Plan § Source freshness | On-disk `sha256` | Match? |
|----------|-------------------------|------------------|--------|
| Product spec | `5a2bb496…` | `5a2bb4965b705911c8ffb0673ac1a8bf5cbe948f1b6376a4b29ea2a9e716a861` | **yes** |
| Feasibility | `e34b9f54…` | `4aa8038c2e13345dcfef78c92a6ce2617a30094e18a88d7344f27e3c8a4bfc2a` | **no** — `f49aab3` (2026-07-28) ADR-004 wording hygiene |
| Technical review | `4feaf597…` | `1493c3f7428c69fae937a6842f43f375d58daf7b197d78378b02a34ab4af7fa3` | **no** — same commit |
| Implementation plan (self) | handoff `eb95eeaf…` | `d6bc1daf21571e7c765b6c7776ae12502b4b96361b7d998504c3dcf0527d7527` | **no** — post-merge edits on `develop` |

**Gate verdict:** **BLOCKED (stale)** — plan § Source freshness table marks feasibility and TDD `CURRENT` but on-disk digests no longer match. Do **not** open the W2 coding branch or run `/loop-spec` until `/spec-implementation-plan` refreshes the freshness table (or equivalent PE-approved digest update on `develop`). All other gates pass (W1 `human_approved`, board seeded, commands resolved).

---

### Contracts consumed (from prior Ground Report)

> Source: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-005-BOUNDINPUT-W1.md` §Contracts produced.
> Confirmed against `src/` on `develop` @ `469d700` (not spec alone).

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Stored-path handoff ingest | `HandoffReader.read_path` | filesystem path string/Path | `HandoffEnvelope` or fail closed | Ground-Report-005-W1 | **yes** — `src/business_services/handoff_reader.py` |
| Packaged automate ingest SSOT | `RunOrchestrator._ingest_handoff_after_stage` | stored `handoff_path` + expected stage id | envelope; stage must match node | Ground-Report-005-W1 | **yes** — calls `read_path` only; no ambient SSOT |
| Legacy ambient scan | `HandoffReader.find_latest_handoff` | workspace root + optional globs | envelope from newest match | Ground-Report-005-W1 | **yes** — retained; not packaged automate SSOT |
| Dual-run baton isolation | path formula `{GATEFLOW_HANDOFF_ROOT}/{run_id}/handoff.md` | two run ids, shared workspace | each `read_path` returns own envelope | Ground-Report-005-W1 | **yes** — unit coverage per as-built |
| W0 substrate retained | `PromptResolver`, thin Cursor, define/store, ticket, RunStore columns | (see Ground-Report-005-W0) | — | Ground-Report-005-W1 | **yes** — unchanged on `develop` |
| Implement-lane verify harness | `tests.verify.verify_implement_lane` | opt-in live config | four-node chain + prompt fields | Ground-Report-005-W1 | **yes** — harness present; **live full chain not green** (D-W1-V1) |
| Pin dispatch SSOT (no skill allowlist) | `PolicyEngine.evaluate_dispatch` + `WorkflowEngine` | handoff stage/outcome + pin | dispatch only when pin `dispatch: orchestrated` | Ground-Report-005-W1 / ADR-006 | **yes** — `policy_engine.py` docstring; no skill-id allowlist in `src/` |
| Pin orchestrated implement-lane nodes | `prayog-skills/workflow.yaml` | stage/outcome transitions | `pre-implement`, `loop-spec`, `verify`, `ground-spec` | plan W2 / REQ-10 | **yes** — all four `dispatch: orchestrated` |

**Unconfirmed contracts** (carry-forward — W2 may close):

| ID | Contract gap | W2 relevance |
|----|--------------|--------------|
| D-W1-V1 | Live implement-lane not green past hop-1 (ingest fail on empty baton) | **blocking for REQ-10 exit** — W2 dogfood + verify must prove ≥2 skills with prompt ids; full lane green is plan exit |
| D-W0-B1 | Agent did not write envelope to `handoff_path` after Cursor success | Pin package may now instruct baton dual-write (prayog-skills remount #69); re-prove on live run |
| D-W0-V1 | Alias of D-W1-V1 | Close with live verify |

No additional gateflow code contracts are missing for W2 start — W2 extends **evidence and docs**, not ingest substrate.

---

### Must read (when gate unblocked)

- [ ] `AGENTS.md`
- [ ] MDC rules (domain-filtered for W2 verify / live dogfood / SDD):
  - [ ] `.cursor/rules/testing-verify-flows.mdc` — live verify vs pytest separation; feature map
  - [ ] `.cursor/rules/spec-driven-development.mdc` — as-built + same-PR docs
  - [ ] `.cursor/rules/fail-fast.mdc` — no silent fallback on verify failures
  - [ ] `.cursor/rules/architecture.mdc` — business vs infra boundaries (verify scripts stay in `tests/`)
  - [ ] `.cursor/rules/strong-typing.mdc` / `python-imports.mdc` — if extending verify modules
  - skipped: `database-migrations`, `http-api-conventions`, `repository-pattern` (no new store/API shape expected)
- [ ] ADRs (keyword-matched):
  - [ ] **ADR-006** — adapter registry / dispatch SSOT = pin (no PolicyEngine skill allowlist) — **Accepted**
  - [ ] **ADR-007** — message-only AgentRunner; prompt package ownership — **Accepted** (retain)
  - [ ] **ADR-008** — stored-path ingest authority — **Accepted** (retain; W2 consumes)
  - skipped deep-read: ADR-001…005, ADR-009 (forge publish — not W2 primary touch)
- [ ] Spec: `docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md` (W2 = REQ-10 multi-skill dogfood)
- [ ] Plan wave section: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-005-BOUNDINPUT.md` Phase W2
- [ ] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/57 — TASK list:
  - [ ] TASK-W2-01 — implements REQ-10 — done when evidence lists ≥2 orchestrated packaged skill ids with `prompt_id` / `prompt_revision`; no Gateflow allowlist
  - [ ] TASK-W2-02 — implements REQ-10 — done when as-built INIT-005 complete + `tests/README.md` BOUNDINPUT row final; ground-ready

---

### Governance alignment

- [ ] Slice spec does not contradict ADR-006 (pin dispatch SSOT), ADR-007, or ADR-008
- [ ] Plan TASK MDC notes for W2 reviewed (“no skill allowlist in Gateflow”; ADR-006)
- [ ] ADR-006 / ADR-007 / ADR-008 **Accepted** in `docs/specification/adr/`

---

### Must update (in the same change as the code)

- [ ] Product spec — only if W2 changes contract wording (unlikely; prefer as-built)
- [ ] `docs/specification/as-built/implementation-status.md` — INIT-005 W2 verification row + capability matrix
- [ ] `tests/README.md` — BOUNDINPUT feature map: multi-skill prompt-id evidence; live verify mode documented
- [ ] Live verify — `tests/verify/verify_implement_lane.py` and/or documented multi-skill mode (TASK-W2-01)
- [ ] ADR — **do not** edit Accepted ADR-006/007/008 unless PE supersedes

---

### Must not

- [ ] Add a hardcoded skill-id allowlist in Gateflow (contradicts REQ-10 / ADR-006 / plan W2)
- [ ] Reintroduce ambient ingest as automate SSOT (ADR-008)
- [ ] Duplicate full live journey assertions inside unit tests
- [ ] Treat W1 live deferral (D-W1-V1) as closed without live evidence
- [ ] Implement before plan source freshness is refreshed

---

### Engineering contracts (this wave)

| Concern | Entry point | Input | Output / invariant |
|---------|-------------|-------|--------------------|
| Multi-skill dogfood evidence | `tests.verify.verify_implement_lane` (extend) or sibling verify | opt-in live config; pin orchestrated skills | evidence lists ≥2 skill ids each with non-null `prompt_id` + `prompt_revision` matching pin package |
| Dispatch eligibility | `PolicyEngine` + pin `workflow.yaml` | handoff + trigger | next skill only when pin declares `dispatch: orchestrated` — no repo skill list |
| Live lane chain | four pin nodes | wave-start → Cursor hops → ingest | terminal `stopped` at `wave-human-decision`; baton written at each orchestrated hop |
| Initiative closure docs | as-built + tests README | inspection | INIT-005 W0/W1/W2 rows complete; deferred items explicit or closed |

**Files (plan §2 W2):**

| ID | Path | Action |
|----|------|--------|
| FILE-W2-01 | `tests/verify/verify_implement_lane.py` and/or sibling verify | edit — multi-skill / prompt-id evidence |
| FILE-W2-02 | `tests/README.md`, `docs/specification/as-built/implementation-status.md` | edit — final BOUNDINPUT row |

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | format, lint, types, layers | `make check` |
| Unit | no regression on W0/W1 ingest + resolver substrate | `make test` |
| Live verify | REQ-10: ≥2 orchestrated skills with prompt ids; optional full implement-lane green (close D-W1-V1) | `.venv/bin/python -m tests.verify.verify_implement_lane` |
| Ground check | All W2 REQs + INIT-005 complete; boundaries ADR-006/007/008 | `/ground-spec` (N/A Makefile) |

**Live verify prereqs** (`tests/README.md` § Implement-lane): `GATEFLOW_HANDOFF_ROOT` absolute in `.env`; API + worker with `CURSOR_API_KEY`; `tests/config.yaml` `features.implement_lane.enabled: true`; human Alembic for prompt/handoff columns applied.

---

### Tracker / PR

- Initiative: **INIT-GATEFLOW-005-BOUNDINPUT**
- Issue: [#57](https://github.com/drivestream-lab/gateflow/issues/57)
- Spec path: `docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md`
- Plan: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-005-BOUNDINPUT.md` Phase W2
- Branch (plan): `feature/INIT-GATEFLOW-005-w2-dogfood`
- Verify command: `make check && make test` ; `.venv/bin/python -m tests.verify.verify_implement_lane`
- ADRs in scope: **ADR-006** (primary), ADR-007, ADR-008

---

### Merge order (if cross-module / cross-service)

N/A — gateflow-only. Depends on W1 merged to `develop` ([#63](https://github.com/drivestream-lab/gateflow/pull/63) @ `d719e34`).

---

### Remediation (stale gate)

1. Run `/spec-implementation-plan` on `develop` to refresh § Source freshness digests (feasibility, TDD, plan self-digest) after `f49aab3`.
2. Re-run `/pre-implement` for W2 — expect gate **PASS** if digests align.
3. Then open `feature/INIT-GATEFLOW-005-w2-dogfood`, move [#57](https://github.com/drivestream-lab/gateflow/issues/57) to In Progress, run `/loop-spec`.

---

### Next step (human)

**Blocked on stale plan inputs.** After freshness refresh:

1. Review this checklist.
2. Open branch `feature/INIT-GATEFLOW-005-w2-dogfood` from `develop`.
3. Move board [#57](https://github.com/drivestream-lab/gateflow/issues/57) to In Progress.
4. Run `/loop-spec` for TASK-W2-01…02, then `/ground-spec` for W2.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: stale
  artifact:
    path: docs/specification/reports/Pre-Implement-Checklist-INIT-GATEFLOW-005-BOUNDINPUT-W2.md
    digest: sha256:ead73b4ce877490762a54f5368137d779b5e7c94d936442fe83a9c41659d4de0
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
    stale_sources:
      - docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-005-BOUNDINPUT.md
      - docs/specification/reports/Technical-Review-INIT-GATEFLOW-005-BOUNDINPUT.md
    stale_commit: f49aab334c25707db46b63e7d2fdb0e003622b61
    plan_digest_on_disk: sha256:d6bc1daf21571e7c765b6c7776ae12502b4b96361b7d998504c3dcf0527d7527
    check_command: make check
    test_command: make test
    verify_command: make check && make test ; .venv/bin/python -m tests.verify.verify_implement_lane
    ground_command: N/A
    prior_ground_report: docs/specification/reports/Ground-Report-INIT-GATEFLOW-005-BOUNDINPUT-W1.md
    branch_suggested: feature/INIT-GATEFLOW-005-w2-dogfood
    adr_primary: docs/specification/adr/adr-006-adapter-registry-fail-closed.md
    gate_verdict: blocked_stale_plan_freshness
  next_candidates:
    - spec-implementation-plan
  human_checkpoint: false
  external_action: false
```
