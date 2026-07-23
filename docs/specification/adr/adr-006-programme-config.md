# ADR-006 — Programme config location and load contract (W1)

| Field | Value |
|-------|-------|
| Status | Draft |
| Initiative | INIT-GATEFLOW-001 |
| Feasibility finding | F-06 |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-001.md` |
| Decision owner | PE |
| Approval evidence | Pending |
| Approved head | Pending |

## Context

PRD places W1 programme config in the **gateflow repo** (not prayog-meta harness).
Keys include `trigger.label`, handoff refs/globs, retry budget, metrics retention,
runner default, model profiles/overrides, tools.slots. Spec FR-18 and fail-fast
rules forbid silent defaults for required keys.

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — Env vars only for every key | 12-factor | Unwieldy nested maps; hard to review in PR |
| B — Committed YAML `config/programme.yaml` + Pydantic model; path overridable by env | Reviewable; matches PRD “config in repo” | Must not commit secrets |
| C — Meta repo harness YAML in W1 | Shared across services | Contradicts Decision / PRD W1 location |

## Recommendation

**Option B.**

- Canonical path: `config/programme.yaml` (committed defaults for dogfood).
- Optional override: `PROGRAMME_CONFIG_PATH` env points to another file.
- Load once at process startup into a Pydantic v2 `ProgrammeConfig` model in
  `src/models/` (or `src/configs/` settings-style singleton via `get_instance()`
  pattern used for settings — **not** injector-bound).
- Required keys for W1: `trigger.label`, `handoff.ref`, `handoff.ref_fallback`,
  `handoff.artifact_globs`, `retry.findings_budget`, `metrics.retention_days`,
  `runner.default`, `model.profiles` (must include `default`). Empty
  `model.overrides` / `tools.slots` allowed as `{}`.
- Missing/invalid file or schema → **fail startup** (API and worker).
- Secrets (App key, webhook secret, programme token, Postgres URL) stay in env /
  secret store — never in programme YAML.

## Consequences

- PE can change trigger label / budgets via PR without code change.
- Example file `config/programme.yaml.example` may be committed if defaults need
  redaction; dogfood may commit non-secret defaults directly.

## Revisit triggers

- W2 moves shared keys to meta/harness schema.
- Per-initiative config overlays required.

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
