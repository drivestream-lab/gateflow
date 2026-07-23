# ADR-004 — Programme configuration authority

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

## Revisit triggers

- Shared multi-repo programme config moves to meta/harness.
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
