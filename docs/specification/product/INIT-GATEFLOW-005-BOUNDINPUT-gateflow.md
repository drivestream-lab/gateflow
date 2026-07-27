# INIT-GATEFLOW-005-BOUNDINPUT — spec slice for gateflow

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-005-BOUNDINPUT |
| PRD | `prayog-meta/prd/INIT-GATEFLOW-005-BOUNDINPUT.md` |
| PRD digest | `sha256:40fb856dd5068290c1d14f010239e6206bee2625aaf6a6e3970d769e9bb5e970` |
| Meta PR | https://github.com/drivestream-lab/prayog-meta/pull/16 |
| Meta PR approved head | `0b6b11e4470517842affb894d7ea581c3819ead3` |
| Impact map | `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-005-BOUNDINPUT.md` |
| Impact-map revision | `1` |
| Repo scope digest | `sha256:2cc5e2151451c47b973fdc86dafe19d5cb2fadd651212a5a00f9d681f274039b` |
| Tech-lead approval | Review `4788143334` by `0xbeefdead`, APPROVED at `2026-07-27T14:31:41Z`; `commit_id` = approved head (map_revision 1 attestation); https://github.com/drivestream-lab/prayog-meta/pull/16#pullrequestreview-4788143334 |
| Repo | drivestream-lab/gateflow |
| Date | 2026-07-27 |
| Status | Draft — dev review required before committing |

## Overview

This repo delivers the **bound-input skill invocation** substrate on the delivered
INIT-GATEFLOW-001 / 002 / 003 control plane: resolve the skill’s prompt package
from the active prayog-skills pin (`prompts/template.md` + `schema.yaml`), bind
known context from wave-start plus Gateflow-owned `run.handoff_path`, validate
and render simple `{{var}}` substitution, dispatch **only** the rendered message
through Cursor AgentRunner (remove Gateflow invent-prose), persist
`prompt_id` / `prompt_revision` / runner / model on the stage, and ingest handoff
**only** from the stored `run.handoff_path`.

**Out of scope for this repo:** authoring/revising prompt packages
(**prayog-skills** — already delivered under INIT-PRAYOG-SKILLS-003-PROMPTS);
changing `dispatch` eligibility (**prayog-skills** / INIT-002); gateflow-ops UI;
Launchpad product features; second AgentRunner (OpenCode / Claude Code);
worktree-per-run as exit criterion; SaaS prompt registry; template engines beyond
`{{var}}`; rewriting PolicyEngine / pin walker architecture.

**As-built baseline (INIT-001…003 W1 human_approved):** API wave-start, pin walker
until gate, live Cursor AgentRunner (`cursor-sdk`), RunStore stages with
runner/model, ambient `HandoffReader` glob/mtime ingest
(`DEFAULT_ARTIFACT_GLOBS`), and Gateflow-owned invent-prose in
`CursorAgentRunner._build_prompt`. **Missing for this INIT:** pin prompt resolve /
render, required ticket bind, thin message-only dispatch, stage `prompt_id` /
`prompt_revision`, RunStore `handoff_path`, ingest-from-stored-path.

**Delivery waves (product-normative; plan may refine):**

| Wave | Intent | Exit REQs |
|------|--------|-----------|
| **W0** | Resolve + bind + validate/render + thin Cursor + persist ids + define/store `handoff_path` + strip invent-prose + one automated hop | REQ-1…REQ-7, REQ-8a, REQ-9, REQ-10 |
| **W1** | Ingest only from stored `handoff_path`; dual-run isolation | REQ-8b (+ harden fail-closed) |
| **W2** | Broaden orchestrated packaged skills / dogfood under then-current pin policy | Multi-skill evidence |

## Functional requirements

