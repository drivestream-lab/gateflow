# INIT-GATEFLOW-007 — spec slice for gateflow

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-007 |
| PRD | TBD — PE-directed from prayog-skills Pass-1/Pass-2 pin brief; no `prayog-meta` PRD or Impact-Map yet (Gate 1 open) |
| PRD digest | TBD |
| Meta PR | TBD |
| Meta PR approved head | TBD |
| Impact map | TBD |
| Impact-map revision | TBD |
| Repo scope digest | TBD — gateflow-only intended |
| Tech-lead approval | TBD (Gate 1 follow-on) |
| Architecture | [`adr-001-runtime-and-durable-store.md`](../adr/adr-001-runtime-and-durable-store.md) (**Accepted** — Postgres SSOT); [`adr-005-programme-token-control-plane-mutations.md`](../adr/adr-005-programme-token-control-plane-mutations.md); [`adr-007-invocation-brief-and-agent-message-contract.md`](../adr/adr-007-invocation-brief-and-agent-message-contract.md); [`adr-008-packaged-skill-handoff-ingest-authority.md`](../adr/adr-008-packaged-skill-handoff-ingest-authority.md); [`adr-009-pin-forge-publish-mutate-authority.md`](../adr/adr-009-pin-forge-publish-mutate-authority.md); [`adr-010-lane-intake-and-dual-workspace-authority.md`](../adr/adr-010-lane-intake-and-dual-workspace-authority.md) (**Accepted** — **amended** for closeout Pass-2 intake; no ADR-011). |
| Repo | drivestream-lab/gateflow |
| Date | 2026-07-29 |
| Status | Draft — PE review required; Gate 1 / retrospective PRD follow-on required |

## Overview

This initiative completes the **implement/spec wave lifecycle** against the remounted
prayog-skills Pass-1 / Pass-2 pin:

1. **Pass-1** (already remounted): Enter-at lane start → orchestrated coding/spec
   hops → stop at `live-verify` (human prove + tip fix). Pin park
   `wave-awaiting-closeout` is terminal status/UI only — it does **not**
   auto-dispatch closeout skills.
2. **Pass-2 / wave closeout** (this INIT): programme-token
   `POST /api/v1/waves/closeout/start` always Enter-ats **`learning-extract`**,
   creates a **new run** bound to the **existing wave PR**, then walks
   `learning-extract` → `ground-spec` → stop at `wave-signoff`.
3. **Learning SSOT**: worker/DB ingest of the Learning-Extract artifact
   (`learning_extract:` YAML, `L-*` taxonomy). Skill must **not** call Gateflow
   HTTP as success (pin H6). `reports/` remains emit-only; Ground Report cites
   `L-*` and still owns §Contracts.

**Product intent:** humans keep the high-value seat (live prove, tip fix, merge /
wave-signoff). Gateflow owns unattended Pass-2 hops and durable learning rows.
Pin remains dispatch / forge / skill-package SSOT — Gateflow does not overlay
`workflow.yaml` and does not invent skill bind variables beyond what pin
`schema.yaml` declares.

**Applies to both lanes** (implement and spec): closeout finishes **a wave**,
regardless of which Pass-1 start created the PR tip.

**Out of scope for this INIT:** authorize→resume from `live-verify` into skills;
laptop pin overlay; skill-authored Ground Report / learning DB writes;
gateflow-ops UI; second AgentRunner; inventing PE gate labels.

