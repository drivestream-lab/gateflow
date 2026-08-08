# Ground report — INIT-GATEFLOW-012 W0

| Field | Value |
|-------|-------|
| Wave | W0 — Tenant registry |
| Spec | `docs/specification/product/INIT-GATEFLOW-012-gateflow.md` |
| Initiative | INIT-GATEFLOW-012 |
| Date | 2026-08-08 |
| Wave head (exact) | `feature/INIT-GATEFLOW-012-w0-tenant-registry` @ `0fb1f2f272a81c185d94338fb22137425282f200` — reviewed head for sign-off |
| PR URL | https://github.com/drivestream-lab/gateflow/pull/191 |
| Board wave | [#185](https://github.com/drivestream-lab/gateflow/issues/185) |
| Status | Ready for wave-signoff package |
| Review deadline | 2026-08-12 |
| Deciders | Tech lead / reviewer — human_approved already at wave-acceptance (`wave-accepted`); wave-signoff is merge only |
| Outcome | **pass** |
| Outcome reason | All W0-assigned REQs map to unit/inspection evidence; `wave-accepted` on tip; Contracts produced complete for W1; no Blocking GF-* |
| Assigned REQs | REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, REQ-07, REQ-08, REQ-09, REQ-32 |

## Evidence sources (separate layers)

| Layer | Source | Summary |
|-------|--------|---------|
| Unit | `make test` / Wave-Execution | **419 passed** (reconfirmed 2026-08-08); TASK-W0-01…08 green |
| Ground | Manual `src/` + `tests/**` scan (no `{ground_command}` in harness profile) | Routes/service/repo/probe/token + unit modules inspected against REQ claims |
| Accept | `wave-accepted` on [#191](https://github.com/drivestream-lab/gateflow/pull/191) tip `0fb1f2f` (@nikd10x, 2026-08-08T08:49:04Z) | Human wave-acceptance; live script co-shipped |
| Learning | `Learning-Extract-INIT-GATEFLOW-012-W0.md` | `human_fix_detected: false`; `items: []` |

## Automated ground check output

`{ground_command}` is **not defined** in `.harness/profile.yaml` — SKIPPED with reason: perform manual source + tests scan (documented in REQ checklist and Boundary checks).

```text
make test → 419 passed (2026-08-08)
```

## REQ checklist (wave-assigned only)

| REQ | Spec claim | Verified artifact | Status |
|-----|-----------|-------------------|--------|
| REQ-01 | Register accepts name/pat/repos/workspace_root/optional board; malformed → 400, 0 rows | `POST /api/v1/tenants` → `TenantService.register_tenant`; `test_tenant_routes` / `test_tenant_service` | pass |
| REQ-02 | PAT persisted plaintext; never in response bodies | `TenantSchema.pat`; `TenantReadModel` / register response omit `pat`; unit no-pat assertions | pass |
| REQ-03 | Tenant-scoped bearer distinct from programme token | `secrets.token_urlsafe` issuance; `tenant_token.verify_tenant_bearer_token` (ADR-011 Option A) | pass |
| REQ-04 | Attach identity; invalid/absent/unattached → 401 before lane logic | `POST .../users`; `X-Tenant-Identity` gate on detail; `test_tenant_token` / routes 401 matrix; verify script co-shipped | pass |
| REQ-05 | No per-repo ACL within tenant | Inspection: no repo-scoped permission branch in `tenant_service` / `tenant_routes` (tenant + optional identity only) | pass |
| REQ-06 | Eager PAT probe all-or-nothing; 422 itemized | `GithubPatProbe.verify_read_access`; `UnprocessableEntityError` failures list; `test_github_pat_probe` / `test_tenant_service` | pass |
| REQ-07 | Absolute `workspace_root` or 400 | Service `Path.is_absolute` → `ValidationError` 400; unit + verify script | pass |
| REQ-08 | Tenant board default when project_number omitted; explicit wins | `BoardService.resolve_board_default`; `test_resolve_board_default_*` | pass |
| REQ-09 | Nth tenant needs no GithubSettings/env edit | Per-row PAT + probe credential; `test_second_tenant_no_env_change` | pass |
| REQ-32 | List/detail return repos/workspace/board; never PAT | `GET /api/v1/tenants` (+ `/{id}`); read DTOs; route unit asserts | pass |

## Boundary checks

| Rule | Source | Status |
|------|--------|--------|
| Fourth trust zone — Bearer dependency, no JWT auth-context populate | ADR-011 Accepted | pass — `tenant_token.py` mirrors programme-token shape |
| Do not reactivate AuthMiddleware JWT path for tenants | ADR-011 / product G3 | pass — `/api/v1/tenants` on `public_paths`; dependency auth only |
| Agents do not author Alembic `versions/` | database-migrations.mdc | pass — DDL-NOTE only; `versions/` untouched |
| Repos return Pydantic; no ORM in business/API | repository-pattern.mdc | pass — import-linter KEPT; `TenantRepository` maps rows |
| PAT never logged | logging-loguru.mdc / NFR | pass — registration logs tenant_id/repo_count only |
| Probe not ForgeClient singleton credential | TDD §3.2 / infra-services.mdc | pass — per-call httpx in `GithubPatProbe` |

## Cross-spec contracts consumed

| Assumed contract | Source | Match? |
|-----------------|--------|--------|
| Programme-token Bearer dependency pattern | ADR-002 / ADR-005 zone mechanics (shape only) | yes — reused as ADR-011 Option A without folding into programme secret |
| `BoardTicketCreateRequest` override precedent | A-5 / existing board create | yes — optional `project_number` + tenant default resolve |
| Postgres session/transaction + DI modules | prior gateflow waves (as-built) | yes — same `PostgresService.transaction` / module bindings |
| Prior INIT-012 Ground Report | N/A (W0 is first wave) | SKIPPED — no W−1 contracts |

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
| Tenant register | TenantService / tenant routes | `register_tenant` / `POST /api/v1/tenants` | name, pat, repos[], absolute workspace_root, optional board | tenant_id + one-time bearer + repos/workspace/board (no pat) | Probe-all-or-nothing; 0 rows on 422; PAT column plaintext never echoed | W1 (workspace resolve uses stored tenant + PAT) |
| Tenant token resolve | tenant_token + TenantRepository | `verify_tenant_bearer_token` / `resolve_tenant_by_token` | Authorization Bearer | TenantResolvedContext or 401 | Does not populate JWT `request.state.auth` | W1+ tenant-scoped callers |
| Tenant user attach | TenantService | `attach_user` / `POST /tenants/{id}/users` | tenant_id path + identity body + matching tenant token | attach ack | Path tenant must match token; identity stored without per-repo ACL | W1+ identity gates |
| Tenant read model | TenantRepository / TenantService | `get_tenant` / `list_tenants` | tenant token (+ optional identity header on detail) | repos, workspace_root, board; never pat | Unattached identity → 401 when header supplied | W1+ |
| PAT probe | GithubPatProbe | `verify_read_access` | caller-submitted credential, org, repo | ok/reason pair | No credential persistence; expected auth failures return reason | W0 complete; W1 uses stored PAT for git, not re-probe at register |
| Board default resolve | BoardService | `resolve_board_default` / `create_ticket` omit path | optional tenant_id + optional project_number/owner | concrete owner + project_number | Explicit number wins; omit loads tenant default | W1+ board-touching flows |
| Tenant ORM aggregate | tenant_schema + DDL-NOTE | tables `tenants` / `tenant_repos` / `tenant_users` | human Alembic apply | durable rows + bearer unique | `harness_verified` column reserved for W3; PAT column present for W1 git | W1–W3 |

## Exact-head merge package (for wave-signoff)

> Ground Report and as-built updates written **locally**. Do **not** commit, push, merge, or apply labels from this skill. Human approved was `wave-acceptance`. At `wave-signoff` the human merges/publishes the **exact wave head** only.

- PR URL / wave head: https://github.com/drivestream-lab/gateflow/pull/191 @ `0fb1f2f272a81c185d94338fb22137425282f200` — **expected reviewed head SHA**
- Ground Report path: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-012-W0.md`
- Accept evidence: `wave-accepted` on tip (wave-acceptance) — human approved already
- Wave-Execution path: `docs/specification/reports/Wave-Execution-INIT-GATEFLOW-012-W0.md`
- Learning-Extract path: `docs/specification/reports/Learning-Extract-INIT-GATEFLOW-012-W0.md`
- Optional/legacy Live-Verify path: n/a (not required; verify script co-shipped)
- As-built: W0 `human_approved` from wave-acceptance (recorded below; not re-approved here)
- Required merge fields (human fills at `wave-signoff`; not `handoff.forge`):
  `reviewed_head_sha`, `merge_commit_sha`

### Human merge checklist (wave-signoff)

- [ ] Review REQ checklist — all wave-assigned REQs pass or explicitly deferred
- [ ] Review §Contracts produced — accurate and complete for next wave
- [ ] Confirm reviewed head SHA matches the package above (`0fb1f2f…`)
- [ ] Confirm human_approved already recorded at wave-acceptance (do not re-mark)
- [ ] Merge the wave PR manually at wave-signoff (human only) — record merge commit SHA
- [ ] Do not ask Gateflow/Forge to merge; no approval-label auto-merge
- [ ] Publish Pass-2 artifacts (Learning-Extract + Ground-Report + as-built) via `/commit-workspace` before or with merge package as policy requires

## Ready for wave-signoff (merge)?

**yes** — G1–G10 satisfied; no Blocking GF-*; Contracts produced ready for W1 `/pre-implement`; next pin hop is `wave-done-action` then human merge.

### Checks G1–G10

| ID | Result |
|----|--------|
| G1 Wave scope | PASS — W0 REQs only |
| G2 Ground command / evidence | PASS — ground_command absent → manual scan + unit cited |
| G3 Assigned-REQ coverage | PASS — REQ-01–09, REQ-32 |
| G4 Acceptance evidence | PASS — Wave-Execution + unit + `wave-accepted` |
| G5 ADR boundaries | PASS — ADR-011 |
| G6 MDC boundaries | PASS — migrations / repository / logging |
| G7 Contracts consumed / produced | PASS — §Contracts produced complete |
| G8 Learning citations | PASS — empty extract cited |
| G9 Stable GF-* | PASS — no discrepancies |
| G10 Complete handoff | PASS — this report + forge ticket for Done |

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: ground-spec
  outcome: pass
  artifact:
    path: docs/specification/reports/Ground-Report-INIT-GATEFLOW-012-W0.md
  blockers: []
  signals:
    wave: W0
    contracts_produced: 7
    assigned_reqs: [REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, REQ-07, REQ-08, REQ-09, REQ-32]
    reviewed_head_sha: 0fb1f2f272a81c185d94338fb22137425282f200
    draft_pr: "https://github.com/drivestream-lab/gateflow/pull/191"
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/185"
  next_candidates:
    - wave-done-action
  human_checkpoint: false
  external_action: true
  forge:
    action: update_board_status
    status: done
    ticket: "185"
    commit_workspace: required
```