| ID | Requirement | PRD source | Acceptance criteria | Evidence type |
|----|-------------|-----------|---------------------|---------------|
| REQ-1 | Resolve the skill prompt package from the **active pin** for every automated packaged-skill dispatch: load `prompts/template.md` + `prompts/schema.yaml` per INIT-PRAYOG-SKILLS-003-PROMPTS layout for the skill under the pin tree consumed by Gateflow (`.harness-pin.yaml` / synced harness). Missing or unreadable package → fail closed before AgentRunner. | PRD REQ-1, US-2; §4 Normative consumer flow; Success Criteria Pin SSOT | Packaged automated skill ⇒ package loaded from pin path for that skill id; missing/invalid package ⇒ run/stage failure recorded; **0** AgentRunner calls | unit + integration |
| REQ-2 | Bind inputs from wave-start + run record into the shared dictionary: `ticket` (required), `initiative` (optional → `""`), `skill_id` (resolved automated skill), `workspace` (run worker workspace root), `handoff_path` (stored run field from REQ-8a). Wave-start remains the known-context entry; programme service token auth unchanged (inherit INIT-001). | PRD REQ-2, US-1, §4.4 Bound-input mapping | Successful bind map contains all five names; missing required `ticket` ⇒ fail closed (REQ-9); `initiative` omitted ⇒ empty string at render; `handoff_path` equals stored run value | unit |
| REQ-3 | Validate the bound map against pin `schema.yaml` variables (required/optional per INIT-003). Required miss → fail closed; optional omit → empty string at render. | PRD REQ-3; Error Handling | Invalid/missing required schema var ⇒ no AgentRunner; optional absent ⇒ `""` in render | unit |
| REQ-4 | Render **simple `{{var}}` substitution only** — no filters, conditionals, or template engines. Every template placeholder must be declared in `schema.yaml`. | PRD REQ-4; Non-Goals | Render output is pure substitution of declared vars; undeclared template var or engine feature ⇒ fail closed before dispatch | unit |
| REQ-5 | AgentRunner message body **equals** render output only. **Remove** Gateflow-owned invent-prose paths (as-built: `CursorAgentRunner._build_prompt` skill brief + durable-handoff instructions). Anti-hardcode: tests fail if a Gateflow-authored brief is used when a pin package exists. Missing/invalid package must not fall back to a stub brief. | PRD REQ-5, US-4; Success Criteria No invent-prose | Automated packaged-skill path: message == render; invent-prose helpers unused/removed on that path; anti-hardcode unit fails on regression | unit + inspection |
| REQ-6 | Persist `prompt_id` and `prompt_revision` on every automated packaged-skill stage/outcome; values match the resolved package (`schema.yaml` `prompt_id` + `revision`). | PRD REQ-6, US-2; Success Criteria Traceability | 100% successful automated packaged-skill stages have both fields; values equal resolved package | unit + live verify |
| REQ-7 | Persist `runner` + `model_id` on every automated packaged-skill stage (already partially as-built). `model_profile` / `model_provider` optional — omit or null if adapter does not return them. | PRD REQ-7 | Stage row always has `runner` + `model_id` for automated packaged-skill stages; optional fields null-safe | unit |
| REQ-8a | At run create/continue, Gateflow **defines** and **persists** `handoff_path` on the run record (RunStore SSOT). Value is independent of repo document trees / skill folder conventions. Inject stored value into the bind map as `handoff_path`. **W0.** | PRD REQ-8a, US-3; §4.4 handoff_path rules 1–3 | Every automated run has non-empty stored `handoff_path` before dispatch; bind uses that value; unset when required ⇒ fail closed | unit |
| REQ-8b | Post-agent handoff ingest reads **only** `run.handoff_path`. Ambient repo globs / mtime discovery (`HandoffReader.find_latest_handoff` / `DEFAULT_ARTIFACT_GLOBS` / INIT-001 `handoff.artifact_globs`) are **not** SSOT for packaged-skill automated ingest. Two concurrent runs must not ingest each other’s baton via shared layout. **W1.** Narrow supersession of INIT-001 ambient ingest for packaged-skill automated runs only — no formal INIT-001 PRD amendment. | PRD REQ-8b, US-3; Decision #11; Error Handling | Ingest opens stored path only; missing/unreadable → fail closed, no ambient advance; dual-run fixture isolates batons | unit + integration |
| REQ-9 | Fail closed **before** AgentRunner on package/schema/bind/`handoff_path` failures; record failure reason on the run; never invent an alternate brief. Inherit concurrent active-run reject (HTTP 409) and programme-token auth reject from INIT-001 / WaveStartService. | PRD REQ-9; Error Handling; Success Criteria Fail closed | Named failure cases ⇒ 0 AgentRunner calls; reason persisted; 409 on concurrent automate | unit |
| REQ-10 | Prove-it: ≥1 live Cursor automated hop using a pinned prompt package for **any** skill with `dispatch: orchestrated` on the active pin. Substrate must work for any packaged skill Gateflow automates under then-current policy (not a hardcoded skill allowlist). Concrete skill id chosen at W0 among pin-orchestrated packaged skills (today: implement-lane set; TDD default `pre-implement`). | PRD REQ-10, US-1; A7; Phased Rollout W0 | Live hop records prompt ids + thin message path; skill id documented in ground/verify evidence; no PolicyEngine skill allowlist added | live verify — extend `tests/verify/verify_implement_lane.py` (assert stage `prompt_id` / `prompt_revision`) |

