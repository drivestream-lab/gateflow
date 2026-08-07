# Ground report — INIT-GATEFLOW-011 W0

| Field | Value |
|-------|-------|
| Wave | W0 — Checkpoint status-check foundation (CAP-01) |
| Spec | `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` |
| Initiative | INIT-GATEFLOW-011 |
| Date | 2026-08-07 |
| Wave head (exact) | `feature/INIT-GATEFLOW-011-w0-checkpoint-status` @ `088d125c67d6306c1d1ddba28ee5cb01c1ec9f3d` — reviewed head for sign-off |
| PR URL (if any) | https://github.com/drivestream-lab/gateflow/pull/171 — open |
| Board | https://github.com/drivestream-lab/gateflow/issues/161 |
| Status | Draft — ready for `wave-done-action` / wave-signoff |
| Review deadline | 2026-08-11 |
| Deciders | Tech lead / reviewer — `wave-accepted` on tip; merge at wave-signoff only |
| Outcome | **pass** |
| Outcome reason | Wave-assigned REQs verified; tip `088d125` has `wave-accepted`; GF-01 closed; §Contracts produced complete for W1 |
| Assigned REQs | REQ-01, REQ-02, REQ-04, REQ-05, REQ-28 — from WorkManifest TASK-W0-01…05 `implements` |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution W0 | Pass-1 **283 passed**; ground re-proof 2026-08-07 **283 passed**; W0-focused subset **27 passed** (`test_forge_client`, `test_checkpoint_vocab`, `test_checkpoint_evidence`, `test_checkpoints_api`) |
| Ground | `{ground_command}` undefined — manual `src/` + `tests/` scan | Entry points mapped below; mutate guards inspected on CAP-01 path |
| Accept | `wave-accepted` on tip / wave-acceptance | **pass** — tip labels=`[wave-accepted]` @ `088d125` (2026-08-07 re-check); human attested live verify |

## Automated ground check output

`{ground_command}` not defined in harness profile — **SKIPPED** (manual source + tests scan used).

Manual re-proof at ground time (2026-08-07):

