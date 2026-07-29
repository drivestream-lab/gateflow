# INIT-GATEFLOW-006 — spec slice for gateflow

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-006 |
| PRD | TBD — retrospective / PE-directed; no `prayog-meta` PRD or Impact-Map yet (Gate 1 open) |
| PRD digest | TBD |
| Meta PR | TBD |
| Meta PR approved head | TBD |
| Impact map | TBD |
| Impact-map revision | TBD |
| Repo scope digest | TBD — gateflow-only intended |
| Tech-lead approval | TBD (Gate 1 follow-on) |
| Architecture | [`docs/specification/adr/adr-009-pin-forge-publish-mutate-authority.md`](../adr/adr-009-pin-forge-publish-mutate-authority.md) (**Accepted**); [`adr-010-lane-intake-and-dual-workspace-authority.md`](../adr/adr-010-lane-intake-and-dual-workspace-authority.md) (**Accepted**) |
| Repo | drivestream-lab/gateflow |
| Date | 2026-07-29 |
| Status | Draft — PE review required; Gate 1 / retrospective PRD follow-on required |

## Overview

This repo delivers an **unattended delivery factory** upgrade on the INIT-001…005
control plane:

1. **Pin `forge:` publish/mutate** — after packaged content hops, Gateflow applies
   pin policy via ForgeClient (workspace publish to the run head; external-action
   mutates only after explicit authorize). Architecture is **ADR-009 Accepted**;
   this INIT productizes acceptance criteria and live evidence (catch-up vs code
   already on `develop` via #70).
2. **Separate lane start APIs** — distinct HTTP contracts for **implement** vs
   **spec** waves so required arguments stay fail-closed and OpenAPI-honest
   (no optional mega-body).
3. **Spec-lane intake** — start from a **meta PR URL** with **dual workspace bind**:
   `workspace` = app coding root; `meta_workspace` = checked-out `prayog-meta`
   tree so prompt packages can bind both roots deterministically.

**Product intent:** humans consume PRs for high-value judgment (ADR accept /
verify); Gateflow runs unattended hops. Launchpad owns gate labels
(`spec-pending`, `impact-map-*`, …). Gateflow never invents new PE gate labels
and never writes `*-lgtm`.

**Out of scope for this INIT:** INIT-GATEFLOW-005 **W2** dogfood (#57);
authorize-then-**resume** walker; inventing labels; authoring prayog-skills
packages (pin ownership); gateflow-ops UI; second AgentRunner.

**As-built baseline (2026-07-29):** ADR-009 Accepted; forge parse/merge/publish/
authorize/sparse-notify **unit-complete** on `develop` (#70). Live
`stage_commit` / authorize dogfood **deferred**. Lane starts are
`POST /api/v1/waves/implement/start` and `POST /api/v1/waves/spec/start`
(undifferentiated `/waves/start` removed). Spec skills remain
`dispatch: manual` on the pin until prayog-skills promote; dual bind + meta
accept-gate are unit-wired pending human Alembic for `runs.meta_*` and pin.
INIT-005 W0/W1 BOUNDINPUT (prompt resolve, thin Cursor, stored baton) is
**human_approved**; W2 multi-skill dogfood is **out of this track**.

**Delivery waves (product-normative; plan may refine):**

| Wave | Intent | Exit REQs |
|------|--------|-----------|
| **W0** | Workspace publish from pin `forge.commit_workspace` (parse, path filter, commit to run head, publish-before-ingest, timeline evidence) | REQ-1…REQ-6 |
| **W1** | External-action forge authorize (`open_draft_pr`, `create_board_tickets`); dual executor; Launchpad labels only; FR-24 worker isolation | REQ-7…REQ-11 |
| **W2** | Sparse PR run-event comments (milestone-only) + `stage_started` timeline | REQ-12…REQ-13 |
| **W3** | Separate implement vs spec wave-start APIs; shared run core; strict per-lane validators | REQ-14…REQ-16 |
| **W4** | Spec accept-gate from `meta_pr_url`; dual bind `workspace` + `meta_workspace`; pin schema/dispatch dependency for orchestrated spec chain | REQ-17…REQ-21 |

## Functional requirements

| ID | Requirement | Source | Acceptance criteria | Evidence type |
|----|-------------|--------|---------------------|---------------|
| REQ-1 | Parse pin node `forge` for skills; **absent** forge ⇒ workspace publish **disabled**. Handoff may carry **instance** slots only; it must not override pin policy. Policy/instance conflicts fail closed. | ADR-009; pin forge-side-effects | Unit: absent → disabled; invalid mode → fail closed; pin wins over handoff policy | unit |
| REQ-2 | Collect publish paths with repository ignore semantics + hard secret denylist; **exclude** run-scoped handoff batons under `GATEFLOW_HANDOFF_ROOT`. | ADR-009 path class | Unit: gitignore honored; `.env` denied; handoff root excluded | unit |
| REQ-3 | After successful content hop, when pin enables publish, commit collected paths to the **run head** via ForgeClient (blobs → tree → commit → ref). Head comes from **run context** only — not pin/handoff head selectors. | ADR-009 | Unit: ForgeClient commit path; head from run targeting | unit |
| REQ-4 | When publish and handoff ingest both apply on the same hop, **publish before ingest**. | ADR-009 ordering | Unit: publish awaited before `read_path` ingest | unit |
| REQ-5 | Publish policy class: **optional** + nothing to publish → continue; **required** + nothing → fail closed; publish I/O failure → fail closed. Concrete enums remain pin SSOT. | ADR-009 | Unit: optional empty OK; required empty fails; I/O fails closed | unit |
| REQ-6 | Live prove-it: an opted-in implement-lane (or equivalent orchestrated) run leaves `stage_commit` (or equivalent timeline) evidence for pin-**required** publish nodes after successful hops. | ADR-009; as-built verify | Live verify asserts required-node commits when forge dogfood enabled | live verify |
| REQ-7 | On pin **external-action** with `forge.action`, content hop must **not** mutate forge. Run **STOP**s with a pending forge signal until explicit authorize. | ADR-009 dual executor | Unit: STOP path; no open_draft_pr / board create inside `process_job` | unit |
| REQ-8 | Programme **authorize** path executes pin ⋉ handoff forge for `open_draft_pr` and `create_board_tickets` only when `authorized=true` and run is STOPPED at that external-action. Mount is TDD (as-built: `POST /api/v1/runs/{id}/forge/authorize`). | ADR-009; as-built | Unit: authorize happy/fail paths; missing requires fail closed | unit |
| REQ-9 | `open_draft_pr` applies **only** Launchpad/pin-declared projection labels (e.g. `spec-pending`, `impact-map-pending`). **Never** write `*-lgtm`. Do not invent Gateflow-only PE gate labels. | ADR-009; Launchpad label vocabulary | Unit: forbid lgtm; apply_labels from pin only | unit + inspection |
| REQ-10 | `create_board_tickets` seeds from plan WorkManifest via BoardService primitives; idempotent EPIC + wave Features. Worker `process_job` must not call BoardService (FR-24). | ADR-009; FR-24 | Unit: board seed via authorize; `process_job` never board-mutates | unit |
| REQ-11 | Dual executor: human forge skills **or** programme authorize may perform the same pin actions; orchestrator must not Cursor-dispatch forge skills as content outcomes. | ADR-009 | Inspection + unit: no forge-skill dispatch on content hop | unit + inspection |
| REQ-12 | Notifier posts run events to the PR only for **milestone** types (as-built: e.g. `run_stopped`, `api_trigger` if posted). `stage_*` hop chatter is timeline-only. | Product UX; as-built | Unit: stage_started/completed skip PR comment; run_stopped posts | unit |
| REQ-13 | Orchestrator records `stage_started` (or equivalent) on the RunStore timeline when PR hop comments are sparse. | Product UX; as-built | Unit: timeline event present for hop start | unit |
| REQ-14 | Expose **separate** authenticated start APIs for lanes, e.g. `POST /api/v1/waves/implement/start` and `POST /api/v1/waves/spec/start` (exact paths TDD). Shared run/enqueue core; **no** single optional mega-body for both lanes. | Product vision (API B) | OpenAPI shows distinct required fields; wrong-lane body rejected | unit |
| REQ-15 | **Implement** start requires board/wave identity (`ticket_id`, `initiative_id`, `wave_id`, …) and Enter-at an **orchestrated** implement skill (default `pre-implement`). Must **not** require `meta_pr_url` / `meta_workspace`. | Product vision | Missing ticket → 4xx; meta-only fields rejected or ignored per forbid | unit |
| REQ-16 | **Spec** start requires `meta_pr_url`, app `org`/`repo`/`workspace_path`, and `meta_workspace_path` (absolute checkout of prayog-meta). Enter-at an orchestrated spec skill (default `spec-draft` once pin allows). Must not reuse implement-only required sets. | Product vision (API B + meta C) | Missing meta_pr_url or meta_workspace → 4xx before enqueue | unit |
| REQ-17 | Spec accept-gate: resolve `meta_pr_url` via ForgeClient; enforce initiative consistency (caller-supplied and/or derived+checked); fail closed if PR missing, wrong repo, or Gate 1 evidence rules fail (TDD). Persist meta head / URL on the run for audit. | Product vision | Unit/integration: bad URL / mismatch → no enqueue | unit |
| REQ-18 | Dual bind: for packaged spec-lane hops, bind map includes `workspace` (app) and `meta_workspace` (meta checkout) plus existing BOUNDINPUT fields (`ticket`/`initiative`/`skill_id`/`handoff_path` as applicable). Pin `schema.yaml` for those skills must declare the new vars (pin dependency). | Product vision (meta C); INIT-005 bind | Rendered brief contains both roots; required miss → fail closed before AgentRunner | unit |
| REQ-19 | Spec coding writes land under **app** `workspace`; meta tree is **read** intake. Spec PR targeting is the app `org`/`repo` from the start request. | Product vision | Inspection + unit: PR head on app repo; bind distinguishes roots | unit + inspection |
| REQ-20 | Pin dependency (documented, not authored in gateflow): orchestrate `spec-draft` → `initiative-feasibility` → `spec-technical-review` (`dispatch: orchestrated`); keep plan / ADR human-checkpoint / gate-2 human-guarded. Until pin lands, REQ-16 Enter-at remains blocked fail-closed. | Product vision; pin SSOT | Spec start rejects non-orchestrated start_node; after pin promote, chain walks until human ADR gate | unit + live verify (after pin) |
| REQ-21 | Prove-it (spec intake): one live spec-lane start with valid meta PR + dual workspaces produces ≥1 successful packaged hop with prompt ids and non-empty baton dual-write, stopping at the pin human ADR (or equivalent) gate with an app PR using Launchpad labels only. | Product vision | Live verify / ground evidence documents meta_pr, skill ids, stop node | live verify |

> **Id convention:** `REQ-*` canonical. This INIT assigns **REQ-1…REQ-21** as above.
> Traceability is to **ADR-009**, pin forge-side-effects, FR-24, INIT-005 bind
> contracts, and PE-directed product vision until a meta PRD exists (see Spec
> questions).

**Inherited (unless superseded above):** INIT-001…005 control-plane and BOUNDINPUT
REQs remain in force (wave-start auth, pin walker, Cursor, RunStore baton,
prompt resolve/render, board primitives, programme token, ADR-006 registry).
This INIT **adds** forge publish/authorize productization and **supersedes** the
single undifferentiated wave-start body with lane-specific start contracts
(W3+). Ambient ingest remains non-SSOT for packaged automate (INIT-005 REQ-8b).

**Explicit non-goals (may become later INITs):** authorize-then-resume walker to
the next orchestrated node after forge mutate; INIT-005 W2 multi-skill dogfood;
automatic merge-webhook continuation.

## Negative and failure paths

| REQ | Condition | Required behavior | Evidence |
|-----|-----------|-------------------|----------|
| REQ-1 | Invalid pin forge / handoff policy conflict | Fail closed; no publish | unit |
| REQ-2 | Path would include secret or handoff baton | Excluded from commit set | unit |
| REQ-5 | Required publish with empty tree | Fail closed; no ingest advance | unit |
| REQ-5 | Publish I/O / GitHub error | Fail closed; stage/run records failure | unit |
| REQ-7 / REQ-10 | Board/forge mutate inside `process_job` | Must not occur | unit |
| REQ-8 | Authorize with `authorized=false` or wrong node | 4xx / validation error; no mutate | unit |
| REQ-9 | Attempt `*-lgtm` label | Forbid; fail closed | unit |
| REQ-14…16 | Wrong lane body / missing required field | 4xx; 0 enqueue | unit |
| REQ-17 | Meta PR unreadable / initiative mismatch / Gate 1 fail | Fail closed; 0 enqueue | unit |
| REQ-18 | `meta_workspace` missing or not a directory when required | Fail closed before AgentRunner | unit |
| REQ-20 | Spec start_node not orchestrated on active pin | Fail closed at accept | unit |

## Out of scope for this repo

- **INIT-GATEFLOW-005 W2** multi-skill packaged dogfood (board #57) — separate track
- **Authorize → resume** walker (mutate-only authorize remains; new wave after tickets)
- Inventing PE gate labels beyond Launchpad vocabulary
- **prayog-skills** package authoring / pin promote (document dependency only)
- **prayog-meta** PRD authoring (Gate 1 follow-on; see Spec questions)
- **gateflow-ops** / Mission Control UI
- Second AgentRunner (OpenCode / Claude Code)
- Allowlist-first publish packaging (ADR-009 revisit)
- Formal auto-merge or writing `*-lgtm`

## Cross-service contracts

| Contract ID | Provider / owner | Consumer / owner | Entry point | Input shape | Output shape | Invariants | Errors | Compatibility | Contract-test location |
|-------------|------------------|------------------|-------------|-------------|--------------|------------|--------|---------------|------------------------|
| CTR-01 | prayog-skills / PE | gateflow | Pin node `forge:` + forge-side-effects | pin YAML | Policy + action vocabulary | Pin is policy SSOT; handoff instance-only | Invalid forge ⇒ fail closed | Active pin line | `test_forge_policy`, `test_forge_merge` |
| CTR-02 | gateflow / PE | GitHub (forge) | ForgeClient publish + authorize mutates | paths / PR / issues | commit SHA, PR number, issue ids | No `*-lgtm`; no auto-merge; App/PAT via token provider | HTTP/I/O ⇒ fail closed | ADR-003 transport | `test_forge_client`, `test_forge_action_service` |
| CTR-03 | Launchpad / PE | gateflow | Gate label vocabulary on PRs | pin `apply_labels` | Projection labels only | Never invent; never write `*-lgtm` | Forbid on lgtm | Label set owned upstream | unit forbid + inspection |
| CTR-04 | prayog-meta (intake) | gateflow | Spec start `meta_pr_url` + `meta_workspace` | PR URL + checkout path | Bound meta context | Meta is read intake; app is write workspace | Accept-gate fail ⇒ 0 enqueue | New in W3/W4 | Planned unit + live |
| CTR-05 | pin packages | gateflow | Spec skill `schema.yaml` bind vars | dual workspace fields | Rendered brief | Packages declare `meta_workspace` when required | Bind miss ⇒ fail closed | Pin bump required for W4 | `test_prompt_resolver` + pin fixtures |

Inherited: INIT-005 CTR pin packages + baton; INIT-003 Cursor AgentRunner; board FR-24 primitives.

## Non-functional requirements

| Area | Requirement or N/A rationale | Acceptance / evidence |
|------|------------------------------|-----------------------|
| Security | Programme token on start/authorize; secrets never in publish tree; meta checkout treated as trusted intake path; no `*-lgtm` writes | unit + inspection |
| Reliability | Fail closed on publish/authorize/accept/bind; FR-24 worker isolation retained | unit |
| Performance / capacity | N/A new SLAs — correctness of forge and accept gates over throughput | inspection |
| Observability | Timeline `stage_commit` / forge_executed / stage_started; structured logs with run_id, workflow_node, meta_pr when set | unit + live |
| Privacy / data handling | Ticket/initiative/meta URLs may appear in briefs/logs — no secret materialization into commits | inspection |
| Migration / compatibility | Additive APIs preferred; deprecate monolithic `/waves/start` via TDD window after W3 | inspection |
| Rollback / recovery | Disable authorize / withhold pin forge / stop worker; runs reconstructable from Postgres | runbook inspection |
| Operations / support | Document dual checkout expectation for spec start; PE owns pin + labels; Gateflow eng owns runtime | docs |

## Assumptions

| ID | Assumption | Evidence | Owner | Status | Invalidated when |
|----|------------|----------|-------|--------|------------------|
| A-1 | ADR-009 remains Accepted for publish/mutate authority | ADR file; PE accept 2026-07-28 | PE | confirmed | Superseding ADR |
| A-2 | Pin remains SSOT for forge wiring and dispatch | prayog-skills workflow + forge-side-effects | PE | confirmed | Product moves policy into Gateflow |
| A-3 | Launchpad label vocabulary is sufficient; Gateflow must not invent PE gates | prayog-skills README; ADR-009 | PE | confirmed | Launchpad adds required new labels via pin only |
| A-4 | Separate lane start APIs are the long-term control-plane shape | PE design chat 2026-07-29 (API B) | PE | confirmed | Product reverts to one body |
| A-5 | Dual workspace bind is the meta access model | PE design chat 2026-07-29 (meta C) | PE | confirmed | Single-workspace or fetch-only model adopted |
| A-6 | INIT-005 W2 dogfood is out of this INIT’s delivery | PE direction 2026-07-29 | PE | confirmed | PE folds W2 into 006 |
| A-7 | Authorize-resume is not required for the happy path (tickets API + new implement start) | As-built gap; PE playbook | PE | confirmed | Product mandates same-run resume |
| A-8 | Meta Gate 1 / PRD may follow the engineering INIT (catch-up) | No meta PRD today | PE | open | Gate 1 lands with digests |

## Spec questions (ambiguities — need PE confirmation)

| ID | Lane | Question | Owner | Blocking | Required by | Default if deferred | Status | Resolution link |
|----|------|----------|-------|----------|-------------|---------------------|--------|-----------------|
| Q-1 | PE | Retrospective meta PRD + Impact-Map for INIT-GATEFLOW-006 (Gate 1) vs PE waive Gate 1 for catch-up forge + vision INIT? | PE | yes for formal Gate 2 package | feasibility / board-seed | Draft INIT proceeds; open thin meta PRD before `/board-seed` | open | — |
| Q-2 | PE | Exact paths for lane APIs (`/waves/implement/start` + `/waves/spec/start` vs alternate prefix)? | PE | no | TDD W3 | `/api/v1/waves/implement/start` and `/api/v1/waves/spec/start`; keep legacy `/waves/start` as implement alias briefly | open | — |
| Q-3 | PE | Spec accept-gate minimum evidence (GitHub APPROVED only vs `impact-map-lgtm` + Approve + digests)? | PE | no | TDD W4 | Match existing Gate 1 discipline: APPROVED on head + map/PRD digests when present; labels projection-only | open | — |
| Q-4 | PE | Is `initiative_id` always required on spec start, or may Gateflow derive-only from meta PR with caller override check? | PE | no | TDD W4 | Require `initiative_id`; derive from PR and **fail closed on mismatch** | open | — |
| Q-5 | PE | NEW-ADR (candidate **ADR-010**): spec intake authority = meta PR URL + dual workspace bind; implement intake = board ticket — accept before W3/W4 code? | PE | no | technical review | Yes — Draft ADR-010 in `/spec-technical-review` before W3 implement | **resolved** | [`adr-010-lane-intake-and-dual-workspace-authority.md`](../adr/adr-010-lane-intake-and-dual-workspace-authority.md) (**Accepted** 2026-07-29) |
| Q-6 | PE | Pin promote timing: orchestrate spec-draft → feasibility → technical-review before or with W4 Gateflow drop? | PE | yes for REQ-20/21 live | W4 live | Pin change lands first (or same programme release); Gateflow fail-closed until orchestrated | open | — |
| Q-7 | PE | Bind variable names for meta root (`meta_workspace` vs `meta_root`) and whether `meta_pr_url` is in schema or run-only audit? | PE | no | pin schema + TDD | `meta_workspace` + `meta_pr_url` both in bind when schema requires | open | — |

## Draft check summary (D1–D12)

| Check | Status | Evidence / findings |
|-------|--------|---------------------|
| D1 Approved handoff current | **FAIL / waived** | No meta PRD / Impact-Map / APPROVED head — Q-1; PE-directed catch-up draft |
| D2 Complete PRD traceability | **PARTIAL** | Trace to ADR-009 + vision + as-built; CAP-* pending retrospective PRD |
| D3 Repo-bounded scope | PASS | gateflow-only; pin/meta called out as dependencies |
| D4 Observable acceptance | PASS | Each REQ has criteria + evidence type |
| D5 Negative/failure paths | PASS | Publish/authorize/lane/accept/bind covered |
| D6 Assumptions/questions | PASS | A-1…A-8; Q-1…Q-7 with defaults |
| D7 Cross-repository contracts | PASS | CTR-01…05 |
| D8 NFR applicability | PASS | Eight rows |
| D9 As-built alignment | PASS | Distinguishes unit-complete forge vs deferred live; missing lane APIs |
| D10 Dependency order | PASS | W0–W2 forge productization → W3 APIs → W4 intake/pin |
| D11 Zero unresolved blockers | **PARTIAL** | Q-1 (Gate 1) and Q-6 (pin) block formal package / live spec prove-it |
| D12 Output completeness | PASS | Header, waves, REQs, NFR, contracts, questions, PR readiness |

**Draft verdict:** PASS WITH GATES — suitable for PE review as engineering INIT;
do not claim Gate 1 CURRENT until Q-1 closes.

Do not advance to `/initiative-feasibility` for board-seed until Q-1 has a PE
resolution (retrospective PRD or explicit waive).

## PR readiness handoff

| Item | Value |
|------|-------|
| Verdict | DRAFT READY FOR PE REVIEW (Gate 1 incomplete) |
| Existing spec PR | none |
| Proposed branch | `chore/INIT-GATEFLOW-006-spec-gateflow` |
| Proposed base | `develop` |
| Proposed title | `[INIT-GATEFLOW-006] Spec — gateflow (forge + lane starts + dual meta)` |
| PR type | **Draft** |
| Files to commit | `docs/specification/product/INIT-GATEFLOW-006-gateflow.md`, `docs/specification/README.md`, `docs/specification/as-built/implementation-status.md` |
| Reviewer | @drivestream-lab/prayog-pe-team |
| Initial Gate 2 label | `spec-pending` (when Draft PR opened) |
| Blocking items | Q-1 Gate 1 / retrospective PRD; Q-6 pin orchestrate for W4 live |

**No GitHub side effects have occurred** in this drafting step. Present this
section before creating a Draft spec PR.

### Proposed Draft PR body

```markdown
## Initiative

INIT-GATEFLOW-006 — Pin forge publish/mutate + lane start APIs + dual-workspace
spec intake (gateflow)

## Meta handoff

- Meta PRD / Impact-Map: **TBD** (Q-1 — retrospective Gate 1)
- Architecture: ADR-009 Accepted

## Spec path

`docs/specification/product/INIT-GATEFLOW-006-gateflow.md`

## Summary

- REQ-1…13 productize forge publish / authorize / sparse PR notify (ADR-009)
- REQ-14…16 separate implement vs spec wave-start APIs
- REQ-17…21 meta PR accept-gate + dual workspace bind + pin dependency for
  orchestrated spec chain
- Out of scope: INIT-005 W2 dogfood; authorize-resume; invented labels

## Gate 2 — spec package readiness

Initial label: `spec-pending` (after Draft PR exists)

## Verify

N/A for spec-only PR — `make check` on docs; live forge/lane verify in later waves
```

## Handoff envelope (draft artifact)

```yaml
handoff:
  schema_version: "1"
  skill_id: spec-draft
  initiative: INIT-GATEFLOW-006
  outcome: pass
  artifact:
    path: docs/specification/product/INIT-GATEFLOW-006-gateflow.md
  notes:
    - PE-directed INIT; Gate 1 TBD (Q-1)
    - ADR-009 remains architecture-only
    - INIT-005 W2 explicitly out of scope
  forge:
    action: open_draft_pr
    title: "[INIT-GATEFLOW-006] Spec — gateflow (forge + lane starts + dual meta)"
    body_path: docs/specification/product/INIT-GATEFLOW-006-gateflow.md
    draft: true
    # apply_labels from pin/Launchpad only when publishing — e.g. spec-pending
```
