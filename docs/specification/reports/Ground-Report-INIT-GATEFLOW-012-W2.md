# Ground report — INIT-GATEFLOW-012 W2

| Field | Value |
|-------|-------|
| Wave | W2 — Branch create-or-reuse |
| Spec | `docs/specification/product/INIT-GATEFLOW-012-gateflow.md` |
| Initiative | INIT-GATEFLOW-012 |
| Date | 2026-08-08 |
| Wave head (exact) | `feature/INIT-GATEFLOW-012-w2-branch-resolve` @ `3191407dd4fe2f5e1c67dac01f8b9a2e62b5e0c8` — reviewed head for sign-off (Pass-2 docs publish may advance tip) |
| PR URL | https://github.com/drivestream-lab/gateflow/pull/193 |
| Board wave | [#187](https://github.com/drivestream-lab/gateflow/issues/187) |
| Status | Ready for wave-signoff package |
| Review deadline | 2026-08-12 |
| Deciders | Tech lead / reviewer — human_approved already at wave-acceptance (`wave-accepted`); wave-signoff is merge only |
| Outcome | **pass** |
| Outcome reason | All W2-assigned REQs map to unit/inspection evidence; `wave-accepted` on tip; Contracts produced complete for W3; no Blocking GF-* |
| Assigned REQs | REQ-16, REQ-17, REQ-18, REQ-19 |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution | **440 passed** (reconfirmed 2026-08-08); TASK-W2-01…02 green |
| Ground | Manual `src/` + `tests/**` scan (no `{ground_command}` in harness profile) | `resolve_branch` / naming / checkout / verify script inspected against REQ claims |
| Accept | `wave-accepted` on [#193](https://github.com/drivestream-lab/gateflow/pull/193) tip `3191407` (@nikd10x, 2026-08-08T10:42:26Z) | Human wave-acceptance; live script co-shipped |
| Learning | `Learning-Extract-INIT-GATEFLOW-012-W2.md` | `human_fix_detected: false`; `items: []` |
| PE gate | `PE-Waiver-INIT-GATEFLOW-012-W2-PE1.md` | Coding start = current pin 0 BROKEN existing nodes; CTR-01 consume → DEP-02 |

## Automated ground check output

`{ground_command}` is **not defined** in `.harness/profile.yaml` — SKIPPED with reason: perform manual source + tests scan (documented in REQ checklist and Boundary checks).

```text
make test → 440 passed (2026-08-08)
pytest tests/unit/test_forge_policy.py::test_all_remounted_pin_nodes_parse → PASSED (PE-1 W2 waiver)
pytest …::test_resolve_branch_new_wave_* / continuation_* / explicit_head_missing_* → PASSED
```

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-16 | New wave (no remote head) forks from live `base_branch` tip | `RunOrchestrator.resolve_branch` → `ForgeClient.ensure_branch_from_base`; unit `test_resolve_branch_new_wave_*`; live `verify_branch_lifecycle` | pass |
| REQ-17 | Deterministic head naming; no second scheme | `build_wave_head_branch` / `branch_slug_from_head_ref`; `BranchResolveModeType`; `test_pr_branch_naming` + slug-from-head tests | pass |
| REQ-18 | Continuation reuses existing head; zero new branch creates | Remote tip exists or explicit `head_ref` → no `ensure_branch_from_base`; unit continuation + process_job missing-head; live tip-stable assert | pass |
| REQ-19 | Continuation on never-cloned workspace composes clone then checkout | Tenant `resolve_workspace` + `checkout_branch` when omitted-path (`tenant_bound`); unit checkout companion; live never-cloned path | pass |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Compose existing forge + naming primitives only (no third branch API) | TDD §3.5 / ADR-010 D2 | pass — `resolve_branch` uses `ensure_branch_from_base` + tip probe + `branch_slug_from_head_ref` |
| Fail closed when explicit continuation head missing | fail-fast.mdc / product negative path | pass — ValueError `continuation branch not found on remote`; no re-fork |
| Explicit workspace path never mutated by checkout | REQ-12 / W1 contract | pass — checkout only when `tenant_bound` from omit-path resolve |
| Subprocess git only for local checkout | FF-04 / infra-services.mdc | pass — `checkout_branch` via `_run_git` |
| No ORM in business; ForgeClient remains infra | architecture.mdc / repository-pattern.mdc | pass — import-linter KEPT |
| CTR-01 / REQ-28–31 not claimed | PE-Waiver W2 / impact map H2 | pass — no invented pin node shapes; coding-start waiver only |
| Agents do not author Alembic `versions/` | database-migrations.mdc | pass — no DDL this wave |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Workspace resolve (clone/fetch) | Ground-Report W1 | yes — `TenantGitWorkspaceClient.resolve_workspace` + DI |
| Tenant git credential lookup | Ground-Report W1 | yes — omit-path resolve still binds tenant before checkout |
| Orchestrator workspace bind | Ground-Report W1 | yes — `_resolve_job_workspace_path` returns `(path, tenant_bound)` |
| Existing branch primitives | Ground-Report W1 + source | yes — `ensure_branch_from_base` / naming helpers composed, not replaced |
| PE-1 pin sequencing (W2 coding-start waiver) | PE-Waiver W2 + W1 note | yes — existing-node 0 BROKEN; consume gate remains DEP-02 |

## Discrepancies (must fix before human checkpoint)

| ID | REQ | Finding | Severity |
|----|-----|---------|----------|
| — | — | None | — |

## Learning cited

| L-id | Class | How it affects this ground |
|------|-------|----------------------------|
| *(none)* | — | Learning-Extract reports `items: []` with `human_fix_detected: false`; no L-* to cite |

## Contracts produced by this wave

| Contract | Module / component | Entry point | Input shape | Output shape | Invariants | Next wave |
|----------|--------------------|-------------|-------------|--------------|------------|-----------|
| Branch resolve (new vs continuation) | `RunOrchestrator` | `resolve_branch` | org, repo, run, job payload (`base_branch`, identity / optional `head_ref`) | head ref string + mode (`new_wave` \| `continuation`) | New-wave calls `ensure_branch_from_base` from live base tip; continuation never creates refs; explicit `head_ref` missing → named fail-closed | W3 harness-readiness may assume head already bound |
| Local head checkout after tenant resolve | `TenantGitWorkspaceClient` | `checkout_branch` | workspace path, branch, org, repo | side-effect: workspace on `origin/{branch}` | Only after omitted-path tenant bind; never on explicit caller cwd | W3+ walker hops on correct branch tree |
| Deterministic naming (unchanged scheme) | `pr_branch_naming` | `build_wave_head_branch` / `branch_slug_from_head_ref` | initiative, wave, slug / head_ref | `feature/{INIT}-{wn}-{slug}` | No second naming scheme | All later waves |
| Live branch lifecycle verify | `tests/verify/verify_branch_lifecycle.py` | module main | API + worker + PAT + programme token | exit 0 for new fork + continuation tip-stable + never-cloned checkout | P15 human at wave-acceptance; `require_worker: true` | W3 may keep secondary |
| PE-1 coding-start vs consume | PE-Waiver W2 | board [#187] + pin tip | existing remounted nodes | 0 BROKEN existing; CTR-01 shapes deferred | Do not invent absent pin shapes; remount before consume | W3+ if pin dispatch shapes required |

## Exact-head merge package (for wave-signoff)

> Ground Report and as-built updates written **locally**. Do **not** commit, push, merge, or apply labels from this skill. Human approved was `wave-acceptance`. At `wave-signoff` the human merges/publishes the **exact wave head** only.

- PR URL / wave head: https://github.com/drivestream-lab/gateflow/pull/193 @ `3191407dd4fe2f5e1c67dac01f8b9a2e62b5e0c8` — **accept tip** (Pass-2 `/commit-workspace` may add Learning/Ground/as-built commits on the same head)
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-012-W2.md`
- Accept evidence: `wave-accepted` on tip (wave-acceptance) — human approved already
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-012-W2.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-012-W2.md`
- Optional/legacy Live-Verify path: n/a (not required; verify script co-shipped)
- As-built: W2 `human_approved` from wave-acceptance (recorded below; not re-approved here)
- Required merge fields (human fills at `wave-signoff`; not `handoff.forge`):
  `reviewed_head_sha`, `merge_commit_sha`

### Human merge checklist (wave-signoff)

- [ ] Review REQ checklist — all wave-assigned REQs pass or explicitly deferred
- [ ] Review §Contracts produced — accurate and complete for next wave
- [ ] Confirm reviewed head SHA matches the accept tip (or Pass-2 publish tip on same PR)
- [ ] Confirm human_approved already recorded at wave-acceptance (do not re-mark)
- [ ] Merge the wave PR manually at wave-signoff (human only) — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge; no approval-label auto-merge
- [ ] Publish Pass-2 artifacts via `/commit-workspace` before merge as policy requires

## Ready for wave-signoff (merge)?

**yes** — G1–G10 satisfied; no Blocking GF-*; Contracts produced ready for W3 `/pre-implement`; next pin hop is `wave-done-action` then human merge.

### Checks G1–G10

| ID | Result |
|----|--------|
| G1 Wave scope | PASS — W2 REQs only (REQ-16–19) |
| G2 Ground command / evidence | PASS — ground_command absent → manual scan + unit cited |
| G3 Assigned-REQ coverage | PASS — REQ-16–19 |
| G4 Acceptance evidence | PASS — Wave-Execution + unit + `wave-accepted` |
| G5 ADR boundaries | PASS — ADR-010 D2 compose; ADR-009 forge consume |
| G6 MDC boundaries | PASS — fail-fast / infra / architecture / migrations |
| G7 Contracts consumed / produced | PASS — W1 contracts match; §Contracts produced complete for W3 |
| G8 Learning citations | PASS — empty extract cited |
| G9 Stable GF-* | PASS — no discrepancies |
| G10 Complete handoff | PASS — this report + forge ticket for Done |

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-012-W2.md
  blockers: []
  signals:
    wave: W2
    contracts_produced: 5
    assigned_reqs: [REQ-16, REQ-17, REQ-18, REQ-19]
    reviewed_head_sha: 3191407dd4fe2f5e1c67dac01f8b9a2e62b5e0c8
    draft_pr: "https://github.com/drivestream-lab/gateflow/pull/193"
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/187"
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    status: done
    ticket: "187"
    commit_workspace: required
    head_ref: feature/INIT-GATEFLOW-012-w2-branch-resolve
    base_ref: develop
```
