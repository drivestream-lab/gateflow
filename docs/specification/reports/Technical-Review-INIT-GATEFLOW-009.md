# Technical Design Document — INIT-GATEFLOW-009

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-009 |
| Spec | `docs/specification/product/INIT-GATEFLOW-009-gateflow.md` |
| Spec digest | `sha256:f4c93f4a13bb72617555fe320b3926130a0885ede45f9574c4ff1a09e2cad642` |
| Feasibility report | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-009.md` |
| Feasibility digest | `sha256:99dec941857a7e8112d9ec6d4b3821feca2b34f9019495a20a6a6ae0020caa31` |
| PRD digest | `sha256:76ab22b3c197b9d0cb6b08e6cea379c4e07b3a471b8a88203fddca6014c1c012` |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-009.md` / `1` |
| Repo scope digest | `sha256:d0a2b62632113db0fa64cb7d7e63dc393fa5a8217092dda242a99b3392978e9b` |
| Approved meta PR head | `6660aa4fefbcd80324cb970aa5bab642d3e5e0a1` |
| Source freshness | **CURRENT** — spec, feasibility, PRD digest, map revision 1, scope digest, and approved meta head match prior `initiative-feasibility` handoff |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-03 |
| Branch | `chore/INIT-GATEFLOW-009-spec-gateflow` (Draft spec PR — TDD published via Forge) |
| Initiative segment | `INIT-GATEFLOW-009` |
| Status | Draft |
| Review deadline | 2026-08-10 |
| Deciders | PE: @drivestream-lab/prayog-pe-team — explicit LGTM required, not approval by silence |

---

## 1. Problem statement

INIT-GATEFLOW-009 is a **factory prove-out**, not a greenfield feature build. Engineering
must confirm how existing control-plane modules (orchestrator, forge, lane starts,
closeout, verify scripts, CI) satisfy approved REQ-1…REQ-20 using pin `v0.5.0-rc.2` and
Accepted ADR-009/010 — then document W0–W3 execution boundaries, test policy, and the
four non-blocking PE questions (Q-1…Q-4) so `/spec-implementation-plan` can sequence
live dogfood without inventing architecture or product behavior.

---

## 2. Module / package boundaries

No new packages. Prove-out extends **existing** layers only.

| Module | Current state | Change | Owns |
|--------|---------------|--------|------|
| `.harness-pin.yaml` / `prayog-skills/` submodule | Pin `v0.5.0-rc.2` ≡ `72ad383` | **Consume only** — no pin redesign | Pin SSOT (CTR-01) |
| `src/business_services/run_orchestrator.py` | Walker, publish-before-ingest, automated/explicit EA | W1 live attestation; harden publish fail-closed (R-1) | Run lifecycle, stage commits |
| `src/business_services/forge_action_service.py` | Authorize + apply for explicit EA | W3 live `create_board_tickets` path | Forge mutate orchestration (CTR-03) |
| `src/business_services/wave_start_service.py` + `meta_pr_intake.py` | Spec start + meta accept-gate | W1 live verify only | Spec intake (ADR-010, CTR-04) |
| `src/api/routes/waves_routes.py` + closeout route | Spec/closeout starts | W2 live closeout dogfood | HTTP edge (CTR-04, CTR-05) |
| `src/infra_services/forge_client.py` | commit, open_draft_pr, branch tip | Unchanged transport | GitHub I/O (ADR-003) |
| `tests/verify/verify_spec_lane.py` | W1 Pass-1 scaffold | Live dogfood + docstring hygiene (AF-2) | Live verify contract (REQ-9) |
| `tests/verify/verify_wave_closeout.py` | W2 scaffold | Live dogfood | Live verify (REQ-10…12) |
| `docs/specification/reports/` | Feasibility + (this) TDD | W0 checklist, W1–W3 live-verify reports, freeze doc | Prove-out artifacts |
| `docs/specification/as-built/implementation-status.md` | Baseline + stale §006 rows (FF-02) | W0/W3 hygiene per AF-1 | As-built SSOT |
| `.github/workflows/ci.yml` | Placeholder echo | W3: real `make check-ci` + `make test` (Q-4) | CI gate (REQ-19…20) |

**Accepted ADR constraint set (full catalogue read — T2 Analyze):**

