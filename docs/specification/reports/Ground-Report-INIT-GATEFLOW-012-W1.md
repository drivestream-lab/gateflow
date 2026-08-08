# Ground report — INIT-GATEFLOW-012 W1

| Field | Value |
|-------|-------|
| Wave | W1 — Repo clone/refresh workspace prep |
| Spec | `docs/specification/product/INIT-GATEFLOW-012-gateflow.md` |
| Initiative | INIT-GATEFLOW-012 |
| Date | 2026-08-08 |
| Wave head (exact) | `feature/INIT-GATEFLOW-012-w1-workspace-prep` @ `aa4445e921d6734de769d6542fd4734d021137e1` — reviewed head for sign-off |
| PR URL | https://github.com/drivestream-lab/gateflow/pull/192 |
| Board wave | [#186](https://github.com/drivestream-lab/gateflow/issues/186) |
| Status | Ready for wave-signoff package |
| Review deadline | 2026-08-12 |
| Deciders | Tech lead / reviewer — human_approved already at wave-acceptance (`wave-accepted`); wave-signoff is merge only |
| Outcome | **pass** |
| Outcome reason | All W1-assigned REQs map to unit/inspection evidence; `wave-accepted` on tip; Contracts produced complete for W2; no Blocking GF-* |
| Assigned REQs | REQ-10, REQ-11, REQ-12, REQ-13, REQ-14, REQ-15 |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution | **432 passed** (reconfirmed 2026-08-08); TASK-W1-01…04 green |
| Ground | Manual `src/` + `tests/**` scan (no `{ground_command}` in harness profile) | git client / wave-start / orchestrator / repo lookup inspected against REQ claims |
| Accept | `wave-accepted` on [#192](https://github.com/drivestream-lab/gateflow/pull/192) tip `aa4445e` (@nikd10x, 2026-08-08T10:25:53Z) | Human wave-acceptance; live script co-shipped |
| Learning | `Learning-Extract-INIT-GATEFLOW-012-W1.md` | `human_fix_detected: false`; `items: []` |
| PE gate | `PE-Waiver-INIT-GATEFLOW-012-W1-PE1.md` | TASK-W1-01 = current pin 0 BROKEN existing nodes; CTR-01 new shapes → W2 |

## Automated ground check output

`{ground_command}` is **not defined** in `.harness/profile.yaml` — SKIPPED with reason: perform manual source + tests scan (documented in REQ checklist and Boundary checks).

```text
make test → 432 passed (2026-08-08)
pytest tests/unit/test_forge_policy.py::test_all_remounted_pin_nodes_parse → PASSED (TASK-W1-01 / PE waiver)
```

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-10 | Omitted `workspace_path` + registered org/repo → deterministic workspace before Enter-at; no `Path.cwd()` | `WaveStartService._resolve_implement_workspace_path` → `TenantGitWorkspaceClient.resolve_workspace`; path `{workspace_root}/{org}/{repo}`; `RunOrchestrator._resolve_job_workspace_path`; unit + `verify_workspace_lifecycle` | pass |
| REQ-11 | Clone/refresh auth uses Tenant stored PAT (not deploy-key / GithubSettings singleton) | `TenantRepository.find_workspace_credential_by_org_repo` + `TenantService.get_workspace_credential_for_repo`; client `http.extraHeader` Basic `x-access-token`; PAT never logged | pass |
| REQ-12 | Explicit `workspace_path` honored unchanged | Explicit branch skips credential lookup/resolve in wave-start; orchestrator uses context path when set; `test_implement_explicit_path_skips_tenant_resolve`; smoke helpers set cwd | pass |
| REQ-13 | Valid existing checkout → fetch-in-place, not re-clone | Client mode `fetched` when `.git` + origin matches; unit `test_resolve_fetches_*`; live script second start | pass |
| REQ-14 | Invalid/mismatched existing path → 422; tree untouched | `TenantGitWorkspaceError` reason `workspace_mismatch`; unit keeps marker file; wave-start maps to 422 0 enqueue; live script | pass |
| REQ-15 | Omitted path + unregistered → 422; 0 enqueue; no clone | wave-start before board In Progress / enqueue; `test_implement_omitted_path_unregistered_*`; live script | pass |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Subprocess `git` only — no Python git package | FF-04 TDD_ONLY / infra-services.mdc | pass — `tenant_git_workspace_client.py`; unit asserts no GitPython/pygit2 |
| Per-org+repo serialize independent of W4 concurrency | TF-01 TDD_ONLY | pass — asyncio lock in client; unit lock test |
| PAT never logged | logging-loguru.mdc / NFR | pass — logs mode/org/repo/rel path only |
| No ORM in business; credential lookup in repository | repository-pattern.mdc | pass — `find_workspace_credential_by_org_repo`; import-linter KEPT |
| Tenant token zone unchanged for git | ADR-011 | pass — git uses stored PAT column; Bearer zone not reused for clone |
| Gap-fill ADR-010 (omit path) not a reversal | FF-01 TDD_ONLY | pass — explicit path path unchanged; omit → resolve or 422 |
| Agents do not author Alembic `versions/` | database-migrations.mdc | pass — no new DDL this wave; W0 DDL still human-owned |
| PE-1 new pin shapes not claimed on W1 | PE waiver / plan DEP-02 | pass — TASK-W1-01 evidence is existing-node parse only |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Tenant register / aggregate + stored PAT column | Ground-Report W0 | yes — credential lookup joins `tenants` + `tenant_repos` |
| Tenant read model never exposes PAT | Ground-Report W0 / REQ-32 | yes — internal `TenantWorkspaceCredential` only; HTTP DTOs unchanged |
| Tenant ORM + human DDL applied for live | Ground-Report W0 / DDL-NOTE | yes — live verify still requires human Alembic |
| Board / implement start ticket gates | prior waves | yes — resolve runs before In Progress + enqueue |
| Explicit `workspace_path` on job payload | TriggerContext / WaveStartJobPayload | yes — REQ-12 path |

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
| Workspace resolve (clone/fetch) | `TenantGitWorkspaceClient` | `resolve_workspace` | tenant credential (tenant_id, workspace_root, pat, org, repo) | absolute path + mode (`cloned` \| `fetched`) | Serial per org+repo; mismatch leaves tree untouched; PAT never logged; subprocess git only | W2 branch lifecycle composes on resolved path |
| Tenant git credential lookup | TenantRepository / TenantService | `find_workspace_credential_by_org_repo` / `get_workspace_credential_for_repo` | org, repo | credential or none; ambiguous multi-tenant → 422 | PAT only on internal DTO; read/list DTOs unchanged | W2+ any git/workspace caller |
| Implement omit-path resolve | WaveStartService | `_resolve_implement_workspace_path` / `start_implement_wave` | ImplementWaveStartRequest | absolute workspace_path on job or 422 | Unregistered omit → 422 **before** board/enqueue; explicit path skips resolve | W2 starts that omit path |
| Orchestrator workspace bind | RunOrchestrator | `_resolve_job_workspace_path` | org, repo, optional workspace_path | absolute path or job fail | Never `Path.cwd()` for omitted path; registered → client; unregistered → fail closed | W2 walker hops on pre-resolved or re-resolved path |
| Live workspace lifecycle verify | `tests/verify/verify_workspace_lifecycle.py` | module main | API + PAT + programme token + ticket | exit 0 when clone/fetch/mismatch/unregistered matrix holds | P15 human at wave-acceptance | W2 may extend or keep secondary |
| PE-1 pin sequencing (W1 waiver) | PE-Waiver + pin tip `v0.5.0-rc.2` | TASK-W1-01 evidence | remounted workflow nodes | 0 BROKEN **existing** nodes | Net-new Tenant workspace-prep / branch pin shapes remain **W2 hard gate** | W2 TASK for CTR-01 remount |

## Exact-head merge package (for wave-signoff)

> Ground Report and as-built updates written **locally**. Do **not** commit, push, merge, or apply labels from this skill. Human approved was `wave-acceptance`. At `wave-signoff` the human merges/publishes the **exact wave head** only.

- PR URL / wave head: https://github.com/drivestream-lab/gateflow/pull/192 @ `aa4445e921d6734de769d6542fd4734d021137e1` — **expected reviewed head SHA**
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-012-W1.md`
- Accept evidence: `wave-accepted` on tip (wave-acceptance) — human approved already
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-012-W1.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-012-W1.md`
- Optional/legacy Live-Verify path: n/a (not required; verify script co-shipped)
- As-built: W1 `human_approved` from wave-acceptance (recorded below; not re-approved here)
- Required merge fields (human fills at `wave-signoff`; not `handoff.forge`):
  `reviewed_head_sha`, `merge_commit_sha`

### Human merge checklist (wave-signoff)

- [ ] Review REQ checklist — all wave-assigned REQs pass or explicitly deferred
- [ ] Review §Contracts produced — accurate and complete for next wave
- [ ] Confirm reviewed head SHA matches the package above (`aa4445e…`)
- [ ] Confirm human_approved already recorded at wave-acceptance (do not re-mark)
- [ ] Merge the wave PR manually at wave-signoff (human only) — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge; no approval-label auto-merge
- [ ] Publish Pass-2 artifacts (Learning-Extract + Ground-Report + as-built) via `/commit-workspace` before or with merge package as policy requires

## Ready for wave-signoff (merge)?

**yes** — G1–G10 satisfied; no Blocking GF-*; Contracts produced ready for W2 `/pre-implement`; next pin hop is `wave-done-action` then human merge.

### Checks G1–G10

| ID | Result |
|----|--------|
| G1 Wave scope | PASS — W1 REQs only (REQ-10–15) |
| G2 Ground command / evidence | PASS — ground_command absent → manual scan + unit cited |
| G3 Assigned-REQ coverage | PASS — REQ-10–15 |
| G4 Acceptance evidence | PASS — Wave-Execution + unit + `wave-accepted` |
| G5 ADR boundaries | PASS — ADR-011 consume; FF-01 gap-fill |
| G6 MDC boundaries | PASS — infra / repository / logging / migrations |
| G7 Contracts consumed / produced | PASS — W0 contracts match; §Contracts produced complete for W2 |
| G8 Learning citations | PASS — empty extract cited |
| G9 Stable GF-* | PASS — no discrepancies |
| G10 Complete handoff | PASS — this report + forge ticket for Done |

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-012-W1.md
  blockers: []
  signals:
    wave: W1
    contracts_produced: 6
    assigned_reqs: [REQ-10, REQ-11, REQ-12, REQ-13, REQ-14, REQ-15]
    reviewed_head_sha: aa4445e921d6734de769d6542fd4734d021137e1
    draft_pr: "https://github.com/drivestream-lab/gateflow/pull/192"
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/186"
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    status: done
    ticket: "186"
    commit_workspace: required
    head_ref: feature/INIT-GATEFLOW-012-w1-workspace-prep
    base_ref: develop
```