> **Id convention:** `REQ-*` is canonical (`prayog-skills/references/id-conventions.md`).
> Legacy display alias `FR-{n}` ≡ `REQ-{n}` (same number). This INIT’s product ids are
> **REQ-1…REQ-10** (incl. REQ-8a / REQ-8b) as assigned in the PRD — do not invent
> wave-scoped `REQ-W*` ids.

**Inherited (unless superseded above):** INIT-GATEFLOW-001 / 002 / 003 control-plane
REQs remain in force (wave-start, pin walker, live Cursor, metrics, board,
ForgeClient, programme token, fail-closed adapter registry). This INIT **narrowly
supersedes** ambient glob/mtime handoff ingest for **packaged-skill automated
runs** (REQ-8b). PolicyEngine / `dispatch` eligibility rules are unchanged
(orthogonal — INIT-PRAYOG-SKILLS-002).

## Negative and failure paths

| REQ | Condition | Required behavior | Evidence |
|-----|-----------|-------------------|----------|
| REQ-1 / REQ-9 | Prompt package missing or unreadable on pin | Fail closed; record reason; 0 AgentRunner | unit |
| REQ-3 / REQ-9 | `schema.yaml` invalid or required var missing | Fail closed; 0 AgentRunner | unit |
| REQ-2 / REQ-9 | Required bind `ticket` missing | Fail closed; 0 AgentRunner | unit |
| REQ-4 / REQ-9 | Template uses undeclared var / non-`{{var}}` feature | Fail closed; 0 AgentRunner | unit |
| REQ-8a / REQ-9 | `run.handoff_path` unset when automate requires it | Fail closed; 0 AgentRunner | unit |
| REQ-8b | Handoff missing/unreadable at stored `run.handoff_path` | Fail closed on ingest; do not advance via ambient glob/mtime | unit + integration |
| REQ-5 | Residual invent-prose path invoked when package exists | Must not be success path; anti-hardcode test fails | unit |
| REQ-9 | AgentRunner failure/timeout/crash | Stop stage; record failure; do not invent alternate brief; no dishonest advance | unit (inherit 003) |
| REQ-9 | Wave-start auth reject | Fail closed; record reason; 0 AgentRunner | unit (inherit) |
| REQ-9 | Concurrent automate while active run exists | HTTP 409 Conflict / fail closed; record reason | unit (inherit) |
| REQ-8b | Two concurrent runs share workspace tree | Ingest for run A never reads run B’s baton | integration |
| — | Human manual skill execution | Out of scope — may freeform (INIT-003) | N/A |

## Out of scope for this repo

- **prayog-skills** prompt package authoring / revision / eval-before-promote (delivered INIT-003)
- **prayog-skills** `dispatch` enum or eligibility changes (INIT-PRAYOG-SKILLS-002)
- **gateflow-ops** / Mission Control UI (impact-map not affected)
- **launchpad** product features (harness sync consume only)
- Second AgentRunner (OpenCode / Claude Code / …) — Cursor only
- Worktree-per-run as exit criterion
- Repo-relative handoff discovery as SSOT
- Template engines beyond simple `{{var}}`
- Rewriting PolicyEngine / pin walker architecture
- SaaS prompt registry
- Formal INIT-GATEFLOW-001 PRD amendment (narrow supersession documented in this INIT only)
- Requiring humans to use packages

## Cross-service contracts

| Contract ID | Provider / owner | Consumer / owner | Entry point | Input shape | Output shape | Invariants | Errors | Compatibility / versioning | Contract-test location |
|-------------|------------------|------------------|-------------|-------------|--------------|------------|--------|----------------------------|------------------------|
| CTR-01 | prayog-skills / prayog-pe-team | gateflow / prayog-pe-team | Active pin skill tree `prompts/template.md` + `prompts/schema.yaml` (INIT-003 package layout) | skill id + pin ref | `prompt_id`, `revision`, template text, variable schema | Pin is SSOT for automated brief; Gateflow does not author packages; bumping evaluated revision applies without Gateflow code change | Missing/invalid package ⇒ fail closed before AgentRunner | Consume now (was deferred on INIT-003 map); pin tag/promote | Planned: unit fixtures from pin packages + W0 live hop |
| CTR-02 | gateflow / prayog-pe-team | gateflow (worker / orchestrator) | Wave-start known-context bind + RunStore `handoff_path` define/store/ingest (REQ-2, REQ-8a, REQ-8b) | wave-start fields + run id | Bound map + stored path + ingest envelope | `handoff_path` Gateflow-owned; ingest uses stored path only; no ambient SSOT for packaged-skill automate | Unset/unreadable path ⇒ fail closed | **new** internal baton contract | Planned: unit + dual-run isolation (W1) |

