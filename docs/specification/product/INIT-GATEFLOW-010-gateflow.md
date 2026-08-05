# INIT-GATEFLOW-010 — spec slice for gateflow

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-010 |
| Delivery wave (this ticket) | **W0** — pin parse parity (board-status + purpose/owner) |
| PRD | `prayog-meta/prd/INIT-GATEFLOW-010.md` |
| PRD digest (H1) | `sha256:457f19617113171c973abdbc15d1afaa00df2f6947ab4567b57d8440bd88b206` |
| Meta PR | https://github.com/drivestream-lab/prayog-meta/pull/28 |
| Meta PR approved head (G1) | `df0f5a5c09b6c4f951463bb42f277305310aaa80` |
| Impact map | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-010.md` |
| Impact-map revision (H3) | `1` |
| Repo scope digest (H2) | `sha256:09c89c143c14401c8812738c162c05a2f5e504cabafd1818ee72eb4e9b781532` |
| Tech-lead approval | @0xbeefdead APPROVED 2026-08-05T09:32:32Z on `df0f5a5c09b6c4f951463bb42f277305310aaa80` — attestation: map_revision 1, prd_digest match, artifact `prd/reports/Impact-Map-INIT-GATEFLOW-010.md` |
| Architecture | [`adr-009-pin-forge-publish-mutate-authority.md`](../adr/adr-009-pin-forge-publish-mutate-authority.md) (**Accepted** — hygiene strip INIT-010); [`adr-010-lane-intake-and-dual-workspace-authority.md`](../adr/adr-010-lane-intake-and-dual-workspace-authority.md) (**Accepted** — closeout §6; **closure §7**, no ADR-011); pin SSOT [`prayog-skills/workflow.yaml`](../../../prayog-skills/workflow.yaml), [`references/forge-side-effects.md`](../../../prayog-skills/references/forge-side-effects.md), [`delivery-contract.yaml`](../../../prayog-skills/delivery-contract.yaml) |
| Repo | drivestream-lab/gateflow |
| Date | 2026-08-05 |
| Status | Accepted — PE package accept 2026-08-05 (proceed to implementation plan) |

> **H4 citations:** H1–H3 and G1 rows above are the durable authority carrier for
> mid-lane freshness. Feas / TDD / plan digests are walk-time only.

## Overview

Gateflow must become the **executable control plane** for the full engineering
lifecycle against pinned `sdd-delivery/v2` @ `v0.5.0-rc.2`:

```text
spec → tickets → implement (per wave) → closeout (per wave) → eng purge (initiative)
```

This INIT closes the gap between remounted pin tip and **tip-faithful execution**:
board-status forge hops must parse and (in later waves) apply; create-tickets
predicates must fail closed; implement-start must board-resolve tickets; closeout
must apply Done; eng initiative closure needs Enter-at
`POST /api/v1/initiatives/closure/start` with Done-gate and programme EPIC Done
hygiene; verify scripts must prove each lane.

**This spec draft ticket (`:W0`)** scopes the **first delivery wave** to pin-parse
parity only — no board side effects, no new lane APIs, no verify suite expansion
beyond unit coverage for parse. Later waves (W1–W4) inherit this document; plan
and implement waves refine exit criteria per PRD §5.

**Product intent:** PE runs eng lanes through Gateflow alone; two ticket APIs stay
separate (create-tickets forge explicit, then implement-start with ticket); Gateflow
never merges PRs or auto-applies `*-lgtm`; PM Enter-at and meta purge remain out
of scope.

**Out of scope for this repo:** gateflow-ops UI; prayog-skills pin redesign;
`purge-initiative-artifacts-meta`; Forge merge / `delete_branch`; ops UI / second
agent / Slack; Initiative C2 probes; discover waves via `list_tickets(initiative_id)`
alone (caller must pass `wave_ticket_ids[]` from create-tickets).

**As-built baseline (2026-08-05):** Submodule `prayog-skills` @ `6561c7c` ≡ tag
`v0.5.0-rc.2` ≡ `.harness-pin.yaml` `agent_skills.ref`. Partial W0 work exists:
`ForgeActionType.update_board_status`, `parse_node_forge` status validation, and
`test_all_remounted_pin_nodes_parse` (REQ-02 partial). **Gaps for W0 exit:** pin
`purpose` / `owner` not carried on `ResolvedWorkflowNode`; `run_stopped` timeline
payload lacks pin `purpose` when next node is `human-checkpoint` (REQ-10).
`ForgeActionService` does not execute `update_board_status` (W1 / REQ-03).

**W1 as-built (local — pending live-verify):** `ForgeActionService.execute_update_board_status`
apply branch; implement-start In Progress pre-hop (`WaveStartService`); REQ-11 policy
guard blocks same-run resume from `board-tickets-action` pass.

**Delivery waves (product-normative; PRD §5):**

| Wave | Intent | Exit PRD REQs |
|------|--------|---------------|
| **W0** | Parse board-status hops + status + ticket requires; purpose/owner on stops; all remounted nodes `get_node`; unit green | REQ-01, REQ-02, REQ-10 |
| **W1** | Wire APPLY_FORGE board-status; implement-start In Progress before pre-implement (idempotent) | REQ-03, REQ-04, REQ-11 |
| **W2** | Ticket gate 400/422; create predicates; verify tickets + implement | REQ-06, REQ-07, REQ-08, REQ-17 (partial) |
| **W3** | Closeout Done → wave-signoff; spec Pass-1 verify; wave-complete no auto-chain | REQ-05, REQ-09, REQ-16, REQ-17, REQ-19 |
| **W4** | Closure Enter-at + Done-gate + EPIC Done + purge walk + REQ-20; closure verify; freeze | REQ-12, REQ-13, REQ-14, REQ-15, REQ-17, REQ-18, REQ-20 |

## Functional requirements

| ID | Requirement | PRD source | Condition / event | Observable result | Evidence layer | Wave |
|----|-------------|-----------|-------------------|-------------------|----------------|------|
| REQ-01 | Consume pin family `v0.5.0-rc.2`; harness `agent_skills.ref` equals submodule tip SHA/tag at runtime. No pin redesign. | PRD REQ-01; CAP-01, CAP-06; A3 | Before W1+ lane verify | Pin load resolves orchestrated nodes including `spec-draft`, board-status external-actions; harness pin == submodule | unit + inspection | W0 |
| REQ-02 | Gateflow parses pin board-status forge hops: `forge.action: update_board_status`, required `forge.status` (`in_progress` \| `done`), and pin `requires` including ticket binding. Every remounted `workflow.yaml` node id must `get_node` without error (0 BROKEN). | PRD REQ-02; CAP-06; G1 | Pin load / unit matrix | `wave-in-progress-action` and `wave-done-action` resolve with correct action, status, authorization; invalid status omits fail closed | unit | W0 |
| REQ-03 | APPLY_FORGE board-status hop updates the board ticket to the pin status (column+state per BoardService contract). Ticket resolved from run context / handoff forge merge. | PRD REQ-03; CAP-06; G1 | Automated board-status hop after predicate pass | Board shows In Progress or Done for bound ticket | unit + verify | W1 |
| REQ-04 | Implement-start applies In Progress for run `ticket_id` before `pre-implement` dispatch; idempotent if ticket already board In Progress. | PRD REQ-04; CAP-03; G8-A1 | Accepted implement-start request | Board In Progress before coding hop; no error solely for already `in_progress` | verify | W1 |
| REQ-05 | Closeout applies Done after `ground-spec.pass` then stops at `wave-signoff` with terminal purpose visible. | PRD REQ-05; CAP-04; G1 | Closeout walk reaches ground-spec pass | Timeline includes Done hop; terminal stop exposes `wave-signoff` purpose | verify | W3 |
| REQ-06 | Create-tickets hard-fails unless all three predicates pass: `spec-pr-merged`, `implementation-plan-current`, `workmanifest-contract-pass`. | PRD REQ-06; CAP-02; G2 | Create authorize/apply | **422** (or authorize fail); 0 tickets on failure | unit + verify | W2 |
| REQ-07 | Create success returns `epic_ticket_id` and non-empty `wave_ticket_ids[]`. | PRD REQ-07; CAP-02; G9-A1 | Create success | Response fields present and usable for later implement/closure binds | unit + verify | W2 |
| REQ-08 | Implement-start requires board-resolved `ticket_id` agreeing with initiative/wave; missing/malformed → **400**; unresolvable/mismatch/already Done → **422**; 0 enqueue. Non-empty string alone is insufficient. | PRD REQ-08; CAP-03; G5 | Bad/missing ticket on implement-start | No run enqueued; HTTP status per PRD error table | unit + verify | W2 |
| REQ-09 | No Forge merge; `spec-merge` and signoff merges remain human-only. | PRD REQ-09; CAP-06; G6 | Any eng walk | No merge API/action invoked by Gateflow | code guard + verify | W3 |
| REQ-10 | Resolve/stop events include pin `purpose` when present on the stopped/next node; include pin `owner` when set. Human-checkpoint stops must expose purpose on timeline/API fields PE uses. | PRD REQ-10; CAP-01, CAP-06; G7; US-1 | Walker stops at human-checkpoint or gate node with pin purpose | `run_stopped` (or equivalent run detail) payload includes `purpose`; `owner` when pin declares it | unit | W0 |
| REQ-11 | Create-tickets does not resume into implement on the same run; coding only via new implement-start. | PRD REQ-11; CAP-02; G8 | After create-tickets success | Walker does not dispatch `pre-implement` on same run | unit + verify | W1 |
| REQ-12 | `POST /api/v1/initiatives/closure/start` accepts programme token + required body binds; malformed → **400**; valid → **202** + `run_id`. | PRD REQ-12; CAP-05; G4 | Closure start request | Route exists exactly as programme token; field validation per PRD | unit + verify | W4 |
| REQ-13 | Closure Done-gate: every `wave_ticket_ids` entry must be board Done; else **422**, 0 enqueue, no purge, EPIC not mutated. | PRD REQ-13; CAP-05; G9-A1 | Closure start with wave ids | Fail closed when any wave not Done | unit + verify | W4 |
| REQ-14 | After Done-gate passes, set `epic_ticket_id` → Done **before** dispatching `purge-initiative-artifacts-app` (programme board hygiene — not a pin external-action node). | PRD REQ-14; CAP-05; draft lock | Closure enter after Done-gate | EPIC Done on board before purge hop | verify | W4 |
| REQ-15 | Closure walk: `purge-initiative-artifacts-app` → automated `initiative-closure-pr-action-app` → STOP `initiative-closure-signoff-app`; never purge-meta. | PRD REQ-15; CAP-05; G3 | Closure run | Timeline stops at signoff-app; no meta purge dispatch | verify | W4 |
| REQ-16 | Never auto-apply labels ending in `-lgtm`; only pin `apply_labels` lists on automated forge hops. | PRD REQ-16; CAP-06; G10 | Any `open_draft_pr` or label projection | Label audit shows no `*-lgtm` from Gateflow | unit + verify | W3 |
| REQ-17 | Verify suite covers spec, tickets, implement (with In Progress), closeout (with Done), closure paths; scripts exit 0 under programme knobs. | PRD REQ-17; CAP-01…05; G11 | Programme exit / wave completion | Live-Verify records under `tests/verify/` | live verify | W2–W4 |
| REQ-18 | Feature-readiness freeze doc lists proven vs deferred eng capabilities (PM Enter-at, meta purge, ops UI, C2, authorize→resume). | PRD REQ-18; CAP-06 | W4 exit | Freeze doc in gateflow reports | inspection | W4 |
| REQ-19 | After `wave-signoff` / wave-complete semantics, Gateflow does not auto-start next wave or closure; PE starts implement-start or closure-start deliberately. | PRD REQ-19; CAP-04; US-6 | After wave-signoff terminal | No auto-chain to next wave or closure | unit + verify | W3 |
| REQ-20 | If EPIC → Done succeeds but purge-app or closure Draft PR fails: record failure; do not claim closure complete; PE may re-enter / compensate. | PRD REQ-20; CAP-05; VF-09 | Partial failure after EPIC Done | Failure recorded; no success claim | unit + verify | W4 |

> **Id convention:** `REQ-*` ids in this table mirror PRD **REQ-01…REQ-20** one-to-one
> for traceability. Do not invent wave-scoped `REQ-W*` ids.

**Inherited (unless superseded):** INIT-001…009 control plane; ADR-009 publish before
ingest and dual `authorization`; ADR-010 meta intake + dual workspace; INIT-008
automated `spec-pr-action` / `wave-pr-action`; ForgeClient transport; programme token;
explicit authorize for board create; WorkManifest `prayog/v1` validator (INIT-008).

## Negative and failure paths

| REQ | Condition | Required behavior | Evidence |
|-----|-----------|-------------------|----------|
| REQ-01 | Harness pin SHA/tag ≠ submodule consumed at runtime | Fail closed or refuse remount claim; no silent drift | inspection |
| REQ-02 | `update_board_status` node missing `forge.status` or unknown status enum | Pin parse / `get_node` raises; no silent default | unit |
| REQ-02 | Any remounted node id fails `get_node` | 0 BROKEN policy violated; unit fails | unit |
| REQ-03 | Board-status hop missing ticket at apply time | Fail closed hop; no silent skip (PRD error table) | unit |
| REQ-06 | Any create predicate fails | **422**; 0 board creates | unit + verify |
| REQ-08 | Missing/malformed `ticket_id` on implement-start | **400**; 0 enqueue | unit + verify |
| REQ-08 | Unresolvable ticket, initiative/wave mismatch, or ticket already Done | **422**; 0 enqueue | unit + verify |
| REQ-10 | Stop at human-checkpoint without purpose in pin | N/A when pin omits purpose; when pin sets purpose, payload must include it | unit |
| REQ-12 | Closure missing/malformed required fields or empty `wave_ticket_ids` | **400**; 0 enqueue | unit + verify |
| REQ-13 | Closure any wave not board Done | **422**; no purge; EPIC not mutated | unit + verify |
| REQ-16 | Attempt to apply `*-lgtm` via forge | Fail closed at merge/validate | unit |
| REQ-20 | EPIC Done ok; purge-app or closure Draft PR fails | Run failure recorded; no closure-complete claim | unit + verify |

## Out of scope for this repo

- **gateflow-ops** — Mission Control / ops UI (deferred INIT).
- **prayog-meta** — PM Enter-at, meta purge orch, PRD hosting (meta is Gate 1 source only).
- **prayog-skills** — Pin redesign; consume tip `v0.5.0-rc.2` only (monitor).
- **launchpad** — No new human forge skill for `update_board_status` (pin forbids).
- Same-run resume from create-tickets into implement (two-API model).
- Implement-start creating board tree or picking first wave automatically.
- Forge merge / `delete_branch`; auto `*-lgtm`; authorize→resume Pass-1 on same run.

## Cross-service contracts

| Contract ID | Provider / owner | Consumer / owner | Entry point | Input shape | Output shape | Invariants | Errors | Compatibility / versioning | Contract-test location |
|-------------|------------------|------------------|-------------|-------------|--------------|------------|--------|----------------------------|------------------------|
| CTR-01 | prayog-skills / prayog-pe-team | gateflow / prayog-pe-team | Load pinned `workflow.yaml` + `delivery-contract.yaml` @ `v0.5.0-rc.2` | Remounted submodule path; harness ref must match | Parsed nodes, forge policy, dispatch edges | Gateflow must not overlay pin YAML; missing external-action `authorization` fails closed | Pin load / get_node errors fail closed | Pin family frozen for INIT (A3); tip retag → separate INIT | `tests/unit/test_forge_policy.py`; `tests/unit/test_handoff_workflow.py` |
| CTR-02 | GitHub forge/board | gateflow / prayog-pe-team | ForgeClient board create + status update + Draft PR open | org/repo; ticket ids; label projections | Issue state column+state; PR numbers | Board Done/In Progress vocabulary = pin `status: done` \| `in_progress` (A1); never merge via Forge | GitHub API failures propagate; predicate failures → no side effect | Existing BoardService contract; label asymmetry for initiative vs wave | `tests/unit/test_board_service.py`; `tests/unit/test_forge_client_board.py`; `tests/verify/verify_board.py` |
| CTR-03 | gateflow / prayog-pe-team | GitHub forge/board | Outbound forge actions: `open_draft_pr`, `create_board_tickets`, `update_board_status` | Pin `forge.action` + merged handoff instance slots | Draft PR / issues / status updates | Never merge; never `*-lgtm`; explicit vs automated per pin | Incomplete `requires` → fail closed | W0: parse only for `update_board_status`; W1+ apply | `tests/unit/test_forge_action_service.py`; lane verify scripts (W2+) |

## Non-functional requirements

| Area | Requirement or N/A rationale | Acceptance / evidence |
|------|------------------------------|-----------------------|
| Security | Programme service token on lane/forge/board routes (existing pattern). No secrets in handoff/verify artifacts. Content skills must not treat local `gh` as automate success. | Existing auth middleware tests; runbook inspection |
| Reliability | Lane APIs fail closed on bad binds (400/422, 0 enqueue). Board-status hop missing ticket fails closed (no silent skip). REQ-20 partial closure failure must not claim success. | Unit + verify negative cases per PRD error table |
| Performance / capacity | N/A for W0 parse-only wave. Later waves inherit existing orchestrator hop cap (`GATEFLOW_MAX_ORCHESTRATED_HOPS`). | Inspection |
| Observability | REQ-10: stop timeline exposes pin `purpose` / `owner`. Existing run timeline + metrics dims retained. | Unit on `run_stopped` payload; verify scripts W2+ |
| Privacy / data handling | No new PII stores. Learning DB unchanged by this INIT until closeout paths exercised. | N/A — no schema change in W0 |
| Migration / compatibility | W0 additive parse fields on `ResolvedWorkflowNode`; no API breaking changes. Later waves add routes/validators incrementally. | Unit regression green |
| Rollback / recovery | REQ-20: PE may re-enter closure after partial failure; EPIC may already be Done. | Verify closure negative path W4 |
| Operations / support | Verify scripts + freeze doc (REQ-17/18) are ops evidence SSOT for lane claims. | Live-Verify reports; Feature-Readiness doc W4 |

## Assumptions

| ID | Assumption | Evidence | Owner | Status | Invalidated when |
|----|------------|----------|-------|--------|------------------|
| A-1 | Board Done / In Progress vocabulary = pin `status: done` \| `in_progress` as applied by board-status hops / BoardService | PRD A1; INIT-002 board MVP | prayog-pe-team | confirmed | Board column contract changes |
| A-2 | PE retains `epic_ticket_id` + `wave_ticket_ids[]` from create-tickets for implement-start and closure-start | PRD A2; two-API model | prayog-pe-team | confirmed | Single-API create+implement introduced |
| A-3 | Pin tip family `v0.5.0-rc.2` frozen for INIT delivery; harness ref == submodule tip | Submodule `6561c7c` == tag; `.harness-pin.yaml` | prayog-pe-team | confirmed | Tip retag mid-INIT without programme decision |
| A-4 | INIT-008 automated forge + INIT-009 prove-out baseline remains on `develop` before W1+ dogfood | as-built INIT-008/009 human_approved | prayog-pe-team | confirmed | Regression on develop breaks lane baseline |

## Spec questions (ambiguities — need PM or domain confirmation before feasibility)

| ID | Lane | Question | Owner | Blocking | Required by | Default if deferred | Status | Resolution link |
|----|------|----------|-------|----------|-------------|---------------------|--------|-----------------|
| Q-1 | PE | Exact problem+json / OpenAPI error body field names for lane APIs (**PRD OQ-01** / **IM-01**) | prayog-pe-team | no | OpenAPI / technical review | HTTP **400**/**422** semantics and side-effect table remain normative; field names TBD | open | pending OpenAPI pass |
| Q-2 | PM | Parallel open GATEFLOW meta PRs (#10–#23) sequencing vs this INIT (**IM-02**) | programme PM | no | Gate 1 scheduling | Proceed; distinct INIT ids | open | n/a |
| Q-3 | PE | Whether W0 unit tests alone satisfy REQ-17 “verify suite” claim for W0 exit, or W0 requires no verify script | prayog-pe-team | no | feasibility / plan | W0 exit = unit only per PRD §5 table; REQ-17 partial deferred to W2+ | resolved | PRD §5 W0 row — REQ-17 not listed |

## Draft check summary (D1–D12)

| Check | Status | Evidence / findings |
|-------|--------|---------------------|
| D1 Approved handoff current | PASS | Meta PR #28 head `df0f5a5…` = tech-lead APPROVED review commit_id; H1/H3 match impact map rev 1; gateflow affected with H2 scope digest |
| D2 Complete PRD traceability | PASS | CAP-01…06 map to REQ-01…REQ-20; every REQ cites PRD REQ/CAP/US |
| D3 Repo-bounded scope | PASS | Matches H2 payload; deferred repos gateflow-ops, prayog-skills consume-only; meta not eng delivery |
| D4 Observable acceptance | PASS | Each REQ has condition/event, observable result, evidence layer |
| D5 Negative/failure paths | PASS | Table covers PRD error table + W0 parse failures; N/A rows justified |
| D6 Assumptions/questions | PASS | A-1…A-4 documented; Q-1/Q-2 non-blocking with defaults; Q-3 resolved |
| D7 Cross-repository contracts | PASS | CTR-01…03 semantic boundaries with owners and test locations |
| D8 NFR applicability | PASS | All areas addressed or N/A with reason |
| D9 As-built alignment | PASS | Partial REQ-02 parse; REQ-10 gap noted; REQ-03 apply deferred W1 |
| D10 Dependency order | PASS | Matches impact map §7: pin → W0…W4 → deferred ops |
| D11 Zero unresolved blockers | PASS | No blocking PM/PE/domain question; Q-1/Q-2 deferred with defaults |
| D12 Output completeness | PASS | Header H4, tables, checks, outcome, PR readiness, dev review present |

**Draft verdict:** PASS

**Selected workflow outcome:** `pass`
**Outcome reason:** D1–D12 PASS; Gate 1 approved on current meta head; zero material unresolved questions after clarification loop.

Do not advance to `/initiative-feasibility` unless workflow outcome is `pass`, draft
verdict is PASS, and developer review below is complete.

## PR readiness handoff

| Item | Value |
|------|-------|
| Workflow outcome | `pass` — Gate 1 current; full traceability; no material blockers |
| Verdict | PR READY |
| Existing spec PR | none |
| Proposed branch | `feature/INIT-GATEFLOW-010-w0-spec-lane` |
| Proposed base | `develop` |
| Proposed title | `[INIT-GATEFLOW-010] Spec — eng-lane pin tip executor parity (gateflow)` |
| PR type | **Draft** (entire spec lifecycle) |
| Local artifacts to publish | `docs/specification/product/INIT-GATEFLOW-010-gateflow.md`, `docs/specification/README.md` |
| Forge readiness | fill `handoff.forge` for `open_draft_pr`; recommend `/commit-workspace` then orchestrator `spec-pr-action` |
| Reviewer | @drivestream-lab/prayog-pe-team |
| Initial Gate 2 label | `spec-pending` |
| Additional invalidation label | none |
| Blocking items | none |

**No GitHub side effects have occurred.** Persist the draft locally; authorize Forge publish separately.

### Proposed Draft PR body

```markdown
## Initiative