| ADR | Interaction with INIT-009 |
|-----|---------------------------|
| ADR-001 | Postgres run store — unchanged; learning ingest orthogonal to spec Pass-1 |
| ADR-002 | Programme token + forge trust — constrains authorize API (REQ-13…15) |
| ADR-003 | ForgeClient in infra — all GitHub I/O stays infra layer |
| ADR-004 | Programme config — no new config surface in prove-out |
| ADR-005 | Programme token on starts/authorize — **constrains** W3 authorize path |
| ADR-006 | Adapter registry — independent |
| ADR-007 | Bound prompt inputs — dual workspace bind keys for spec hops |
| ADR-008 | Handoff baton ingest — publish-before-ingest ordering with ADR-009 |
| ADR-009 | **Constrains** publish/mutate: automated `spec-pr-action`; explicit `board-tickets-action`; never `*-lgtm` |
| ADR-010 | **Constrains** spec meta intake, dual workspace, closeout Enter-at fixed |

**Boundary diagram (text):**

```
[POST /waves/spec/start] → meta_pr_intake (fail-closed)
  → run_orchestrator Pass-1 walker
       → [content hop] → ForgeClient.commit_workspace (required hops)
       → ingest handoff baton
       → resolve_next(pin outcome)
            ├── orchestrated skill → DISPATCH (spec-draft, initiative-feasibility, spec-technical-review)
            ├── automated EA (spec-pr-action) → apply open_draft_pr
            ├── manual skill (spec-implementation-plan) → STOP
            └── human-checkpoint (technical-review-approval) → STOP

[W1 attestation] verify_spec_lane → API + worker + postgres + forge creds

[W2] POST /waves/closeout/start → Pass-2 → learning-extract → ground-spec → wave-signoff STOP

[W3] explicit EA board-tickets-action STOP → POST /forge/authorize → create_board_tickets
```

---

## 3. Public interface contracts

### 3.1 `WaveStartService` → spec lane accept (ADR-010)

**Entry point:** `POST /api/v1/waves/spec/start`

**Arguments:**
- `meta_pr_url`: HTTPS GitHub PR URL — must resolve to approved meta head matching digests
- `meta_workspace`: absolute path to checked-out prayog-meta tree (read intake)
- `workspace`: absolute app coding root (write target for forge publish)
- `initiative_id`, programme identity fields per existing wave-start model

**Return:**
- `202` + `run_id` on success
- `4xx` on precondition fail — **0 enqueue** (REQ-3 negative path)

**Invariants:**
- Meta accept-gate fail-closed before AgentRunner dispatch
- Persist `meta_pr_url` / `meta_head_sha` on run for audit

### 3.2 `RunOrchestrator` → post-hop publish (ADR-009)

**Method:** `_publish_stage_workspace_if_needed(run, stage, handoff)`

**Arguments:**
- Run head ref from job context
- Pin `forge.commit_workspace` mode (`required` | `optional` | `disabled`)
- Collectable workspace paths per ADR-009 path class

**Return:** commit SHA on success; no-op when optional + empty

**Errors:** required-empty → terminal fail closed (REQ-4 negative)

**Invariants:** publish **before** handoff ingest on same hop

### 3.3 `ForgeActionService` → explicit authorize apply (ADR-009, REQ-13…15)

**Entry point:** `POST /api/v1/runs/{id}/forge/authorize` with `authorized: true`

**Pending node (W3 default):** `board-tickets-action` with `forge.action: create_board_tickets`

**Arguments (merged pin ⋉ handoff):**
- `initiative`: initiative segment string
- `plan_path`: path to implementation plan markdown on workspace head

**Return:** board issues created (EPIC + wave Features) when WorkManifest contract passes

**Errors:** deny / wrong state / incomplete requires / WorkManifest reject → no side effect

**Invariants:**
- Worker path never calls board mutate (FR-24 isolation preserved)
- `board-tickets-action` remains **`authorization: explicit`** — never automated

### 3.4 `verify_spec_lane` → W1 prove-out contract (REQ-9)

**Entry point:** `python -m tests.verify.verify_spec_lane` (opt-in via `tests/config.yaml`)

**Preconditions:** API + worker + migrated Postgres; programme token; `features.spec_lane.enabled`

**Asserts when run:**
- Spec start accepted; timeline includes `api_trigger`
- Cursor stages for executed hops in `_SPEC_HAPPY_CHAIN` succeed
- Terminal `stopped` at node ∈ `_SPEC_STOP_NODES`
- `pr_number` present when walker reached `spec-pr-action`
- Stop reason + handoff context emitted on `run_stopped` event

**Invariants:** script is live-verify only — not a substitute for unit coverage (FF-06)