Inherited cross-repo contracts from INIT-003 (Cursor SDK AgentRunner, ForgeClient,
Launchpad harness sync, run/metrics APIs) remain in force and are not re-specified
here except where REQ-5 changes the AgentRunner **message** source to pin render.

## Non-functional requirements

| Area | Requirement or N/A rationale | Acceptance / evidence |
|------|------------------------------|-----------------------|
| Security | Programme service token for wave-start/status unchanged (inherit INIT-001). Fail closed on package/bind failures — never dispatch on invalid input. Per-run `handoff_path` isolation — no cross-run ambient discovery. Prompt packages are not a secret store; existing Cursor credential handling unchanged (REQ-29 inherit). | unit + inspection |
| Reliability | Fail closed before AgentRunner (REQ-9); ingest fail closed (REQ-8b); concurrent active-run 409 unchanged; AgentRunner failure does not invent briefs. | unit + integration |
| Performance / capacity | N/A for new capacity targets this INIT — substrate correctness over throughput SLAs; hop cap / existing orchestration limits unchanged. | inspection |
| Observability | Persist `prompt_id` + `prompt_revision` + runner/model on stages (REQ-6/7); structured loguru logging with correlation; failure reasons on run/stage. | unit + live verify |
| Privacy / data handling | Ticket/initiative bind values may appear in rendered messages and logs — treat as programme operational data; do not log full secrets; no cross-run handoff leakage. | inspection |
| Migration / compatibility | Additive RunStore fields (`handoff_path`, stage prompt ids) via human-owned Alembic; narrow supersession of ambient ingest for packaged-skill automate only; pin consumer compatible with INIT-003 packages on current pin line (`v0.5.0-rc.2`). | inspection + migration review |
| Rollback / recovery | Disable automate / withhold pin packages / stop worker to halt packaged-skill path; runs reconstructable from Postgres; do not re-enable invent-prose as success path. | runbook inspection |
| Operations / support | Document wave-start required bind fields, `handoff_path` ownership, and prove-it skill choice; PE owns pin promote; Gateflow eng owns runtime. | docs + verify |

## Assumptions

| ID | Assumption | Evidence | Owner | Status | Invalidated when |
|----|------------|----------|-------|--------|------------------|
| A-1 | Upstream prompt packages delivered (INIT-PRAYOG-SKILLS-003-PROMPTS) on consumable pin | PRD A1; meta PR #14 merged; local pin `v0.5.0-rc.2` has packages for implement-lane skills | PE | confirmed | Pin lacks packages for target skill |
| A-2 | Bound context enters via wave-start API | PRD A2 User-confirmed | PE | confirmed | Product moves bind to another surface |
| A-3 | `ticket`, `initiative`, `skill_id`, `workspace` are already known at automate time | PRD A3 / §4.4 | PE | confirmed | Required known field unavailable |
| A-4 | Gateflow defines + stores `handoff_path`; not repo-owned | PRD A4 User-confirmed | PE | confirmed | Product reassigns ownership to repos |
| A-5 | Remove Gateflow invent-prose; pin template is automated brief SSOT | PRD A5 | PE | confirmed | Product allows Gateflow briefs again |
| A-6 | Impact map is gateflow-only | PRD A6; map rev 1 | PE | confirmed | Map adds other repos |
| A-7 | Prove-it = any `dispatch: orchestrated` packaged skill on active pin; substrate for any packaged skill | PRD A7 | PE | confirmed | Product hardcodes a single skill forever |
| A-8 | Second runner out of scope | PRD A8 | PE | confirmed | Product mandates second runner |
| A-9 | Worktree-per-run is not an exit criterion | PRD A9 | PE | confirmed | Product makes worktree mandatory exit |
| A-10 | ADR-001 dual API+worker + Postgres RunStore and ADR-006 fail-closed registry remain topology/selection rules | Accepted ADRs | Eng | confirmed | ADR superseded |

## Spec questions (ambiguities — need PM or domain confirmation before feasibility)