INIT-GATEFLOW-010 — Engineering-lane pin tip executor parity (gateflow only)

## Meta handoff

- Meta PRD PR: https://github.com/drivestream-lab/prayog-meta/pull/28
- Approved meta head: `df0f5a5c09b6c4f951463bb42f277305310aaa80`
- Impact-map revision: 1
- PRD digest: `sha256:457f19617113171c973abdbc15d1afaa00df2f6947ab4567b57d8440bd88b206`
- Repo scope digest: `sha256:09c89c143c14401c8812738c162c05a2f5e504cabafd1818ee72eb4e9b781532`

## Spec path

`docs/specification/product/INIT-GATEFLOW-010-gateflow.md`

## Summary

- Full INIT scope: eng lifecycle tip parity (spec → tickets → implement → closeout → eng closure)
- W0 exit (this wave): REQ-01 pin consume, REQ-02 board-status parse (0 BROKEN), REQ-10 purpose/owner on stops
- W1–W4: board-status apply, ticket gates, create predicates, closure Enter-at, verify suite, freeze (see spec wave table)
- Open engineering questions: Q-1, Q-2 (non-blocking; defaults documented)

## Gate 2 — spec package readiness

Initial label: `spec-pending`

- [ ] Spec slice published on this PR head (via Forge `/commit-workspace` / `spec-pr-action`)
- [ ] Feasibility report (later Forge publish)
- [ ] Technical design + ADRs (later Forge publish)
- [ ] Implementation plan §9 (later Forge publish)
- [ ] PE sets `spec-lgtm` on exact final head before merge

