# Ground report — INIT-GATEFLOW-007 W1

| Field | Value |
|-------|-------|
| Wave | W1 — Learning Postgres ingest |
| Spec | `docs/specification/product/INIT-GATEFLOW-007-gateflow.md` |
| Initiative | INIT-GATEFLOW-007 |
| Date | 2026-08-01 |
| Wave head (exact) | `feature/INIT-GATEFLOW-007-w1-learning-ingest` @ `317f5c586675cafd17ec31da4771b3a39808a7f5` — reviewed head for sign-off |
| PR URL | https://github.com/drivestream-lab/gateflow/pull/102 — Draft |
| Board | https://github.com/drivestream-lab/gateflow/issues/86 |
| Status | Draft |
| Review deadline | 2026-08-05 |
| Deciders | Tech lead / reviewer — explicit LGTM required (human merge at wave-signoff) |
| Outcome | **pass** |
| Outcome reason | Wave-assigned REQs verified against ORM/service/orchestrator + unit + human Alembic + human `verify_all`; no Blocking GF-*; Contracts produced ready for W2 `/pre-implement` |
| Assigned REQs | REQ-9, REQ-10, REQ-11, REQ-12, REQ-17 — from plan TASK-W1-01…05 (REQ-12 cite path unit/inspection; live Ground cite dogfood = W2) |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution | **215 passed**; `test_learning_ingest` (parse/taxonomy/order); board label-wait unit |
| Ground | `{ground_command}` undefined — manual `src/` + `tests/**` scan | Entry points and tests mapped below |
| Live | `Live-Verify-INIT-GATEFLOW-007-W1.md` | Human **approved** `verify_all` at tip `317f5c5`; P15 N/A for learning HTTP |

## Automated ground check output

`{ground_command}` not defined in harness profile — **SKIPPED** (manual source + tests scan used).

Manual re-proof at ground time:

- `make check` → exit 0 (prior tip)
- `make test` → **215 passed**
- Human Alembic revision present: `postgres_migrations/versions/cc5feda8fe3d_add_learning_extracts_and_items.py`
- Ingest service: `src/business_services/learning_ingest_service.py`
- Orchestrator hook: `LEARNING_EXTRACT_NODE` after handoff ingest in `run_orchestrator.py`
- No learning HTTP routes under `src/api/`

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-9 | Persist Learning-Extract YAML in Postgres; human Alembic | `learning_schema` + `LearningRepository.upsert_extract` + migration `cc5feda8fe3d` + `test_learning_ingest` | **pass** |
| REQ-10 | Taxonomy `L-*` / SPEC\|SKILL\|HARNESS\|ENV; open\|codified | `LearningClassType` / `LearningItemDocument`; unit unknown class fails | **pass** |
| REQ-11 | No skill→Gateflow HTTP; worker ingest after hop; publish-before-ingest | Orchestrator order unit; no learning routes; H6 inspection | **pass** |
| REQ-12 | Ground cites `L-*` when Learning-Extract exists; does not re-author SSOT | This report §Learning cited; ingest SSOT in Postgres/artifact | **pass** (cite path); live tip cite in Pass-2 dogfood = W2 |
| REQ-17 | As-built + feature map for learning ingest | as-built W1 row; `tests/README` learning unit row | **pass** |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Postgres learning SSOT (ADR-001) | ADR-001 | **pass** — tables + human Alembic |
| Repo-only ORM; Pydantic at boundary | `repository-pattern.mdc`, `pydantic-schemas.mdc` | **pass** |
| DI bind LearningIngestService + repo | `dependency-injection.mdc` | **pass** |
| Fail closed missing/malformed artifact | `fail-fast.mdc` | **pass** — unit |
| Publish → handoff → ingest → policy (ADR-009 / Q-4) | ADR-009; TDD §3.4 | **pass** — unit order |
| Agent must not own `versions/` | `database-migrations.mdc` | **pass** — human `cc5feda8fe3d` |
| No learning HTTP (Q-7) | TDD / product | **pass** |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Closeout Enter-at `learning-extract` + baton | Ground-Report-007-W0 §Contracts | **yes** |
| Pass-2 pin: learning-extract → ground-spec → wave-signoff | pin / W0 Ground | **yes** |
| Forge publish-before-ingest on hop | ADR-009; existing `_publish_stage_workspace_if_needed` | **yes** |
| INIT-008: no PR-at-start; Draft PR at wave-pr-action | Ground-Report / as-built 008 | **yes** — drove L-01 harness fix |

## Discrepancies (must fix before human checkpoint)

| ID | REQ | Finding | Severity |
|----|-----|---------|----------|
| — | — | none | — |

## Learning cited

| L-id | Class | How it affects this ground |
|------|-------|----------------------------|
| L-01 | HARNESS | Tip includes `verify_pr_thread` rewrite — smoke aggregator no longer false-fails on missing PR-at-start |
| L-02 | HARNESS | Tip includes BoardService post-label visibility wait + verify Idempotency-Key replay — board idempotency live-stable |

## Contracts produced by this wave