- Tip SHA `088d125c67d6306c1d1ddba28ee5cb01c1ec9f3d` on `feature/INIT-GATEFLOW-011-w0-checkpoint-status`
- Product content SHA `ee9f706` (CAP-01); tip `088d125` is forge publish-SHA chore only
- `make test` → **283 passed**
- W0 subset: `.venv/bin/pytest tests/unit/test_forge_client.py tests/unit/test_checkpoint_vocab.py tests/unit/test_checkpoint_evidence.py tests/unit/test_checkpoints_api.py -q` → **27 passed**
- PR [#171](https://github.com/drivestream-lab/gateflow/pull/171) CI green; labels observed (re-check): **`wave-accepted`**
- Learning-Extract W0 present with L-01 (SKILL — label vocabulary; GF-01 closed after label fix)

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-01 | Checkpoint status-check accepts pin checkpoint id + PR refs; read-only | `GET /api/v1/checkpoints/status` (`checkpoints_routes.py`); `CheckpointEvidenceService.evaluate`; `test_checkpoints_api`, `test_checkpoint_evidence`; live script `tests/verify/verify_checkpoint_status.py` | **pass** (code/unit; live human-attested) |
| REQ-02 | Evidence from pinned delivery-contract labels+review_roles+checks live at head | `WorkflowEngine.get_github_checkpoint_vocab`; `ForgeClient.list_reviews` / `list_check_runs`; merge fields on `GithubPullRequestDocument`; `test_checkpoint_vocab`, `test_forge_client` | **pass** |
| REQ-04 | Non-pass lists missing items by name | `CheckpointMissingItem` + `_collect_missing` in `checkpoint_evidence_service.py`; unit missing-item cases | **pass** |
| REQ-05 | Status-check never mutates GitHub/board | CAP-01 path uses only `get_pull_request` / `list_reviews` / `list_check_runs`; no `apply_labels` / board / merge on evaluate route; zero-mutate unit tests | **pass** |
| REQ-28 | GET-only; no mutate from CAP paths | Router GET only; non-GET → 405 in `test_checkpoints_api`; `/api/v1/checkpoints` on `public_paths` in `app.py` | **pass** |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Business → repo/infra; no ORM in services | `architecture.mdc`, `repository-pattern.mdc` | **pass** — CAP-01 service uses ForgeClient + WorkflowEngine only (no persistence this wave) |
| Models in `src/models/` only | `pydantic-schemas.mdc` | **pass** — `checkpoint_models.py`; routes import models |
| Programme-token on control-plane reads | ADR-005 | **pass** — `verify_programme_service_token` on status route |
| Pin forge mutate authority; CAP-01 read-only | ADR-009, REQ-05/28 | **pass** — evaluate path has no write Forge actions |
| Fail closed on GitHub down | `fail-fast.mdc`, REQ-01 error table | **pass** — `could_not_verify` verdict |
| Unit vs live separation | `testing-verify-flows.mdc` | **pass** — unit owns evidence logic; live `verify_checkpoint_status` co-shipped |
| No persistence in W0 | plan GOAL-W0 | **pass** — history/persist deferred W1 |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| ForgeClient PR read + pin forge policy baseline | INIT-GATEFLOW-010 Ground Reports / as-built | **yes** — extended with `list_reviews` / `list_check_runs` / merge fields; no write APIs added for CAP-01 |
| Programme-token HTTP pattern | ADR-005 / existing `api/v1` routes | **yes** — same dependency as other programme GETs |
| Pinned `delivery-contract.yaml` review_roles / labels | pin consume INIT-010 | **yes** — vocab resolved from tip pin, not hardcoded |
| Prior wave Ground Report for INIT-011 | n/a (W0 first wave) | **n/a** — no prior INIT-011 Ground Report |

## Discrepancies (must fix before human checkpoint)

| ID | REQ | Finding | Severity |
|----|-----|---------|----------|
| GF-01 | — (accept gate) | Tip lacked `wave-accepted` (had `spec-lgtm`) — **closed** 2026-08-07: tip now `wave-accepted` @ `088d125`; cite L-01 | Closed |

## Learning cited

| L-id | Class | How it affects this ground |
|------|-------|----------------------------|
| L-01 | SKILL | Documented accept-label vocabulary miss; GF-01 closed after human applied `wave-accepted`; keep open for skill/AGENTS codify |

## Contracts produced by this wave

(REQUIRED — input for `/pre-implement` W1.)

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Live CAP-01 evaluate | `CheckpointEvidenceService` | `evaluate(checkpoint_id, pr_ref)` | pin checkpoint id ∈ six review_roles keys; owner/repo/PR number | `CheckpointStatusResult` with verdict ∈ {satisfied, not_satisfied, could_not_verify}, optional `checked_sha`/`checked_at`, itemized `missing_items` | Read-only Forge calls only; unknown checkpoint → 404; GitHub down → could_not_verify never silent pass | W1 wraps same evaluate with persist + stale rules |
| Pin checkpoint vocabulary | `WorkflowEngine` | `get_github_checkpoint_vocab()` | pinned delivery-contract at process tip | map of six checkpoint ids → labels + review_roles + required check-runs | No hardcoded per-phase evidence sets | W1 reuses; stale uses head SHA vs evidence timing |
| ForgeClient evidence reads | `ForgeClient` | `list_reviews`, `list_check_runs`, `get_pull_request` (merge fields) | org/repo/PR or commit SHA | review / check-run / PR documents | No CAP-01 path may call label/board/merge writes | W1 unchanged read surface |
| HTTP status surface | `api/v1/checkpoints_routes` | `GET /api/v1/checkpoints/status` | query: checkpoint_id, owner, repo, pr_number + programme token | `CheckpointStatusResult` JSON | GET-only; prefix on `public_paths`; no persistence response fields yet | W1 adds history + composed readout routes under same prefix |
| Live verify CAP-01 | `tests/verify/verify_checkpoint_status.py` | module main | programme knobs; optional `GATEFLOW_CHECKPOINT_PR` | exit 0 under prereqs | Smoke only; does not prove persistence | W1 adds `verify_checkpoint_history` |

## Exact-head merge package (for wave-signoff)

> Write the Ground Report and as-built updates **locally**. Emit Forge readiness for publication. Do **not** commit, push, merge, or apply labels from this skill. Human approved was `wave-acceptance`. At `wave-signoff` the human merges/publishes the **exact wave head** only.

- PR URL / wave head: https://github.com/drivestream-lab/gateflow/pull/171 @ `088d125c67d6306c1d1ddba28ee5cb01c1ec9f3d` — **expected reviewed head SHA**
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W0.md`
- Accept evidence: `wave-accepted` on tip `088d125` (wave-acceptance) — human approved already
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-011-W0.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-011-W0.md`
- Optional/legacy Live-Verify path: n/a (not required)
- As-built: W0 `human_approved` from wave-acceptance (do not re-mark as a second approve here)
- Required merge fields (human fills at `wave-signoff`; not `handoff.forge`):
  `reviewed_head_sha`, `merge_commit_sha`

### Human merge checklist (wave-signoff)

- [x] Apply **`wave-accepted`** on tip `088d125`
- [x] Ground Outcome **pass** (GF-01 closed)
- [ ] Review REQ checklist — all wave-assigned REQs pass
- [ ] Review §Contracts produced — accurate for W1 `/pre-implement`
- [ ] Confirm reviewed head SHA matches the package above
- [ ] Confirm human_approved already recorded at wave-acceptance (label on tip)
- [ ] Merge the wave PR manually at wave-signoff (human only) — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge; no approval-label auto-merge

## Ready for wave-signoff (merge)?

**yes** — after `wave-done-action` moves board [#161](https://github.com/drivestream-lab/gateflow/issues/161) → Done; then human merges #171 @ `088d125` only.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W0.md
    digest: sha256:4a1e7b1150639818dfb3eadee19432cedda0cd280b6fc519ad0e7195f4a519ec
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-011
    wave: W0
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/161"
    ticket_id: "161"
    epic_ticket_id: "160"
    pr_number: 171
    pr_url: "https://github.com/drivestream-lab/gateflow/pull/171"
    reviewed_head_sha: "088d125c67d6306c1d1ddba28ee5cb01c1ec9f3d"
    pass1_tip_sha: "ee9f706"
    contracts_produced: 5
    assigned_reqs:
      - REQ-01
      - REQ-02
      - REQ-04
      - REQ-05
      - REQ-28
    learning_cited:
      - L-01
    tip_labels: ["wave-accepted"]
    wave_accepted_present: true
    unit_passed: 283
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    ticket: "161"
    commit_workspace: required
    head_ref: feature/INIT-GATEFLOW-011-w0-checkpoint-status
    paths:
      - docs/specification/reports/Learning-Extract-INIT-GATEFLOW-011-W0.md
      - docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W0.md
      - docs/specification/as-built/implementation-status.md
```
