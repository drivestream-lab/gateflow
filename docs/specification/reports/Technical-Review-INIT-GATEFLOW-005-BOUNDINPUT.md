# Technical Design Document — INIT-GATEFLOW-005-BOUNDINPUT

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-005-BOUNDINPUT |
| Spec | `docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md` |
| Spec digest | `sha256:5a2bb4965b705911c8ffb0673ac1a8bf5cbe948f1b6376a4b29ea2a9e716a861` |
| Feasibility report | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-005-BOUNDINPUT.md` |
| Feasibility digest | `sha256:e34b9f54fdb509cc4847f6300ae2c68546999485c68f781fca3a1c92499dd15a` |
| PRD digest | `sha256:40fb856dd5068290c1d14f010239e6206bee2625aaf6a6e3970d769e9bb5e970` |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-005-BOUNDINPUT.md` / `1` |
| Repo scope digest | `sha256:2cc5e2151451c47b973fdc86dafe19d5cb2fadd651212a5a00f9d681f274039b` |
| Approved meta PR head | `0b6b11e4470517842affb894d7ea581c3819ead3` |
| Source freshness | CURRENT — meta PR #16 head + APPROVED review `4788143334` + PRD/map/scope digests match spec + feasibility headers; Draft spec PR #52 |
| Repo | drivestream-lab/gateflow |
| Date | 2026-07-27 |
| Branch | `chore/INIT-GATEFLOW-005-BOUNDINPUT-spec-gateflow` (Draft spec PR #52) |
| Initiative segment | `INIT-GATEFLOW-005-BOUNDINPUT` |
| Status | **Accepted** — PE @nikd10x 2026-07-27 via Cursor chat (https://github.com/drivestream-lab/gateflow/pull/52); ADR-007 + ADR-008 Accepted (architecture-only Option B); product path/bind/columns remain TDD. **TDD_ONLY revision (same day):** Q-3 handoff baton uses configured `GATEFLOW_HANDOFF_ROOT`, not `{workspace}/.gateflow/` |
| Approval evidence | Explicit PE acceptance by @nikd10x on 2026-07-27 via Cursor chat on Draft spec PR #52; architecture package attested on tip; mid-lane only (not Gate 2) |
| Approved head | `a008af2f44c57204fb1dfd663cef40d266ff2ac6` |
| Review deadline | 2026-08-03 |
| Deciders | PE: @nikd10x / @drivestream-lab/prayog-pe-team |

---

## 1. Problem statement

Gateflow must consume pinned skill prompt packages for automated packaged-skill
runs: bind known context from wave-start, validate/render simple `{{var}}`,
dispatch **only** the rendered message through Cursor AgentRunner (remove
invent-prose), persist `prompt_id` / `prompt_revision` / runner / model, and own
a per-run `handoff_path` (define/store + ingest-only) — without rewriting
PolicyEngine, pin walker, or Live Cursor topology from INIT-001…003.

---

## 2. Module / package boundaries

| Module | Current state | Change | Owns |
|--------|---------------|--------|------|
| `src/business_services/prompt_resolver.py` | **new** | Resolve pin package, validate schema, render `{{var}}` | Brief construction (ADR-007) |
| `src/models/prompt_package_models.py` | **new** | Pydantic for schema.yaml + bind map + resolve result | Data contracts |
| `src/infra_services/cursor_agent_runner.py` | invent-prose `_build_prompt` | Accept pre-rendered `message`; remove packaged-skill invent-prose path | AgentRunner infra (ADR-003 / ADR-007) |
| `src/business_services/run_orchestrator.py` | ambient ingest + prompt_context JSON | Define/store `handoff_path`; bind → resolve → render → thin `run_skill`; persist prompt ids; W1 ingest from stored path | Run lifecycle (ADR-008 ingest authority) |
| `src/business_services/handoff_reader.py` | glob/mtime SSOT | Add `read_path(path)`; packaged automate must not use ambient as SSOT | Handoff parse (ADR-008) |
| `src/business_services/wave_start_service.py` | `ticket_id` optional | Reject empty `ticket_id` for packaged-skill automate before enqueue | Accept boundary |
| `src/models/adapter_models.py` | `WaveStartRequest` | Keep field name `ticket_id`; enforce non-empty for automate (service and/or model) | API body |
| `src/models/run_store_models.py` | no prompt/handoff fields | Add `handoff_path` on run; `prompt_id`/`prompt_revision` on stage | DTOs |
| `src/database/postgres/schema/run_store_schema.py` | missing columns | ORM columns matching DTOs | ORM |
| `src/database/postgres/repository/run_store_repository.py` | exists | Map new columns | Persistence |
| `postgres_migrations/versions/` | human-owned | Human Alembic for new columns | DDL (ADR-001) |
| `src/di/modules/business_services_module.py` | exists | Bind PromptResolver singleton | DI |
| `src/configs/orchestration_settings.py` (or sibling) | exists | Add required `GATEFLOW_HANDOFF_ROOT` | Handoff root config (TDD §3.4) |
| `src/business_services/policy_engine.py` | exists | **unchanged** — dispatch eligibility orthogonal | Pin walker |
| `tests/unit/test_prompt_resolver.py` | **new** | Resolve/validate/render/fail-closed/anti-hardcode | Unit |
| `tests/unit/test_handoff_workflow.py` | glob tests | Add `read_path` + isolation; stop treating ambient as automate SSOT | Unit |
| `tests/unit/test_cursor_agent_runner.py` | exists | Message-only path; invent-prose absent for packaged success | Unit |
| `tests/verify/verify_implement_lane.py` | live prove-it | Assert stage `prompt_id`/`prompt_revision` after orchestrated hop(s) | Live verify |
| `tests/README.md` | feature map | BOUNDINPUT row | Docs |

**Accepted ADR constraint set:**

| ADR | Interaction |
|-----|-------------|
| ADR-001 | Postgres RunStore + human Alembic for new columns |
| ADR-002 / ADR-005 | Programme-token wave-start zone unchanged |
| ADR-003 | AgentRunner stays **infra**; brief construction stays **business** (ADR-007) |
| ADR-004 | No programme.yaml revive; pin filesystem consume only (paths in TDD) |
| ADR-006 | Fail-closed honesty unchanged; Cursor-only this INIT |
| ADR-007 | **Accepted** — business owns invocation brief; AgentRunner message-only |
| ADR-008 | **Accepted** — packaged-skill automate handoff SSOT = run-stored Gateflow locator |

**Boundary diagram (text):**

```
POST /waves/start (programme token)
  → WaveStartService (require ticket_id; enqueue)
       └── RunStore create run + define handoff_path

[worker]
  RunOrchestrator
       ├── PolicyEngine (dispatch — unchanged)
       ├── PromptResolver (business)
       │     └── pin skills/.../prompts/{template.md,schema.yaml}
       ├── CursorAgentRunner.run_skill(message=rendered)  (infra)
       ├── persist stage prompt_id/prompt_revision + runner/model
       └── HandoffReader.read_path(run.handoff_path)   (W1 SSOT)
```

---

## 3. Public interface contracts

### 3.1 PromptResolver (business) — REQ-1…REQ-4

**Entry points (engineering names):**

| Method | Role |
|--------|------|
| `resolve_package(workspace_root, skill_id)` | Locate package under pin skills tree |
| `bind_and_render(package, bound_inputs)` | Validate against schema + render |

**`resolve_package` arguments:**
- `workspace_root`: absolute workspace path (run worker root)
- `skill_id`: pin node id (e.g. `pre-implement`)

**Search roots (while Launchpad sync is stub):** for each
`area ∈ {development, requirements}`, try
`{workspace_root}/prayog-skills/skills/{area}/{skill_id}/prompts/`.
First existing directory with both `template.md` and `schema.yaml` wins.
Missing → terminal fail closed (no AgentRunner).

**Return (resolve):**
- `prompt_id`: string from schema (must equal skill_id per upstream contract)
- `prompt_revision`: semver string from schema `revision`
- `template_text`: raw template
- `schema`: validated variable declarations

**`bound_inputs` shape (shared dictionary):**
- `ticket` (required string, non-empty)
- `initiative` (string; empty allowed)
- `skill_id` (required)
- `workspace` (required — workspace root string)
- `handoff_path` (required — stored run path string)

**Render invariants:**
- Simple `{{var}}` substitution only; no filters/conditionals
- Every template placeholder declared in schema; undeclared → fail closed
- Optional schema vars omitted → empty string
- Output message string is the sole AgentRunner message body

**Errors:** raise typed/domain errors (or `ValueError` with stable reason codes)
for missing package, invalid schema, bind failure — orchestrator maps to stage/run
`failed` with reason; **zero** AgentRunner calls.

### 3.2 RunOrchestrator → CursorAgentRunner (REQ-5)

**Method:** `run_skill`

**Arguments (packaged-skill automate path):**
- `workspace_path`: string
- `skill_id`: string (logging / agent name only — not for inventing prose)
- `message`: string — **exact** PromptResolver render output
- `model_profile`, `runner`, `model_id`, `model_provider`: as today

**Remove / forbid on packaged success path:**
- `CursorAgentRunner._build_prompt` invent-prose (skill brief + durable-handoff
  instructions authored by Gateflow)

**Return:** `AgentRunResult` unchanged (runner, outcome, model fields, error_message).

**Invariant:** packaged-skill automate ⇒ `message` non-empty and equal to render;
anti-hardcode unit fails if invent-prose helper is used when a package exists.

**Unit doubles:** `mock-*` skill ids may short-circuit without pin packages; not
REQ-10 evidence.

### 3.3 Wave-start bind (REQ-2, Q-1)

**Field mapping:**
- Bind `ticket` ← `WaveStartRequest.ticket_id` (required non-empty for automate)
- Bind `initiative` ← `initiative_id` (always present for wave identity today)
- Keep API JSON name **`ticket_id`** (no new `ticket` alias this INIT)

**Accept gate:** `WaveStartService` rejects blank/missing `ticket_id` before
enqueue when the start path will automate a packaged skill (all current
`dispatch: orchestrated` Enter-at starts). Structured 4xx with field name
`ticket_id`.

### 3.4 Handoff baton (REQ-8a / REQ-8b, Q-3)

**Authority (ADR-008):** packaged-skill automate ingest SSOT is a Gateflow-defined,
run-scoped locator stored on the run — not ambient glob/mtime discovery.

**Concrete representation (TDD_ONLY) — configured root, not the git workspace:**

Do **not** place batons under the coding workspace / repo tree (rejects
`{workspace}/.gateflow/...` as the default). Runtime state must not pollute the
agent cwd or risk accidental commit.

| Setting | Shape | Invariant |
|---------|-------|-----------|
| `GATEFLOW_HANDOFF_ROOT` | Absolute directory path (env; `OrchestrationSettings` or dedicated settings singleton via `get_instance()`) | **Required** for packaged-skill automate; fail closed at start / before define if unset or not an absolute writable directory |

```text
handoff_path = {GATEFLOW_HANDOFF_ROOT}/{run_id}/handoff.md
```

- Persist the resulting **absolute** path string on `runs.handoff_path`
- Ensure `{GATEFLOW_HANDOFF_ROOT}/{run_id}/` exists; create empty baton file if absent
- Inject stored value into bind map as `handoff_path` (agent writes here by absolute path; `workspace` bind remains the coding root — orthogonal)
- Local/dev example only: e.g. `/tmp/gateflow/handoffs` or a host data volume — **never** a path inside the cloned repo unless an operator explicitly sets that (discouraged)

**Ingest (W1):** `HandoffReader.read_path(handoff_path)` parses YAML handoff
envelope from that file only. Missing/unreadable → fail closed; **do not** call
`find_latest_handoff` for packaged-skill automate.

**Isolation:** path includes `run_id` under the configured root ⇒ concurrent runs
cannot share batons. Ambient `DEFAULT_ARTIFACT_GLOBS` may remain for legacy/debug
but is **not** automate SSOT.

### 3.5 RunStore persistence (REQ-6, REQ-7, Q-2)

| Location | Field | Type | Notes |
|----------|-------|------|-------|
| `runs` | `handoff_path` | text, nullable until set; required before packaged dispatch | Q-2 default |
| `stages` | `prompt_id` | text, nullable | set on automated packaged stages |
| `stages` | `prompt_revision` | text, nullable | set on automated packaged stages |
| `stages` | `runner`, `model_id`, … | exists | REQ-7 reuse |

Human Alembic revision owns DDL; agents update ORM/DTO only.

### 3.6 HandoffReader

| Method | Role |
|--------|------|
| `read_path(path)` | **new** — packaged automate SSOT |
| `find_latest_handoff(...)` | legacy/debug only — not automate SSOT after W1 |
| `parse_handoff_yaml` | unchanged |

---

## 4. ADR resolutions

Every feasibility `NEW-ADR` appears once. FF-06 is split into **two** architectural
decisions (brief/message ownership vs handoff ingest authority). Product path
strings, bind maps, column names, and pin search roots remain **TDD_ONLY** (§3, §9).

| Finding | Classification | ADR file / TDD section | Recommendation / default | Status | Digest |
|---------|----------------|------------------------|--------------------------|--------|--------|
| FF-06 (brief / runner) | ADR_REQUIRED | `docs/specification/adr/adr-007-invocation-brief-and-agent-message-contract.md` | Option B — business owns brief construction; AgentRunner message-only | Accepted | `sha256:fd8f11f61be203db409e1dc23df12f78f26dfe5b75c819fce22e0723b0225d89` |
| FF-06 (handoff authority) | ADR_REQUIRED | `docs/specification/adr/adr-008-packaged-skill-handoff-ingest-authority.md` | Option B — automate SSOT = Gateflow-defined run-stored locator; ambient not automate SSOT | Accepted | `sha256:cc94079602762d58622d321f4bdefacf2c54fcd0a6511da3415daacb48b52cad` |
| Q-3 path string | TDD_ONLY | §3.4 | `{GATEFLOW_HANDOFF_ROOT}/{run_id}/handoff.md` — required configured absolute root outside repo by default | Resolved | N/A |
| Q-1 / Q-2 / Q-4 / FF-05 / FF-09 / FF-02 / FF-03 | TDD_ONLY | §3 / §5 / §9 | Field maps, columns, prove-it, pin search roots, invent-prose removal shape | Resolved | N/A |

**Derived counts:**

- ADR_REQUIRED: 2
- TDD_ONLY: 7 (Q-1, Q-2, Q-3, Q-4, FF-05, FF-09, FF-02/03)
- DEFERRED_WITH_DEFAULT: 0
- Draft ADR files created: 2
- Missing/broken ADR files: 0

---

## 5. Test policy

| Module / area | Unit layer tests | Integration layer | Live verify | Golden test strategy |
|---------------|-----------------|-------------------|-------------|----------------------|
| PromptResolver | missing package, invalid schema, missing ticket, optional empty, undeclared `{{var}}`, happy render | optional fixture against real pin package files on disk (no network) | — | exact string match on render vs fixture `happy_path.expected.md` where useful |
| Anti-hardcode (REQ-5) | packaged path never calls invent-prose builder; message equals render | — | — | exact |
| Wave-start ticket | blank `ticket_id` → 4xx; no enqueue | — | `verify_wave_start` may supply ticket | exact status |
| RunStore fields | DTO/ORM mapping for new columns | — | — | exact |
| HandoffReader.read_path | reads only given path; dual-run isolation fixture | — | — | exact |
| CursorAgentRunner | accepts message; mock-* unchanged | — | — | exact |
| Prove-it (REQ-10) | — | — | Extend `verify_implement_lane` (Enter-at `pre-implement`): after hop(s), stage rows have non-null `prompt_id` + `prompt_revision` matching pin package | exact field presence; AI coding work remains live qualitative as today |

**AI-output determinism policy:**
- Prompt **render** output: exact (deterministic substitution).
- Cursor agent coding work / handoff prose: not exact-matched in unit tests;
  live prove-it asserts control-plane fields (`prompt_id`, `prompt_revision`,
  run outcome), not LLM text.

---

## 6. Error handling strategy

| Failure mode | Module where it originates | Propagation path | Recovery |
|--------------|---------------------------|------------------|----------|
| Package missing / schema invalid | PromptResolver | orchestrator → stage/run `failed` + notify | terminal — 0 AgentRunner |
| `GATEFLOW_HANDOFF_ROOT` unset / not absolute / not writable | Settings / define-handoff | fail closed at start or before define | terminal |
| Required bind miss (`ticket`, `handoff_path`) | WaveStartService / PromptResolver | 4xx at accept or stage `failed` | terminal |
| Undeclared template var / non-`{{var}}` | PromptResolver | stage `failed` | terminal |
| `handoff_path` unset at dispatch | RunOrchestrator | fail closed before AgentRunner | terminal |
| Handoff unreadable at stored path (W1) | HandoffReader.read_path | fail closed; no ambient fallback | terminal |
| AgentRunner timeout/crash | CursorAgentRunner | stage `failed`; no invent brief | terminal (inherit 003) |
| Concurrent active run | WaveStartService | HTTP 409 | terminal (inherit) |
| Auth reject | programme token dep | 401/403 | terminal (inherit) |

---

## 7. Observability contract

| Module | Log level | Structured fields | Notes |
|--------|-----------|-------------------|-------|
| PromptResolver | INFO on resolve success; WARNING/ERROR on fail closed | `skill_id`, `prompt_id`, `prompt_revision`, `workspace_path` | never log full secrets |
| RunOrchestrator | INFO stage start/complete | `run_id`, `workflow_node`, `prompt_id`, `prompt_revision`, `handoff_path` | |
| CursorAgentRunner | INFO/ERROR as today | `skill_id`, `runner`, `model_id`; **do not** log full message body at INFO in prod if large — DEBUG optional | |
| HandoffReader | INFO path selected | `path` (stored path) | no glob candidate spam on automate path |
| WaveStartService | INFO accept; WARNING reject | `ticket_id` present bool, `initiative_id`, `start_node` | |

---

## 8. Data contract ownership

| Schema / data type | Owner (defines + validates) | Validation layer | Versioning |
|--------------------|----------------------------|------------------|------------|
| Pin `schema.yaml` / `template.md` | prayog-skills (upstream) | PromptResolver validates at consume | semver `revision` in schema |
| Bound-input map | Gateflow PromptResolver + wave-start | edge (wave-start) + pre-dispatch | INIT-003 shared dictionary |
| `runs.handoff_path` | Gateflow RunStore | repository + orchestrator invariant | additive column; human Alembic |
| `stages.prompt_id` / `prompt_revision` | Gateflow RunStore | repository on write | additive; human Alembic |
| Handoff envelope | sdd-delivery/v2 contract | HandoffReader.parse | forward-compat `extra=ignore` as today |
| Wave-start body | Gateflow API models | Pydantic edge | `ticket_id` semantics tightened |

---

## 9. Resolved engineering decisions

| Finding ID | Owner | Status | Question | Resolution | Required by | Default if deferred | Evidence / reference |
|------------|-------|--------|----------|------------|-------------|---------------------|----------------------|
| FF-06 | PE | resolved | Brief ownership + handoff ingest authority | ADR-007 Option B + ADR-008 Option B **Accepted**; concrete path/columns in TDD | plan | N/A | §4; ADR-007; ADR-008 |
| Q-1 | PE | resolved | ticket field naming | Keep `ticket_id`; bind as `ticket`; require non-empty for automate | W0 | same | §3.3 |
| Q-2 | PE | resolved | RunStore field names | `runs.handoff_path`; `stages.prompt_id`; `stages.prompt_revision` | W0 | same | §3.5 |
| Q-3 | PE | resolved | handoff_path concrete form | `{GATEFLOW_HANDOFF_ROOT}/{run_id}/handoff.md` (configured absolute root; **not** under workspace/repo). ADR-008 owns authority only | W0 | same | §3.4 |
| Q-4 | PE | resolved | Prove-it skill id | `pre-implement` (pin orchestrated + package present) | W0 | same | §5 |
| FF-05 | PE | resolved | Verify policy | Extend `verify_implement_lane` with prompt_id/revision asserts | W0 | same | §5 |
| FF-09 | PE | resolved | Pin root while Launchpad stub | Search `prayog-skills/skills/{development,requirements}/{skill_id}/prompts/` under workspace | W0 | same | §3.1 |
| FF-02 | PE | resolved | Invent-prose removal shape | Message-only `run_skill`; delete/unused `_build_prompt` on packaged path; anti-hardcode unit | W0 | same | §3.2 |
| FF-03 | PE | resolved | Ambient ingest | W0 may still use ambient until W1; W1 switches packaged automate to `read_path` only (ADR-008) | W1 | same | §3.4 |
| FF-08 | PE | resolved | Optional ticket_id | Enforce non-empty at WaveStartService for automate | W0 | same | §3.3 |

---

## 10. Routed out — product questions (PM)

| ID | Owner | Status | Question | Blocking | Required by | Default if deferred | Evidence | Resolution reference |
|----|-------|--------|----------|----------|-------------|---------------------|----------|----------------------|
| — | — | — | none | — | — | — | — | Meta PR #16 decisions already confirmed |

---

## 11. Routed out — domain clarifications (SME)

| ID | Owner | Status | Question | Blocking | Required by | Default if deferred | Evidence | Resolution reference |
|----|-------|--------|----------|----------|-------------|---------------------|----------|----------------------|
| — | — | — | none | — | — | — | — | — |

---

## 12. Fix disposition

| ID | Status | Item | Target/evidence | Result digest |
|----|--------|------|-----------------|---------------|
| AF-1 | auto-fixed | Name REQ-10 verify evidence | Spec REQ-10 evidence → extend `verify_implement_lane` | `sha256:e0eb225ace9c2d49f5cf04d36f6fc5647e5c79fcdff749a52c2492881b725b3f` |

---

## 13. Implementation readiness verdict

| Gate | Status |
|------|--------|
| All T1–T11 checks | PASS |
| Engineering decisions resolved | 10 resolved, 0 deferred |
| Draft ADR files written | 2 / 2 required — both **Accepted** |
| PM questions outstanding | 0 |
| Domain questions outstanding | 0 |
| Ready for PE review | YES — accepted |
| **Ready for /spec-implementation-plan** | **YES — TDD + ADR-007 + ADR-008 Accepted on this branch** (Gate 2 `spec-lgtm` still deferred until plan is on head) |

---

## Check summary

| Check | Status | Notes |
|-------|--------|-------|
| T1 Module boundaries | PASS | PromptResolver business; runner infra; RunStore; handoff read_path |
| T2 Interface contracts | PASS | §3.1–§3.6 shapes and invariants |
| T3 NEW-ADR dispositions | PASS | FF-06 → ADR-007 + ADR-008 **Accepted** (architecture-only); product detail TDD_ONLY |
| T4 Test policy | PASS | Unit exact render; live field asserts; AI text not exact |
| T5 Error handling | PASS | Fail closed matrix §6 |
| T6 Observability | PASS | §7 structured fields |
| T7 Data contract ownership | PASS | §8 pin vs RunStore vs API |
| T8 Dependency graph | PASS | api → business → repo; infra injected; no cycle |
| T9 Engineering questions zero | PASS | Q-1…Q-4 + FF-* PE items resolved |
| T10 PE review readiness | PASS | PE accepted; ready_for_plan true; Gate 2 still spec-pending |
| T11 ADR artifact integrity | PASS | ADR-007 + ADR-008 Accepted and linked; no product catalogue in ADRs |

---

## PR instructions

> Commit this TDD + Draft ADR to the **Draft spec PR** branch. PE reviews on the
> **same PR**. Gate 2 label stays **`spec-pending`** until the implementation plan
> exists. PE accepts architecture by committing **Accepted** TDD/ADR files — not
> by setting `spec-lgtm` yet.

```
Branch:   chore/INIT-GATEFLOW-005-BOUNDINPUT-spec-gateflow
PR:       https://github.com/drivestream-lab/gateflow/pull/52
PR title: "[INIT-GATEFLOW-005-BOUNDINPUT] Spec — gateflow"

Required reviewers:
  @drivestream-lab/prayog-pe-team

Review deadline: 2026-08-03
PE review checklist:
  [ ] T1 Module boundaries — PromptResolver business vs AgentRunner infra
  [ ] T2 Interface contracts — message-only runner; handoff path shape (TDD)
  [ ] T3 ADR-007 / ADR-008 Draft — architecture-only Option B acceptable
  [ ] T4 Test policy — exact render + live prompt_id asserts
  [ ] T9 Zero unresolved PE items
  [ ] T11 ADR artifact integrity — no product bind/path catalogue in ADRs

PE action (artifact acceptance — mid-lane):
  Review/comment or Request changes → update TDD/ADR
  Explicitly state when decisions are ready for acceptance
  Update ADR-007 + ADR-008 + TDD Status Draft → Accepted; commit to spec branch
  Label remains spec-pending

After artifact acceptance:
  → /spec-implementation-plan on the same branch
  → after plan on head: PE sets spec-lgtm + Approve + attestation
```

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: technical-review-approval
  outcome: pass
  artifact:
    path: docs/specification/reports/Technical-Review-INIT-GATEFLOW-005-BOUNDINPUT.md
    digest: sha256:227913ee27946184d3353c5212245e28434922d127e4a4f3d511e0bc0e5e3ac6
  blockers: []
  signals:
    ready_for_pe_review: true
    ready_for_plan: true
    new_adr: true
    tdd_status: Accepted
    adr_required_paths:
      - docs/specification/adr/adr-007-invocation-brief-and-agent-message-contract.md
      - docs/specification/adr/adr-008-packaged-skill-handoff-ingest-authority.md
    adr_required_digests:
      - sha256:fd8f11f61be203db409e1dc23df12f78f26dfe5b75c819fce22e0723b0225d89
      - sha256:cc94079602762d58622d321f4bdefacf2c54fcd0a6511da3415daacb48b52cad
    adr_status: Accepted
    draft_verdict: PASS
    pe_acceptor: nikd10x
    meta_pr_head_sha: 0b6b11e4470517842affb894d7ea581c3819ead3
    map_revision: 1
    prd_digest: sha256:40fb856dd5068290c1d14f010239e6206bee2625aaf6a6e3970d769e9bb5e970
    scope_digest: sha256:2cc5e2151451c47b973fdc86dafe19d5cb2fadd651212a5a00f9d681f274039b
    spec_pr: https://github.com/drivestream-lab/gateflow/pull/52
    gate2_label: spec-pending
  next_candidates:
    - spec-implementation-plan
  human_checkpoint: false
  external_action: false
```
