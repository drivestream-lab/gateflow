# ADR-009 — Pin ``forge:`` publish/mutate authority

| Field | Value |
|-------|-------|
| Status | Accepted |
| Initiative | INIT-GATEFLOW-006; amended by INIT-GATEFLOW-008 (006A) |
| Feasibility finding | FF-01 |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-008.md` |
| Source spec | `docs/specification/product/INIT-GATEFLOW-008-gateflow.md` |
| product_constraints | `[REQ-4, REQ-5, REQ-6, REQ-7, REQ-8, REQ-9, REQ-10, REQ-12]` |
| changes_user_visible_behavior | `false` |
| spec_amendment_required | `false` |
| supersedes | none |
| superseded_by | none |
| Relates to | Extends ADR-003 (ForgeClient in infra; orchestration in business); pin contract narrative in `prayog-skills/references/forge-side-effects.md` |
| Decision owner | @nikd10x / @drivestream-lab/prayog-pe-team |
| Approval evidence | Original: Explicit PE acceptance 2026-07-28 (INIT-006). **Dual-authorization amendment:** Explicit PE Accept 2026-07-30 via Cursor chat on Draft spec PR #91 (yes to amend ADR-009; ensure_branch-only; pin WorkManifest subprocess; W0 unit-test fix) |
| Approved head | Original `03e72600394c2b0e1fcb7cfebcf9e2a6b3ad44b8`; amendment head recorded on acceptance publish tip |
| Amendment | Dual pin `authorization` (`explicit` \| `automated`) — Recommendation §2 + Consequences; **Accepted** with INIT-GATEFLOW-008 TDD |

## Product decisions excluded

- Which pin nodes are day-one `automated` vs `explicit` — owned by pin + approved REQ-2 / REQ-8 / REQ-12 / REQ-15
- Exact HTTP mount strings and programme token catalogue — ADR-005 / TDD
- WorkManifest schema fields beyond “pin validator is SSOT” — pin contract + REQ-13…15

## Context

**ADR-003** places outbound forge HTTP in **infra** (ForgeClient) and run/workflow
orchestration in **business**. Upstream pin contracts declare per-node ``forge:``
policy for (a) workspace publish after content hops and (b) forge *actions* on
external-action nodes.

Automated packaged-skill runs can leave durable artifacts on the worker
workspace while the remote run head stays empty. Gateflow must decide
**authority** for automated forge mutations.

The original Accepted text required an **explicit authorization** step before
every external-action mutate. The remounted pin (INIT-GATEFLOW-008 / brand 006A)
introduces required node field **`authorization: explicit | automated`** and
places implement Pass-1 Draft PR open **after** coding (`wave-pr-action`).
Approved product REQs REQ-4/REQ-6/REQ-7/REQ-8 bind Gateflow to consume that
dual mode without inventing env backdoors.

This ADR decides:

1. Who is SSOT for forge *policy* after a hop — pin vs handoff
2. Who performs mutations — Cursor-dispatched forge skills vs ForgeClient
3. How external-action mutate is gated when pin declares `authorization`
4. How the remote ref for workspace publish (and `open_draft_pr` head/base) is bound
5. The *class* of path filter for workspace publish (not concrete path lists)

Product catalogues (skill ids, lane names, HTTP mounts, event type strings,
artifact schemas, comment UX, wave delivery slices) remain in INIT / TDD /
pin / as-built — this ADR does **not** catalogue them (same stance as ADR-007 /
ADR-008).

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — Agent push / forge CLI during the content skill hop | No orchestrator forge path | Non-deterministic; secrets risk; empty remote head still common |
| B — Cursor-dispatch forge skills as workflow graph nodes | Reuses human skill docs | Pin forbids forge skills as outcomes; conflates content vs mutate; dual auth confusion |
| C — Pin ``forge:`` is policy SSOT; business applies via ForgeClient; **all** EA mutates need interactive/programme authorize | Deterministic; original INIT-006 | Contradicts remounted pin `automated` nodes; empty early PRs if PR-at-start retained |
| D — **Pin ``forge:`` + pin `authorization` SSOT; ForgeClient for both modes; `explicit` STOP+authorize; `automated` apply when requires complete (no interactive STOP)** | Matches pin algorithm; keeps content ≠ mutate; fail-closed | Orchestrator must branch on authorization; ADR text must supersede “always explicit” consequence |

## Recommendation

**Option D** (extends original Option C with dual `authorization`).

1. **Pin is policy SSOT.** Absent skill-node ``forge`` means workspace publish is
   **disabled**. Handoff may carry **instance** slots only; it does **not**
   override pin policy. Policy/instance conflicts fail closed.
2. **Orchestrator never Cursor-dispatches forge skills.** After a successful
   content hop, business applies pin workspace-publish policy via **ForgeClient**.
   For the next node when it is `type: external-action`:
   - Parse required pin field **`authorization`**: only **`explicit`** or
     **`automated`**. Missing or unknown → **fail closed** (no schema default).
   - Merge pin ⋉ handoff for action slots; if any pin `forge.requires` slot is
     missing → **fail closed**.
   - **`authorization: explicit`** — STOP with pending forge; mutate only via
     human forge skill **or** programme-authorized control-plane path
     (`POST …/forge/authorize` with `authorized=true`) — dual executor retained
     (ADR-005 catalogue unchanged for this path).
   - **`authorization: automated`** — **no** interactive STOP and **no**
     `/forge/authorize` requirement for that hop. ForgeClient.apply runs in the
     orchestrator path when requires are complete, then the walker continues on
     the node’s `outcomes.pass` edge.
   - No env or API flag may reinterpret `explicit` as automated.
3. **Head binding** for workspace publish and for `open_draft_pr` `head_ref` /
   `base_ref` (when listed in pin `requires`) comes from **run context** already
   owned by the run job. Do **not** invent pin `forge.head` enums. Handoff
   supplies instance slots such as `title` / `body_path`.
4. **Path include class** for workspace publish: repository ignore semantics
   plus a hard secret denylist, excluding run-scoped handoff batons.
   Allowlist-first packaging needs a superseding decision.
5. **Ordering:** when workspace publish and handoff ingest both apply on the
   same hop, publish **before** ingest so required empty publish fails closed
   without advancing on a half-published tree. Automated or explicit
   `open_draft_pr` must not skip a required empty `commit_workspace` on the
   preceding content hop.
6. **Publish policy class:** optional + nothing to publish → continue;
   required + nothing to publish → fail closed; publish I/O failure → fail
   closed. Concrete enums and node wiring are pin / TDD.
7. **Draft PR creation timing (product REQ-10):** Implement (and automated
   spec) jobs must **not** create Draft PRs as a side-effect of job start
   (“PR-at-start”). Optional **ensure_branch-only** from the run base before
   the first publish is allowed. PR create/update is only via Forge action
   `open_draft_pr` on the pin’s `wave-pr-action` / `spec-pr-action` (or
   explicit authorize for other nodes). Exact ensure_branch call sites are TDD.

## Consequences

- Content-skill success remains separable from forge mutate success.
- Automated publish/mutate remains deterministic and testable without an agent SDK.
- Infra ForgeClient remains the production mutate transport (ADR-003); business
  owns *when* to call it from pin policy **and** pin `authorization`.
- Completing a content hop must **not** silently perform **`explicit`**
  external-action mutates; those still require the authorize path.
- Completing a content hop **may** immediately perform **`automated`**
  external-action mutates when requires are complete — this **supersedes** the
  prior consequence that *all* external-action mutates require explicit
  authorization. INIT-GATEFLOW-006 REQ-7 (“always STOP until authorize”) is
  superseded for `automated` nodes only (product REQ-4 / as-built note).
- “All `external-action` ⇒ STOP” is **not** a valid Gateflow hard rule; policy
  must branch on `authorization`.

## Revisit triggers

- Workers span hosts without a shared workspace filesystem for publish trees.
- Product requires allowlist-first path packages instead of ignore + denylist.
- PE requires forge skills on the workflow graph as first-class outcomes.
- Pin adds merge / auto-merge Forge actions (out of scope for this amendment).
- A superseding ADR changes publish/mutate authority or invents a third
  authorization mode.