### 3.5 Closeout start → Pass-2 (ADR-010 §6, REQ-10…12)

**Entry point:** `POST /api/v1/waves/closeout/start`

**Arguments:** existing PR bind + workspace; Enter-at fixed `learning-extract`

**Return:** new `run_id`; Pass-2 timeline to `wave-signoff` STOP

**Invariants:** does not resume Pass-1 run; meta fields not required for spec closeout

---

## 4. ADR resolutions

Feasibility F13: **no NEW-ADR** — prove-out consumes Accepted ADR-009/010 and pin SSOT.
Informational feasibility findings map to TDD-only or planned-auto-fix dispositions.

| Finding | Classification | ADR file / TDD section | product_constraints | Product exclusions | Recommendation / default | Status | Digest |
|---------|----------------|------------------------|---------------------|--------------------|--------------------------|--------|--------|
| (none) | — | — | — | — | No NEW-ADR required | N/A | N/A |
| FF-01 | TDD_ONLY | §9 PE-01 | `[REQ-2]` | W0 checklist content (meta preconditions, reviewer steps) | Deliver `W0-Prove-Out-Checklist-INIT-GATEFLOW-009.md` under reports in W0 | Resolved | N/A |
| FF-02 | planned-auto-fix | §12 AF-1 | `[REQ-18]` | — | Update as-built §006 stale rows during W0/W3 prove-out | Planned | N/A |
| FF-03 | TDD_ONLY | §9 PE-04 / §5 | `[REQ-19, REQ-20]` | Branch-protection settings | Replace CI placeholder per Q-4 | Resolved | N/A |
| FF-04 | TDD_ONLY | §5 / §9 | `[REQ-8, REQ-12, REQ-15]` | — | Live prove-outs are W1–W3 deliverables; baseline deferred is expected | Resolved | N/A |
| FF-05 | TDD_ONLY | §9 PE-03 | `[REQ-16, REQ-17, REQ-18]` | Proven/deferred feature naming | Standalone freeze doc path per Q-3 | Resolved | N/A |
| FF-06 | TDD_ONLY | §5 | `[REQ-9]` | — | Unit covers APIs/orchestrator; verify covers end-to-end lane journey — intentional split | Resolved | N/A |

**Derived counts:**

- ADR_REQUIRED: **0**
- TDD_ONLY: **5**
- DEFERRED_WITH_DEFAULT: **0**
- Draft ADR files created: **0**
- Missing/broken ADR files: **0**

---

## 5. Test policy

| Module / area | Unit layer tests | Integration layer | Live verify | Golden test strategy |
|---------------|-----------------|-------------------|-------------|----------------------|
| Pin load / handoff workflow | `test_handoff_workflow`, `test_forge_policy` | — | — | exact graph edges |
| Meta intake | `test_meta_pr_intake`, `test_wave_start` | — | `verify_spec_lane` | exact 4xx on reject |
| Publish-before-ingest | `test_publish_stage_workspace_*` | — | W1 dogfood | exact fail-closed on required-empty |
| Automated spec-pr | `test_forge_action_service`, orchestrator | — | W1 dogfood | exact PR bind + labels |
| Spec Pass-1 stop | `test_run_orchestrator`, `test_trigger_policy` | — | `verify_spec_lane` | exact stop node set |
| Closeout Pass-2 | `test_wave_closeout`, learning ingest unit | — | `verify_wave_closeout` | timeline stage names exact |
| Authorize explicit | `test_forge_action_service`, board isolation | — | W3 dogfood | side effect present/absent |
| WorkManifest gate | `test_forge_action_service` (prayog/v1) | — | W3 pre-check | subprocess exit code exact |
| CI replacement | — | — | GitHub Actions run on PR | job conclusion exact |
| W0 checklist | — | — | inspection | checklist sections present |

**Overlap policy (FF-06):** Unit tests prove module contracts in isolation; live verify
scripts prove cross-module journeys. No requirement to duplicate orchestrator assertions
inside `verify_spec_lane` beyond stop-node and timeline checks already scoped to REQ-9.

**AI-output determinism policy:** N/A — prove-out does not introduce new LLM output
contracts. Existing Cursor stage success is boolean + timeline evidence.

---

## 6. Error handling strategy

