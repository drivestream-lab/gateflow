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
| Relates to | Ownership decision unchanged by later carrier evolution (INIT-002+); pin remains graph SSOT; concrete keys/paths are INIT / TDD / as-built |

## Context

Gateflow needs non-secret programme/runtime configuration (orchestration knobs,
adapter selection, and related behaviour) while keeping secrets out of committed
config. Platform and product already decided that **W1 ownership of those knobs
is this service repo**, not prayog-meta harness YAML.

This ADR decides **how that ownership is enforced architecturally**:

1. Where programme/runtime config authority lives (this repo’s process vs meta)
2. That non-secret config is validated at startup and fails closed when invalid
3. That secrets never ride in the non-secret config carrier

Which knobs exist, defaults, env names, file paths, and API fields are product /
schema (INIT + TDD + as-built) — this ADR does **not** catalogue them.

## Options considered

| Option | Benefits | Costs / risks |
|--------|----------|---------------|
| A — Env vars for every nested key only | 12-factor purity | Nested maps hard to review when a file carrier is desired |
| B — **This-repo non-secret carrier + validate at startup; secrets in env/secret store** | Reviewable ownership; fail-closed; matches in-repo authority | Carrier shape may evolve (file vs env vs API) without changing ownership |
| C — Load programme config from meta/harness in W1 | Shared across services | Contradicts accepted W1 ownership |

## Recommendation

**Option B** (ownership + fail-closed validation — not a frozen file path).

1. **Authority:** Non-secret programme/runtime configuration for this service is
   owned by **this repository’s process**, not by prayog-meta harness YAML.
2. **Validation:** Load and validate once at process startup (settings-style
   singleton — not injector-bound). Missing or invalid required config fails
   startup for API and worker alike.
3. **Secrets:** Credentials and connection secrets remain in env / secret store
   only — never in a committed non-secret programme document.
4. **Carrier is TDD:** The concrete carrier (versioned file, env-backed settings,
   control-plane request fields, and/or pin for process graph) may evolve per
   INIT without a new ADR **as long as** (1)–(3) hold. Pin remains SSOT for
   workflow graph and dispatch; Enter-at / runner-model plan ownership follows
   the active INIT — not listed here.

## Consequences

- Programme behaviour is changeable under this repo’s review process without
  waiting on meta harness schema.
- Shared multi-repo overlays via meta/harness remain a revisit, not W1 default.
- Implementers must not treat a historical file path or key list in old drafts
  as architectural SSOT — see as-built / active INIT for the live carrier.

## Revisit triggers

- Shared multi-repo programme overlays move to meta/harness (would revisit
  Option C or a successor ADR).
- Per-initiative overlays become required as a new authority layer.
- Non-secret config must be mutable at runtime without process restart (new
  validation/lifecycle decision).
