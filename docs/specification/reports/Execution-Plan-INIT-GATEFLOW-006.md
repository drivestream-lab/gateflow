# Execution plan — INIT-GATEFLOW-006 (interactive)

> **Not** the Gate-2 implementation plan. Companion to
> [`Implementation-Plan-INIT-GATEFLOW-006.md`](Implementation-Plan-INIT-GATEFLOW-006.md).
> Use this for day-to-day execution. **PE OK on implementation plan**; this file
> adds file-level steps and **immediate dead-code removal** (no long deprecation
> windows).

| Field | Value |
|-------|-------|
| Spec | `docs/specification/product/INIT-GATEFLOW-006-gateflow.md` |
| Implementation plan | `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-006.md` |
| Mode | Interactive / backfill |
| Out of track | INIT-005 W2 dogfood |

## Policy: dead code

- Remove unused paths **in the same change** that introduces replacements.
- **No** multi-release “legacy alias” for `/waves/start` — at W3 cutover, replace
  callers and **delete** the undifferentiated start body/route (or thin redirect
  only if a live verify still hard-requires it for one PR, then delete next).
- Sweep ambient-only / superseded helpers when no remaining production caller.

---

## E0 — Dead-code sweep (do first)

| Step | Files | Action |
|------|-------|--------|
| E0.1 | `src/business_services/handoff_reader.py` | Confirm `find_latest_handoff` / `DEFAULT_ARTIFACT_GLOBS` have **no** packaged-automate callers (only debug/legacy tests). If zero production callers remain after audit, either delete or mark debug-only module with tests moved under `tests/unit` debug section — prefer **delete** if unused. |
| E0.2 | `tests/unit/test_handoff_workflow.py` | Drop or rewrite ambient-only tests if API removed; keep `read_path` tests. |
| E0.3 | `src/infra_services/cursor_agent_runner.py` | Confirm invent-prose / `_build_prompt` gone on automate path; delete any dead private helpers. |
| E0.4 | Grep tree | `programme.yaml`, `ProgrammeConfig`, `StageToolResolver` — ensure no resurrected stubs under `src/`. |
| E0.5 | `make check && make test` | Must stay green after sweep. |

---

## E1 — W0 forge publish (catch-up + live)

| Step | Files | Action |
|------|-------|--------|
| E1.1 | `src/models/forge_models.py`, `forge_types.py` | Gap audit vs REQ-1…5 |
| E1.2 | `src/business_services/workspace_commit_paths.py` | Gap audit path filter |
| E1.3 | `src/infra_services/forge_client.py` | Gap audit `commit_paths_to_branch` |
| E1.4 | `src/business_services/run_orchestrator.py` | Gap audit publish-before-ingest |
| E1.5 | `tests/unit/test_forge_policy.py`, `test_forge_client.py`, `test_workspace_commit_paths.py`, `test_run_orchestrator.py` | Fill unit gaps only |
| E1.6 | `tests/verify/verify_implement_lane.py`, `tests/config.yaml`, `.env` | Live `stage_commit` dogfood |
| E1.7 | `docs/specification/as-built/implementation-status.md`, `tests/README.md` | Record W0 live |

---

## E2 — W1 authorize (catch-up + live)

| Step | Files | Action |
|------|-------|--------|
| E2.1 | `src/business_services/forge_action_service.py` | Gap audit |
| E2.2 | `src/api/v1/forge_routes.py`, `src/api/v1/__init__.py` | Gap audit mount |
| E2.3 | `src/models/forge_models.py` (`ForgeAuthorizeRequest`) | Gap audit |
| E2.4 | `tests/unit/test_forge_action_service.py`, `test_forge_merge.py` | Gaps |
| E2.5 | Live authorize against STOPPED run | Evidence in as-built |
| E2.6 | as-built + `tests/README.md` | W1 complete |

---

## E3 — W2 sparse notify (catch-up)

| Step | Files | Action |
|------|-------|--------|
| E3.1 | `src/business_services/notifier.py` | Confirm milestone allowlist |
| E3.2 | `src/business_services/run_orchestrator.py` | Confirm `stage_started` append |
| E3.3 | `tests/unit/test_notifier.py` | Gaps |
| E3.4 | as-built | W2 complete |

---

## E4 — ADR-010 (before lane APIs)

| Step | Files | Action |
|------|-------|--------|
| E4.1 | `docs/specification/adr/adr-010-lane-intake-and-dual-workspace-authority.md` | **Create** Draft → PE Accept |
| E4.2 | `docs/specification/product/INIT-GATEFLOW-006-gateflow.md` | Resolve Q-5 |
| E4.3 | `docs/specification/as-built/implementation-status.md` | Truth-split row for ADR-010 |
| E4.4 | `docs/specification/README.md` | Link ADR-010 when Accepted |

---

## E5 — W3 lane start APIs (+ delete undifferentiated start)

| Step | Files | Action |
|------|-------|--------|
| E5.1 | `src/models/wave_start_models.py` (**new**) or split in `adapter_models.py` | `ImplementWaveStartRequest`, `SpecWaveStartRequest`, shared response; **remove** undifferentiated `WaveStartRequest` once callers moved |
| E5.2 | `src/api/v1/waves_routes.py` | Add `implement/start` + `spec/start`; **delete** `POST /waves/start` after verify/helper updates |
| E5.3 | `src/business_services/wave_start_service.py` | Refactor / split; implement path = ticket Enter-at; spec path = require meta fields (path checks); delete dead branches |
| E5.4 | `src/business_services/trigger_router.py` | Update error text to new paths |
| E5.5 | `src/di/modules/business_services_module.py`, `dependency_container.py` | Only if new service types |
| E5.6 | `tests/unit/test_wave_start.py`, `tests/verify/verify_wave_start.py`, `tests/_helpers/*` | Retarget implement path; remove old body fixtures |
| E5.7 | `tests/README.md`, as-built | Document two starts; no legacy route |

---

## E6 — W4 meta accept + dual bind + spec verify

| Step | Files | Action |
|------|-------|--------|
| E6.1 | `src/infra_services/forge_client.py` and/or `src/business_services/meta_pr_intake.py` (**new**) | Parse URL, fetch PR, initiative check |
| E6.2 | `src/database/postgres/schema/run_store_schema.py`, `src/models/run_store_models.py`, `src/database/postgres/repository/run_store_repository.py`, `postgres_migrations/env.py` | Persist `meta_pr_url` / `meta_head_sha` (names TDD) |
| E6.3 | `postgres_migrations/versions/` | **Human** Alembic |
| E6.4 | `src/business_services/prompt_resolver.py`, bind models if any, `run_orchestrator.py` | Inject `meta_workspace` / `meta_pr_url` |
| E6.5 | `src/business_services/wave_start_service.py` | Wire accept-gate before enqueue |
| E6.6 | pin (prayog-skills): `workflow.yaml`, skill `prompts/schema.yaml` | Orchestrate spec chain; declare bind vars — **not gateflow commit** |
| E6.7 | `tests/verify/verify_spec_lane.py`, `tests/config.yaml.example` | Replace stub; implement live harness |
| E6.8 | `tests/unit/*` for intake + bind | New/updated |
| E6.9 | as-built, `tests/README.md`, INIT-006 | W4 complete |

---

## Order

```text
E0 dead code → E1 W0 → E2 W1 → E3 W2 → E4 ADR-010 → E5 W3 (delete old start) → E6 W4
```

## Explicit non-work

- INIT-005 W2
- Authorize-resume
- Invented labels
- Long-lived `/waves/start` alias
