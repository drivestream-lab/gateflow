# Technical Design Document — INIT-GATEFLOW-007

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-007 |
| Spec | `docs/specification/product/INIT-GATEFLOW-007-gateflow.md` |
| Spec digest | `sha256:1c613846f4b0ea5c9c2db3deab982ddf791bd93bba81dfdc2fdc175aa3051793` |
| Feasibility report | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-007.md` |
| Feasibility digest | `sha256:ca40b9e2a77926a75569306a272e280fad086ddaf97d3bf7a37c3fecce3f6f64` |
| PRD digest | TBD — Gate 1 open (spec Q-1) |
| Impact map / revision | TBD / TBD |
| Repo scope digest | TBD |
| Approved meta PR head | TBD |
| Source freshness | **STALE / WAIVED** — Gate 1 digests absent; PE-directed INIT (same waive as feasibility). Not CURRENT until Q-1 closes. |
| Repo | drivestream-lab/gateflow |
| Date | 2026-07-29 |
| Branch | `chore/INIT-GATEFLOW-007-spec-gateflow` (Draft spec PR [#77](https://github.com/drivestream-lab/gateflow/pull/77)) |
| Initiative segment | `INIT-GATEFLOW-007` |
| Status | **Accepted** — PE direction 2026-07-29 via Cursor chat (fold closeout into ADR-010; proceed `/spec-implementation-plan` on Draft spec PR #77). Mid-lane architecture acceptance — not Gate 2 `spec-lgtm`. |
| Approval evidence | Explicit PE acceptance by proceeding to `/spec-implementation-plan` after ADR-010 fold (no ADR-011); Draft spec PR https://github.com/drivestream-lab/gateflow/pull/77 |
| Approved head | Record on acceptance commit tip before plan |
| Review deadline | 2026-08-05 |
| Deciders | PE: @nikd10x / @drivestream-lab/prayog-pe-team — explicit acceptance required |

---

## 1. Problem statement

After Pass-1 stops at pin `live-verify` (human prove + tip fix), Gateflow must
**finish the wave** with a programme-token Pass-2 walk: new run Enter-at
`learning-extract` → `ground-spec` → stop at `wave-signoff`, bind the existing
wave PR, and persist structured `L-*` learning in Postgres (skill emits artifact
only — no skill→HTTP). No authorize→resume; no new ADR number — closeout intake
folds into **ADR-010** (with ADR-005 token zone unchanged).

---

## 2. Module / package boundaries

| Module | Current state | Change | Owns |
|--------|---------------|--------|------|
| `src/api/v1/waves_routes.py` | implement + spec start | Add `POST /waves/closeout/start` | HTTP edge |
| `src/models/wave_start_models.py` (or `wave_closeout_models.py`) | lane bodies only | Add `CloseoutWaveStartRequest` (`extra=forbid`) | API DTO |
| `src/business_services/wave_start_service.py` | `_enqueue_wave` shared | Add `start_closeout_wave`; fixed Enter-at; require PR | Accept + enqueue |
| `src/business_services/run_orchestrator.py` | Pass-1 walker + forge + baton ingest | Unchanged walker; after `learning-extract` hop invoke learning ingest | Run lifecycle |
| `src/business_services/learning_ingest_service.py` | **new** | Parse Learning-Extract fence → upsert rows | Learning ingest (business) |
| `src/models/learning_models.py` | **new** | Pydantic for fence + row DTOs + class enum | Data contracts |
| `src/database/postgres/schema/learning_schema.py` | **new** | ORM for learning extract + items | ORM |
| `src/database/postgres/repository/learning_repository.py` | **new** | Persist/query learning | Persistence |
| `postgres_migrations/versions/` | human-owned | Human Alembic for learning tables | DDL (ADR-001) |
| `src/di/modules/*` | exists | Bind learning service + repo | DI |
| `prayog-skills` pin | Pass-2 graph ready | **unchanged** (consume) | Dispatch/forge SSOT |
| `tests/unit/test_wave_closeout.py` | **new** | Accept/bind/concurrency/Enter-at | Unit |
| `tests/unit/test_learning_ingest.py` | **new** | Parse/taxonomy/fail-closed | Unit |
| `tests/verify/verify_wave_closeout.py` | **new** | Pass-2 live prove-it | Live verify |
| `tests/README.md` / as-built | Pass-1 rows | Feature map + matrix | Docs |
| `docs/specification/adr/adr-010-…md` | Accepted | **Amendment** §6 closeout intake (no ADR-011) | Intake authority |

**Accepted ADR constraint set:**

| ADR | Interaction |
|-----|-------------|
| ADR-001 | Learning SSOT in Postgres; human Alembic |
| ADR-005 | Closeout is a documented programme-token **write** (TDD catalogue) |
| ADR-007 | Bind map from pin `learning-extract` `schema.yaml` |
| ADR-008 | Baton dual-write + `read_path` ingest for Pass-2 hops |
| ADR-009 | Pin forge: learning-extract optional; ground-spec required |
| ADR-010 | **Amended** — third start contract = closeout (this INIT) |
| ADR-003 / ADR-006 | Business owns ingest; Cursor fail-closed; no second runner |

**Boundary diagram (text):**

```
POST /api/v1/waves/closeout/start  (programme token)
  → WaveStartService.start_closeout_wave
       ├── validate body + pin learning-extract orchestrated
       ├── find_active_run → 409 if ACTIVE
       ├── create NEW run (pr_number required) + handoff_path baton
       └── enqueue job start_node=learning-extract

[worker] RunOrchestrator
  hop learning-extract (Cursor + PromptResolver bind)
       ├── ForgeClient commit if pin optional/required
       ├── HandoffReader.read_path → continue
       └── LearningIngestService.ingest_from_workspace (after hop)
  hop ground-spec → STOP at wave-signoff
```

---

## 3. Public interface contracts

### 3.1 HTTP — `POST /api/v1/waves/closeout/start`

**Auth:** programme service token (ADR-005); path on `public_paths`.

**Body (`CloseoutWaveStartRequest`, `extra=forbid`):**
- `initiative_id`, `wave_id`, `ticket_id` — non-empty; dual-identity rules as implement
- `org`, `repo` — non-empty
- `pr_number` — **required** positive int (or TDD-equivalent `pr_url` that resolves to org/repo/number — prefer `pr_number` in v1)
- `workspace_path` — **required** absolute path (app checkout on PR tip)
- `runner`, `model_id` — required; optional `node_dispatch` inherit map
- `prior_run_id` — optional UUID; audit link only; must exist if present; **must not** resume stages
- **Forbidden:** client `start_node`, `meta_pr_url`, `meta_workspace_path` (reject if present)

**Return:** same shape as lane starts (`run_id`, `job_id`, `status`).

**Errors:** 401 token; 400 validation / pin not orchestrated / bad prior_run; 409 ACTIVE concurrent; 0 enqueue on failure.

**Invariants:**
- Enter-at always `learning-extract` (server-set)
- New `run_id` every successful accept
- Does not mutate prior Pass-1 run row status

### 3.2 WaveStartService → RunStore / Job queue

**Method:** `start_closeout_wave(request) → WaveStartResponse`

**Behaviour:**
1. Fail closed if pin node `learning-extract` missing or not `dispatch: orchestrated`
2. `find_active_run` for org/repo + initiative/wave (and/or pr_number) — if ACTIVE → 409
3. Create run: `status=active`, set `pr_number`, identity, `handoff_path` via existing baton helper
4. Persist optional `prior_run_id` in job payload and/or run event (column optional in W0 — payload key sufficient; TDD default = **job payload + run_event**, no new runs column unless PE prefers FK)
5. Enqueue job with `start_node=learning-extract`, `dispatch_plan`, `workspace_path`, `trigger_source=api`

### 3.3 Prompt bind (ADR-007) — `learning-extract`

**Bound inputs (after Gateflow fills orchestrator fields):**
- `ticket` ← `ticket_id`
- `initiative` ← `initiative_id` (always send)
- `workspace` ← `workspace_path`
- `handoff_path` ← run baton (Gateflow-owned)
- `skill_id` = `learning-extract`

Pin schema SSOT: `prayog-skills/skills/development/learning-extract/prompts/schema.yaml`.
Missing required → fail closed before AgentRunner.

### 3.4 LearningIngestService (business)

**Method:** `ingest_after_learning_extract(run, workspace_path) → LearningExtractModel`

**Locate artifact:** `{workspace}/{reports_dir}/Learning-Extract-{initiative}-W{N}.md`
where `reports_dir` defaults from `.harness/profile.yaml` / pin layout-defaults
(`docs/specification/reports`). Wave token normalize as existing `W{N}` helpers.

**Parse:** single fenced YAML block with root key `learning_extract:` (pin template).
Validate with Pydantic (`extra=forbid` on known fields; items list required).

**Persist:** upsert extract header + replace/insert items for `(initiative_id, wave_id, run_id)`
(idempotent re-ingest on same run).

**Ordering:** after successful content hop for `learning-extract`, apply ADR-009
**publish-before-ingest** when forge publish also applies on that hop; then learning
ingest; then handoff baton ingest for walker continue (existing order: publish →
handoff read). Learning ingest runs **after publish**, **before or after** handoff
read — **default: after publish, after handoff envelope is readable, before
dispatching `ground-spec`** so ground-spec tip may already contain committed
Learning-Extract when forge optional committed it.

**Errors:** missing file / missing fence / unknown `class` / invalid id → fail
closed (run/stage failed); empty `items: []` with parseable document **allowed**.

**Forbidden:** skill HTTP to Gateflow; learning service must not be called from
Cursor success path inside the skill.

### 3.5 Learning repository

**Operations:** `upsert_extract(extract)`, `list_items(initiative_id, wave_id)`,
`get_by_run_id(run_id)`.

No public HTTP read API in this INIT (Q-7).

### 3.6 Walker Pass-2 (reuse)

Pin outcomes SSOT. Terminal stop when next node is `wave-signoff` (`human-checkpoint`).
Do not dispatch `verify` (manual).

---

## 4. ADR resolutions

| Finding | Classification | ADR file / TDD section | Recommendation / default | Status | Digest |
|---------|----------------|------------------------|--------------------------|--------|--------|
| FF-05 (possible NEW-ADR closeout intake) | **TDD_ONLY** + **fold into ADR-010** | `docs/specification/adr/adr-010-lane-intake-and-dual-workspace-authority.md` §6 | Third start contract = closeout; **no ADR-011** | **Accepted** (amendment) | `sha256:b627494120db5a68b8da272617b50686031413d7f0a6735672e310c9a60f23e5`* |
| Learning store authority | **TDD_ONLY** | ADR-001 + §8 | Postgres SSOT; reports emit-only | Resolved | N/A |
| Skill→API forbidden | **TDD_ONLY** | pin H6 + §3.4 | Worker ingest only | Resolved | N/A |

**Derived counts:**

- ADR_REQUIRED: **0** (no ADR-011)
- TDD_ONLY: 3
- DEFERRED_WITH_DEFAULT: 0 (PE questions deferred in §9 with defaults)
- Draft ADR files created: **0** new; **1** existing ADR amended
- Missing/broken ADR files: 0

---

## 5. Test policy

| Module / area | Unit layer tests | Integration layer | Live verify | Golden test strategy |
|---------------|------------------|-------------------|-------------|----------------------|
| Closeout accept | validation, fixed Enter-at, 409 ACTIVE, forbid start_node/meta | TestClient programme token | `verify_wave_closeout` opt-in | exact status codes / body fields |
| Prompt bind | schema required vars for learning-extract | — | stage prompt_id on hop | exact |
| Learning parse | fence happy/empty/malformed/unknown class | — | artifact on tip after hop | exact schema; fuzzy free-text summary not asserted |
| Walker Pass-2 | multi-hop fixture learning→ground→stop | — | stages + `workflow_node=wave-signoff` | exact node ids |
| Checkpoint hygiene | mocks use `wave-signoff` / `live-verify` | — | — | exact |

**AI-output determinism:** do not assert LLM prose; assert artifact presence,
YAML schema validity, DB row counts/classes, stage outcomes, terminal node.

---

## 6. Error handling strategy

| Failure mode | Module | Propagation | Recovery |
|--------------|--------|-------------|----------|
| Bad/missing programme token | API dep | 401 | terminal |
| Missing PR / identity / workspace | closeout accept | 400 | terminal |
| `learning-extract` not orchestrated | closeout accept | 400 | terminal |
| ACTIVE concurrent run | closeout accept | 409 | terminal — wait/stop prior |
| Bind miss | PromptResolver | stage/run failed | terminal — no AgentRunner |
| Agent failure | Cursor runner | run failed | terminal |
| Required forge empty/I/O | ForgeClient | run failed | terminal (ADR-009) |
| Learning artifact missing/malformed | LearningIngestService | stage/run failed | terminal |
| Handoff baton missing | HandoffReader | run failed | terminal (ADR-008) |

---

## 7. Observability contract

| Module | Level | Structured fields |
|--------|-------|-------------------|
| Closeout accept | INFO | `run_id`, `initiative_id`, `wave_id`, `pr_number`, `start_node` |
| Closeout reject | WARNING | reason code, org, repo, wave_id |
| Learning ingest | INFO | `run_id`, `initiative_id`, `wave_id`, `item_count`, `artifact_path` |
| Learning fail | ERROR | `run_id`, reason, `artifact_path` |
| Orchestrator hops | existing | `workflow_node`, `prompt_id`, forge commit ids |

No silent swallow; use `get_logger()` / `self.logger` patterns.

---

## 8. Data contract ownership

| Schema / data type | Owner (defines + validates) | Validation layer | Versioning |
|--------------------|----------------------------|------------------|------------|
| Pin `learning_extract` YAML fence | prayog-skills template | Gateflow Pydantic on ingest | Pin revision; unknown class fail closed |
| `CloseoutWaveStartRequest` | Gateflow models | API edge | amend-by-PE / INIT |
| Learning ORM tables | Gateflow schema + human Alembic | Repository validate ↔ Pydantic | Additive columns |

### 8.1 Learning relational shape (CTR-G2) — v1

**Table `learning_extracts` (header):**
- `id` UUID PK
- `run_id` UUID FK → `runs.id` ON DELETE CASCADE (unique) — ingest tied to Pass-2 run
- `initiative_id` VARCHAR NOT NULL
- `wave_id` VARCHAR NOT NULL
- `org`, `repo` VARCHAR NOT NULL
- `pr_number` INT NULL
- `human_fix_detected` BOOLEAN NOT NULL
- `artifact_path` TEXT NOT NULL
- `source_sha` VARCHAR(64) NULL (optional tip SHA if known)
- `prior_run_id` UUID NULL (audit; no FK required in v1)
- timestamps per `PostgresBaseModel`

**Table `learning_items`:**
- `id` UUID PK
- `extract_id` UUID FK → `learning_extracts.id` ON DELETE CASCADE
- `item_key` VARCHAR NOT NULL — pin `L-01` …
- `class_type` VARCHAR NOT NULL — enum `SPEC` \| `SKILL` \| `HARNESS` \| `ENV`
- `summary` TEXT NOT NULL
- `evidence` JSONB NOT NULL — list of strings
- `codify_hint` JSONB NOT NULL — `{target, ref}` object
- `status_type` VARCHAR NOT NULL — `open` \| `codified`
- UNIQUE (`extract_id`, `item_key`)

**Indexes:** `(initiative_id, wave_id)`; `(run_id)`.

**Pydantic:** `LearningClassType`, `LearningItemStatusType`, `LearningExtractDocument`
(fence), `LearningItemDocument`, repo DTOs — all under `src/models/learning_models.py`.
JSONB validated on read/write at repository boundary.

---

## 9. Resolved engineering decisions

| Finding ID | Owner | Status | Question | Resolution | Required by | Default if deferred | Evidence / reference |
|------------|-------|--------|----------|------------|-------------|---------------------|----------------------|
| FF-05 | PE | **resolved** | ADR-011 vs fold | **Fold into ADR-010 §6**; no ADR-011 | plan | — | ADR-010 amendment; PE direction 2026-07-29 |
| FF-04 | PE | **resolved** | Learning table shape | §8.1 two tables + enums | W1 | — | this TDD |
| Q-3 / FF-08 | PE | **resolved** | Park-ack API? | **No** — closeout allowed after Pass-1 `stopped@live-verify` | W0 | — | pin park status/UI only |
| Q-4 / FF-09 | PE | **resolved** | Ingest timing | After successful `learning-extract` hop; publish-before-ingest then learning ingest before `ground-spec` dispatch | W1 | — | §3.4 |
| Q-5 | PE | **resolved** | `prior_run_id` | Optional; audit via payload/event; no walker resume | W0 | — | REQ-13 |
| Q-6 | PE | **resolved** | Spec live in W2 | Both lanes in scope; **implement live first**; spec live or PE-waived as-built deferral | W2 | implement-first | REQ-15 |
| Q-7 | PE | **resolved** | Learning HTTP read | **None** in 007 — repo only | W1 | — | — |
| FF-11 | PE | **resolved** | Concurrent vs stopped Pass-1 | `find_active_run` ACTIVE-only; stopped Pass-1 does not block closeout | W0 | — | `run_store_repository.py` |
| FF-01 | PM/PE | **deferred** | Gate 1 CURRENT | Engineering Draft waived; formal CURRENT blocked until Q-1 | board-seed | waive recorded | feasibility |

---

## 10. Routed out — product questions (PM)

| ID | Owner | Status | Question | Blocking | Required by | Default if deferred | Evidence | Resolution reference |
|----|-------|--------|----------|----------|-------------|---------------------|----------|----------------------|
| Q-1 / PM-1 | PM/PE | open | Retrospective Gate 1 meta PRD / Impact-Map vs explicit waive | yes for formal Gate 2 CURRENT / board-seed | board-seed | Engineering Draft proceeds waived | Spec header TBD | pending |

---

## 11. Routed out — domain clarifications (SME)

| ID | Owner | Status | Question | Blocking | Required by | Default if deferred | Evidence | Resolution reference |
|----|-------|--------|----------|----------|-------------|---------------------|----------|----------------------|
| — | — | — | None (taxonomy closed in pin) | — | — | — | — | — |

---

## 12. Fix disposition

| ID | Status | Item | Target/evidence | Result digest |
|----|--------|------|-----------------|---------------|
| AF-1 | planned-auto-fix | Feature map + `verify_wave_closeout` | W2 implement | N/A |
| AF-2 | planned-auto-fix | Retarget unit mocks off `wave-human-decision` | W0/W2 hygiene | N/A |
| AF-3 | auto-fixed | Fold closeout into ADR-010 (no ADR-011) | `adr-010-…md` amendment | see §4 |

---

## 13. Implementation readiness verdict

| Gate | Status |
|------|--------|
| All T1–T11 checks | PASS (freshness waived — documented) |
| Engineering decisions resolved | 9 resolved, 1 PM deferred (Q-1) |
| Draft ADR files written | 0 new; ADR-010 amended (pending PE re-accept) |
| PM questions outstanding | 1 (Q-1 Gate 1) |
| Domain questions outstanding | 0 |
| Ready for PE review | **YES** (accepted) |
| **Ready for /spec-implementation-plan** | **YES — PE acceptance recorded 2026-07-29; plan may run** |

---

## Check summary

| Check | Status | Notes |
|-------|--------|-------|
| T1 Module boundaries | PASS | §2 |
| T2 Interface contracts | PASS | §3 |
| T3 NEW-ADR dispositions | PASS | FF-05 → fold ADR-010; ADR_REQUIRED=0 |
| T4 Test policy | PASS | §5 |
| T5 Error handling | PASS | §6 |
| T6 Observability | PASS | §7 |
| T7 Data contract ownership | PASS | §8 + §8.1 |
| T8 Dependency graph | PASS | api→business→repo; pin consume |
| T9 Engineering questions zero | PASS | §9; PM Q-1 out of PE lane |
| T10 PE review readiness | PASS | ready_for_pe_review true; ready_for_plan false |
| T11 ADR artifact integrity | PASS | No ADR-011; amendment linked in §4 |

---

## PR instructions

> Commit this TDD + ADR-010 amendment to Draft spec PR [#77](https://github.com/drivestream-lab/gateflow/pull/77).
> Gate 2 label stays **`spec-pending`**. PE accepts by updating ADR-010 amendment
> + TDD Status → **Accepted** (metadata), then `/spec-implementation-plan`.
> Do **not** set `spec-lgtm` until plan is on head.

```
Branch:   chore/INIT-GATEFLOW-007-spec-gateflow
PR:       https://github.com/drivestream-lab/gateflow/pull/77

PE review checklist:
  [ ] Closeout folded into ADR-010 §6 (no ADR-011) — accept?
  [ ] Learning §8.1 table shape — accept?
  [ ] Ingest timing / prior_run / no park-ack / no learning read API — accept?
  [ ] T1–T2 boundaries/contracts sufficient for plan?

PE action (artifact acceptance — mid-lane):
  Explicitly state decisions ready for acceptance
  Developer/PE: TDD Status → Accepted; clear ADR-010 "amendment Draft" → Accepted amendment
  Commit acceptance package (label remains spec-pending)
  → /spec-implementation-plan
```

## Handoff envelope

```yaml
handoff:
  schema_version: "1"
  contract: "sdd-delivery/v2"
  stage: spec-technical-review
  outcome: pass
  initiative: INIT-GATEFLOW-007
  human_checkpoint: true
  external_action: false
  next_candidates:
    - technical-review-approval
  artifact:
    path: docs/specification/reports/Technical-Review-INIT-GATEFLOW-007.md
  signals:
    ready_for_pe_review: true
    ready_for_plan: false
    adr_required: 0
    adr_amended:
      - path: docs/specification/adr/adr-010-lane-intake-and-dual-workspace-authority.md
    new_adr: false
    source_freshness: STALE_WAIVED
  blockers: []
  notes:
    - No ADR-011 — closeout intake folded into ADR-010 §6
    - Learning data contract in TDD §8.1 (ADR-001 store)
    - PE must Accept TDD + ADR-010 amendment before plan
  forge:
    action: commit_workspace
    # same Draft PR #77 tip
```
