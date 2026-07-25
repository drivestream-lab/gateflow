# ADR-004 — Programme configuration authority

| Field | Value |
|-------|-------|
| Status | Accepted |
| Initiative | INIT-GATEFLOW-001 |
| Feasibility finding | F-06 |
| Technical review | `docs/specification/reports/Technical-Review-INIT-GATEFLOW-001.md` |
| Decision owner | @nikd10x |
| Approval evidence | Explicit PE acceptance by @nikd10x on 2026-07-23 via Cursor chat (https://github.com/drivestream-lab/gateflow/pull/4); architecture package tip `ca74d77949046b8d91357c37bb2ea864dad60c26` |
| Approved head | `6e81923fe2b1fad3dd818c0ca8a0b26a961448a4` |

## Context

W1 programme knobs (triggers, handoff refs, retry budgets, model profiles, tool
slots) are owned by the gateflow repo per accepted product decision — not by
prayog-meta harness YAML. Secrets must stay out of committed config. This ADR
chooses how that non-secret config is loaded and validated.

Which keys exist and their defaults are product/schema (INIT + example YAML +
TDD), not architectural options.

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — Env vars for every nested key | 12-factor purity | Nested maps unreadable; hard to review in PRs |
| B — Versioned file in this repo + Pydantic validate at startup; path overridable by env | Reviewable; matches in-repo ownership | Must keep secrets out of the file |
| C — Load programme config from meta/harness in W1 | Shared across services | Contradicts accepted W1 ownership |

## Recommendation

**Option B.**

- Canonical non-secret file under this repo (e.g. `config/programme.yaml`);
  `PROGRAMME_CONFIG_PATH` may override location.
- Validate once at process startup into a Pydantic model (settings-style
  singleton — not injector-bound).
- Missing/invalid config → fail startup (API and worker).
- Secrets (App keys, webhook secret, programme token, DB URLs) remain in env /
  secret store only.

## Consequences

- Programme behaviour knobs change via PR without code edits.
- Meta/harness shared config schema is deferred (W2+ revisit).

## Evolution (INIT-GATEFLOW-002 Enter-at)

Accepted product evolution (TDD-002 / FR-15–16):

- **Removed from programme YAML:** `trigger`, `runner`, `model`, `pr.*`,
  `retry.findings_budget`, `metrics.retention_days`.
- **Wave-start API owns:** PR targeting, `start_node`, runner/model dispatch plan.
- **Env owns:** `GATEFLOW_FINDINGS_BUDGET`, `GATEFLOW_METRICS_RETENTION_DAYS`.
- **Programme YAML retained (interim):** `notifier`, `handoff.artifact_globs`,
  `tools.slots`.

Pin `prayog-skills/workflow.yaml` remains SSOT for process graph and `dispatch`.

## Evolution (programme.yaml removed)

Accepted follow-on (pin walker / no YAML):

- **`config/programme.yaml` deleted** — Option B file no longer exists.
- **Env owns:** `GATEFLOW_NOTIFIER`, `GATEFLOW_FINDINGS_BUDGET`,
  `GATEFLOW_METRICS_RETENTION_DAYS`, `GATEFLOW_MAX_ORCHESTRATED_HOPS`.
- **Code constants own:** handoff artifact globs in `HandoffReader` (match skill
  durable-handoff convention).
- **`tools.slots` / StageToolResolver removed** (ToolProvider `none` remains
  product intent without programme slot map).
- Pin remains SSOT for graph + `dispatch`; wave-start API remains SSOT for
  Enter-at and runner/model plan.

Secrets stay env / secret store only (unchanged).

## Revisit triggers

- Shared multi-repo programme overlays move to meta/harness.
- Per-initiative overlays become required.

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
