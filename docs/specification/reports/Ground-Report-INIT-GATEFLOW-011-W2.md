# Ground report — INIT-GATEFLOW-011 W2

| Field | Value |
|-------|-------|
| Wave | W2 — Initiative list/detail (Gateflow-owned) (CAP-03) |
| Spec | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` |
| Initiative | INIT-GATEFLOW-011 |
| Date | 2026-08-07 |
| Wave head (exact) | `feature/INIT-GATEFLOW-011-w2-initiatives-owned` @ `e9654c2d4475f6e50a9e721e27dcdc8d8ce9f3de` — reviewed head for sign-off |
| PR URL | https://github.com/drivestream-lab/gateflow/pull/174 — open; `wave-accepted` on tip |
| Status | Draft — ready for `wave-done-action` / wave-signoff |
| Review deadline | 2026-08-11 |
| Deciders | Tech lead / reviewer — `wave-accepted` on tip; merge at wave-signoff only |
| Outcome | **pass** |
| Outcome reason | Wave-assigned REQs verified; tip `e9654c2` has `wave-accepted`; G1–G10 satisfied; §Contracts produced complete for W3+ |
| Assigned REQs | REQ-09 (partial), REQ-10, REQ-28 — from WorkManifest TASK-W2-01…03 `implements` |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution W2 | Pass-1 **319 passed**; ground re-proof 2026-08-07 **319 passed**; W2 subset **17 passed** (`test_initiative_readout` 9, `test_initiatives_read_api` 8) |
| Ground | `{ground_command}` undefined — manual `src/` + `tests/` scan | Entry points mapped below; service/routes/models/verify inspected; import-linter layers KEPT |
| Accept | `wave-accepted` on tip / wave-acceptance | **pass** — tip labels=`[wave-accepted]` @ `e9654c2`; human attested wave-acceptance |

## Automated ground check output

`{ground_command}` not defined in harness profile — **SKIPPED** (manual source + tests scan used).

Manual re-proof at ground time (2026-08-07):

- Tip SHA `e9654c2d4475f6e50a9e721e27dcdc8d8ce9f3de` on `feature/INIT-GATEFLOW-011-w2-initiatives-owned`
- `make check` → exit 0 (black, ruff, pyright, import-linter — layers KEPT, 1 contract kept)
- `make test` → **319 passed**
- W2 subset: 17 passed (9 service + 8 API)
- WorkManifest contract: "WorkManifest contract passed." (validated at pre-implement)
- PR [#174](https://github.com/drivestream-lab/gateflow/pull/174) labels: **`wave-accepted`**
- Learning-Extract W2 present with `items: []` (no human-fix signal; no prior-wave learning recurred)

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-09 (partial) | Initiative list/detail returns id, name/description, PRD approval state, affected repos, current stage, link to in-flight run — fields present or explicitly `unavailable` | `InitiativeReadoutService.list_initiatives` / `get_initiative`; `initiatives_routes.py` GET `/initiatives` + `/initiatives/{initiative_id}`; `initiative_readout_models.py` (`InitiativeListItem`/`InitiativeReadout` carry `initiative_id`, `name`, `prd_approval`, `prd_approval_reason`, `affected_repos`, `current_stage`, `current_stage_detail`, `in_flight_run`, `epic_ticket_id`, `epic_ticket_url`); `test_initiative_readout` (list/detail fields), `test_initiatives_read_api` (200 shape, 404 unknown initiative). **Partial**: PRD approval state is `unavailable` in W2 (W3 populates via meta bridge) — matches plan `GOAL-W2`. | **pass (partial)** |
| REQ-10 | Initiative read-out composed only from Gateflow-owned data (runs, board tickets) plus at most one read-only meta PR/label read — no new source of truth | `InitiativeReadoutService` reads `RunRepository.list_runs` (runs) + `BoardService.list_tickets` (board EPIC tickets); no meta read in W2; no parallel SoT; `PrdApprovalStateType.UNAVAILABLE` until W3; `test_initiative_readout` (composition from runs+board only). | **pass** |
| REQ-28 | No capability CAP-01–CAP-10 introduces POST/PUT/PATCH/DELETE product routes or calls `apply_labels`, review create/update, merge, or `update_board_status` | `/initiatives` + `/initiatives/{id}` GET-only (405 on POST — `test_initiatives_read_api`); 401 without programme token; no Forge write APIs on CAP-03 path (board reads via `BoardService.list_tickets` only); existing `POST /initiatives/closure/start` (INIT-010 W4) unchanged. | **pass** |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Business → repo/infra; no ORM in services | `architecture.mdc`, `repository-pattern.mdc` | **pass** — `InitiativeReadoutService` uses `RunRepository` (Pydantic out) + `BoardService` (business); ORM confined to repos |
| Models in `src/models/` only | `pydantic-schemas.mdc` | **pass** — DTOs in `initiative_readout_models.py`; routes import models; no models defined in `src/api/` |
| Programme-token on control-plane reads | ADR-005 | **pass** — `verify_programme_service_token` on `/initiatives` + `/initiatives/{id}`; `/api/v1/initiatives` on `public_paths` |
| Pin forge mutate authority; CAP-03 read-only | ADR-009, REQ-28 | **pass** — CAP-03 path has no Forge write actions; board reads via `BoardService.list_tickets` (read-only) |
| Fail closed on unknown initiative | `fail-fast.mdc`, REQ-09 | **pass** — 404 `no run or EPIC ticket found for initiative` distinct from malformed |
| Unit vs live separation | `testing-verify-flows.mdc` | **pass** — unit owns logic (mocked repos/board); live `verify_initiatives_readout` co-shipped (smoke only) |
| No new ORM table / no Alembic revision | `database-migrations.mdc` | **pass** — reads existing `runs` + board via ForgeClient; no `versions/` touched |
| Import layers | `python-tooling.mdc` (.importlinter) | **pass** — layers KEPT, 1 contract kept |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Run data (runs carry initiative_id/wave_id/org/repo/status) | as-built INIT-001/002; Ground-Report-W1 | **yes** — `RunRepository.list_runs` returns `RunModel` with required fields |
| Board EPIC ticket data (initiative_id label, column, title) | as-built INIT-002 W2; Ground-Report-W1 | **yes** — `BoardService.list_tickets` returns `BoardTicketResource` with `initiative_id`/`column`/`title` |
| Programme-token auth + public_paths | ADR-005; Ground-Report-W0/W1 | **yes** — `/api/v1/initiatives` already on `public_paths`; `verify_programme_service_token` reused |
| GET-only route + service + model precedent | Ground-Report-W0/W1 (checkpoints) | **yes** — CAP-03 follows CAP-01/02 structural shape |

## Discrepancies (must fix before human checkpoint)

| ID | REQ | Finding | Severity |
|----|-----|---------|----------|
| *(none)* | | | |

No open `GF-*` findings. G1–G10 satisfied.

## Learning cited

(From `Learning-Extract-INIT-GATEFLOW-011-W2.md` — cite only.)

| L-id | Class | How it affects this ground |
|------|-------|----------------------------|
| *(none)* | | W2 Learning-Extract emitted `items: []` — no human-fix signal; no prior-wave learning recurred (`wave-accepted` applied correctly on tip `e9654c2`) |

## Contracts produced by this wave

(REQUIRED — input for `/pre-implement` of W3 and later waves.)

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Initiative list (Gateflow-owned) | `InitiativeReadoutService` + `api/v1/initiatives_routes` | `list_initiatives(*, org, repo, limit, skip)` / `GET /api/v1/initiatives` | `org`, `repo` (board EPIC repo), `limit`, `skip` + programme token | `InitiativeListResult` (`initiatives[]` of `InitiativeListItem`: `initiative_id`, `name`, `prd_approval`, `prd_approval_reason`, `affected_repos`, `current_stage`, `current_stage_detail`, `in_flight_run?`, `epic_ticket_id?`, `epic_ticket_url?`) | Union of distinct `initiative_id` on runs + EPIC board tickets in `org/repo`; `affected_repos` deduped from runs; `current_stage` derived from active run / EPIC column / latest run; `prd_approval=UNAVAILABLE` in W2; read-only (no Forge writes) | W3 (PRD approval via meta bridge populates `prd_approval`); W4+ (wave map / spec lane / progress read-outs reuse initiative identity) |
| Initiative detail (Gateflow-owned) | `InitiativeReadoutService` + `api/v1/initiatives_routes` | `get_initiative(initiative_id, *, org, repo)` / `GET /api/v1/initiatives/{initiative_id}` | `initiative_id` (path) + `org`, `repo` (query) + programme token | `InitiativeReadout` (same fields as list item) | 404 `no run or EPIC ticket found for initiative` when neither runs nor EPIC exist (distinct from malformed); `prd_approval=UNAVAILABLE` in W2 | W3 (extends with meta-derived `prd_approval` + `unavailable` on meta-down per REQ-11) |
| `prd_approval` field contract | `initiative_readout_models.PrdApprovalStateType` | enum on `InitiativeListItem`/`InitiativeReadout` | — | `satisfied` \| `not_satisfied` \| `could_not_verify` \| `unavailable` | W2 always `unavailable` with `prd_approval_reason="meta bridge not yet wired (W3)"`; W3 populates via composed CAP-01 (`CheckpointEvidenceService.evaluate_composed`) against `prd-impact-acceptance` on the meta PR; meta-down → `unavailable` (REQ-11) | W3 |
| `current_stage` derivation | `InitiativeReadoutService._derive_stage` | called by `_build_item` | runs[] + epic? | `InitiativeStageType` + detail | `IN_PROGRESS` (active run) > `DONE` (EPIC column Done) > `IN_PROGRESS` (EPIC column In Progress) > `WAITING` (runs exist, none active) > `NOT_STARTED` (EPIC only) > `UNKNOWN` | W4 (wave map may reuse stage derivation); W6 (progress read-out) |
| Live verify CAP-03 | `tests/verify/verify_initiatives_readout.py` | module main | programme knobs; optional `GATEFLOW_INITIATIVE_ID` | exit 0 under prereqs | Smoke only; covers auth/shape/404 + live detail when env set; does not duplicate unit assertions | W3+ verify scripts |

## Exact-head merge package (for wave-signoff)

> Write the Ground Report and as-built updates **locally**. Emit Forge readiness for publication. Do **not** commit, push, merge, or apply labels from this skill. Human approved was `wave-acceptance`. At `wave-signoff` the human merges/publishes the **exact wave head** only.

- PR URL / wave head: https://github.com/drivestream-lab/gateflow/pull/174 @ `e9654c2d4475f6e50a9e721e27dcdc8d8ce9f3de` — **expected reviewed head SHA**
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W2.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-011-W2.md`
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-011-W2.md`
- Accept evidence: `wave-accepted` on tip `e9654c2` (wave-acceptance) — human approved already
- As-built: W2 `code complete (unit)` row already present; `human_approved` from wave-acceptance (do not re-mark as a second approve here)
- Required merge fields (human fills at `wave-signoff`; not `handoff.forge`):
  `reviewed_head_sha`, `merge_commit_sha`

### Human merge checklist (wave-signoff)

- [x] Apply **`wave-accepted`** on tip `e9654c2`
- [x] Ground Outcome **pass** (no GF-* findings)
- [ ] Review REQ checklist — all wave-assigned REQs pass (REQ-09 partial / REQ-10 / REQ-28)
- [ ] Review §Contracts produced — accurate for W3 `/pre-implement`
- [ ] Confirm reviewed head SHA matches the package above
- [ ] Confirm human_approved already recorded at wave-acceptance (label on tip)
- [ ] Merge the wave PR manually at wave-signoff (human only) — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge; no approval-label auto-merge

## Ready for wave-signoff (merge)?

**yes** — after `wave-done-action` moves board [#163](https://github.com/drivestream-lab/gateflow/issues/163) → Done; then human merges #174 @ `e9654c2` only.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W2.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-011
    wave: W2
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/163"
    ticket_id: "163"
    epic_ticket_id: "160"
    pr_number: 174
    pr_url: "https://github.com/drivestream-lab/gateflow/pull/174"
    reviewed_head_sha: "e9654c2d4475f6e50a9e721e27dcdc8d8ce9f3de"
    pass1_tip_sha: "e9654c2"
    contracts_produced: 5
    assigned_reqs:
      - REQ-09
      - REQ-10
      - REQ-28
    learning_cited: []
    tip_labels: ["wave-accepted"]
    wave_accepted_present: true
    unit_passed: 319
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "163"
    commit_workspace: required
    head_ref: feature/INIT-GATEFLOW-011-w2-initiatives-owned
    paths:
      - docs/specification/reports/Learning-Extract-INIT-GATEFLOW-011-W2.md
      - docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W2.md
      - docs/specification/as-built/implementation-status.md
```

