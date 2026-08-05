# Feasibility report — INIT-GATEFLOW-010

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-010 |
| Delivery wave (this ticket) | **W0** — pin parse parity |
| Spec | `docs/specification/product/INIT-GATEFLOW-010-gateflow.md` |
| Spec digest | `sha256:f98e101a508407dcebaa5fd0fc9033744dbed24a388c4e50c4303f687b4d91ea` |
| PRD digest | `sha256:457f19617113171c973abdbc15d1afaa00df2f6947ab4567b57d8440bd88b206` |
| Impact map / revision | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-010.md` / `1` |
| Repo scope digest | `sha256:09c89c143c14401c8812738c162c05a2f5e504cabafd1818ee72eb4e9b781532` |
| Approved meta PR head | `df0f5a5c09b6c4f951463bb42f277305310aaa80` |
| Impact-map approval | @0xbeefdead APPROVED 2026-08-05T09:32:32Z on `df0f5a5…` — [prayog-meta#28](https://github.com/drivestream-lab/prayog-meta/pull/28) |
| Source freshness | **CURRENT** — H1/H2/H3 match live meta @ `df0f5a5…`; G1 APPROVED review on same head; harness pin `v0.5.0-rc.2` ≡ submodule `6561c7c` |
| Prior stage | `/spec-draft` → `pass` (handoff baton) |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-05 |
| Branch | `feature/INIT-GATEFLOW-010-w0-spec-lane` — Draft spec PR (Forge pending) |
| Initiative segment | `INIT-GATEFLOW-010` |
| Status | Accepted |
| Review deadline | 2026-08-08 |
| Deciders | PM: programme · Domain SME: N/A (eng control plane) |

## Summary

INIT-GATEFLOW-010 is **buildable in this repo** against the current codebase and
pinned `v0.5.0-rc.2` tip. Gate 1 authority is current; the spec slice accurately
reflects as-built partial W0 work (REQ-02 parse largely exists; REQ-10
purpose/owner and REQ-03 apply remain documented gaps). W0 exit criteria map to
well-bounded modules (`ResolvedWorkflowNode`, `WorkflowEngine._to_resolved`,
`run_orchestrator._finalize_run`) with existing unit harness
(`test_all_remounted_pin_nodes_parse`). Later-wave REQs (W1–W4) have clear
touch surfaces and defer correctly — no ADR conflicts or blocking PM/domain
items. Proceed to `/spec-technical-review` on **`pass`**.

**Findings:** 6 total (0 Critical, 0 Should fix, 2 Verify, 4 Gap)

### Derived counts (lane × severity)

| Lane | Blocking open | Non-blocking open | Resolved |
|------|---------------|-------------------|----------|
| PM | 0 | 1 | 0 |
| PE / ADR | 0 | 2 | 1 (Q-3) |
| Domain | 0 | 0 | 0 |
| Auto-fix | 0 | 0 | 0 |

| Severity | Unresolved count |
|----------|------------------|
| Critical | 0 |
| Should fix | 0 |
| Verify / Gap (informational) | 6 |

### Selected workflow outcome

| Field | Value |
|-------|-------|
| Outcome | `pass` |
| Rationale | Source freshness CURRENT; zero unresolved blocking PE/ADR/PM/domain items; W0 gaps are expected implementation work aligned with spec as-built |
| Next (from workflow) | `spec-technical-review` |

Informational Gap/Verify observations do **not** select `findings`. Technical
review remains required per pin (pass and findings both route there).

---

## Baseline snapshot (F1)

| Area | Current state | Evidence |
|------|---------------|----------|
| Toolchain | `make check` (black, ruff, pyright, import-linter) | `.harness/profile.yaml`; `Makefile` |
| Unit tests | `make test` → `tests/unit/` — **16/16** forge policy tests green | `tests/unit/test_forge_policy.py` (observed 2026-08-05) |
| Live verify | 10 scripts under `tests/verify/`; W0 scoped to unit only per Q-3 | `tests/README.md`; no closure verify script yet |
| Pin consume | `.harness-pin.yaml` `agent_skills.ref: v0.5.0-rc.2` ≡ submodule `6561c7c` | `git -C prayog-skills describe --exact-match` |
| As-built | INIT-001…009 matrices; **no INIT-010 section yet** (updated 2026-07-30) | `docs/specification/as-built/implementation-status.md` |
| CI | `.github/workflows/ci.yml` — `make check-ci` + unit | as-built INIT-009 row |

## Traceability matrix

| Spec REQ / wave | Spec claim | Code evidence | Unit | Verify | Status |
|-----------------|------------|---------------|------|--------|--------|
| REQ-01 / W0 | Pin `v0.5.0-rc.2`; harness == submodule | `.harness-pin.yaml`; submodule @ `6561c7c` | `test_all_remounted_pin_nodes_parse` loads pin | — | **exists** |
| REQ-02 / W0 | Parse `update_board_status` + status + ticket requires; 0 BROKEN nodes | `parse_node_forge` in `forge_models.py`; `WorkflowEngine.get_node` | `test_parse_node_forge_update_board_status*`; `test_all_remounted_pin_nodes_parse` | — | **partial→exists** (parse done; apply W1) |
| REQ-03 / W1 | APPLY_FORGE board-status hop | `ForgeActionService.apply_external_action` — no `UPDATE_BOARD_STATUS` branch | — | — | **gap** (deferred W1) |
| REQ-04 / W1 | Implement-start In Progress | `waves_routes` implement start — no board-status pre-hop | `test_wave_start` | `verify_wave_start` | **gap** (deferred W1) |
| REQ-05 / W3 | Closeout Done before signoff | closeout walker exists (INIT-007); no Done hop apply | `test_wave_closeout` | `verify_wave_closeout` | **gap** (deferred W3) |
| REQ-06–08 / W2 | Create predicates + implement ticket gate | `execute_create_board_tickets` runs WorkManifest only; no triple predicate gate on authorize | `test_forge_action_service` | — | **gap** (deferred W2) |
| REQ-09 / W3 | No Forge merge | no merge action in `ForgeActionService` | forge tests | — | **exists** |
| REQ-10 / W0 | Stop payload includes pin `purpose` / `owner` | `ResolvedWorkflowNode` has no purpose/owner; `_finalize_run` `run_stopped` payload omits them | no REQ-10 assertion test | — | **gap** (W0 exit — implement) |
| REQ-11 / W1 | Create-tickets does not resume implement | walker separate starts | policy/orchestrator tests | — | **exists** (pattern) |
| REQ-12–15 / W4 | Closure Enter-at + Done-gate + purge walk | no `POST /api/v1/initiatives/closure/start` route | — | — | **gap** (deferred W4) |
| REQ-16 / W3 | Never auto `*-lgtm` | `parse_node_forge` rejects `*-lgtm` labels | `test_parse_node_forge_forbids_lgtm_apply_labels` | — | **exists** |
| REQ-17 / W2–W4 | Full verify suite | existing lane scripts; no closure verify | partial unit | partial live | **partial** (W0 unit-only per PRD §5) |
| REQ-18–20 / W4 | Freeze + partial failure hygiene | Feature-Readiness pattern from INIT-009 | — | — | **gap** (deferred W4) |

## ADR pass (pre-T2)

| ADR | Domain matched | Status |
|-----|----------------|--------|
| ADR-009 | pin forge publish/mutate, dual `authorization`, APPLY_FORGE | **Accepted** — spec aligned; `update_board_status` apply is incremental W1 work |
| ADR-010 | lane intake, dual workspace | **Accepted** — spec inherits; W4 closure Enter-at is ADR-010 §7 (no separate ADR) |
| ADR-003 | ForgeClient transport | Accepted — aligned |
| ADR-005 | programme token | Accepted — aligned |

## ADR traceability (F13)

| Spec REQ / wave | Relevant ADR(s) | Status | Finding |
|-----------------|-----------------|--------|---------|
| REQ-01–02, REQ-09, REQ-16 / W0 | ADR-009 | aligned | — |
| REQ-04, REQ-08 / W1–W2 | ADR-010 | aligned | — |
| REQ-12–15 / W4 | ADR-010 §7 | aligned — distinct start contract; Done-gate / EPIC / path remain product REQs | — |

## MDC pass (pre-T2)

| MDC file | Domain | Read / skipped |
|----------|--------|----------------|
| `architecture.mdc` | layer boundaries | read — spec respects business/infra split |
| `http-api-conventions.mdc` | REST shapes for W4 closure route | read — spec REQ-12 JSON-body pattern aligned |
| `testing-verify-flows.mdc` | unit vs live boundary | read — W0 unit-only consistent |
| `pydantic-schemas.mdc`, `fail-fast.mdc` | models / validation | read — REQ-10 additive fields fit existing patterns |
| Other rules (DB, logging, imports) | not touched W0 | skipped — no spec conflict |

## Governance findings (F13–F14)

| ID | Check | Spec quote | Governing doc | Finding |
|----|-------|------------|---------------|---------|
| — | F13 | "ADR-009 … ADR-010 … pin SSOT" | ADR-009, ADR-010 | aligned — no conflict |
| — | F14 | W4 `POST /api/v1/initiatives/closure/start` JSON body | `http-api-conventions.mdc` | aligned |

## Findings by severity

### Critical

_None._

### Should fix

_None._

### Verify

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-01 | F4 | No unit test yet asserts `run_stopped` includes pin `purpose`/`owner` when stop node declares them | Spec REQ-10; `_finalize_run` payload in `run_orchestrator.py:1157–1170` lacks purpose; grep `purpose` in `src/` → no node-purpose field |
| FF-02 | F5 | As-built matrix lacks INIT-GATEFLOW-010 row (spec self-documents partial W0) | `implementation-status.md` last updated 2026-07-30; spec § as-built baseline 2026-08-05 |

### Gap (informational)

| ID | Check | Finding | Evidence |
|----|-------|---------|----------|
| FF-03 | F2 | `ResolvedWorkflowNode` does not carry pin `purpose` / `owner` | `handoff_models.py:31–52`; `WorkflowEngine._to_resolved` ignores raw pin fields |
| FF-04 | F2 | `ForgeActionService` rejects `update_board_status` at apply time | `forge_action_service.py:226–228` — `Unsupported forge.action` |
| FF-05 | F3 | No closure or ticket-gate verify scripts for W2–W4 REQs | `tests/verify/` inventory — 10 scripts; no `verify_closure` |
| FF-06 | F9 | No `POST /api/v1/initiatives/closure/start` route | repo grep — only spec reference |

## Impact surface

| Wave / area | Likely files/modules | Test touch |
|-------------|----------------------|------------|
| **W0** parse + purpose/owner | `handoff_models.py`, `workflow_engine.py`, `run_orchestrator.py` | extend `test_forge_policy.py`; new REQ-10 stop-payload tests |
| **W1** board-status apply | `forge_action_service.py`, `board_service.py`, `policy_engine.py` | `test_forge_action_service.py`; orchestrator walker tests |
| **W2** ticket gates + create predicates | `waves_routes.py`, `forge_action_service.py`, wave start validators | `test_wave_start.py`, `test_forge_action_service.py`; new verify |
| **W3** closeout Done hop | `run_orchestrator.py`, closeout routes | `test_wave_closeout.py`, `verify_wave_closeout.py` |
| **W4** closure Enter-at + purge | new routes under `src/api/`, orchestrator enqueue | new unit + `verify_closure` script |

## Risks & assumptions

| ID | Risk / assumption | Mitigation |
|----|-------------------|------------|
| R-1 | Pin tip retag mid-INIT breaks REQ-01 | A-3 frozen; programme decision required |
| R-2 | REQ-10 purpose exposure needs API/DTO decision (field names) | Q-1 deferred; HTTP semantics normative; TDD resolves |
| R-3 | W4 closure product rules (Done-gate, EPIC hygiene) mis-filed as ADR | ADR-010 §7 authority only; REQs stay product SSOT |
| A-1…A-4 | Spec assumptions | confirmed per spec table; board vocab + two-API model match code |

## Recommended spec edits

- None blocking. Optional: add as-built cross-link once INIT-010 section is opened during W0 implement.
- Closure Enter-at: apply ADR-010 §7 in TDD; **no ADR-011** (product REQs remain SSOT).

---

## Open items by lane

| ID | Lane | Question / item | Blocking | Owner | Status | Required by | Default if deferred | Evidence | Resolution reference |
|----|------|-----------------|----------|-------|--------|-------------|---------------------|----------|----------------------|
| Q-1 | PE | OpenAPI problem+json field names (PRD OQ-01 / IM-01) | no | prayog-pe-team | open | technical review | 400/422 semantics remain normative | spec Q-1; impact map IM-01 | pending OpenAPI pass |
| Q-2 | PM | Parallel GATEFLOW meta PRs (#10–#23) sequencing | no | programme PM | open | Gate 1 scheduling | Proceed; distinct INIT ids | spec Q-2; impact map IM-02 | n/a |
| Q-3 | PE | W0 unit-only vs REQ-17 verify claim | no | prayog-pe-team | resolved | feasibility | W0 exit = unit only per PRD §5 | spec Q-3 | PRD §5 W0 row |
| PE-1 | PE | NEW-ADR vs ADR-010 amend for initiative-closure Enter-at (W4) | no | prayog-pe-team | resolved | technical review | Fold into ADR-010 §7; TDD_ONLY for route/validators; **no ADR-011** | REQ-12–15 product; ADR-010 Option B | ADR-010 §7 hygiene (INIT-010) |

### PM questions (product scope, UX, priority)

#### Blocking — must resolve before spec merge

_None._

#### Defer — can proceed with documented assumption

1. **Q-2** — Parallel meta PR sequencing vs INIT-GATEFLOW-010; default: proceed with distinct INIT ids.

### PE questions (engineering decisions — resolved by `/spec-technical-review`)

#### Blocking for implementation plan

_None._

#### Defer with default

1. **Q-1** — Exact OpenAPI error body field names; HTTP 400/422 table remains normative.

#### Resolved

1. **PE-1** — Fold closure intake into ADR-010 §7; no ADR-011; product REQs remain SSOT for Done-gate / EPIC / path.

### Domain clarifications (business source-of-truth)

_None._

### Auto-fixable (agent resolves later — not inside this skill)

_None recorded._

---

## Check summary

| Check | Status | Findings |
|-------|--------|----------|
| F1 Baseline snapshot | PASS | — |
| F2 Spec → code map | PASS | FF-03, FF-04, FF-06 (expected gaps) |
| F3 Spec → verify map | SKIPPED (W0) | FF-05 — W0 unit-only per Q-3 / PRD §5 |
| F4 Spec → unit map | PASS | FF-01 (Verify — REQ-10 test TBD) |
| F5 As-built drift | PASS | FF-02 (Verify — as-built lag) |
| F6 Docs drift | PASS | README lists INIT-010; ADRs cited |
| F7 Overlap risk | PASS / N/A | W0 parse-only |
| F8 CI vs live boundary | PASS | W0 unit in CI; live deferred W2+ |
| F9 Cross-service touch | PASS | CTR-01 pin + CTR-02/03 forge paths exist |
| F10 Assumptions | PASS | A-1…A-4 evidenced |
| F11 Effort drivers | PASS | W0 low; W2–W4 incremental on existing walker/forge |
| F12 PM questions | PASS | Q-1, Q-2 numbered non-blocking |
| F13 ADR conformance | PASS | PE-1 resolved — ADR-010 §7; no ADR-011 |
| F14 MDC conformance | PASS | no conflicts |

**Check PASS** = zero unresolved blocking findings (informational OK).

---

## Next steps

Persist this report locally. Fill `handoff.forge` for `/commit-workspace` onto the
Draft spec PR branch — **do not** commit, push, open PRs, or apply labels inside
this skill. Gate 2 stays **`spec-pending`**.

**PM questions** → meta PRD PR [#28](https://github.com/drivestream-lab/prayog-meta/pull/28) comment (Q-2).

**PE questions** → Draft spec PR; proceed **`/spec-technical-review`** (pin routes
`pass` and `findings` identically).

### Forge readiness

| Item | Value |
|------|-------|
| Local report path | `docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-010.md` |
| Target branch | `feature/INIT-GATEFLOW-010-w0-spec-lane` |
| Recommended forge | `/commit-workspace` (Gate 2 stays `spec-pending`) |
| Mutations performed by this skill | **none** |

```
Draft spec PR: feature/INIT-GATEFLOW-010-w0-spec-lane  (spec-pending)
When ready:
  [x] Source freshness is CURRENT
  [ ] Spec + feasibility published via Forge (/commit-workspace)
  [ ] Proceed: /spec-technical-review
  [ ] After TDD + plan on branch: PE sets spec-lgtm on exact head → merge