| ID | Lane | Question | Owner | Blocking | Required by | Default if deferred | Status | Resolution link |
|----|------|----------|-------|----------|-------------|---------------------|--------|-----------------|
| Q-1 | PE | Wave-start JSON field for required bind `ticket`: reuse optional as-built `ticket_id` (make required on automate) vs add `ticket` alias? PRD §4.4 / open item #1 | PE | no | feasibility / W0 | Map bind `ticket` ← wave-start `ticket_id`; require non-empty `ticket_id` for packaged-skill automate | resolved | TDD §3.3 / §9 |
| Q-2 | PE | Exact RunStore column/event field names for `handoff_path`, `prompt_id`, `prompt_revision` (run vs stage vs event payload)? PRD open item #2 | PE | no | technical review / W0 | `runs.handoff_path`; `stages.prompt_id` + `stages.prompt_revision` | resolved | TDD §3.5 / §9 |
| Q-3 | PE | Concrete `handoff_path` representation (workspace-relative file path vs absolute path vs internal URI / blob key)? Ownership stays Gateflow. PRD §4.4 rule 6 / open item #3 | PE | no | technical review / W0 | `{workspace}/.gateflow/runs/{run_id}/handoff.md` absolute (TDD §3.4); authority = ADR-008 | resolved | TDD §3.4 / ADR-008 |
| Q-4 | PE | Prove-it skill id among pin `dispatch: orchestrated` packaged skills (today: `pre-implement`, `loop-spec`, `verify`, `ground-spec`)? PRD REQ-10 / open item #4 | PE | no | W0 | `pre-implement` (first implement-lane orchestrated node; package present on pin) | resolved | TDD §9 / §5 — `verify_implement_lane` |

## Draft check summary (D1–D12)

| Check | Status | Evidence / findings |
|-------|--------|---------------------|
| D1 Approved handoff current | PASS | Meta PR #16 head `0b6b11e4470517842affb894d7ea581c3819ead3` = APPROVED review `4788143334` `commit_id`; map_revision 1 attestation; PRD digest `sha256:40fb856d…e970` matches file sha256; label `impact-map-lgtm`; gateflow affected with scope digest `sha256:2cc5e215…039b`; not deferred/blocked |
| D2 Complete PRD traceability | PASS | PRD REQ-1…REQ-10 (8a/8b), US-1…US-4, §4.4, Error Handling, Success Criteria, Decisions #1–13, A1–A9 mapped to spec REQs |
| D3 Repo-bounded scope | PASS | Matches impact-map gateflow-only scope digest; skills/ops/launchpad/meta out of delivery called out |
| D4 Observable acceptance | PASS | Each REQ has observable criteria + evidence type |
| D5 Negative/failure paths | PASS | Package/schema/bind/path/auth/concurrent/AgentRunner/isolation covered |
| D6 Assumptions/questions | PASS | A-1…A-10 with status; Q-1…Q-4 non-blocking with defaults |
| D7 Cross-repository contracts | PASS | CTR-01 (pin packages) + CTR-02 (Gateflow baton); inherited 003 contracts noted |
| D8 NFR applicability | PASS | All eight NFR rows populated |
| D9 As-built alignment | PASS | Overview distinguishes invent-prose + ambient ingest (live) vs pin render + stored-path ingest (new) |
| D10 Dependency order | PASS | Aligns with map §7: skills packages delivered → Gate 1 → gateflow W0 → W1 → W2 |
| D11 Zero unresolved blockers | PASS | No blocking questions; Q-1…Q-4 have safe defaults |
| D12 Output completeness | PASS | Header, REQ/NFR/contracts/questions, D-summary, PR readiness, handoff envelope present |

**Draft verdict:** PASS

Do not advance to `/initiative-feasibility` unless the verdict is PASS and the
developer review below is complete.

## PR readiness handoff

| Item | Value |
|------|-------|
| Verdict | PR READY |
| Existing spec PR | none |
| Proposed branch | `chore/INIT-GATEFLOW-005-BOUNDINPUT-spec-gateflow` |
| Proposed base | `develop` |
| Proposed title | `[INIT-GATEFLOW-005-BOUNDINPUT] Spec — gateflow` |
| PR type | **Draft** (entire spec lifecycle) |
| Files to commit | `docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md`, `docs/specification/README.md` |
| Reviewer | @drivestream-lab/prayog-pe-team |
| Initial Gate 2 label | `spec-pending` |
| Additional invalidation label | none |
| Blocking items | none |

