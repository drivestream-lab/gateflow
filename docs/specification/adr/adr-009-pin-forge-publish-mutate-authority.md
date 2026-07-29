# ADR-009 — Pin ``forge:`` publish/mutate authority

| Field | Value |
|-------|-------|
| Status | Accepted |
| Initiative | INIT-GATEFLOW-006 |
| Relates to | Extends ADR-003 (ForgeClient in infra; orchestration in business); pin contract narrative in `prayog-skills/references/forge-side-effects.md` |
| Decision owner | @nikd10x |
| Approval evidence | Explicit PE acceptance directed on 2026-07-28 via Cursor chat (INIT-GATEFLOW-006 forge publish/mutate session) |
| Approved head | `03e72600394c2b0e1fcb7cfebcf9e2a6b3ad44b8` |

## Context

**ADR-003** places outbound forge HTTP in **infra** (ForgeClient) and run/workflow
orchestration in **business**. Upstream pin contracts declare per-node ``forge:``
policy for (a) workspace publish after content hops and (b) forge *actions* on
external-action nodes.

Automated packaged-skill runs can leave durable artifacts on the worker
workspace while the remote run head stays empty. Gateflow must decide
**authority** for automated forge mutations.

This ADR decides:

1. Who is SSOT for forge *policy* after a hop — pin vs handoff
2. Who performs mutations — Cursor-dispatched forge skills vs ForgeClient
3. How the remote ref for workspace publish is bound
4. The *class* of path filter for workspace publish (not concrete path lists)

Product catalogues (skill ids, lane names, HTTP mounts, event type strings,
artifact schemas, comment UX, wave delivery slices) remain in INIT / TDD /
pin / as-built — this ADR does **not** catalogue them (same stance as ADR-007 /
ADR-008).

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — Agent push / forge CLI during the content skill hop | No orchestrator forge path | Non-deterministic; secrets risk; empty remote head still common |
| B — Cursor-dispatch forge skills as workflow graph nodes | Reuses human skill docs | Pin forbids forge skills as outcomes; conflates content success with mutate success; dual auth confusion |
| C — **Pin ``forge:`` is policy SSOT; business applies it via ForgeClient; content skills do not mutate** | Deterministic; matches pin forge-side-effects; demixes content vs forge | Orchestrator must honor pin semantics and fail closed |

## Recommendation

**Option C.**

1. **Pin is policy SSOT.** Absent skill-node ``forge`` means workspace publish is
   **disabled**. Handoff may carry **instance** slots only; it does **not**
   override pin policy. Policy/instance conflicts fail closed.
2. **Orchestrator never Cursor-dispatches forge skills.** After a successful
   content hop, business applies pin workspace-publish policy via **ForgeClient**.
   External-action forge *actions* require an **explicit authorization** step
   before mutate (human forge skill **or** programme-authorized control-plane
   path — dual executor). Exact mounts and triggers are TDD / INIT.
3. **Head binding** for workspace publish comes from **run context** already
   owned by the run job. Do **not** accept a pin or handoff head selector for
   that publish.
4. **Path include class** for workspace publish: repository ignore semantics
   plus a hard secret denylist, excluding run-scoped handoff batons.
   Allowlist-first packaging needs a superseding decision.
5. **Ordering:** when workspace publish and handoff ingest both apply on the
   same hop, publish **before** ingest so required empty publish fails closed
   without advancing on a half-published tree.
6. **Publish policy class:** optional + nothing to publish → continue;
   required + nothing to publish → fail closed; publish I/O failure → fail
   closed. Concrete enums and node wiring are pin / TDD.

## Consequences

- Content-skill success is separable from forge mutate success.
- Automated publish/mutate is deterministic and testable without an agent SDK.
- Infra ForgeClient remains the production mutate transport for this path
  (ADR-003); business owns *when* to call it from pin policy.
- Completing a content hop must not silently perform external-action mutates
  (draft PR / board seed); those require the explicit authorization path.

## Revisit triggers

- Workers span hosts without a shared workspace filesystem for publish trees.
- Product requires allowlist-first path packages instead of ignore + denylist.
- PE requires forge skills on the workflow graph as first-class outcomes.
- A superseding ADR changes publish/mutate authority.