```

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: initiative-feasibility
  outcome: pass
  artifact:
    path: docs/specification/reports/Initiative-Feasibility-Report-INIT-GATEFLOW-010.md
    digest: sha256:dd6629153a206c9ae5d46df7bffad51300d1f51863e3003e9bda691ccad0869b
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-010
    delivery_wave: W0
    source_freshness: CURRENT
    meta_pr: "https://github.com/drivestream-lab/prayog-meta/pull/28"
    meta_pr_head: "df0f5a5c09b6c4f951463bb42f277305310aaa80"
    map_revision: 1
    prd_digest: "sha256:457f19617113171c973abdbc15d1afaa00df2f6947ab4567b57d8440bd88b206"
    scope_digest: "sha256:09c89c143c14401c8812738c162c05a2f5e504cabafd1818ee72eb4e9b781532"
    ripple_action: continue
    new_adr: false
    new_adr_w4_signal: false
    lane_counts:
      pm: 1
      pe: 1
      domain: 0
      auto_fix: 0
    findings_critical: 0
    findings_should_fix: 0
    findings_verify: 2
    findings_gap: 4
    pin_ref: v0.5.0-rc.2
    pin_sha: "6561c7c508539fbdb182159d3fdae5abef4b9b01"
    nonblocking_questions: "Q-1,Q-2"
  next_candidates:
    - spec-technical-review
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    # Pin: initiative-feasibility forge.commit_workspace = required.
    # Publish spec + this report onto Draft spec PR head — invoke /commit-workspace
    # (or Gateflow ForgeClient). This skill does not mutate.
```
