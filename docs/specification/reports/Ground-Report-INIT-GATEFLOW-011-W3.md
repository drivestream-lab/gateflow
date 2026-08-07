# Ground report — INIT-GATEFLOW-011 W3

| Field | Value |
|-------|-------|
| Wave | W3 — Meta bridge + partial success (CAP-03 PRD approval) |
| Spec | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` |
| Initiative | INIT-GATEFLOW-011 |
| Date | 2026-08-07 |
| Wave head (exact) | `feature/INIT-GATEFLOW-011-w3-meta-bridge` @ `438761a21aa7bc110458b9d42b944a3ef4c542c4` — reviewed head for sign-off |
| PR URL | https://github.com/drivestream-lab/gateflow/pull/175 — open; `wave-accepted` on tip |
| Status | Draft — ready for `wave-done-action` / wave-signoff |
| Review deadline | 2026-08-11 |
| Deciders | Tech lead / reviewer — `wave-accepted` on tip; merge at wave-signoff only |
| Outcome | **pass** |
| Outcome reason | Wave-assigned REQs verified; tip `438761a` has `wave-accepted`; G1–G10 satisfied; §Contracts produced complete for W4+ |
| Assigned REQs | REQ-09 (complete), REQ-11, REQ-28 — from WorkManifest TASK-W3-01…03 `implements` |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution W3 | Pass-1 **325 passed**; ground re-proof 2026-08-07 **325 passed**; W3 service subset **15 passed** (`test_initiative_readout`) |
| Ground | `{ground_command}` undefined — manual `src/` + `tests/` scan | Entry points mapped below; service/verify inspected; import-linter layers KEPT |
| Accept | `wave-accepted` on tip / wave-acceptance | **pass** — tip labels=`[wave-accepted]` @ `438761a`; human attested wave-acceptance |

## Automated ground check output

`{ground_command}` not defined in harness profile — **SKIPPED** (manual source + tests scan used).

Manual re-proof at ground time (2026-08-07):

- Tip SHA `438761a21aa7bc110458b9d42b944a3ef4c542c4` on `feature/INIT-GATEFLOW-011-w3-meta-bridge`
- `make check` → exit 0 (black, ruff, pyright, import-linter — layers KEPT, 1 contract kept)
- `make test` → **325 passed**
- W3 subset: 15 passed (`test_initiative_readout`)
- WorkManifest contract: "WorkManifest contract passed."
- PR [#175](https://github.com/drivestream-lab/gateflow/pull/175) labels: **`wave-accepted`**
- Learning-Extract W3 present with `items: []` (no human-fix signal)

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-09 (complete) | Initiative list/detail returns PRD approval state (CAP-01 against `prd-impact-acceptance`) among owned fields — present or explicitly `unavailable` | `InitiativeReadoutService._resolve_prd_approval` → `MetaPrIntakeService.parse_url` + `CheckpointEvidenceService.evaluate("prd-impact-acceptance", meta CheckpointPrRef)`; list/detail via `_build_item`; `test_initiative_readout` (satisfied / not_satisfied / unavailable paths); `verify_initiative_meta_bridge` co-shipped. **Complete:** W2 Gateflow-owned fields + W3 meta-derived `prd_approval`. | **pass** |
| REQ-11 | When prayog-meta unreachable, Gateflow-owned fields still return **200**; meta-derived field marked `unavailable` | `_map_cap01_verdict` maps CAP-01 `could_not_verify` → `unavailable`; catch `httpx.HTTPError` / `NotFoundError` / invalid URL / missing `meta_pr_url` → `unavailable` with owned fields still composed; `test_initiative_readout` (ConnectError, NotFound, invalid URL, could_not_verify, no meta URL) | **pass** |
| REQ-28 | No CAP path introduces mutate routes or Forge write actions | Existing GET `/initiatives` + `/initiatives/{id}` only (no new routes); CAP-01 evaluate is read-only Forge; no `apply_labels`/review/merge/`update_board_status` from path; `test_initiatives_read_api` + `verify_initiative_meta_bridge` smoke | **pass** |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Business → repo/infra; no ORM in services | `architecture.mdc`, `repository-pattern.mdc` | **pass** — service uses `RunRepository` (Pydantic) + `BoardService` + `CheckpointEvidenceService` + `MetaPrIntakeService` |
| Models in `src/models/` only | `pydantic-schemas.mdc` | **pass** — reuses `PrdApprovalStateType` / DTOs; no models in `src/api/` |
| Programme-token on control-plane reads | ADR-005 | **pass** — existing GET routes + `public_paths` unchanged |
| Pin forge mutate authority; CAP-03 read-only | ADR-009, REQ-28 | **pass** — meta bridge is CAP-01 read only |
| Meta-down partial success (not full failure) | `fail-fast.mdc`, REQ-11 | **pass** — product-specified degrade to `unavailable` on 200 |
| Unit vs live separation | `testing-verify-flows.mdc` | **pass** — unit owns meta-up/down logic; live `verify_initiative_meta_bridge` smoke only |
| No new ORM table / no Alembic revision | `database-migrations.mdc` | **pass** — reads existing `meta_pr_url` column |
| Import layers | `python-tooling.mdc` | **pass** — layers KEPT, 1 contract kept |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Initiative list/detail (Gateflow-owned) | Ground-Report-W2 | **yes** — `list_initiatives` / `get_initiative` extended in place; owned fields unchanged |
| `prd_approval` field contract (`PrdApprovalStateType`) | Ground-Report-W2 | **yes** — W3 populates; W2 stub reason removed when meta wired |
| Live CAP-01 `evaluate(checkpoint_id, pr_ref)` | Ground-Report-W0 | **yes** — called with `prd-impact-acceptance` + meta ref |
| Meta PR URL parse (`MetaPrIntakeService.parse_url`) | as-built; W3 pre-implement | **yes** — used to build `CheckpointPrRef` |
| Run `meta_pr_url` durable field | as-built INIT-001 / wave-start | **yes** — `_first_meta_pr_url` reads runs |
| `evaluate_composed` is **not** the meta path | Ground-Report-W1 / W3 pre-implement design note | **yes** — service calls `evaluate` only for PRD line |

## Discrepancies (must fix before human checkpoint)

| ID | REQ | Finding | Severity |
|----|-----|---------|----------|
| *(none)* | | | |

No open `GF-*` findings. G1–G10 satisfied.

## Learning cited

(From `Learning-Extract-INIT-GATEFLOW-011-W3.md` — cite only.)

| L-id | Class | How it affects this ground |
|------|-------|----------------------------|
| *(none)* | | W3 Learning-Extract emitted `items: []` — no human-fix signal; tip `438761a` accepted correctly |

## Contracts produced by this wave

(REQUIRED — input for `/pre-implement` of W4 and later waves.)

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Meta PRD-approval resolve | `InitiativeReadoutService` | `_resolve_prd_approval(initiative_id, runs)` (used by list/detail) | initiative runs carrying optional `meta_pr_url` | `(PrdApprovalStateType, reason?)` | Meta URL → parse → `evaluate("prd-impact-acceptance", meta CheckpointPrRef)`; never uses `evaluate_composed`; read-only | W4+ (wave map / later read-outs may reuse initiative identity; PRD field already populated) |
| CAP-01 → initiative `prd_approval` map | `InitiativeReadoutService._map_cap01_verdict` | called after evaluate | CAP-01 `verdict` + optional `stale_reason` | `satisfied` / `not_satisfied` / `unavailable` | satisfied/not_satisfied 1:1; CAP-01 `could_not_verify` → `unavailable` (REQ-11); reason present when not satisfied/unavailable | W4+ consumers of list/detail shape |
| Meta-down partial success | `InitiativeReadoutService` + existing GET routes | list/detail HTTP | meta unreachable / missing URL / invalid URL / PR NotFound | HTTP 200; `prd_approval=unavailable`; owned fields still present | Never 5xx solely for meta-down; unknown initiative still 404 | W4+ must not regress partial-success envelope |
| Initiative list/detail (extended) | `InitiativeReadoutService` + `api/v1/initiatives_routes` | `list_initiatives` / `get_initiative` / GET `/api/v1/initiatives[+/{id}]` | org, repo (+ id) + programme token | `InitiativeListResult` / `InitiativeReadout` with populated `prd_approval` | Same Gateflow-owned composition as W2 + meta CAP-01; GET-only | W4 wave map nests under `/initiatives/{id}/waves` |
| Live verify CAP-03 meta | `tests/verify/verify_initiative_meta_bridge.py` | module main | programme knobs; optional initiative / expect / meta-down ids | exit 0 under prereqs | Smoke only; does not duplicate unit | W4+ verify scripts |

## Exact-head merge package (for wave-signoff)

> Write the Ground Report and as-built updates **locally**. Emit Forge readiness for publication. Do **not** commit, push, merge, or apply labels from this skill. Human approved was `wave-acceptance`. At `wave-signoff` the human merges/publishes the **exact wave head** only.

- PR URL / wave head: https://github.com/drivestream-lab/gateflow/pull/175 @ `438761a21aa7bc110458b9d42b944a3ef4c542c4` — **expected reviewed head SHA**
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W3.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-011-W3.md`
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-011-W3.md`
- Accept evidence: `wave-accepted` on tip `438761a` (wave-acceptance) — human approved already
- As-built: W3 row updated to `human_approved` from wave-acceptance (do not re-mark as a second approve here)
- Required merge fields (human fills at `wave-signoff`; not `handoff.forge`):
  `reviewed_head_sha`, `merge_commit_sha`

### Human merge checklist (wave-signoff)

- [x] Apply **`wave-accepted`** on tip `438761a`
- [x] Ground Outcome **pass** (no GF-* findings)
- [ ] Review REQ checklist — all wave-assigned REQs pass (REQ-09 / REQ-11 / REQ-28)
- [ ] Review §Contracts produced — accurate for W4 `/pre-implement`
- [ ] Confirm reviewed head SHA matches the package above
- [ ] Confirm human_approved already recorded at wave-acceptance (label on tip)
- [ ] Merge the wave PR manually at wave-signoff (human only) — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge; no approval-label auto-merge

## Ready for wave-signoff (merge)?

**yes** — after `wave-done-action` moves board [#164](https://github.com/drivestream-lab/gateflow/issues/164) → Done; then human merges #175 @ `438761a` only.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W3.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-011
    wave: W3
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/164"
    ticket_id: "164"
    epic_ticket_id: "160"
    pr_number: 175
    pr_url: "https://github.com/drivestream-lab/gateflow/pull/175"
    reviewed_head_sha: "438761a21aa7bc110458b9d42b944a3ef4c542c4"
    pass1_tip_sha: "438761a"
    contracts_produced: 5
    assigned_reqs:
      - REQ-09
      - REQ-11
      - REQ-28
    learning_cited: []
    tip_labels: ["wave-accepted"]
    wave_accepted_present: true
    unit_passed: 325
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "164"
    commit_workspace: required
    head_ref: feature/INIT-GATEFLOW-011-w3-meta-bridge
    paths:
      - docs/specification/reports/Learning-Extract-INIT-GATEFLOW-011-W3.md
      - docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W3.md
      - docs/specification/as-built/implementation-status.md
```