**As-built baseline (2026-07-29):** Pass-1 pin remounted (#76); implement-lane
live verify expects `stopped` at `live-verify`; `learning-extract` on harness
skill list. Closeout HTTP, learning tables, and Pass-2 live prove-it **not**
implemented.

**Delivery waves (product-normative; plan may refine):**

| Wave | Intent | Exit REQs |
|------|--------|-----------|
| **W0** | Closeout start API + new-run PR bind + fixed Enter-at `learning-extract`; walker to `wave-signoff`; pin bind fail-closed | REQ-1…REQ-8 |
| **W1** | Learning ingest into Postgres (global); parse artifact / baton; no skill→API; Ground Report cite path unchanged | REQ-9…REQ-13 |
| **W2** | Live prove-it both lanes (or implement-first with spec parity unit); checkpoint-id hygiene; as-built + verify scripts | REQ-14…REQ-17 |

## Functional requirements

| ID | Requirement | Source | Acceptance criteria | Evidence type |
|----|-------------|--------|---------------------|---------------|
| REQ-1 | Expose authenticated **`POST /api/v1/waves/closeout/start`** (exact path fixed unless TDD renames under same semantics). Programme token required (ADR-005). Distinct from `/waves/implement/start` and `/waves/spec/start`. | PE alignment 2026-07-29; pin CTR-G1 | OpenAPI documents the route; unauthorized → 401; wrong token → no enqueue | unit |
| REQ-2 | Closeout **always** Enter-ats pin node **`learning-extract`**. Client must **not** choose arbitrary `start_node` on this route (field absent or rejected if present). Node must be `type: skill` and `dispatch: orchestrated` on the active pin — else fail closed. | Pin CTR-P2; for-gateflow.md | Unit: Enter-at fixed; non-orchestrated / missing node → 4xx, 0 enqueue | unit |
| REQ-3 | Closeout creates a **new** `run_id` (does not resume a stopped Pass-1 run). Bind the **existing wave PR** via `org` + `repo` + `pr_number` (and/or `pr_url` if TDD adds alias). Concurrent active run for same org/repo/wave (or same PR) fails closed per existing concurrency policy. | PE alignment; pin “no authorize-resume” | Unit: new run row; prior Pass-1 run untouched; duplicate active → 409 | unit |
| REQ-4 | Closeout body supplies **wave identity** + **workspace** + **dispatch** needed to bind `learning-extract` after Gateflow fills orchestrator-owned fields. Minimum product fields: `initiative_id`, `wave_id`, `ticket_id`, `org`, `repo`, `pr_number` (or equivalent PR bind), absolute `workspace_path`, `runner`, `model_id`. Optional future fields only when a REQ lands — v1 body uses `extra="forbid"`. | Pin `learning-extract/prompts/schema.yaml`; ADR-007/010 | Missing required → 4xx; OpenAPI lists required set; undeclared keys rejected | unit |
| REQ-5 | **Bind contract:** after accept, packaged `learning-extract` hop must satisfy pin `schema.yaml` required variables. Gateflow owns `handoff_path` (baton create) and `skill_id=learning-extract`. Client/API supply `ticket`, `workspace`, and `initiative` (send even if schema marks initiative optional). Product REQs **cite** the pin schema path — they do not invent a parallel bind vocabulary. | ADR-007; pin schema; PE alignment | Bind miss → fail closed before AgentRunner; rendered brief contains required vars | unit |
| REQ-6 | Closeout applies to **both lanes**. Same route finishes an implement-lane or spec-lane wave PR tip. Spec-lane Pass-1 meta intake fields (`meta_pr_url`, `meta_workspace_path`) are **not** required on closeout unless a later REQ adds a documented need. | PE alignment | Unit: implement-shaped and spec-shaped prior context both accepted when PR+workspace+identity present | unit |
| REQ-7 | After enqueue, walker runs orchestrated Pass-2: `learning-extract` → (handoff `pass`) → `ground-spec` → stop at **`wave-signoff`** (`human-checkpoint`). Do **not** auto-dispatch manual `verify`. Pin `forge:` rules apply (`learning-extract` optional commit; `ground-spec` required) via existing ForgeClient path (ADR-009). | Pin CTR-P1/P2; forge-side-effects | Unit multi-hop + hop-cap; live: stages for both skills; terminal `stopped` at `wave-signoff` | unit + live verify |
| REQ-8 | `learning-extract` **handoff** is first-class: skill writes envelope `stage: learning-extract`; on `pass`, next is `ground-spec` with `human_checkpoint: false`; dual-write baton when `handoff_path` bound (ADR-008). Gateflow continues the walk from stored baton — ambient ingest remains non-SSOT. | Pin SKILL + handoff-envelope; ADR-008 | Unit: packaged ingest uses `read_path`; missing baton fail-closed | unit |
| REQ-9 | Persist structured learning in **PostgreSQL** as programme SSOT (ADR-001 global store — not git). Ingest from workspace artifact `{reports_dir}/Learning-Extract-{initiative}-W{N}.md` fenced `learning_extract:` YAML (and/or equivalent baton dual-write payload if TDD chooses). Human Alembic owns revisions; agent updates ORM schema only. | Pin CTR-P3/CTR-G1; ADR-001 | Unit: parse → rows; empty `items: []` with rationale allowed; malformed YAML fail-closed | unit |
| REQ-10 | Learning item model preserves pin taxonomy: ids `L-*`, classes `SPEC` \| `SKILL` \| `HARNESS` \| `ENV`, summary, evidence, codify hint, status `open` \| `codified`. Exact table/column shapes are TDD data-contract (CTR-G2). | Pin learning-extract taxonomy | Unit round-trip; reject unknown class | unit |
| REQ-11 | **Skill must not** HTTP POST to Gateflow (or write Postgres) as success criterion (pin H6). Ingest is worker/orchestrator-owned after the content hop (ordering vs forge publish follows ADR-009 when both apply). | Pin H6; for-gateflow.md | Inspection + unit: no skill success path calls closeout/learning APIs | unit + inspection |
| REQ-12 | Ground Report ownership unchanged: `/ground-spec` writes Ground Report + §Contracts; when Learning-Extract exists, report **cites** `L-*` and does not re-author learning SSOT. | Pin ground-spec SKILL; CTR-P3 | Inspection + live: Ground Report cites L-* when artifact present | live verify / inspection |
| REQ-13 | Optional `prior_run_id` (or equivalent) may be accepted to audit-link Pass-1 → Pass-2; it must **not** be required to resume walker state. PR bind remains authoritative for tip. | PE alignment | Unit: omit prior_run OK; invalid UUID → 4xx; no resume of prior stages | unit |
| REQ-14 | Live prove-it (**implement**): after Pass-1 stop at `live-verify` + human tip on PR, closeout start walks to `wave-signoff`; Learning-Extract artifact present; learning rows ingested; Ground Report on tip cites `L-*` when items non-empty. | Pin CTR-P2; product UX | `verify_wave_closeout` (or extend feature map) documents command + pass | live verify |
| REQ-15 | Live prove-it (**spec**) or documented parity: same closeout route finishes a spec-lane wave PR under the same REQs, or W2 records an explicit deferred deferral with PE accept — default is **both lanes in scope**. | PE alignment | Live or PE-waived deferral row in as-built | live verify / inspection |
| REQ-16 | Checkpoint id hygiene: Gateflow **runtime** must not hardcode retired pin ids `gate-1`, `gate-2`, `wave-human-decision` as live transitions. Prefer pin-resolved node ids (`prd-impact-acceptance`, `coding-readiness`, `wave-signoff`, `live-verify`). Historical reports may retain old names. | Pin breaking rename | Grep/unit: no live transition constants on old ids in `src/` | unit + inspection |
| REQ-17 | Update as-built + `tests/README.md` feature map for closeout start, learning ingest, and Pass-2 verify command when waves land. | SDD | Feature map row + as-built verification matrix | inspection |

> **Id convention:** `REQ-*` canonical. This INIT assigns **REQ-1…REQ-17**.
> Traceability is to the prayog-skills Pass-1/Pass-2 brief (CTR-P\*/CTR-G\*),
> remounted pin, and PE alignment until a meta PRD exists (see Spec questions).

**Inherited (unless superseded above):** INIT-001…006 control-plane, lane starts,
BOUNDINPUT, forge publish/authorize, Cursor AgentRunner, RunStore baton. Pass-1
stop at `live-verify` is **pin + as-built** (not re-specified here except as
prerequisite). This INIT **adds** closeout start and learning DB ingest.

**Explicit non-goals (may become later INITs):** authorize-then-resume from
`live-verify` / `wave-awaiting-closeout` into `learning-extract`; automatic
merge-webhook continuation; Mission Control learning UI; skill→API learning push.

## Negative and failure paths

| REQ | Condition | Required behavior | Evidence |
|-----|-----------|-------------------|----------|
| REQ-1 | Missing/invalid programme token | 401; 0 enqueue | unit |
| REQ-2 | Pin lacks orchestrated `learning-extract` | 4xx; 0 enqueue | unit |
| REQ-3 | Active concurrent run for same wave/PR | 409; 0 enqueue | unit |
| REQ-3 | PR missing / unreadable when accept requires forge resolve | Fail closed; 0 enqueue | unit |
| REQ-4 | Missing `workspace_path` / identity / PR bind | 4xx; 0 enqueue | unit |
| REQ-5 | Required prompt bind var empty after construction | Fail closed before AgentRunner | unit |
| REQ-7 | `learning-extract` handoff `findings` / `failed` | Stop or re-enter per pin; no silent skip of ground-spec | unit |
| REQ-9 | Malformed / missing `learning_extract:` fence when ingest required | Fail closed; stage/run records failure | unit |
| REQ-11 | Skill attempts Gateflow HTTP as success | Not part of happy path; ingest remains worker-owned | inspection |
| REQ-13 | `prior_run_id` that does not exist | 4xx; 0 enqueue | unit |

## Out of scope for this repo

- **Authorize → resume** walker (Pass-2 is always new Enter-at closeout start)
- **prayog-skills** package/pin authoring (consume remounted pin only)
- **prayog-meta** PRD authoring (Gate 1 follow-on; see Spec questions)
- Skill calling Gateflow HTTP/DB as success (H6)
- **gateflow-ops** / Mission Control UI for learning browse
- Second AgentRunner
- Inventing PE gate labels / writing `*-lgtm`
- Replacing Ground Report with Learning-Extract

## Cross-service contracts

| Contract ID | Provider / owner | Consumer / owner | Entry point | Input shape | Output shape | Invariants | Errors | Compatibility | Contract-test location |
|-------------|------------------|------------------|-------------|-------------|--------------|------------|--------|---------------|------------------------|
| CTR-01 | prayog-skills / PE | gateflow | Pin Pass-1/Pass-2 graph | `workflow.yaml` | Stop at `live-verify`; closeout Enter-at `learning-extract` → `ground-spec` → `wave-signoff` | No laptop overlay; `verify` manual | Invalid pin ⇒ fail closed | Active pin line | `test_handoff_workflow` |
| CTR-02 | prayog-skills / PE | gateflow | `learning-extract` package | `schema.yaml` + artifact template | MD + `learning_extract:` YAML + handoff | Taxonomy L-\*; no Gateflow HTTP success | Bind miss / bad artifact ⇒ fail closed | Pin bump | `test_prompt_resolver` + ingest unit |
| CTR-03 | gateflow / PE | programme callers | `POST /api/v1/waves/closeout/start` | identity + PR + workspace + runner/model | `run_id` / job accept | New run; fixed Enter-at; both lanes | 4xx/409; 0 enqueue | Additive body fields only | `test_wave_closeout` (planned) |
| CTR-04 | gateflow / PE | next waves / PE | Postgres learning rows | ingested YAML items | queryable L-\* SSOT | DB SSOT; reports emit-only | Ingest fail closed | TDD data contract | planned unit |
| CTR-05 | pin `ground-spec` | gateflow / humans | Ground Report on tip | cites Learning-Extract when present | Ground Report + §Contracts | Learning not re-authored in Ground | ground findings per pin | Pin skill | live verify / inspection |

Pin-facing obligations (consumer view of upstream brief): **CTR-P1** Pass-1 stop;
**CTR-P2** closeout Enter-at chain; **CTR-P3** learning package taxonomy — owned by
prayog-skills; Gateflow **CTR-G1/G2** = this INIT’s closeout trigger + learning DB
(+ bind map detail in TDD).

## Non-functional requirements

| Area | Requirement or N/A rationale | Acceptance / evidence |
|------|------------------------------|-----------------------|
| Security | Programme token on closeout start; secrets never committed; learning rows must not store raw secrets from evidence paths | unit + inspection |
| Reliability | Fail closed on accept/bind/ingest; FR-24 worker isolation retained; no resume of terminal Pass-1 runs | unit |
| Performance / capacity | N/A new SLAs — correctness of Pass-2 walk + ingest over throughput | inspection |
| Observability | Timeline stages for `learning-extract` / `ground-spec`; structured logs with `run_id`, `workflow_node`, `pr_number`, `initiative_id`, `wave_id` | unit + live |
| Privacy / data handling | Ticket/initiative/PR URLs may appear in briefs/logs — no secret materialization into learning YAML or commits | inspection |
| Migration / compatibility | Additive closeout API; learning tables additive Alembic (human-owned); checkpoint rename is pin-breaking for hardcoded ids only | inspection |
| Rollback / recovery | Disable closeout route / stop worker; runs + learning rows reconstructable from Postgres | runbook inspection |
| Operations / support | Document Pass-1 then closeout sequence in `tests/README.md`; PE owns pin; Gateflow eng owns runtime + ingest | docs |

## Assumptions

| ID | Assumption | Evidence | Owner | Status | Invalidated when |
|----|------------|----------|-------|--------|------------------|
| A-1 | Remounted pin Pass-1/Pass-2 graph remains SSOT (`live-verify` stop; closeout via `learning-extract`) | prayog-skills `workflow.yaml` + for-gateflow.md; #76 | PE | confirmed | Pin supersedes graph |
| A-2 | Closeout is a **named wave phase** with its own start route (not reuse of lane Pass-1 start) | PE alignment 2026-07-29 | PE | confirmed | Product merges into lane starts |
| A-3 | New run + PR bind is the Pass-2 model (no authorize-resume this slice) | Pin brief; PE alignment | PE | confirmed | Product mandates same-run resume |
| A-4 | Both lanes share one closeout route | PE alignment | PE | confirmed | Product splits implement/spec closeout bodies as mandatory |
| A-5 | Learning SSOT is Postgres; `reports/` is emit-only | ADR-001; pin H6; PE alignment | PE | confirmed | Product chooses git SSOT |
| A-6 | No new ADR required unless TDD finds a store/topology conflict | PE discussion | PE | confirmed | Learning store leaves Postgres or intake authority changes |
| A-7 | `wave-awaiting-closeout` needs no separate Gateflow mutate API in v1 — `stopped@live-verify` is sufficient precursor to closeout start | Pin park = status/UI; PE default | PE | open | Product requires explicit park-ack API |
| A-8 | Meta Gate 1 / PRD may follow engineering INIT (catch-up) | No meta PRD today | PE | open | Gate 1 lands with digests |
| A-9 | Plan §9 WorkManifest must satisfy pin `prayog/v1` (`workmanifest_contract.py`); `launchpad/v1` rejected fail-closed (INIT-008 W2) | Pin + Gateflow `run_workmanifest_contract`; pre-implement gate | PE | confirmed | Pin supersedes WorkManifest contract |

## Spec questions (ambiguities — need PE confirmation)

| ID | Lane | Question | Owner | Blocking | Required by | Default if deferred | Status | Resolution link |
|----|------|----------|-------|----------|-------------|---------------------|--------|-----------------|
| Q-1 | PE | Retrospective meta PRD + Impact-Map for INIT-GATEFLOW-007 (Gate 1) vs PE waive for pin-driven catch-up? | PE | yes for formal Gate 2 package | feasibility / board-seed | Draft INIT proceeds; thin meta PRD before `/board-seed` | open | — |
| Q-2 | PE | Exact closeout path confirmed as `/api/v1/waves/closeout/start`? | PE | no | TDD W0 | Use that path | **resolved** (PE alignment) | this spec REQ-1 |
| Q-3 | PE | Is explicit API to advance `live-verify` → `wave-awaiting-closeout` required in this INIT? | PE | no | W0/W1 | **No** — closeout start allowed after Pass-1 `stopped@live-verify` | open | A-7 |
| Q-4 | PE | Learning ingest trigger: immediately after `learning-extract` hop vs after `ground-spec`? | PE | no | TDD W1 | After successful `learning-extract` hop (publish-before-ingest if both apply) | open | — |
| Q-5 | PE | Require `prior_run_id` on closeout, or optional audit-only? | PE | no | TDD W0 | Optional (REQ-13) | open | — |
| Q-6 | PE | Spec-lane live prove-it in W2 vs implement-first + unit parity for spec? | PE | no | W2 | Both lanes in scope (REQ-15); implement live first if time-box | open | — |
| Q-7 | PE | Learning table shape / query API for ops — expose HTTP read in this INIT or DB-only? | PE | no | TDD W1 | DB + repository only; no public read API in 007 | open | — |

## Draft check summary (D1–D12)

| Check | Status | Evidence / findings |
|-------|--------|---------------------|
| D1 Approved handoff current | **FAIL / waived** | No meta PRD / Impact-Map / APPROVED head — Q-1; PE-directed from pin brief |
| D2 Complete PRD traceability | **PARTIAL** | Trace to pin CTR-P\*/G\* + PE alignment; CAP-* pending retrospective PRD |
| D3 Repo-bounded scope | PASS | gateflow-only; pin/meta called out as dependencies |
| D4 Observable acceptance | PASS | Each REQ has criteria + evidence type |
| D5 Negative/failure paths | PASS | Accept/bind/concurrency/ingest covered |
| D6 Assumptions/questions | PASS | A-1…A-8; Q-1…Q-7 with defaults |
| D7 Cross-repository contracts | PASS | CTR-01…05 + pin CTR-P/G mapping |
| D8 NFR applicability | PASS | Eight rows |
| D9 As-built alignment | PASS | Pass-1 remounted; closeout/learning not built |
| D10 Dependency order | PASS | W0 API/walk → W1 ingest → W2 prove-it |
| D11 Zero unresolved blockers | **PARTIAL** | Q-1 blocks formal Gate 2 package |
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
| Proposed branch | `chore/INIT-GATEFLOW-007-spec-gateflow` |
| Proposed base | `develop` |
| Proposed title | `[INIT-GATEFLOW-007] Spec — gateflow (wave closeout + learning DB)` |
| PR type | **Draft** |
| Files to commit | `docs/specification/product/INIT-GATEFLOW-007-gateflow.md`, `docs/specification/README.md`, `docs/specification/as-built/implementation-status.md` |
| Reviewer | @drivestream-lab/prayog-pe-team |
| Initial Gate 2 label | `spec-pending` (when Draft PR opened) |
| Blocking items | Q-1 Gate 1 / retrospective PRD |

**No GitHub side effects have occurred** in this drafting step. Present this
section before creating a Draft spec PR.

### Proposed Draft PR body

```markdown
## Initiative

INIT-GATEFLOW-007 — Wave closeout start + learning DB ingest (gateflow)

## Meta handoff

- Meta PRD / Impact-Map: **TBD** (Q-1 — retrospective Gate 1)
- Pin SSOT: Pass-1 `live-verify` stop; Pass-2 Enter-at `learning-extract`
- Architecture: ADR-001 / 005 / 007 / 008 / 009 / 010 (no new ADR by default)

## Spec path

`docs/specification/product/INIT-GATEFLOW-007-gateflow.md`

## Summary

- REQ-1…8: `POST /api/v1/waves/closeout/start`, fixed Enter-at `learning-extract`,
  new run + PR bind, both lanes, walk to `wave-signoff`
- REQ-9…13: Postgres learning SSOT from Learning-Extract YAML; no skill→API (H6)
- REQ-14…17: live prove-it, checkpoint hygiene, as-built
- Out of scope: authorize-resume; pin authoring; Mission Control UI

## Gate 2 — spec package readiness

Initial label: `spec-pending` (after Draft PR exists)

## Verify

N/A for spec-only PR — `make check` on docs; Pass-2 live verify in later waves
```

## Handoff envelope (draft artifact)

```yaml
handoff:
  schema_version: "1"
  skill_id: spec-draft
  initiative: INIT-GATEFLOW-007
  outcome: pass
  artifact:
    path: docs/specification/product/INIT-GATEFLOW-007-gateflow.md
  notes:
    - PE-directed INIT from prayog-skills Pass-1/Pass-2 brief
    - Closeout route separate from lane Pass-1 starts; fixed Enter-at learning-extract
    - Learning SSOT = Postgres; skill emits artifact + handoff only
    - Gate 1 TBD (Q-1)
  forge:
    action: open_draft_pr
    title: "[INIT-GATEFLOW-007] Spec — gateflow (wave closeout + learning DB)"
    body_path: docs/specification/product/INIT-GATEFLOW-007-gateflow.md
    draft: true
    # apply_labels from pin/Launchpad only when publishing — e.g. spec-pending
```
