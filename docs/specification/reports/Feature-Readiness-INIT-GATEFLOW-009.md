# Feature readiness — INIT-GATEFLOW-009

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-009 — Both-lane delivery factory prove-out |
| Spec | [`product/INIT-GATEFLOW-009-gateflow.md`](../product/INIT-GATEFLOW-009-gateflow.md) |
| Date | 2026-08-04 |
| Status | **Freeze** — programme exit with PE waiver on authorize live |
| Board epic | [#120](https://github.com/drivestream-lab/gateflow/issues/120) |
| Evidence chore | `chore/INIT-GATEFLOW-009-evidence-closeout` |

## Proven capabilities (feature names)

| Capability | Evidence |
|------------|----------|
| Harness pin consume (`v0.5.0-rc.2` family) | W0 checklist + Ground-Report W0; pin ≡ submodule |
| Spec lane Pass-1 (Draft Spec PR tip deliverable) | [`Live-Verify-INIT-GATEFLOW-009-W1.md`](Live-Verify-INIT-GATEFLOW-009-W1.md) — run `89fd636d-…` → PR [#119](https://github.com/drivestream-lab/gateflow/pull/119) |
| Implement lane Pass-1 (coding → Draft PR → live-verify) | [`Live-Verify-INIT-GATEFLOW-009-W0.md`](Live-Verify-INIT-GATEFLOW-009-W0.md) — run `4ace4f79-…` → PR [#126](https://github.com/drivestream-lab/gateflow/pull/126) |
| Wave closeout Pass-2 (learning → ground → wave-signoff) | [`Live-Verify-INIT-GATEFLOW-009-W2.md`](Live-Verify-INIT-GATEFLOW-009-W2.md) — run `4da11692-…` on #126 |
| Closeout API path (INIT-007) for programme wrap-up | Same Live-Verify W2; lifts INIT-007 REQ-15 deferral **for INIT-009 exit** |
| Basic automated PR checks | `.github/workflows/ci.yml` — `make check-ci` + `make test` (this freeze package) |

## Deferred / PE-waived

| Capability | Status | Notes |
|------------|--------|-------|
| **Authorize API live** (stop → `POST …/forge/authorize` → side effect) | **PE-waived** for INIT-009 exit | REQ-13…15 unit-complete (`test_forge_action_service`, etc.); no `verify_authorize` live run in this INIT |
| Ops portal / Mission Control UI | Deferred | Out of scope for INIT-009 |
| Second coding agent | Deferred | Out of scope |
| Slack / Teams notifiers | Deferred | Out of scope |
| Programme-wide self-dogfood beyond gateflow | Deferred | Out of scope |

## REQ-17 — programme vision hygiene (checklist)

| Item | Owner | Path | Blocking this freeze? |
|------|-------|------|------------------------|
| Update programme vision / planning note after freeze | PE / programme | `prayog-meta/planning/gateflow-programme-vision.md` | **No** — meta hygiene; track separately |

## Wave exit summary

| Wave | Board | Outcome |
|------|-------|---------|
| W0 | [#121](https://github.com/drivestream-lab/gateflow/issues/121) | **human_approved** — merged #126 |
| W1 | [#122](https://github.com/drivestream-lab/gateflow/issues/122) | **live proven** — Live-Verify W1 |
| W2 | [#123](https://github.com/drivestream-lab/gateflow/issues/123) | **live proven** — Live-Verify W2 (closeout on #126 after Spec #119 merge) |
| W3 | [#124](https://github.com/drivestream-lab/gateflow/issues/124) | **partial** — freeze + CI shipped; authorize live **PE-waived** |

## As-built alignment

See [`as-built/implementation-status.md`](../as-built/implementation-status.md) INIT-GATEFLOW-009 section — must match this freeze.