| Failure mode | Module where it originates | Propagation path | Recovery |
|--------------|---------------------------|------------------|----------|
| Meta accept mismatch | `meta_pr_intake` | 4xx to API caller; 0 enqueue | terminal — fix meta head/digest |
| Required-empty publish | `run_orchestrator` publish | run failure; no ingest advance | terminal — content skill must produce files |
| Forge I/O error mid-walk | `forge_client` / orchestrator | run failure recorded | terminal — retry new run; incomplete tip ≠ W1 success (REQ-8) |
| Incomplete `handoff.forge` requires | forge merge | fail closed before EA apply | terminal — fix handoff envelope |
| Authorize deny / wrong state | `forge_action_service` | 4xx/409; no board mutate | recoverable — human may re-authorize when preconditions met |
| WorkManifest contract fail | board-tickets pre-check | authorize path rejects | terminal until plan §9 fixed |
| CI toolchain fail | GitHub Actions | workflow conclusion failure | recoverable — fix code and push |
| Empty Draft Spec PR | spec-pr-action / inspection | W1 attestation fails | terminal — not initiative success (REQ-8) |

---

## 7. Observability contract

| Module | Log level | Structured fields | Notes |
|--------|-----------|-------------------|-------|
| `run_orchestrator` | INFO stage transitions; ERROR on fail | `run_id`, `stage`, `outcome`, `stop_node` | REQ-7/REQ-13 stop reason on timeline |
| `forge_action_service` | INFO on apply; ERROR on I/O | `run_id`, `forge.action`, `authorization` | Distinguish automated vs explicit paths |
| `meta_pr_intake` | WARNING on reject | `meta_pr_url`, `expected_head`, `initiative_id` | No secrets in logs |
| `verify_spec_lane` | INFO milestones | `run_id`, `pr_number`, `stop_node`, handoff excerpt | Prints stop context for ops portal parity (REQ-9) |
| CI workflow | GitHub Actions default | job name **`ci`** must remain stable | REQ-20 branch-protection compatibility |

---

## 8. Data contract ownership

| Schema / data type | Owner (defines + validates) | Validation layer | Versioning |
|--------------------|----------------------------|------------------|------------|
| Handoff envelope `sdd-delivery/v2` | prayog-skills delivery contract | orchestrator ingest (ADR-008) | pin version family |
| Wave start request bodies | product INIT + OpenAPI models | API edge (Pydantic) | additive only |
| Run timeline events | Gateflow ORM + emitter | repository persist | append-only |
| WorkManifest `prayog/v1` | pin `workmanifest_contract.py` | subprocess before board create | pin SSOT — Gateflow does not fork schema |
| Feature readiness freeze tables | prove-out report (REQ-16) | PE inspection at W3 | amend-by-PE when capabilities change |
| W0 checklist preconditions | prove-out report (REQ-2) | PE inspection before W1 | single INIT revision |

---

## 9. Resolved engineering decisions

All feasibility PE-lane items resolved. Defaults from feasibility adopted unless noted.

| Finding ID | Owner | Status | Question | Resolution | Required by | Default if deferred | Evidence / reference |
|------------|-------|--------|----------|------------|-------------|---------------------|----------------------|
| Q-1 | PE | **resolved** | W1 minimum path: feasibility → technical-review vs stop at plan? | On pin `v0.5.0-rc.2`, **`initiative-feasibility` outcomes `pass` and `findings` both route to orchestrated `spec-technical-review`**. W1 minimum orchestrated chain is `spec-draft` → automated `spec-pr-action` → `initiative-feasibility` → **`spec-technical-review`**. Honest Pass-1 stop after orchestrated content hops is **`technical-review-approval`** (human-checkpoint). `spec-implementation-plan` is valid only **after** PE accepts TDD at that checkpoint and a human invokes the manual plan skill — not as a W1 substitute that skips technical review. | W1 verify | Follow `_SPEC_HAPPY_CHAIN` in `verify_spec_lane.py` | `workflow.yaml` L148–167; `verify_spec_lane.py` L58–72 |
| Q-2 | PE | **resolved** | W3 authorize side-effect target | **`board-tickets-action`** with `forge.action: create_board_tickets`. Preconditions: spec PR merged, implementation plan current, WorkManifest `prayog/v1` pass. Deny/wrong-state paths must show **no** ticket side effect. | W3 live verify | Same default (A-8) | `workflow.yaml` L219–235; REQ-13…15 |
| Q-3 | PE | **resolved** | Freeze record location | Canonical standalone **`docs/specification/reports/Feature-Readiness-INIT-GATEFLOW-009.md`** with proven/deferred feature tables (REQ-16 headline language). **`implementation-status.md`** gains a summary row linking to that doc (REQ-18). REQ-17 planning-note checklist item lives **inside** the freeze package. | W3 | Standalone report + as-built row | REQ-16…18 |
| Q-4 | PE | **resolved** | CI minimum bar for REQ-19 | Single job named **`ci`** on `ubuntu-latest`: checkout → Poetry install → **`make check-ci`** then **`make test`**. No branch-name lint job in W3 scope. Replace placeholder echo only; do not invent branch-protection settings (REQ-20). | W3 CI PR | `make check` + `make test` | `Makefile` L6–29; `.github/workflows/ci.yml` |
| PE-01 | PE | **resolved** | W0 checklist artifact shape | Markdown under `docs/specification/reports/` named `W0-Prove-Out-Checklist-INIT-GATEFLOW-009.md` covering REQ-2 bullets (meta preconditions, dual workspace, programme token, reviewer tip inspection, verify config knobs). | W0 | Same path | REQ-2; FF-01 |
| PE-02 | PE | **resolved** | Publish hardening (R-1) | On publish I/O or blocked-handoff edge cases, preserve **fail-closed** semantics per ADR-009; re-run `verify_spec_lane` after any publish fix. No new retry policy beyond existing orchestrator failure recording. | W1 | Fail closed | Feasibility R-1 |
| PE-03 | PE | **resolved** | W2 before W3 sequencing | Spec closeout live prove-out (REQ-10…12) **must complete before** W3 authorize dogfood — lifts INIT-007 REQ-15 deferral for this programme exit (REQ-11). No PE waiver. | Plan W2→W3 | W2 first | Feasibility R-3; REQ-11 |

