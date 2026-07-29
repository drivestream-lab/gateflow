# Technical Design Document — INIT-GATEFLOW-001

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-001 |
| Spec | `docs/specification/product/INIT-GATEFLOW-001-gateflow.md` |
| Spec digest | `sha256:6d0094d21994db5ec7f5903f7f01d5ab03bb2e0619802f293b59aa426dc29f00` |
| Feasibility report | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-001.md` |
| Feasibility digest | `sha256:ea81389c06d016b5a4e16d2bf09c677d56d4573878e025859c9987553d6755c9` |
| PRD digest | `sha256:9fa343f11f9497cd278c18ba4b87391b15cab566f285e88a7f4cda9bf700802d` |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-001.md` / `3` |
| Repo scope digest | `sha256:f81fd7c11c9b438524032898b31b028b376bcf766cb5ef675f0ecb81f326e9a0` |
| Approved meta PR head | `d62a9bbcf5960c50c4429dd33bb206208dbbf246` |
| Source freshness | CURRENT — meta PR #9 head + APPROVED review + digests match feasibility/spec headers |
| Repo | drivestream-lab/gateflow |
| Date | 2026-07-23 |
| Branch | `chore/INIT-GATEFLOW-001-spec-gateflow` (Draft spec PR #4) |
| Initiative segment | `INIT-GATEFLOW-001` |
| Status | Accepted — PE @nikd10x 2026-07-23; ADR set consolidated 6→4 |
| Review deadline | 2026-07-30 |
| Deciders | PE: @drivestream-lab/prayog-pe-team — explicit LGTM required, not approval by silence |

> **Living supersession (config carrier):** `config/programme.yaml` / YAML
> `ProgrammeConfig` load were removed after this TDD. Live authority is
> env-backed settings (`GATEFLOW_*`), wave-start API fields, and pin
> `workflow.yaml` — **ADR-004**, INIT-002 **A-7**, as-built. Rows below that
> name `programme.yaml` are wave-time design only.

---

## 1. Problem statement

Gateflow must become a durable delivery control plane: accept GitHub App
webhooks, authorize wave runs from programme config, resolve pinned
`sdd-delivery/v2` workflow nodes, dispatch Cursor agents only when
`dispatch: orchestrated`, stop on contract nodes, and expose reconstructable
run/metrics APIs — without violating platform layering (API → business → repo →
ORM) or writing gate-approval labels.

---

## 2. Module / package boundaries

| Module | Current state | Change | Owns |
|--------|---------------|--------|------|
| `src/main.py` / `src/app.py` | exists | extend public_paths, mount webhook + runs/metrics routers | HTTP composition |
| `src/worker_main.py` | new | create worker entry + job claim loop | Async orchestration process |
| `src/api/webhooks/` (or equiv) | new | GitHub webhook route | Signature verify + enqueue |
| `src/api/v1/runs_routes.py` | new | status read API | Programme-token protected reads |
| `src/api/v1/metrics_routes.py` | new | metrics aggregate API | Programme-token protected reads |
| `src/business_services/*` | base only | TriggerRouter, HandoffReader, WorkflowEngine, PolicyEngine, RunOrchestrator, Notifier, MetricsEmitter, StageToolResolver | Domain orchestration |
| `src/infra_services/forge_client.py` | new | GitHub outbound REST + forbid guards | Comments, run-status labels, audit; single business-facing forge surface |
| `src/infra_services/github_token_provider.py` (or equiv) | new | Outbound Bearer mint/resolve | PAT vs App installation **token strategy** (not an ADR-006 product slot) |
| `src/infra_services/cursor_agent_runner.py` | new | AgentRunner adapter | Cursor SDK dispatch |
| `src/infra_services/launchpad_client.py` | new | Harness sync | Pre-dispatch sync |
| `src/database/postgres/schema/*` | base only | runs, stages, events, jobs, webhook_deliveries | ORM tables |
| `src/database/postgres/repository/*` | base only | RunStore + job repos | Persistence mapping |
| `src/models/*` | scaffold | Run/handoff/job/programme/config DTOs | Pydantic contracts |
| `config/programme.yaml` | **removed (superseded)** | Was W1 YAML carrier; live knobs = env + wave-start API + pin | See ADR-004 / as-built |
| `postgres_migrations/versions/` | empty | human revisions | DDL |

**Boundary diagram (text):**

```
GitHub ──POST /webhooks/github──► [API webhook handler]
                                      │ enqueue job
                                      ▼
                                 [Postgres jobs]
                                      │ claim SKIP LOCKED
                                      ▼
[worker_main] → [RunOrchestrator] → [PolicyEngine] → [WorkflowEngine]
                       │                  │
                       │                  └── [HandoffReader] ← git artifacts
                       ├── [LaunchpadClient] (infra)
                       ├── [CursorAgentRunner] (infra)
                       ├── [Notifier] → [ForgeClient] (infra)
                       └── [RunStore repos] → Postgres
PE ──Bearer programme token──► GET /api/v1/runs/{id}
                             ► GET /api/v1/metrics/runs
```

---

## 3. Public interface contracts

### 3.1 Webhook handler → Job repository

**Method / entry point:** `enqueue_webhook_job`
**Arguments:**
- `delivery_id`: non-empty string — unique GitHub delivery id
- `event_type`: string — GitHub event name
- `payload`: validated Pydantic webhook envelope (extra=ignore as needed)
- `signature_valid`: must be true before call

**Return:**
- `job_id`: UUID
- Error: duplicate delivery → no-op success; DB down → raise infra error → HTTP 503

**Invariants:**
- No PolicyEngine / AgentRunner work in this call
- Idempotent on `delivery_id`

### 3.2 Worker → RunOrchestrator

**Method / entry point:** `process_job`
**Arguments:**
- `job`: claimed job DTO including payload reference

**Return:**
- `run_result_summary`: run_id, terminal status, stop_reason (optional)
- Error: unrecoverable orchestration failure → mark job failed; run `outcome: failed`

**Invariants:**
- Exactly one active run per PR/issue (reject concurrent)
- Never dispatch when policy denies

### 3.3 PolicyEngine → dispatch decision

**Method / entry point:** `evaluate_dispatch`
**Arguments:**
- `handoff`: validated handoff envelope model
- `trigger`: authorised trigger context (label, repo, pr/issue ids)
- `programme_config`: ProgrammeConfig (wave-time; living: env + wave-start + pin — see supersession)
- `pin_workflow`: loaded workflow + delivery-contract from pin `v0.5.0-rc.2`

**Return:**
- `decision`: enum-like — `dispatch` | `stop` | `block`
- `next_node`: optional node id + type + dispatch mode
- `block_reason`: required when `block`/`stop`

**Invariants:**
- `dispatch` only if `type=skill` and `dispatch=orchestrated`
- Pin/orchestration unavailable → `block` (never silent)
- No hardcoded node allowlists

### 3.4 RunOrchestrator → AgentRunner (infra)

**Method / entry point:** `run_skill`
**Arguments:**
- `workspace_path`: absolute path to ephemeral worktree
- `skill_id`: string from workflow node
- `prompt_context`: structured context (initiative, handoff fields)
- `model_profile`: string (H1: `default`)

**Return:**
- `RunResult`: runner, model_id, model_provider (optional), outcome, artifacts metadata
- Error: timeout/crash → outcome `failed`; orchestrator must not advance workflow

**Invariants:**
- Launchpad harness sync completed before call
- No forge gate-label writes inside runner

### 3.5 Notifier → ForgeClient

**Method / entry point:** `post_run_event_comment`
**Arguments:**
- `repo`, `pr_or_issue_ref`
- `event`: run event model (`run_id`, `workflow_node`, `event`, `outcome`, `duration_ms`, `timestamp`)

**Return:**
- `comment_id` or `notify_pending` flag
- Error: after backoff exhaustion → set `notify_pending` on run; do not crash policy success path silently without RunStore flag

**Invariants:**
- H1 comments only (no commit statuses)
- Zero writes to gate-approval labels; zero auto-merge

### 3.5a ForgeClient outbound credential strategy (Q-1 implementation contract)

ADR-003 Q-1 remains normative: **App installation token in production**; **scoped PAT
only when explicitly configured for non-prod**. This section is the **TDD-only**
implementation contract for how ForgeClient obtains the Bearer token. It does
**not** introduce a new ADR and does **not** register PAT/App as ADR-006 adapter
ids (those slots are runner/notifier product choices).

**Boundary:**

```
Business (Notifier / BoardService / RunOrchestrator)
  → ForgeClient (single Protocol / class; PR, comment, board ops)
       → GithubTokenProvider (Protocol; concrete bound in InfraModule)
            ├─ PatTokenProvider          when GITHUB_AUTH_MODE=pat
            └─ AppInstallationTokenProvider  when GITHUB_AUTH_MODE=app
Inbound webhooks remain ADR-002 forge-signature zone (GITHUB_WEBHOOK_SECRET);
webhook auth is out of scope for TokenProvider.
```

**Settings (env — secrets never in committed programme config):**

| Env / field | Purpose |
|-------------|---------|
| `GITHUB_AUTH_MODE` | **Required.** Enum only: `pat` \| `app`. No `auto`, no inference from which secrets are present. |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | **Required** when mode is `pat`; ignored for credential selection when mode is `app` (must not be used as fallback) |
| `GITHUB_APP_ID` | **Required** when mode is `app` |
| `GITHUB_PRIVATE_KEY_PATH` | PEM path; **required** when mode is `app` |
| `APP_ENVIRONMENT` | `production` **forbids** mode `pat` (ADR-003) |

No `GITHUB_APP_INSTALLATION_ID` (or similar) env — installation is **discovered** at startup in `app` mode via `GET /app/installations` (App JWT). Exactly **one** installation → use it; zero or many → **fail fast** with a clear message (operator narrows App installs or splits Apps per environment).

**Mode behavior (explicit only — fail fast on any violation):**

| `GITHUB_AUTH_MODE` | Behavior |
|--------------------|----------|
| `pat` | Bind/use `PatTokenProvider`. **Fail startup** if mode unset/invalid, PAT unset/empty, or `APP_ENVIRONMENT=production`. |
| `app` | Bind/use `AppInstallationTokenProvider`. **Fail startup** if App id / PEM missing, or installation discovery does not yield exactly one install. |

**Not allowed:**

- Defaulting or inferring mode from which env vars are set
- Silent fallback `pat` ↔ `app` at startup or mid-run
- Starting with unset / unknown `GITHUB_AUTH_MODE`

**DI:**

- `InfraModule` binds `GithubTokenProvider` to the concrete class selected by `GITHUB_AUTH_MODE` (fail-fast in the `@provider` if mode/credentials violate the table above).
- `ForgeClient` injects `GithubTokenProvider` only; it does not branch on mode.

**Lifecycle / invariants:**

- Log `auth_mode` once at ForgeClient / provider init (never the secret).
- App installation tokens are short-lived: provider refreshes before expiry (or on 401 once) without business callers knowing.
- Business and routers must not branch on auth mode.
- Production path inspection (FR-25 / INIT-002): `GITHUB_AUTH_MODE` must be `app`.
- Forbidden ops (gate-approval labels, auto-merge, no `gh` subprocess) unchanged.

**Errors:**

| Condition | Behavior |
|-----------|----------|
| Missing/invalid mode, mode/env/credential conflict | Fail fast at DI provider or `initialize()` — process must not serve forge writes |
| GitHub 401/403 after token resolve | Surface via existing ForgeClient error/`notify_pending` paths; **do not** switch modes |

### 3.6 Status / metrics API → RunStore

**Method / entry point:** `get_run` / `aggregate_run_metrics`
**Arguments:**
- Auth: programme service token (ADR-002 edge trust model)
- `run_id` or metrics query filters

**Return:**
- Run status JSON / p50-p95 aggregate JSON
- Error: 401 invalid token; 404 unknown run

**Invariants:**
- Read-only; no user JWT required
- Models from `src/models/` only in routers

**Illustrative mounts (product/TDD — not ADR decisions):**
- `POST /webhooks/github` — forge signature zone
- `GET /api/v1/runs/{run_id}` — programme-token zone
- `GET /api/v1/metrics/runs` — programme-token zone

---

## 4. ADR resolutions

Consolidated from six Drafts to four architecture ADRs (product routes/schema/keys
moved into this TDD). Prior filenames under `adr-00{1-6}-*` are removed.

| Finding | Classification | ADR file / TDD section | Recommendation / default | Status | Digest |
|---------|----------------|------------------------|--------------------------|--------|--------|
| F-01, F-03 | ADR_REQUIRED | `docs/specification/adr/adr-001-runtime-and-durable-store.md` | Dual process + Postgres jobs/runs; repo boundary; human Alembic | Accepted | `sha256:2b57674fdd19dd9b70873a377470a3ea9b5b474b54f91077797cde5820372bbc` |
| F-02, F-04 | ADR_REQUIRED | `docs/specification/adr/adr-002-edge-trust-model.md` | Three trust zones: JWT / forge signature / programme token via allowlist + route deps | Accepted | `sha256:e9751d5c969a27dce82b7b3eebc0d4af6eed9cf5d3caeca0b74300ea9d137849` |
| F-05, Q-1 | ADR_REQUIRED | `docs/specification/adr/adr-003-slot-layer-ownership.md` | Outbound I/O = infra; orchestration = business; App token prod, PAT non-prod only | Accepted | `sha256:581236751ca755a6c26b4f0cbadf5adea010bfeeee20774fc6969013a3a8f632` |
| F-06 | ADR_REQUIRED | `docs/specification/adr/adr-004-programme-config-authority.md` | In-repo file + Pydantic startup validation; secrets in env only | Accepted | `sha256:64df031b81f3e70032f6c363373b5af98b02f50e0d3089eb8a25915d2da1f697` |
| Q-1 (impl) | TDD_ONLY | §3.5a | `GITHUB_AUTH_MODE` + TokenProvider inside ForgeClient; not ADR-006 slots | Resolved | N/A |
| Q-3 | TDD_ONLY | §3.6 mounts | Exact paths listed under interface contracts | Resolved | N/A |
| F-07 | TDD_ONLY | §3.6 / §8 | Models in `src/models/`; no inline router models | Resolved | N/A |
| F-08 | TDD_ONLY | §5 / §6 | Pin unavailable → block + comment; unit assert never silent | Resolved | N/A |
| Q-2 | DEFERRED_WITH_DEFAULT | §9 | GitHub retries + operator watch on 503; no dedicated alert channel in W1 | Deferred | N/A |
| F-10 (A-3) | DEFERRED_WITH_DEFAULT | §9 | Cursor SDK in worker; fail-closed on runner failure; spike during W1 build | Deferred | N/A |

**Derived counts:**

- ADR_REQUIRED: 4
- TDD_ONLY: 4 (includes Q-1 impl §3.5a)
- DEFERRED_WITH_DEFAULT: 2
- Accepted ADR files on branch: 4
- Missing/broken ADR files: 0

**Existing Accepted ADR constraint set:** none (adr_dir empty at first draft) — independent of prior ADRs.

---

## 5. Test policy

| Module / area | Unit layer tests | Integration layer | Live verify | Golden test strategy |
|---------------|-----------------|-------------------|-------------|----------------------|
| Webhook signature + idempotency | HMAC fixtures; duplicate delivery | — | Signed webhook against running API | exact status codes + run count |
| PolicyEngine / WorkflowEngine | Fixtures from pin `workflow_scenarios.json` + gateflow dispatch cases | — | — | exact next-node + decision |
| Concurrent run reject | In-memory/faked repo | — | Optional | exact |
| AgentRunner failure | Mock runner timeout | — | — | exact outcome `failed` |
| ForgeClient forbid gates | Mock HTTP asserts no forbidden calls | — | — | exact |
| ForgeClient TokenProvider | Explicit `pat`/`app` only; prod+`pat` raises; App mint mocked; no fallback | — | Optional live: `GITHUB_AUTH_MODE=app` PR/comment smoke | exact startup errors + Bearer source |
| Status/metrics auth | Token missing/invalid | — | Programme token smoke | exact 401/200 |
| RunStore repos | — | Testcontainers/docker Postgres optional later | docker-compose verify | exact row shapes |
| E2E wave loop | — | — | Label → stop comment on dogfood repo | observational checklist |

**AI-output determinism policy (when applicable):**
- AgentRunner unit tests mock the SDK — no live LLM in CI.
- Live verify may assert RunStore fields and comment schema exactly; agent-written
  code artifacts are checklist/inspection, not golden text diffs in W1.

---

## 6. Error handling strategy

| Failure mode | Module where it originates | Propagation path | Recovery |
|--------------|---------------------------|------------------|----------|
| Invalid webhook signature | webhook handler | HTTP 401 | terminal for request |
| Duplicate delivery | webhook / RunStore | HTTP 2xx no-op | idempotent |
| Postgres down at ingress | webhook / job enqueue | HTTP 503 | GitHub retry |
| Concurrent active run | RunOrchestrator | ForgeClient comment; no dispatch | terminal for new trigger |
| Handoff parse / contract mismatch | HandoffReader / PolicyEngine | block + comment | terminal until PE fixes artifacts |
| Pin / dispatch unavailable | PolicyEngine | block + comment | terminal (Decision #9) |
| AgentRunner timeout/crash | AgentRunner | stop run `failed` + notify | terminal for run; no workflow advance |
| Retry budget exhausted | PolicyEngine | stop + comment | terminal |
| ForgeClient 5xx/rate limit | ForgeClient | retry/backoff; `notify_pending` | recoverable notification |
| Missing programme / required env config | Settings / orchestration settings load | fail startup | terminal process |

---

## 7. Observability contract

| Module | Log level | Structured fields | Notes |
|--------|-----------|-------------------|-------|
| webhook handler | INFO/WARNING | `delivery_id`, `event_type`, `correlation_id` | never log full secrets |
| RunOrchestrator | INFO | `run_id`, `job_id`, `workflow_node`, `outcome` | kwargs not interpolated IDs |
| PolicyEngine | INFO/WARNING | `decision`, `block_reason`, `workflow_node` | |
| AgentRunner | INFO/ERROR | `runner`, `model_id`, `outcome`, `duration_ms` | |
| ForgeClient | INFO/WARNING | `operation`, `notify_pending`, audit ids, `auth_mode` (never token) | |
| status/metrics | INFO | `run_id` | auth failures WARNING without token value |

Align with `logging-loguru.mdc`: static messages + structured kwargs; correlation id from middleware / worker job context.

---

## 8. Data contract ownership

| Schema / data type | Owner (defines + validates) | Validation layer | Versioning |
|--------------------|----------------------------|------------------|------------|
| Programme/runtime config (living) | gateflow env settings + wave-start API + pin | startup / accept | amend-by-PE via PR / env |
| Handoff envelope | prayog-skills pin + gateflow HandoffReader | edge parse in HandoffReader | pin version |
| Workflow / delivery-contract | prayog-skills pin | WorkflowEngine load | pin `v0.5.0-rc.2` |
| Run / stage / event DTOs | gateflow models + repos | repository on read/write | amend with migrations |
| Job payload JSONB | gateflow Pydantic | repository | amend-by-PE |
| Webhook payload | GitHub + gateflow models | webhook edge | ignore unknown keys |
| Run event comment schema | gateflow Notifier | before ForgeClient | stable for H2 |

**Logical persistence groups (illustrative — exact DDL in human migrations):**
webhook delivery idempotency; run headers; per-node stages; append-only events;
async jobs. Column-level product fields stay in INIT/FR metrics schema and
migration review — not in ADRs.

---

## 9. Resolved engineering decisions

| Finding ID | Owner | Status | Question | Resolution | Required by | Default if deferred | Evidence / reference |
|------------|-------|--------|----------|------------|-------------|---------------------|----------------------|
| F-01, F-03 | PE | resolved | Runtime + durable store? | ADR-001 Option B | plan | — | adr-001-runtime-and-durable-store |
| F-02, F-04 | PE | resolved | Edge trust zones? | ADR-002 Option C | plan | — | adr-002-edge-trust-model |
| Q-3 | PE | resolved | Exact status/metrics/webhook paths? | TDD §3.6 illustrative mounts | plan | — | TDD_ONLY (not ADR) |
| F-05 | PE | resolved | Slot layer ownership? | ADR-003 Option B | plan | — | adr-003-slot-layer-ownership |
| Q-1 | PE | resolved | ForgeClient App vs PAT? | App prod; scoped PAT non-prod only (ADR-003); **impl** = required `GITHUB_AUTH_MODE=pat\|app` + InfraModule-bound TokenProvider (§3.5a) | W0 ForgeClient (mint deferred → close via §3.5a build) | — | adr-003 + TDD §3.5a |
| F-06 | PE | resolved | Programme config authority? | ADR-004 Option B | plan | — | adr-004-programme-config-authority |
| F-07 | PE | resolved | Model placement? | `src/models/` only | plan | — | TDD §3/§8 |
| F-08 | PE | resolved | Silent pin failure? | Forbidden; block+comment | plan | — | TDD §6 |
| Q-2 | PE | deferred | Postgres alert channel? | No dedicated alert in W1 | ops runbook | GitHub retry + operator watch | §4 DEFERRED |
| F-10 / A-3 | PE | deferred | Cursor SDK in container? | Assume yes; fail-closed; spike in build | W1 exit | Fail-closed runner | §4 DEFERRED |

---

## 10. Routed out — product questions (PM)

| ID | Owner | Status | Question | Blocking | Required by | Default if deferred | Evidence | Resolution reference |
|----|-------|--------|----------|----------|-------------|---------------------|----------|----------------------|
| — | — | — | None outstanding for this review | — | — | — | — | — |

---

## 11. Routed out — domain clarifications (SME)

| ID | Owner | Status | Question | Blocking | Required by | Default if deferred | Evidence | Resolution reference |
|----|-------|--------|----------|----------|-------------|---------------------|----------|----------------------|
| — | — | — | None | — | — | — | — | — |

---

## 12. Fix disposition

| ID | Status | Item | Target/evidence | Result digest |
|----|--------|------|-----------------|---------------|
| AF-1 | auto-fixed | As-built baseline | `docs/specification/as-built/implementation-status.md` (prior commit) | N/A |
| AF-2 | auto-fixed | Spec PR reference → #4 | `docs/specification/product/INIT-GATEFLOW-001-gateflow.md` References | updated this commit |

---

## 13. Implementation readiness verdict

| Gate | Status |
|------|--------|
| All T1–T11 checks | PASS |
| Engineering decisions resolved | 10 resolved, 2 deferred with defaults |
| Accepted ADR files written | 4 / 4 required |
| PM questions outstanding | 0 |
| Domain questions outstanding | 0 |
| Ready for PE review | YES |
| **Ready for /spec-implementation-plan** | **YES — PE Accepted TDD + ADRs; Gate 2 `spec-lgtm` still after plan on head** |

---

## Check summary

| Check | Status | Notes |
|-------|--------|-------|
| T1 Module boundaries | PASS | §2 table + diagram |
| T2 Interface contracts | PASS | §3.1–3.6 (+ §3.5a credential strategy) |
| T3 NEW-ADR dispositions | PASS | F-01+F-03→ADR-001; F-02+F-04→ADR-002; F-05→ADR-003; F-06→ADR-004; Q-3/F-07/08 TDD_ONLY; Q-2/F-10 deferred |
| T4 Test policy | PASS | §5 |
| T5 Error handling | PASS | §6 |
| T6 Observability | PASS | §7 |
| T7 Data contract ownership | PASS | §8 |
| T8 Dependency graph | PASS | api→business→repo→schema; infra clients upward only via business |
| T9 Engineering questions zero | PASS | §9 all resolved/deferred |
| T10 PE review readiness | PASS | ready_for_pe_review true; ready_for_plan true (artifacts Accepted) |
| T11 ADR artifact integrity | PASS | 4 Accepted files linked with digests |

---

## PR instructions

> Commit this TDD to the **Draft spec PR** branch. PE reviews on the **same PR**.
> Gate 2 label stays **`spec-pending`** until the implementation plan exists.
> PE accepts architecture by committing **Accepted** TDD/ADR files — not by
> setting `spec-lgtm` yet.

```
Branch:   chore/INIT-GATEFLOW-001-spec-gateflow
PR:       https://github.com/drivestream-lab/gateflow/pull/4
Meta PRD: https://github.com/drivestream-lab/prayog-meta/pull/9

Required reviewers:
  @drivestream-lab/prayog-pe-team

Review deadline: 2026-07-30
PE review checklist:
  [ ] T1 Module boundaries
  [ ] T2 Interface contracts
  [ ] T3 ADR dispositions — 4 Draft files (consolidated)
  [ ] T4 Test policy
  [ ] T9 Zero unresolved PE items
  [ ] T11 ADR artifact integrity

PE action (artifact acceptance — mid-lane):
  Review/comment or Request changes → update TDD/ADR files
  Explicitly state when decisions are ready for acceptance
  Update ADR + TDD Status Draft → Accepted; commit to spec branch
  Label remains spec-pending

After artifact acceptance:
  → /spec-implementation-plan on the same branch
  → after plan on head: PE sets spec-lgtm + Approve + attestation
```

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-technical-review
  outcome: pass
  artifact:
    path: docs/specification/reports/Technical-Review-INIT-GATEFLOW-001.md
    digest: sha256:97e0194ac118dae2a187af3c852a4836d577e1a49f25dbfa9d5d6c9e40e0781d
  blockers: []
  signals:
    ready_for_pe_review: true
    ready_for_plan: true
    artifacts_accepted: true
    accepted_by: nikd10x
    accepted_at: 2026-07-23T11:47:42Z
    draft_spec_pr: https://github.com/drivestream-lab/gateflow/pull/4
    gate2_label: spec-pending
    source_freshness: CURRENT
    map_revision: 3
    adr_required: 4
    adr_consolidation: 6_to_4
    adr_draft_files:
      - path: docs/specification/adr/adr-001-runtime-and-durable-store.md
        digest: sha256:2b57674fdd19dd9b70873a377470a3ea9b5b474b54f91077797cde5820372bbc
      - path: docs/specification/adr/adr-002-edge-trust-model.md
        digest: sha256:e9751d5c969a27dce82b7b3eebc0d4af6eed9cf5d3caeca0b74300ea9d137849
      - path: docs/specification/adr/adr-003-slot-layer-ownership.md
        digest: sha256:581236751ca755a6c26b4f0cbadf5adea010bfeeee20774fc6969013a3a8f632
      - path: docs/specification/adr/adr-004-programme-config-authority.md
        digest: sha256:64df031b81f3e70032f6c363373b5af98b02f50e0d3089eb8a25915d2da1f697
    deferred_with_default: [Q-2, F-10]
    tdd_only: [Q-3, F-07, F-08]
  next_candidates:
    - spec-implementation-plan
  human_checkpoint: false
  external_action: false
```