(REQUIRED — input for `/pre-implement` W2.)

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Learning fence document | `src/models/learning_models` | `LearningExtractDocument` | fenced `learning_extract:` YAML | validated items + enums | `extra=forbid`; unknown class fails; empty items allowed | W2 dogfood asserts |
| Learning ORM | `learning_schema` + Alembic `cc5feda8fe3d` | tables `learning_extracts` / `learning_items` | run-scoped header + L-* rows | durable rows | unique `run_id`; UNIQUE(extract_id, item_key) | W2 live row evidence |
| Learning repository | `LearningRepository` | `upsert_extract` / `get_by_run_id` / `list_items` | session + create DTO + items | `LearningExtractModel` | idempotent per `run_id`; JSONB at boundary | W2 query evidence |
| Learning ingest | `LearningIngestService` | `ingest_after_learning_extract` | run + workspace (+ optional tip SHA) | upserted extract model | artifact path under reports_dir; fail closed missing fence | W2 closeout dogfood |
| Orchestrator hook | `RunOrchestrator` | after handoff when node=`learning-extract` | session + run + workspace | continue walker or FAILED | order: publish → handoff → ingest → policy | W2 full Pass-2 |
| Verify hygiene | `verify_pr_thread` / `verify_board` / BoardService wait | smoke aggregator | programme token + forge | exit 0 | no PR-at-start assert; label-index wait | W2 extends `verify_wave_closeout` |

## Exact-head human sign-off package

> Ground Report and as-built updates written **locally**. Emit Forge readiness for publication. Do **not** commit, push, merge, or apply labels from this skill. Human reviews the **exact wave head**, records approval, and merges manually at `wave-signoff`.

- PR URL / wave head: https://github.com/drivestream-lab/gateflow/pull/102 @ `317f5c586675cafd17ec31da4771b3a39808a7f5` — **expected reviewed head SHA** (publish closeout docs via `/commit-workspace` then reconfirm tip)
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-007-W1.md`
- Live evidence path: `docs/specification/reports/Live-Verify-INIT-GATEFLOW-007-W1.md`
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-007-W1.md`
- Learning path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-007-W1.md`
- As-built row prepared locally: INIT-007 W1 → **pending human_approved** (not marked `human_approved` by this skill)
- Required checkpoint evidence fields (human fills at `wave-signoff`; not `handoff.forge`): `reviewed_head_sha`, `merge_commit_sha`

### Human sign-off / merge checklist

- [ ] Review REQ checklist — all wave-assigned REQs pass or explicitly deferred
- [ ] Review §Contracts produced — accurate and complete for next wave
- [ ] Confirm reviewed head SHA matches tip after commit of Ground/Learning docs
- [ ] Mark as-built: INIT-GATEFLOW-007 W1 = human_approved (human only)
- [ ] Merge the wave PR manually (human only) — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge; no approval-label auto-merge

## Ready for human checkpoint?

**yes** — G1–G10 satisfied for wave-assigned REQs; Contracts produced; Learning cited; exact-head package ready after docs publish via `/commit-workspace`.

## Checks G1–G10

| ID | Result |
|----|--------|
| G1 Wave scope | **PASS** — W1 assigned REQs only (REQ-9…12,17); live ingest dogfood deferred W2 |
| G2 Ground / evidence | **PASS** — ground_command N/A; manual `src/` + `tests/**` + Live-Verify cited |
| G3 Assigned-REQ coverage | **PASS** — REQ-9,10,11,12,17 mapped |
| G4 Acceptance evidence | **PASS** — Wave-Execution unit + human Alembic + human `verify_all` |
| G5 ADR boundaries | **PASS** — ADR-001 Postgres SSOT; ADR-009 publish-before-ingest |
| G6 MDC boundaries | **PASS** — repository-pattern, pydantic-schemas, migrations (human versions), fail-fast |
| G7 Contracts consumed / produced | **PASS** — W0 contracts consumed; §Contracts produced for W2 |
| G8 Learning citations | **PASS** — L-01, L-02 cited from Learning-Extract W1 |
| G9 GF-* findings | **PASS** — none open |
| G10 Complete handoff | **PASS** — report + as-built pending + envelope; no commit/merge by this skill |

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-007-W1.md
    digest: sha256:b084c1e4a509896d5de74d1bc345c495561003977ef7c3c8d77e552b327f029d
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-007
    wave: W1
    contracts_produced: 6
    assigned_reqs:
      - REQ-9
      - REQ-10
      - REQ-11
      - REQ-12
      - REQ-17
    tip_sha: "317f5c586675cafd17ec31da4771b3a39808a7f5"
    pr_number: 102
    board_issue: "86"
    learning_cited:
      - L-01
      - L-02
    test_passed: 215
    live_verify: human_approved
  next_candidates:
    - wave-signoff
  human_checkpoint: true
  external_action: false
  forge:
    action: commit_workspace
    draft: false
    title: "[INIT-GATEFLOW-007] W1 — Learning extract + Ground Report closeout"
    body_path: docs/specification/reports/PR-body-INIT-GATEFLOW-007-W1.md
    head_ref: feature/INIT-GATEFLOW-007-w1-learning-ingest
    base_ref: develop
```
