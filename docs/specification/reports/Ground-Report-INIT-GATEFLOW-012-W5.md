# Ground report — INIT-GATEFLOW-012 W5

| Field | Value |
|-------|-------|
| Wave | W5 — Dormant ForgeClient.delete_branch |
| Spec | `docs/specification/product/INIT-GATEFLOW-012-gateflow.md` |
| Initiative | INIT-GATEFLOW-012 |
| Date | 2026-08-08 |
| Wave head (exact) | `aa6d2bf109dd83ba5bd25690bdb610e4c06a7325` |
| PR URL | https://github.com/drivestream-lab/gateflow/pull/196 |
| Board wave | [#190](https://github.com/drivestream-lab/gateflow/issues/190) |
| Status | Pass-2 closeout after `wave-accepted` (exact tip unchanged) |
| Review deadline | 2026-08-12 |
| Deciders | PE / tech lead at wave-signoff (merge only) |
| Outcome | **pass** |
| Outcome reason | REQ-26–27 map to unit + dormancy evidence; Contracts produced for initiative closure / future pin consumers; no Blocking GF-* |
| Assigned REQs | REQ-26, REQ-27 |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution | **461 passed** at loop-spec; delete_branch + dormancy subset **20 passed** (2026-08-08); TASK-W5-01…03 green |
| Ground | Manual `src/` + `tests/**` scan (no `{ground_command}`) | `delete_branch` → DELETE `_git_ref_update_path`; named fail-closed; AST zero callers in `src/` |
| Accept | [#196](https://github.com/drivestream-lab/gateflow/pull/196) tip `aa6d2bf…` label `wave-accepted` by @nikd10x (2026-08-08T11:52:05Z); P15 N/A | Tip SHA unchanged after label |
| Learning | `Learning-Extract-INIT-GATEFLOW-012-W5.md` | `human_fix_detected: false`; `items: []` |

## Automated ground check output

`{ground_command}` is **not defined** in `.harness/profile.yaml` — SKIPPED with reason: perform manual source + tests scan.

```text
make test → 461 passed (loop-spec 2026-08-08)
pytest tests/unit/test_forge_client.py tests/unit/test_delete_branch_dormant.py → 20 passed (2026-08-08)
rg "delete_branch" src → definition + log/error strings only (no Call sites)
```

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-26 | `ForgeClient` delete named branch via existing DELETE-ref transport (no new transport) | `ForgeClient.delete_branch` → `client.delete(_git_ref_update_path)`; unit `test_delete_branch_uses_delete_ref_path`; path family shared with tip PATCH | pass |
| REQ-27 | Fail closed on missing/protected; no silent no-op; gateflow dormancy guard (Q-6) | `LookupError` on 404; `PermissionError` on 403/422; units `test_delete_branch_missing_*` / `*_protected_*`; `test_delete_branch_dormant` zero `src/` Call sites | pass |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Method stays in infra ForgeClient | infra-services.mdc / ADR-009 | pass — no business/route wiring |
| Same DELETE-ref path as tip update | ADR-009 / plan W5 | pass — `_git_ref_update_path` only |
| Fail-fast named errors | fail-fast.mdc | pass — no 404-as-success |
| Structural dormancy G5 | product NFR / Q-6 | pass — unit code-guard; does not claim prayog-skills REQ-28–31 |
| No isolation infra invented | Ground-Report W4 / REQ-25 | pass — delete_branch does not add locks/worktrees |
| Repo-scoped concurrency unchanged | Ground-Report W4 | pass — no `find_active_run` changes |
| No agent Alembic `versions/` | database-migrations.mdc | pass — no DDL this wave |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Git-ref get/update path helpers | Ground-Report W4 / W2 | yes — DELETE composed on update path |
| Branch create/update transport | Ground-Report W2 | yes — no second HTTP client |
| Repo-scoped concurrency | Ground-Report W4 | yes — unrelated; left intact |
| No isolation infra | Ground-Report W4 / REQ-25 | yes |

## Discrepancies (must fix before human checkpoint)

| ID | REQ | Finding | Severity |
|----|-----|---------|----------|
| — | — | *(none)* | — |

## Learning cited

| L-id | Class | How it affects this ground |
|------|-------|----------------------------|
| — | — | Learning-Extract W5 `items: []` — empty extract justified; tip matches intent |

## Contracts produced by this wave

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Dormant branch delete | `ForgeClient` | `delete_branch` | owner, repo, branch | void on 200/204 | DELETE `_git_ref_update_path` only; no new transport | Future pin / prayog-skills may call; gateflow INIT-012 ships unwired |
| Fail-closed delete | `ForgeClient.delete_branch` | same | missing/protected HTTP | `LookupError` / `PermissionError` (branch named) | Never silent no-op; never treat 404 as success | Consumers must handle named errors |
| Dormancy code-guard | `tests/unit/test_delete_branch_dormant.py` | AST scan `src/` | — | assert zero `*.delete_branch(...)` Call sites | Method may exist; production Call sites forbidden this INIT | Relax only when a product wave wires callers |
| Unit-only accept surface | `tests/README.md` / as-built W5 | — | — | P15 N/A documented | No live verify script for delete_branch this INIT | Initiative closure / later activation waves |
| Unchanged concurrency | `RunRepository.find_active_run` | org+repo ACTIVE | — | unchanged from W4 | W5 must not re-narrow | Initiative closure |
| No pin-shape claim | inspection | — | — | gateflow does not own REQ-28–31 | CTR-01 / DEP-02 remains prayog-skills | Meta / skills repo |

## Exact-head merge package (for wave-signoff)

> Merge **only** the accepted tip below. Publish Pass-2 Learning + Ground (+ as-built human_approved) onto this head via `/commit-workspace` before or with signoff package.

- PR URL: https://github.com/drivestream-lab/gateflow/pull/196
- Reviewed / accepted tip SHA: `aa6d2bf109dd83ba5bd25690bdb610e4c06a7325`
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-012-W5.md`
- Accept evidence: GitHub label `wave-accepted` on tip (P15 N/A — unit + dormancy)
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-012-W5.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-012-W5.md`
- As-built: W5 → `human_approved` (this closeout)
- Required merge fields: `reviewed_head_sha` = tip above (update after Pass-2 publish commit if tip advances)

### Human merge checklist (wave-signoff)

- [ ] Draft PR tip matches accepted SHA (or successor Pass-2 publish commit on same head)
- [ ] Required checks green
- [ ] Merge to `develop` (human only — not Forge)
- [ ] Record merge commit SHA on board / as-built after merge
- [ ] Board [#190](https://github.com/drivestream-lab/gateflow/issues/190) → Done (`wave-done-action`)

## Ready for wave-signoff (merge)?

**yes** — after Pass-2 artifacts are on the wave head (`commit_workspace`). Last eng wave for INIT-GATEFLOW-012 gateflow half → initiative closure path after merge.

### Checks G1–G10

| ID | Result |
|----|--------|
| G1 Wave scope | PASS — W5 REQs only (REQ-26–27) |
| G2 Ground command / evidence | PASS — ground_command absent → manual scan + unit cited |
| G3 Assigned-REQ coverage | PASS — REQ-26–27 |
| G4 Acceptance evidence | PASS — `wave-accepted` on tip; P15 N/A contracted |
| G5 ADR boundaries | PASS — ADR-009 method-only; no pin invent |
| G6 MDC boundaries | PASS — infra / fail-fast / testing |
| G7 Contracts consumed / produced | PASS — W4 contracts match; §Contracts produced complete |
| G8 Learning citations | PASS — empty extract cited |
| G9 Stable GF-* | PASS — none open |
| G10 Complete handoff | PASS — exact-head package + forge Done ticket |

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-012-W5.md
  blockers: []
  signals:
    wave: W5
    contracts_produced: 6
    assigned_reqs: [REQ-26, REQ-27]
    reviewed_head_sha: aa6d2bf109dd83ba5bd25690bdb610e4c06a7325
    draft_pr: "https://github.com/drivestream-lab/gateflow/pull/196"
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/190"
    last_eng_wave: true
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    status: done
    ticket: "190"
    commit_workspace: required
    head_ref: feature/INIT-GATEFLOW-012-w5-delete-branch
    base_ref: develop
```
