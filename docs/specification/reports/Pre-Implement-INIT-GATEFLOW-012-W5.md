## Pre-implement — drivestream-lab/gateflow / W5 — Dormant ForgeClient.delete_branch

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-012-W5.md` |
| Initiative | INIT-GATEFLOW-012 |
| Wave | W5 |
| Date | 2026-08-08 |
| Outcome | `pass` |
| Outcome reason | W4 `human_approved` + Ground-Report; WorkManifest contract pass; board [#190] seeded under EPIC [#184]; P15 N/A contracted (dormant zero live callers); develop @ `de59a3f…` |
| Wave head context | Integration tip: `develop` @ `de59a3f…` (W4 Pass-2 publish after merge [#195](https://github.com/drivestream-lab/gateflow/pull/195)). Intended coding head: `feature/INIT-GATEFLOW-012-w5-delete-branch` — **cut from develop before `/commit-workspace` / `/loop-spec`** (this skill does not open the branch) |

---

### Gate check (prior wave)

> Complete this before reading anything else. Board / branch / PR checks are **read-only**.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — on `develop` @ `de59a3f…` (feature head not yet cut) |
| Spec PR merged | Implementation plan on integration branch | [x] yes — [#183](https://github.com/drivestream-lab/gateflow/pull/183) MERGED (`b83006c…`); plan on `develop` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — `spec-lgtm` on [#183](https://github.com/drivestream-lab/gateflow/pull/183) |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — [#190](https://github.com/drivestream-lab/gateflow/issues/190) parent EPIC [#184](https://github.com/drivestream-lab/gateflow/issues/184); body has TASK-W5-01…03 |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — `WorkManifest contract passed.` |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` | [x] complete — TASK-W5-01…03 |
| Live-verification contract | P15: live under `live_verify_dir` **or** N/A with plan reason | [x] N/A — `verification.live.applicable: false` — “P15 N/A — delete_branch ships dormant with zero live callers this INIT (G5)” |
| Plan source freshness | H1–H3 / G2 durable roots | [x] current — product + plan on `develop` via [#183](https://github.com/drivestream-lab/gateflow/pull/183) |
| Impact-map repo scope | match | [x] match — gateflow half only; prayog-skills REQ-28–31 out of scope |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live when P15; else N/A with reason | [x] N/A — P15 N/A; dormant zero live callers (plan `verify_command`) |
| `ground_command` | resolved or N/A | [x] N/A — `/ground-spec` Pass-2 skill, not a Makefile target |
| Co-shipped live verify (P15) | FILE under `live_verify_dir` when surface | [x] N/A — no live product surface this wave |
| Prior wave as-built row | `human_approved` (from prior `wave-acceptance`) | [x] W4 = **human_approved** (retrospective Pass-2; Ground-Report W4 **pass**; merge `20965ab…`) |
| Prior Ground Report exists | `Ground-Report-…-W4.md` | [x] exists — `docs/specification/reports/Ground-Report-INIT-GATEFLOW-012-W4.md` |
| Plan PE sign-off (W0 only) | N/A for W5 | [x] N/A |

**Gate verdict:** **PASS**

**Notes for loop-spec (not start-blocks):**
- **`_git_ref_update_path` docstring already says PATCH/DELETE** — implement `delete_branch` via `client.delete` on that path (same transport family as branch tip update); **no new HTTP transport**.
- Today there is **no** `ForgeClient.delete_branch` method; verify scripts have a local `_delete_branch` helper — do **not** treat that as product API.
- **Structural dormancy (G5 / Q-6):** zero production callers this INIT; add AST/grep guard under REQ-27 evidence (`test_delete_branch_dormant.py`).
- Fail closed on missing/protected branch — named error; **no silent no-op** (REQ-27).
- Do **not** claim prayog-skills pin-shape / REQ-28–31 (DEP-02 / other repo).
- **Process (W4 L-01):** do not skip Pass-2 or tip `wave-accepted` before wave-signoff this wave.
- Intended head: `feature/INIT-GATEFLOW-012-w5-delete-branch`.

---

### Contracts consumed (from prior Ground Report)

> Source: `docs/specification/reports/Ground-Report-INIT-GATEFLOW-012-W4.md` §Contracts produced. Confirmed against `src/` on `develop` @ `de59a3f…`.

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| ForgeClient git-ref helpers | `ForgeClient._git_ref_get_path` / `_git_ref_update_path` | owner, repo, branch | REST path strings | source / ADR-003 infra | [x] yes — update path documented for PATCH/**DELETE** |
| Branch create/update transport | `ensure_branch_from_base` / tip probe | org/repo/branch | create or reuse | Ground-Report W2 | [x] yes — compose DELETE on same update path family |
| Repo-scoped concurrency | `find_active_run(org, repo)` | org, repo | optional ACTIVE | Ground-Report W4 | [x] yes — W5 does not change concurrency |
| No isolation infra | REQ-25 | — | no lock/worktree packages | Ground-Report W4 | [x] yes — delete_branch must not invent isolation |

**Unconfirmed / must extend in W5:**
- **`delete_branch` method** — DELETE on `_git_ref_update_path`; unit success path (REQ-26)
- **Fail-closed missing/protected** — named errors; no silent success (REQ-27)
- **Dormancy code-guard** — zero non-test callers of `delete_branch` (Q-6 / G5)
- **As-built + README** — unit-only / dormant documentation
- **Human wave head** — cut `feature/INIT-GATEFLOW-012-w5-delete-branch` before publishing checklist / coding

---

### Must read

- [x] `AGENTS.md`
- [x] MDC rules (domain-filtered for this slice):
  - [x] `infra-services.mdc` — ForgeClient stays infra; `@inject` lifecycle
  - [x] `fail-fast.mdc` — missing/protected → named fail; no silent no-op
  - [x] `logging-loguru.mdc` — branch / operation as kwargs
  - [x] `testing-verify-flows.mdc` — unit + dormancy guard; no live journey (P15 N/A)
  - [x] `architecture.mdc` / `python-imports.mdc` / `strong-typing.mdc`
- [x] ADRs (keyword-matched):
  - [x] ADR-009 — ForgeClient mutate authority (method in infra; no live pin edge this INIT)
  - [x] ADR-003 consume — outbound forge HTTP in infra (via ADR-009 context)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-012-gateflow.md` — REQ-26, REQ-27; G5 dormancy; Q-6
- [x] Plan / §9 WorkManifest: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-012.md` W5
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/190 — TASK list (projection):
  - [x] TASK-W5-01 — REQ-26 — depends_on: [] — `forge_client.py` — DELETE-ref `delete_branch`
  - [x] TASK-W5-02 — REQ-27 — depends_on: TASK-W5-01 — `test_forge_client.py` + `test_delete_branch_dormant.py` — fail-closed + dormancy guard
  - [x] TASK-W5-03 — REQ-26,27 — depends_on: TASK-W5-02 — as-built + `tests/README.md` — dormant docs

---

### Governance alignment

- [x] Slice does not contradict Accepted ADR-009 / infra placement
- [x] Plan TASK MDC / ADR notes reviewed
- [x] No new ADR required (method-only; dormancy structural)
- [x] Do not invent pin outcome edges or prayog-skills REQ-28–31 claims

---

### Must update (in the same change as the code — via `/loop-spec`)

- [ ] Product spec — only if contract drift (prefer no drift)
- [ ] `as-built/implementation-status.md` — W5 dormant row (TASK-W5-03)
- [ ] `tests/README.md` — unit-only / dormancy note (TASK-W5-03)
- [ ] Unit — `test_forge_client` success/fail + `test_delete_branch_dormant` guard
- [ ] Live — N/A (P15); human accept = unit green + dormancy guard + tip `wave-accepted`
- [ ] ADR — none expected

---

### Must not

- [ ] Wire `delete_branch` into any live walker / route / forge action this INIT
- [ ] Introduce a second HTTP transport outside existing git-ref paths
- [ ] Silent no-op on missing/protected branch
- [ ] Claim CTR-01 / prayog-skills pin remount (REQ-28–31)
- [ ] Skip Pass-2 / tip `wave-accepted` before merge (W4 L-01)
- [ ] Open a branch, commit, push, open a PR, apply labels, or create board issues from this skill

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | format/lint/types/layers | `make check` |
| Unit | DELETE-ref success; missing/protected fail-closed; zero production callers | `make test` |
| Live verify | N/A — P15 N/A dormant (G5) | N/A — reason above |
| Ground check | Pass-2 `/ground-spec` after accept | N/A as Makefile — skill |

> Human wave-acceptance for this wave: confirm unit + dormancy guard; label tip `wave-accepted` (no live smoke script).

### Human wave-acceptance (after loop-spec + Draft PR)

- [ ] `make check` / `make test` green on tip
- [ ] Confirm dormancy guard: no production caller of `delete_branch`
- [ ] Label tip `wave-accepted` (skills never apply it)
- [ ] Run `/learning-extract` → `/ground-spec` **before** wave-signoff merge (do not repeat W4 L-01)

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-012
- Issue: [#190](https://github.com/drivestream-lab/gateflow/issues/190)
- Spec path: `docs/specification/product/INIT-GATEFLOW-012-gateflow.md`
- Verify command (human): N/A — P15 N/A; dormant zero live callers
- ADRs in scope: ADR-009 (consume)
- Wave head: cut `feature/INIT-GATEFLOW-012-w5-delete-branch` from `develop` @ `de59a3f…` before Forge publish
- Prior: W4 Ground-Report + merge `20965ab…`; Pass-2 publish `de59a3f…`

---

### Checklist publish readiness (on `pass` — fill handoff.forge commit_workspace)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — prior wave approved; WM clean; P15 N/A contracted |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish this checklist onto bound `head_ref` **after** feature head is cut |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR |

Recommend: human/Forge cut `feature/INIT-GATEFLOW-012-w5-delete-branch` from `develop`, then `/commit-workspace` (checklist), then `/loop-spec`. Do not open the Draft PR here.

---

### Merge order (if cross-module / cross-service)

1. Human: cut wave feature head from `develop` @ `de59a3f…`  
2. Publish Pre-Implement onto that head  
3. TASK-W5-01 `delete_branch` → TASK-W5-02 fail-closed + dormancy guard → as-built/README  
4. Pass-2 closeout before merge (avoid W4 L-01)

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-012-W5.md
  blockers: []
  signals:
    wave: W5
    wave_issue: "https://github.com/drivestream-lab/gateflow/issues/190"
    prior_wave: W4
    prior_merge_sha: 20965abc6c8d2210fa0c2b57dd375185032c58b6
    develop_tip: de59a3fe6c2f5d7d33c1db2b831614a66c516064
    tasks:
      - TASK-W5-01
      - TASK-W5-02
      - TASK-W5-03
    implements: [REQ-26, REQ-27]
    check_command: "make check"
    test_command: "make test"
    verify_command: "N/A — P15 N/A; dormant zero live callers"
    intended_head_ref: feature/INIT-GATEFLOW-012-w5-delete-branch
    p15: n/a
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    commit_workspace: required
    head_ref: feature/INIT-GATEFLOW-012-w5-delete-branch
    base_ref: develop
```