---

## 10. Routed out — product questions (PM)

No blocking PM questions. Product behavior is fully specified in approved REQ-1…REQ-20
on meta PR #23 head `6660aa4…`.

| ID | Owner | Status | Question | Blocking | Required by | Default if deferred | Evidence | Resolution reference |
|----|-------|--------|----------|----------|-------------|---------------------|----------|----------------------|
| — | — | — | None | no | — | — | Spec §Functional requirements | [meta PR #23](https://github.com/drivestream-lab/prayog-meta/pull/23) |

---

## 11. Routed out — domain clarifications (SME)

Factory prove-out — no business source-of-truth gaps.

| ID | Owner | Status | Question | Blocking | Required by | Default if deferred | Evidence | Resolution reference |
|----|-------|--------|----------|----------|-------------|---------------------|----------|----------------------|
| — | — | — | None | no | — | — | Feasibility §Domain | N/A |

---

## 12. Fix disposition

| ID | Status | Item | Target/evidence | Result digest |
|----|--------|------|-----------------|---------------|
| AF-1 | planned-auto-fix | As-built §006 stale rows (orchestrated spec-draft; meta Alembic applied) | `implementation-status.md` L174–185 vs pin + migration `1cd9a83a94a2` | N/A — during W0/W3 prove-out |
| AF-2 | planned-auto-fix | `verify_spec_lane.py` module docstring L5–8 contradicts `_SPEC_HAPPY_CHAIN` / pin | `tests/verify/verify_spec_lane.py` | N/A — align to Q-1 resolution during W1 prep |

---

## 13. Implementation readiness verdict

| Gate | Status |
|------|--------|
| All T1–T12 checks | **PASS** |
| Engineering decisions resolved | **7 resolved**, **0 deferred** (Q-1…Q-4 + PE-01…03) |
| Draft ADR files written | **0 / 0 required** |
| Product-boundary integrity (T12) | **PASS** — no user-visible behavior invented; all decisions cite REQ-* |
| PM questions outstanding | **0** |
| Domain questions outstanding | **0** |
| Selected workflow outcome | **`pass`** — zero blocking PE findings; no NEW-ADR; Q-1…Q-4 resolved; T12 clean |
| Ready for PE review | **YES** |
| **Ready for /spec-implementation-plan** | **NO — final exact-head PE approval required** |

---

## Check summary

| Check | Status | Notes |
|-------|--------|-------|
| T1 Module boundaries | PASS | §2 table + diagram; no new packages |
| T2 Interface contracts | PASS | §3.1–3.5 name shapes, invariants, errors |
| T3 NEW-ADR dispositions | PASS | Zero NEW-ADR; FF-01…06 mapped |
| T4 Test policy | PASS | §5 unit vs live boundary + FF-06 overlap policy |
| T5 Error handling | PASS | §6 failure modes + propagation |
| T6 Observability | PASS | §7 log fields + timeline contract |
| T7 Data contract ownership | PASS | §8 schema owners + validation layers |
| T8 Dependency graph | PASS | No circular deps; layering matches ADR-003 |
| T9 Engineering questions zero | PASS | Q-1…Q-4 + PE items resolved in §9 |
| T10 PE review readiness | PASS | Draft TDD; `ready_for_pe_review: true`; not claiming plan readiness |
| T11 ADR artifact integrity | PASS | 0 ADR_REQUIRED files; no missing drafts |
| T12 Product-boundary integrity | PASS | Decisions bind REQ-* only; no spec amendment required |

---

## Forge / PR instructions

> Persist this TDD locally and publish via `/commit-workspace` (or Gateflow
> ForgeClient) to the **Draft spec PR** branch. Do **not** commit, push, open
> PRs, or apply labels inside this skill. PE reviews on the **same PR**.
> Gate 2 label stays **`spec-pending`** until the implementation plan exists.
> PE accepts architecture by publishing **Accepted** TDD/ADR files — not by
> setting `spec-lgtm` yet. CODEOWNERS may request PE review on `Technical-Review-*`.

```
Branch:   chore/INIT-GATEFLOW-009-spec-gateflow
PR title: "[INIT-GATEFLOW-009] Spec — both-lane factory prove-out (gateflow)"
PR body:  link meta PRD PR; paste §13 Implementation readiness verdict when TDD is ready

Required reviewers (enforced by CODEOWNERS when TDD file is present):
  @drivestream-lab/prayog-pe-team  ← must give explicit Approve, not just silence

Review deadline: 2026-08-10
PE review checklist (PE works through this on the spec PR):
  [ ] T1 Module boundaries — can I draw the box?
  [ ] T2 Interface contracts — are shapes and invariants specified?
  [ ] T3 ADR dispositions — N/A (0 required); TDD-only rationales valid
  [ ] T4 Test policy — is determinism policy acceptable?
  [ ] T9 Zero unresolved PE items?
  [ ] T11 ADR artifact integrity — 0 required files (confirm light-review path)
  [ ] T12 Product-boundary integrity — every user-visible statement cites approved REQ-*

PE action (artifact acceptance — mid-lane):
  Review/comment or Request changes → developer updates TDD files
  Explicitly state when decisions are ready for acceptance
  Developer/PE updates TDD Status → Accepted (no ADR files to promote)
  Publish acceptance package via Forge to spec branch (label remains spec-pending)

After artifact acceptance:
  → /spec-implementation-plan may run on the same branch
  → after plan on head: PE sets spec-lgtm + Approve + attestation
  → Ready for review → merge → W0–W3 live prove-out per plan
```

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-technical-review
  outcome: pass
  artifact:
    path: docs/specification/reports/Technical-Review-INIT-GATEFLOW-009.md
    digest: sha256:7ec5a04c91ef9e6dfd68dbafc8c58619bf2a109eb32700a537b9d3dba64cd911
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-009
    ticket: "271562"
    meta_pr: "https://github.com/drivestream-lab/prayog-meta/pull/23"
    meta_pr_head: "6660aa4fefbcd80324cb970aa5bab642d3e5e0a1"
    map_revision: 1
    prd_digest: "sha256:76ab22b3c197b9d0cb6b08e6cea379c4e07b3a471b8a88203fddca6014c1c012"
    scope_digest: "sha256:d0a2b62632113db0fa64cb7d7e63dc393fa5a8217092dda242a99b3392978e9b"
    spec_digest: "sha256:f4c93f4a13bb72617555fe320b3926130a0885ede45f9574c4ff1a09e2cad642"
    feasibility_digest: "sha256:99dec941857a7e8112d9ec6d4b3821feca2b34f9019495a20a6a6ae0020caa31"
    source_freshness: CURRENT
    new_adr: false
    adr_required_count: 0
    draft_adr_paths: []
    draft_adr_digests: []
    ready_for_pe_review: true
    ready_for_plan: false
    findings_critical: 0
    findings_should_fix: 0
    pe_questions_resolved: "Q-1,Q-2,Q-3,Q-4"
    pin_ref: v0.5.0-rc.2
    pin_sha: 72ad383a13499b7d4cc69ea5c44d30e9302d0685
    unit_tests_pass: 217
  next_candidates:
    - technical-review-approval
  human_checkpoint: true
  external_action: false
  forge:
    action: commit_workspace
```