Requested reviewer: @drivestream-lab/prayog-pe-team
```

## Developer review

- [x] Scope matches the approved impact-map repo scope digest
- [x] REQs have condition/event, observable result, and evidence layer
- [x] Contracts are semantic (logical operation); no architecture decisions in REQs
- [x] No blocking question remains
- [x] Developer confirmed draft is ready for feasibility — PE accept 2026-08-05

## References

- PRD: `prayog-meta/prd/INIT-GATEFLOW-010.md` @ meta PR #28
- Impact map: `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-010.md` revision 1
- Predecessors: INIT-009 (factory prove-out), INIT-008 (automated forge), INIT-007 (closeout)
- As-built: `docs/specification/as-built/implementation-status.md`

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-draft
  outcome: pass
  artifact:
    path: docs/specification/product/INIT-GATEFLOW-010-gateflow.md
    digest: sha256:82a37302e60fb7d6ab19f4fc0040dc01bccf23b39a8ef60a72311f8049fbbe42
  blockers: []
  signals:
    pr_ready: true
    initiative: INIT-GATEFLOW-010
    delivery_wave: W0
    meta_pr: "https://github.com/drivestream-lab/prayog-meta/pull/28"
    meta_pr_head: "df0f5a5c09b6c4f951463bb42f277305310aaa80"
    map_revision: 1
    prd_digest: "sha256:457f19617113171c973abdbc15d1afaa00df2f6947ab4567b57d8440bd88b206"
    scope_digest: "sha256:09c89c143c14401c8812738c162c05a2f5e504cabafd1818ee72eb4e9b781532"
    d_checks: pass
    nonblocking_questions: "Q-1,Q-2"
  next_candidates:
    - spec-pr-action
  human_checkpoint: false
  external_action: true
  forge:
    action: open_draft_pr
    draft: true
    apply_labels:
      - spec-pending
    title: "[INIT-GATEFLOW-010] Spec — eng-lane pin tip executor parity (gateflow)"
    body_path: docs/specification/product/INIT-GATEFLOW-010-gateflow.md
```
