# Pre-implement — gateflow / W1 — Automated forge apply + retire PR-at-start

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-008-W1.md` |
| Initiative | INIT-GATEFLOW-008 (brand **006A**) |
| Wave | W1 |
| Date | 2026-07-30 |
| Outcome | `blocked` |
| Outcome reason | Prior wave W0 as-built is not `human_approved` (still pending after merge of PR #96) |
| Wave head context | Unbound for coding — on `develop` @ `029481e`; recommended bind `feature/INIT-GATEFLOW-008-w1-automated-forge` only after gate PASS |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — on `develop` @ `029481e` |
| Spec PR merged | Implementation plan on integration branch | [x] yes — PR [#91](https://github.com/drivestream-lab/gateflow/pull/91) MERGED |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — `spec-lgtm` on merge |
| Board seed (read-only) | Wave issue(s) from plan §9 exist | [x] seeded — W1 [#94](https://github.com/drivestream-lab/gateflow/issues/94) OPEN |
| WorkManifest contract | `prayog/v1` §9 | [ ] **not run** — stopped at prior-wave gate |
| TASK exit proof | Every W1 `TASK-*` | [ ] **not assessed** — stopped at prior-wave gate |
| Live-verification contract | P15 applies for W1 | [ ] **not assessed** — stopped at prior-wave gate |
| Plan source freshness | CURRENT | [ ] **not assessed** — stopped at prior-wave gate |
| Impact-map repo scope | match | [ ] **not assessed** — stopped at prior-wave gate |
| `check_command` | resolved | [ ] not assessed |
| `test_command` | resolved | [ ] not assessed |
| `verify_command` | live when P15 | [ ] not assessed |
| `ground_command` | resolved or N/A | [ ] not assessed |
| Co-shipped live verify (P15) | FILE under `live_verify_dir` | [ ] not assessed |
| Prior wave as-built row | `human_approved` | [ ] **W0 = pending human_approved** — **UNSATISFIED** |
| Prior Ground Report exists | `Ground-Report-INIT-GATEFLOW-008-W0.md` | [x] exists |
| Plan PE sign-off (W0 only) | N/A for W1 | [x] N/A |

**Gate verdict:** **BLOCKED** — INIT-008 W0 as-built must be **`human_approved`** before W1 pre-implement may PASS. Ground Report exists; wave PR [#96](https://github.com/drivestream-lab/gateflow/pull/96) is **MERGED** (`029481e`), but as-built still reads **pending human_approved** (and still cites old tip `12a0364`).

**Unblock (human only at wave-signoff / as-built):**

1. Update `docs/specification/as-built/implementation-status.md` INIT-008 row to **`human_approved`** for W0 (record reviewed head / merge SHA `029481e` / tip `9e07a5a` as appropriate).
2. Re-run `/pre-implement W1`.

Do **not** run `/loop-spec` for W1 until this checklist outcome is `pass`.

**Forge readiness:** none for coding — no `commit_workspace` publish of a PASS checklist. Do not open a W1 branch from this skill.

---

### Contracts consumed (from prior Ground Report)

> Not confirmed for coding — gate blocked before contract deep-read for implementation readiness. W0 Ground Report §Contracts produced exists at `docs/specification/reports/Ground-Report-INIT-GATEFLOW-008-W0.md` for use after unblock.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| *(deferred)* | — | — | — | Ground-Report-W0 | [ ] not assessed — gate blocked |

**Unconfirmed contracts:** all W1 dependencies on W0 contracts remain **unconfirmed for coding** until gate PASS.

---

### Must read

- [ ] Deferred until gate PASS

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-008
- Issue: [#94](https://github.com/drivestream-lab/gateflow/issues/94)
- Spec path: `docs/specification/product/INIT-GATEFLOW-008-gateflow.md`
- Verify command (human): deferred — expected W1 live `.venv/bin/python -m tests.verify.verify_implement_lane` after PASS
- Wave head: unbound for W1 coding until PASS

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: blocked
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-008-W1.md
  blockers:
    - GF-W0-human-approved
  signals:
    wave: W1
    initiative: INIT-GATEFLOW-008
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/94"
    prior_wave: W0
    prior_as_built_status: pending_human_approved
    prior_ground_report: docs/specification/reports/Ground-Report-INIT-GATEFLOW-008-W0.md
    w0_merge_commit: "029481e3cef7da7bb9b813bec277e3d22cdcd743"
    unblock: "Mark INIT-008 W0 human_approved in as-built, then re-run /pre-implement W1"
  next_candidates:
    - wave-signoff
  human_checkpoint: true
  external_action: false
```