**No GitHub side effects have occurred.** The agent must present this section in
chat and ask whether to create or update the Draft spec PR. Continue only after
explicit authorization.

### Proposed Draft PR body

```markdown
## Initiative

INIT-GATEFLOW-005-BOUNDINPUT — Bound-input skill invocation (gateflow only)

## Meta handoff

- Meta PRD PR: https://github.com/drivestream-lab/prayog-meta/pull/16
- Approved meta head: `0b6b11e4470517842affb894d7ea581c3819ead3`
- Impact-map revision: 1
- PRD digest: `sha256:40fb856dd5068290c1d14f010239e6206bee2625aaf6a6e3970d769e9bb5e970`
- Repo scope digest: `sha256:2cc5e2151451c47b973fdc86dafe19d5cb2fadd651212a5a00f9d681f274039b`

## Spec path

`docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md`

## Summary

- 11 REQ rows (REQ-1…REQ-7, REQ-8a, REQ-8b, REQ-9, REQ-10) for pin resolve/bind/render, thin Cursor dispatch, prompt+runner telemetry, Gateflow-owned handoff_path define/store/ingest, fail closed, prove-it
- Open engineering questions (non-blocking): Q-1…Q-4 (field names, path representation, prove-it skill id) with defaults

## Gate 2 — spec package readiness

Initial label: `spec-pending`

- [ ] Spec slice committed on this PR head
- [ ] Feasibility report (later commit)
- [ ] Technical design + ADRs (later commit)
- [ ] Implementation plan §9 (later commit)
- [ ] PE sets `spec-lgtm` on exact final head before merge

Requested reviewer: @drivestream-lab/prayog-pe-team
```

## Developer review

- [ ] Scope matches the approved impact-map repo scope digest
- [ ] FRs and acceptance criteria are complete
- [ ] Contracts and NFR applicability are explicit
- [ ] No blocking question remains
- [ ] Developer confirmed draft is ready for feasibility

## After Draft PR creation

PE controls Gate 2 labels on the spec PR. Never infer approval from labels
alone — `spec-lgtm` requires matching artifacts on the exact PR head.

Provision labels before PR creation when missing:

```bash
launchpad apply-gates --repo gateflow --apply
```

| PE action | Remove | Add |
|-----------|--------|-----|
| Pending/new revision | `spec-lgtm`, `spec-blocked` | `spec-pending` |
| Request changes/hold | `spec-pending`, `spec-lgtm` | `spec-blocked` |
| Approve full package | `spec-pending`, `spec-blocked`, `spec-revised`, `spec-stale` | `spec-lgtm` |

## References

- PRD: `prayog-meta/prd/INIT-GATEFLOW-005-BOUNDINPUT.md`
- Meta PRD PR: https://github.com/drivestream-lab/prayog-meta/pull/16
- Spec PR: pending
- Service profile: not present (`docs/specification/product/00-service-profile.md`)
- Predecessor specs: `docs/specification/product/INIT-GATEFLOW-001-gateflow.md`, `docs/specification/product/INIT-GATEFLOW-002-gateflow.md`, `docs/specification/product/INIT-GATEFLOW-003-gateflow.md`
- As-built: `docs/specification/as-built/implementation-status.md`
- ADRs: `docs/specification/adr/` (ADR-001…ADR-006 Accepted; handoff_path storage may need follow-on ADR in technical review)
- Upstream packages: INIT-PRAYOG-SKILLS-003-PROMPTS (delivered)

---

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: spec-draft
  outcome: pass
  artifact:
    path: docs/specification/product/INIT-GATEFLOW-005-BOUNDINPUT-gateflow.md
    digest: sha256:3e591fa02e379ac17769bdbfede8ee271c12036a8da62509ba8c5a1396633cfb
  blockers: []
  signals:
    pr_ready: true
    draft_verdict: PASS
    meta_pr: https://github.com/drivestream-lab/prayog-meta/pull/16
    meta_pr_head_sha: 0b6b11e4470517842affb894d7ea581c3819ead3
    map_revision: 1
    prd_digest: sha256:40fb856dd5068290c1d14f010239e6206bee2625aaf6a6e3970d769e9bb5e970
    scope_digest: sha256:2cc5e2151451c47b973fdc86dafe19d5cb2fadd651212a5a00f9d681f274039b
    gate1_label: impact-map-lgtm
    open_questions: Q-1,Q-2,Q-3,Q-4
  next_candidates:
    - initiative-feasibility
  human_checkpoint: true
  external_action: true
```
