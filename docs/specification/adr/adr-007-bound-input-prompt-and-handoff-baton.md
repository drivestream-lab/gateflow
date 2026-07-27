# ADR-007 — Bound-input prompt resolve and Gateflow-owned handoff baton

| Field | Value |
|-------|-------|
| Status | Draft |
| Initiative | INIT-GATEFLOW-005-BOUNDINPUT |
| Feasibility finding | FF-06 |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-005-BOUNDINPUT.md` |
| Decision owner | PE |
| Approval evidence | Pending |
| Approved head | Pending |
| Relates to | Extends ADR-003 (layer split unchanged); ADR-001 (RunStore SSOT); ADR-004 (pin consume, no programme.yaml revive); narrows ambient handoff globs for packaged-skill automate |

## Context

Pinned skill prompt packages exist (INIT-PRAYOG-SKILLS-003-PROMPTS), but Gateflow
still (1) invents AgentRunner invocation prose in infra
(`CursorAgentRunner._build_prompt`) and (2) ingests handoffs via ambient
repo globs/mtime (`HandoffReader.find_latest_handoff`). Product requires pin
template SSOT, fail-closed bind/render, and a **per-run `handoff_path` defined
and stored by Gateflow** — not derived from document trees.

ADR-003 already places AgentRunner in **infra** and handoff/orchestration in
**business**, but does not decide:

1. Who owns prompt package resolve / schema validate / `{{var}}` render
2. What the AgentRunner public message contract is after invent-prose removal
3. Concrete `handoff_path` representation and ingest SSOT for packaged-skill automate

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — Resolve/render inside `CursorAgentRunner` (infra) | Fewer business types | Couples pin filesystem + schema to SDK adapter; violates ADR-003; hard to unit-test without SDK |
| B — **Business PromptResolver** (resolve + validate + render); **infra AgentRunner message-only**; **RunStore `handoff_path`** = Gateflow-defined workspace-absolute path unique per `run_id`; ingest reads that path only for packaged-skill automate | Aligns ADR-003; testable without Cursor; matches product baton ownership | New business module + RunStore columns + human Alembic |
| C — Object-storage / blob URI for handoff baton | Strong isolation across hosts | Extra infra; overkill for current single-workspace worker; delays W0 |

## Recommendation

**Option B.**

1. **PromptResolver (business)** — given workspace root + skill id, locate
   `prompts/template.md` + `prompts/schema.yaml` under the pin skills tree
   present in the workspace (normative search: `prayog-skills/skills/{area}/{skill_id}/prompts/`
   for `area ∈ {development, requirements}` while Launchpad harness sync remains
   a no-op stub). Fail closed if missing/invalid. Validate bound inputs against
   schema; render simple `{{var}}` only. Return `prompt_id`, `prompt_revision`,
   and rendered message string.
2. **AgentRunner (infra)** — for packaged-skill automate, accept a **pre-rendered
   message string** and must **not** author Gateflow invent-prose. `skill_id`
   remains for logging / agent name only. Unit `mock-*` doubles may keep a
   non-live path; they are not packaged-skill success evidence.
3. **Bind map** — `ticket` ← wave-start `ticket_id` (required non-empty for
   automate); `initiative` ← `initiative_id` or `""`; `skill_id`; `workspace`;
   `handoff_path` ← stored run field.
4. **`handoff_path`** — at run create/continue, Gateflow defines
   `{workspace}/.gateflow/runs/{run_id}/handoff.md` (workspace-absolute string),
   persists it on `runs.handoff_path`, creates parent dir (and empty baton file
   if needed) before AgentRunner. Ingest for packaged-skill automate reads
   **only** that path. Ambient glob/mtime is **not** SSOT for this path
   (narrow supersession of INIT-001 ambient ingest).
5. **Persistence** — `runs.handoff_path` (text); `stages.prompt_id` +
   `stages.prompt_revision` (text). Human-owned Alembic per ADR-001 /
   `database-migrations.mdc`. Exact column nullability and indexes are TDD
   data-contract detail.

## Consequences

- Pin prompt bumps apply without Gateflow code changes (consume layout only).
- Invent-prose removal is an enforceable contract (anti-hardcode unit).
- Concurrent runs isolate batons via per-`run_id` paths under `.gateflow/`.
- `.gateflow/` is runtime state under the worker workspace — not a repo layout
  product concern and not git SSOT.
- Launchpad real harness sync may later relocate the skills tree; revisit pin
  search roots when sync stops being a stub.

## Revisit triggers

- Launchpad harness sync becomes real and relocates skill packages away from
  `prayog-skills/skills/`.
- Multi-host workers require handoff batons outside the workspace filesystem.
- A second AgentRunner needs a different message construction contract.
- Prompt packages gain filters/conditionals (upstream template engine change).

## Acceptance finalization

After PE review comments are resolved and PE explicitly states the decision is
ready for acceptance, update the file before final GitHub approval:

```text
Status: Accepted
Decision owner: @{pe-name}
Approval evidence: {review/comment URL}
Approved head: {full SHA to be approved}
```

The formal PE GitHub Approve must be on the final commit containing this
Accepted metadata. No file changes occur after that approval.
