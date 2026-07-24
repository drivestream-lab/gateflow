# Pre-implement — drivestream-lab/gateflow / W2 — Board APIs + gh-free deploy path

Produced by `/pre-implement` on 2026-07-24 for **INIT-GATEFLOW-002**. **No product code in this stage.**

---

### Gate check (prior wave)

> W2 requires INIT-GATEFLOW-002 W1 Ground Report + as-built `human_approved` (DEP-04). W1 PR must be merged to `develop`.

| Item | Required | Status |
|------|----------|--------|
| Branch context | `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | **ok** — not on `chore/*-spec-*`; W1 PR [#16](https://github.com/drivestream-lab/gateflow/pull/16) **MERGED** to `develop` @ `9c9ffda…`. Local checkout may still be on `feature/INIT-GATEFLOW-002-w1-model-pr-metrics` — **cut W2 from updated `develop` before `/loop-spec`** |
| Spec PR merged | Implementation plan on integration branch | **yes** — `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-002.md` on `origin/develop` |
| Gate 2 at merge | Merged spec PR had `spec-lgtm` on head | **verified** — PR [#10](https://github.com/drivestream-lab/gateflow/pull/10) MERGED; label `spec-lgtm`; head `82db4fe3…` |
| Board seed | Wave issue(s) from plan §9 exist | **seeded** — EPIC [#11](https://github.com/drivestream-lab/gateflow/issues/11); W0 [#12](https://github.com/drivestream-lab/gateflow/issues/12) CLOSED; W1 [#13](https://github.com/drivestream-lab/gateflow/issues/13) CLOSED; W2 [#14](https://github.com/drivestream-lab/gateflow/issues/14) OPEN (parent = #11) on **drivestream-lab Board** |
| Plan source freshness | all upstream rows `CURRENT` | **current** — spec / feasibility / TDD digests match on-disk SHA-256 (`9d437c0…` / `33d5b40…` / `12106d0…`) |
| Impact-map repo scope | revision and scope digest match canonical handoff | **match** — plan + TDD + PE attestation agree `map_revision: 1` and scope `sha256:3662f15e366994defaf08fa43b0a5a568eb152f6a74bcff73a0b0453dba0c901` (local `prayog-meta/` clone absent — not re-hashed from disk) |
| `check_command` | resolved | **`make check`** |
| `test_command` | resolved | **`make test`** |
| `verify_command` | resolved or N/A | **resolved** — W2 target: `.venv/bin/python -m tests.verify.verify_board`; interim baseline `.venv/bin/python -m tests.verify.verify_all` until script lands |
| `ground_command` | resolved or N/A | **N/A** — `/ground-spec` skill (no Makefile ground target) |
| Prior wave as-built row | `human_approved` | **INIT-002 W1 = human_approved** in `docs/specification/as-built/implementation-status.md` |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | **exists** — `docs/specification/reports/Ground-Report-INIT-GATEFLOW-002-W1.md` (**human_approved**) |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | **complete** (recorded; N/A as W2 gate — prior wave approval is the gate) |

**Gate verdict:** PASS

---

### Contracts consumed (from prior Ground Report)

> Source: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-002-W1.md` §Contracts produced. Confirmed against `src/` / `config/` / `tests/verify/`.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| Programme-token AuthN | Bearer programme token; `public_paths` for waves/runs/metrics | Authorization header | void or 401 | Ground-Report-002-W0/W1 + ADR-005 | **yes** — `src/app.py` lists `/api/v1/waves`, `/runs`, `/metrics`; **`/api/v1/board` not yet** |
| Forge PR open/update | ForgeClient `create_or_update_pull_request` | owner/repo, title, body, head, base | PR number | Ground-Report-002-W1 | **yes** — live in `forge_client.py`; board ops **not** present |
| Forge comments | ForgeClient `post_comment` | owner/repo/issue + body | comment id | W0/W1 | **yes** |
| Forbidden forge side effects | ForgeClient `add_labels` / `enable_auto_merge` | — | always raises | W0/W1 | **yes** — must remain for W2 board path |
| PR-at-run-start | RunOrchestrator `_ensure_run_pr` | run + `pr.*` | `pr_number` or `notify_pending` | Ground-Report-002-W1 | **yes** — uses ForgeClient PR only; **no board link/status calls** (FR-24 isolation baseline) |
| Run orchestration | RunOrchestrator `process_job` | claimed job | run summary | W1 | **yes** — worker isolation audit must prove **zero** board ForgeClient mutations on complete |
| Per-node model resolve | `resolve_node_dispatch` | programme + node id | four dispatch fields | W1 | **yes** — unchanged by W2 |
| Metrics dimensions | MetricsEmitter + metrics route | Bearer | `by_workflow_node` / `by_runner` / `by_model_id` | W1 | **yes** — unchanged by W2 |
| Cursor stub path | CursorAgentRunner `run_skill` | skill + model fields | AgentRunResult | W1 / V-3 | **yes** — **real SDK still deferred; not W2 scope** |
| DI / infra lifecycle | InfraModule binds ForgeClient | singleton | initialized client | W0/W1 | **yes** — BoardService will inject ForgeClient |

**Unconfirmed contracts** (new in INIT-002 W2 — no Ground Report backing):

- HTTP board surface TDD §3.3: `PATCH /api/v1/board/tickets/{id}/status`, `POST …/links`, `POST /tickets`, `GET /tickets` — **routes / models / BoardService absent**
- ForgeClient board methods (status update, create issue, list issues, link PR) — **not implemented** (only PR + comment + forbid helpers)
- Optional `Idempotency-Key` + EPIC/Feature idempotency on `initiative_id`+type + partial-failure body — **not implemented**
- Extend `public_paths` with `/api/v1/board` and programme-token dependency on board routes — **not done**
- Worker isolation audit (completing a wave run → zero board ForgeClient mutations) — **no assertion yet**
- Production `gh`-free guards / inspection checklist (FR-25 / FR-26a) — path currently has no `subprocess gh` in ForgeClient, but **explicit guards + docs checklist** still required
- Runbook laptop `gh` vs deploy ForgeClient (FR-26b) — `docs/runbooks/` exists for other topics; **FR-26b note absent**
- Live `tests/verify/verify_board.py` + README / `verify_all` wiring — **absent**
- **Q-4 exit gate** — App/Projects permission matrix still **open / deferred**; **blocks declaring W2 done** until confirmed or board MVP narrowed

→ Treat all of the above as **implementation + exit-gate scope**. No Alembic expected for board HTTP layer (forge-side only) unless PE narrows to a store-backed design (not in plan).

**Carried risks from W1 (non-blocking for start; watch in W2):**

- **D-W1-V1** — worker live soak for PR path still optional
- **D-W1-A1** — Cursor SDK deferred (follow-on; **not** W2)
- **D-W1-B1** — PR create may need remote branch existence in some orgs
- **RISK-02 / Q-4** — App/Projects permissions may force narrowed board MVP at exit

---

### Must read

- [x] `AGENTS.md`
- [x] MDC rules (domain-filtered for W2):
  - [x] `architecture.mdc` — API → business → infra; mount board under `/api/v1`; extend `public_paths`
  - [x] `http-api-conventions.mdc` — PATCH/POST bodies as Pydantic models in `src/models/`; list filters on GET query
  - [x] `pydantic-schemas.mdc` — board request/response DTOs only under `src/models/`; no models in `api/`
  - [x] `dependency-injection.mdc` — BoardService `@inject`; ForgeClient singleton; settings via `get_instance()`
  - [x] `infra-services.mdc` — board GitHub/Projects I/O stays in ForgeClient; BoardService = business
  - [x] `fail-fast.mdc` — bad payload 400; forge errors surface; no silent board success
  - [x] `logging-loguru.mdc` — structured kwargs (`operation=board_*`, ticket ids, initiative_id)
  - [x] `testing-verify-flows.mdc` — `verify_board` + README feature map; unit owns isolation / idempotency edges
  - [x] `strong-typing.mdc` / `python-imports.mdc` / `python-tooling.mdc` / `spec-driven-development.mdc`
  - skipped: `repository-pattern.mdc` / `database-migrations.mdc` as primary — board is forge-backed per TDD (re-read if store tables appear)
  - skipped: `code-guidelines-index.mdc` — index only
- [x] ADRs (keyword-matched):
  - [x] ADR-003 — ForgeClient = infra; App installation token in production; no PAT in prod; adapters stay infra
  - [x] ADR-005 — programme-token zone covers documented board **writes + reads**; extend `public_paths`; no user `AuthContext`
  - [x] ADR-001 — dual process unchanged; worker must not call board APIs
  - [x] ADR-002 — JWT/webhook zones unchanged (programme row superseded by ADR-005)
  - [x] ADR-004 / ADR-006 — background; no new programme board config required for dumb primitives
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-002-gateflow.md` (FR-24, FR-25, FR-26a, FR-26b; Q-3/Q-4)
- [x] Plan wave section: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-002.md` Phase W2
- [x] TDD contracts: `docs/specification/reports/Technical-Review-INIT-GATEFLOW-002.md` §3.3, §3.6, §5–§9 (board paths, Q-4 exit)
- [x] Prior Ground Report: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-002-W1.md`
- [x] `tests/README.md` — W0/W1 feature map; W2 board verify not yet listed

---

### Governance alignment

- [x] Slice spec does not contradict listed Accepted ADRs
- [x] Plan TASK MDC notes and ADR notes for W2 reviewed (TASK-W2-01…06)
- [x] Every initiative ADR cited for W2 is **Accepted** under `docs/specification/adr/`
- [x] Deferred PE defaults acknowledged:
  - **Q-4** — **blocks W2 exit** until App/Projects permission matrix confirmed or board MVP narrowed (TASK-W2-06)
  - **Q-5** / **V-3** — still deferred; **not** W2 coding scope (Cursor real SDK is follow-on)
- [x] Q-3 board list filters resolved in TDD §3.3 (narrow: `initiative_id`, `type`, `state`, `org`, `repo` / project id)

---

### Must update (in the same change as the code)

- [ ] Product spec — only if implementation drifts FR-24/25/26 contracts (prefer no drift)
- [ ] `docs/specification/as-built/implementation-status.md` — INIT-002 W2 verification rows (TASK-W2-05)
- [ ] `tests/README.md` — feature map: board APIs + `gh`-free inspection; wire `verify_board` into `verify_all`
- [ ] Unit — board CRUD/idempotency/partial-failure; worker isolation (zero board mutations); no `gh` subprocess on ForgeClient path
- [ ] Live — `verify_board` on running stack + programme token (+ forge credentials for create/list/status/link)
- [ ] Runbook — `docs/runbooks/` (or equiv): laptop `gh` vs deploy ForgeClient (FR-26b)
- [ ] Q-4 matrix doc or narrowed MVP note before declaring wave done
- [ ] ADR — none expected; do not re-litigate ADR-003/005

---

### Must not

- [ ] Contradict Accepted ADRs without superseding first
- [ ] Duplicate full HTTP board journeys in pytest when `verify_board` owns the live path
- [ ] Assume board ForgeClient methods / routes exist without building them
- [ ] Call board APIs or board ForgeClient methods from RunOrchestrator / job worker on start/finish (FR-24)
- [ ] Parse WorkManifest / governance inside board APIs (dumb primitives only)
- [ ] Shell / depend on `gh` on the production ForgeClient path (FR-25 / FR-26a)
- [ ] Allow PAT as production forge credential (ADR-003)
- [ ] Auto-merge or gate-approval label writes
- [ ] Replace or delete the board-seed skill; do not enforce laptop `gh` policy inside Gateflow runtime (FR-26b)
- [ ] Implement real Cursor SDK / OpenCode / Claude / Slack / Teams backends (out of scope / deferred)
- [ ] Define Pydantic models under `src/api/`
- [ ] Agent-authored Alembic under `postgres_migrations/versions/` (human only if DDL unexpectedly needed)
- [ ] Declare W2 complete without Q-4 confirmation or explicit MVP narrow (TASK-W2-06)

---

### Suggested implementation order (from plan)

1. Update local tree: `git fetch origin && git checkout develop && git pull` then cut `feature/INIT-GATEFLOW-002-w2-board` (plan also names `…-w2-gh-free` / `…-w2-verify` if split)
2. **TASK-W2-01** — board models + `BoardService` + `/api/v1/board/*` routes per TDD §3.3; ForgeClient board methods; EPIC/Feature idempotency; partial-failure body; `Idempotency-Key`; extend `public_paths` + DI
3. **TASK-W2-02** — integration/unit audit: wave-run complete → **zero** board ForgeClient mutations from worker
4. **TASK-W2-03** — production `gh`-free guards + inspection checklist (FR-25 / FR-26a)
5. **TASK-W2-04** — FR-26b runbook (laptop `gh` vs deploy ForgeClient)
6. **TASK-W2-05** — live `verify_board` + README / `verify_all` + as-built W2 rows
7. **TASK-W2-06** — **exit gate:** confirm Q-4 App/Projects permission matrix or narrow board MVP; document outcome

### Concrete paths (plan FILE-W2-*)

| Path | Action |
|------|--------|
| `src/api/v1/board_routes.py`, `src/api/v1/__init__.py` | create/edit — mount board routes |
| `src/models/` board DTOs (new module e.g. `board_models.py`) | create — request/response + partial-failure shapes |
| `src/business_services/board_service.py` | create — use cases → ForgeClient only |
| `src/infra_services/forge_client.py` | edit — board ops (status, create, list, link); keep no-`gh` |
| `src/app.py`, `src/di/modules/*`, `dependency_container.py` | edit — `public_paths` + BoardService bind |
| `tests/unit/**` | create/edit — board, isolation, gh-free guards |
| `tests/verify/verify_board.py`, `verify_all.py` | create/edit |
| `docs/runbooks/` (FR-26b), `tests/README.md`, `docs/specification/as-built/implementation-status.md` | create/edit |
| Q-4 matrix note (as-built or runbook) | create/edit at exit |

---

### W2 contract baselines (to implement against — TDD / spec)

**Board APIs (FR-24 / TDD §3.3 / §3.6)**

- Prefix `/api/v1/board`, programme-token auth (ADR-005)
- Routes: status PATCH; links POST; create POST; list GET with narrow filters (Q-3)
- Creates idempotent for **EPIC** and **Feature** on `initiative_id` + type; optional `Idempotency-Key` for multi-step create
- Partial-failure body lists created vs failed resources; bad payload → 400; forge failure → error (no silent success)
- Caller supplies fields — **no** WorkManifest/governance parsing
- **Wave worker must not invoke** these routes or equivalent ForgeClient board mutations on start/finish

**gh-free deploy (FR-25 / FR-26a)**

- Production PR/comment/**board** writes via ForgeClient only (App installation token preferred)
- Runtime must not depend on / shell `gh`; unit path guards + inspection checklist

**Laptop policy (FR-26b)**

- Document: board-seed / laptop **may** use local `gh`; does **not** replace board-seed skill; **not enforced** in Gateflow runtime

**Exit gate (Q-4 / TASK-W2-06)**

- Confirm App/Projects permission matrix **or** narrow board MVP and document before `human_approved`

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | format, lint, types, layers | `make check` |
| Unit | board CRUD/idempotency/partial; worker isolation; no `gh` | `make test` |
| Live verify | board APIs on stack | `.venv/bin/python -m tests.verify.verify_board` (wire into `verify_all` when ready) |
| Ground check | W2 FRs + boundaries + Q-4 | `/ground-spec` (no Makefile `ground_command`) |

---

### Tracker / PR

- Initiative: **INIT-GATEFLOW-002**
- Issue: **[#14](https://github.com/drivestream-lab/gateflow/issues/14)** (W2); parent EPIC [#11](https://github.com/drivestream-lab/gateflow/issues/11)
- Spec path: `docs/specification/product/INIT-GATEFLOW-002-gateflow.md`
- Verify command: `make check && make test` ; live `.venv/bin/python -m tests.verify.verify_board` (or `verify_all` once wired)
- ADRs in scope: ADR-003, ADR-005 (ADR-001 dual-process isolation; ADR-002 background)
- Suggested branch: `feature/INIT-GATEFLOW-002-w2-board`

---

### Merge order (if cross-module / cross-service)

N/A — single repo `drivestream-lab/gateflow`. Internal order: board models/routes/service + ForgeClient board ops → worker isolation audit → gh-free guards → FR-26b runbook → live verify + as-built → **Q-4 exit gate**. Initiative complete after W2 ground + merge (no W3 in plan).

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-Checklist-INIT-GATEFLOW-002-W2.md
    digest: sha256:69cea77dae9d192c2dc845d576b6a51e3c585193744a49de93932c4ab3cad31c
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-002
    wave: W2
    board_epic: https://github.com/drivestream-lab/gateflow/issues/11
    board_issue: https://github.com/drivestream-lab/gateflow/issues/14
    spec_pr: https://github.com/drivestream-lab/gateflow/pull/10
    prior_ground_report: docs/specification/reports/Ground-Report-INIT-GATEFLOW-002-W1.md
    w1_merged_pr: https://github.com/drivestream-lab/gateflow/pull/16
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_board
    ground_command: N/A — /ground-spec skill
    gate_verdict: PASS
    board_seed: complete
    source_freshness: CURRENT
    map_revision: 1
    deferred_defaults: [Q-4, Q-5, V-3]
    exit_gate: Q-4
    carried_risks: [D-W1-V1, D-W1-A1, D-W1-B1, RISK-02]
    suggested_branch: feature/INIT-GATEFLOW-002-w2-board
    not_in_scope: [cursor-sdk-real-path]
  next_candidates:
    - loop-spec
  human_checkpoint: true
  external_action: false
```
