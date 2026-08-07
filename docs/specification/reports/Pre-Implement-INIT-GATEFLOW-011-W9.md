## Pre-implement — gateflow / W9 — Closure preview + CAP-01 reuse

| Field | Value |
|-------|-------|
| Artifact | `docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W9.md` |
| Initiative | INIT-GATEFLOW-011 |
| Wave | W9 |
| Date | 2026-08-07 |
| Outcome | `pass` |
| Outcome reason | W9 gate checks pass: prior W8 `human_approved` (tip `a0de226` `wave-accepted`; PR #180 merged `c114e94`) with Ground-Report-W8 §Contracts produced complete; spec PR #159 merged with `spec-lgtm`; board seeded (EPIC #160 / W9 #170 with TASK-W9-01…03); WorkManifest contract clean; P15 live verify command resolved; H1–H3 spend fresh on `develop`. |
| Wave head context | Bound by Forge/human context: `develop` @ `c114e94` (after W8 merge) — not opened by this skill; planned coding branch `feature/INIT-GATEFLOW-011-w9-closure-preview` (cut in `/loop-spec`) |

---

### Gate check (prior wave)

> Complete this before reading anything else. Do not proceed if the gate fails.
> Board / branch / PR checks are **read-only**. Do not create tickets or open
> a branch from this skill — emit Forge readiness instead.

| Item | Required | Status |
|------|----------|--------|
| Branch context (read-only) | Bound head is `develop` or `feature/INIT-*-w{N}-*` — not open `chore/*-spec-*` | [x] ok — `develop` @ `c114e94` (not `chore/INIT-GATEFLOW-011-spec-gateflow`) |
| Spec PR merged | Implementation plan on integration branch | [x] yes — [#159](https://github.com/drivestream-lab/gateflow/pull/159) MERGED; plan on `develop` |
| Coding-readiness at merge | Merged spec PR had `spec-lgtm` on head | [x] verified — `gh pr view 159` → labels include `spec-lgtm`; mergeCommit `234f66a1b4d5e9d34522cb6bceb016c5672626a4` |
| Board seed (read-only) | Wave issue(s) from plan §9 exist; TASK ids present in wave body | [x] seeded — EPIC [#160](https://github.com/drivestream-lab/gateflow/issues/160); W9 [#170](https://github.com/drivestream-lab/gateflow/issues/170) (OPEN, title `[INIT-GATEFLOW-011 W9] Closure preview + CAP-01 reuse`, programme Status **Todo**); TASK-W9-01…03 in body; `Board-Seed-INIT-GATEFLOW-011.md` lists W9 #170 |
| WorkManifest contract | `prayog/v1` §9 passes `scripts/workmanifest_contract.py` | [x] pass — `.venv/bin/python prayog-skills/scripts/workmanifest_contract.py …/Implementation-Plan-INIT-GATEFLOW-011.md` → "WorkManifest contract passed." |
| TASK exit proof | Every wave `TASK-*` has `exit.criteria` + `exit.proof` (kind/expected/evidence_expected) | [x] complete — W9 TASK-W9-01…03 in plan §9 (lines 1749–1800); each has `exit.criteria`, `exit.proof.kind=command`, `command`, `expected`, `evidence_expected` |
| Live-verification contract | When P15 applies: `verification.live` applicable + script under `live_verify_dir` (not unit-as-live) | [x] contract — `verification.live.applicable: true`; command `.venv/bin/python -m tests.verify.verify_closure_preview` (FILE co-shipped in TASK-W9-03; script absent today — expected until `/loop-spec`) |
| Plan source freshness | all upstream rows `CURRENT` | [x] current — plan §Source freshness CURRENT (plan is walk-time) |
| Impact-map repo scope | revision and scope digest match canonical handoff | [x] match — product H1 `sha256:eca06cbe…`, H2 `sha256:afdc7bd5…`, H3 revision `1`, G1 `f3da8148…`; product file digest `sha256:0edf9b72…` matches plan `source_spec_digest` |
| `check_command` | resolved | [x] `make check` |
| `test_command` | resolved | [x] `make test` |
| `verify_command` | live script under `live_verify_dir` when P15 applies | [x] `.venv/bin/python -m tests.verify.verify_closure_preview` |
| `ground_command` | resolved or N/A with reason | [x] N/A — `/ground-spec` is Pass-2 pin skill, not a Makefile target |
| Co-shipped live verify (P15) | FILE path under `live_verify_dir` listed | [x] `tests/verify/verify_closure_preview.py` (create in TASK-W9-03) |
| Prior wave as-built row | `human_approved` (from prior `wave-acceptance`) | [x] W8 = `human_approved` — as-built row; tip `a0de226` `wave-accepted`; PR #180 merged `c114e94`; Ground-Report W8 **pass** |
| Prior Ground Report exists | `reports/Ground-Report-{SPEC}-W{N-1}.md` | [x] exists — `Ground-Report-INIT-GATEFLOW-011-W8.md` (outcome `pass`; §Contracts produced complete for W9+) |
| Plan PE sign-off (W0 only) | Implementation-Plan §0 marked complete | [x] N/A — W9 (not first wave); gate is prior-wave Ground Report + human_approved |

**Gate verdict:** PASS — W9 pre-flight gates satisfied; ready for `/loop-spec` after checklist publish.

**Manifest note:** WorkManifest W9 `depends_on: [W1, W8]` (CAP-01 for REQ-27 + completion/closure nesting from W8). Programme prior-wave gate is W8 `human_approved`. Ground-Report-W8 supplies nesting (`…/completion` sibling → add `…/closure`) and CAP-01/05 reuse warnings. Purge plan SSOT is `prayog-skills` artifact-write-contract + purge-app skill allowlist — **not** invented by this INIT.

**Forge readiness:** not required for seed — complete; head bound to `develop`. Planned coding branch: `feature/INIT-GATEFLOW-011-w9-closure-preview`. Board #170 Status is **Todo** (read-only; Forge/human may move In Progress).

---

### Contracts consumed (from prior Ground Reports)

> Nesting / no-regress from Ground-Report-W8.
> CAP-01 from Ground-Report-W1 / W0.
> Purge allowlist from prayog-skills (not a prior Ground Report — flag as design source).

W9 delivers CAP-10 closure preview:  
`GET /api/v1/initiatives/{initiative_id}/closure`  
lists pre-purge planned delete vs keep from the purge skill's own allowlist/plan
(REQ-25 — "not yet run" when purge not executed); post-purge actual deleted/kept
from purge execution evidence (REQ-26); once a closure PR exists, reuses CAP-01
for `initiative-closure-signoff-app` / `initiative-closure-signoff-meta` on current
head (REQ-27 — no separate approval logic); GET-only (REQ-28).

| Assumed contract | Entry point | Input shape | Output shape | Source | Confirmed? |
|-----------------|-------------|-------------|--------------|--------|------------|
| CAP-01 evaluate | `CheckpointEvidenceService.evaluate` | checkpoint_id + PR ref | `CheckpointStatusResult` | Ground-Report-W1 | [x] yes — W9 uses ids `initiative-closure-signoff-app` / `initiative-closure-signoff-meta` (vocab already in `checkpoint_models.py`) |
| Forge PR reads | `ForgeClient.get_pull_request` (+ reviews as CAP-01 needs) | owner/repo/number | PR document | Ground-Report-W0/W1 | [x] yes — closure PR evidence |
| Completion eligibility (nesting neighbor) | `GET …/completion` | — | — | Ground-Report-W8 | [x] yes present — **must not regress**; W9 nests `…/closure` nearby |
| Merge confirm (must not regress) | `GET …/waves/{wave_id}/merge` | — | — | Ground-Report-W8 | [x] yes present — **must not regress** |
| Initiative identity + 404 | GET `/initiatives/{id}` | initiative id | readout or 404 | Ground-Report-W2 | [x] yes |
| Closure start / purge Enter-at | `POST …/closure/start` → Enter-at `purge-initiative-artifacts-app` | closure body | 202 run | as-built INIT-010 W4 | [x] yes present — W9 is **readout only**; must not mutate start/purge |
| Purge allowlist (plan source) | `artifact-write-contract.md` + purge-app skill | INIT id | delete/refuse/keep sets | prayog-skills | [x] yes — normative PURGE/KEEP lists; REQ-25 must mirror this, not invent deletes |
| Purge execution evidence | purge-app handoff `signals.deleted` / `missing_ok` / `refused` (run stages/events/handoff) | run timeline | actual lists | purge-app SKILL | [x] yes present as process — compose from Gateflow-owned run/handoff when available; "not yet run" when absent |

**Unconfirmed contracts** (design risks for `/loop-spec`):
- **REQ-25 pre-purge:** Build planned delete vs keep from the **same** allowlist/refuse rules as `purge-initiative-artifacts-app` / `artifact-write-contract.md` scoped to `INIT-GATEFLOW-011`. When purge-app stage has **not** run → 200 with explicit **"not yet run"** (or equivalent) plan preview — never invent deletes.
- **REQ-26 post-purge:** When purge-app has completed for the initiative, surface **actual** deleted / kept (/ refused) from Gateflow-owned evidence (handoff signals on the closure run, stages/events). Prefer run timeline over ambient workspace scrape.
- **REQ-27:** Call `CheckpointEvidenceService.evaluate` (or composed if PR resolved from closure run) for **both** checkpoint ids on the closure PR head — **no** fork of CAP-01 vocabulary. Report missing items / satisfied like CAP-08 merge confirm.
- **REQ-28:** GET-only; zero Forge/board writes from the new path.
- **File-scope risk:** TASK-W9-01 does not list `business_services_module.py` — include `binder.bind(ClosurePreviewService)` as DI glue (same as W4–W8) and record in Wave-Execution observed files.
- Do **not** call `POST /initiatives/closure/start` or dispatch purge from this GET.

---

### Must read

- [x] `AGENTS.md`
- [x] MDC rules (domain-filtered):
  - [x] `.cursor/rules/architecture.mdc` — new service + route + models
  - [x] `.cursor/rules/dependency-injection.mdc` — `@inject` + singleton bind
  - [x] `.cursor/rules/repository-pattern.mdc` — runs/handoff via repos; no ORM in service
  - [x] `.cursor/rules/pydantic-schemas.mdc` — `closure_preview_models.py` in `src/models/` only
  - [x] `.cursor/rules/http-api-conventions.mdc` — GET `/initiatives/{initiative_id}/closure`; query org/repo
  - [x] `.cursor/rules/fail-fast.mdc` — unknown initiative → 404; not-yet-run is explicit, not silent empty
  - [x] `.cursor/rules/strong-typing.mdc` — preview phase / eligibility enums typed
  - [x] `.cursor/rules/testing-verify-flows.mdc` — co-ship `verify_closure_preview`
  - [x] `.cursor/rules/spec-driven-development.mdc` — as-built W9 row
  - [x] `.cursor/rules/logging-loguru.mdc` — kwargs (`initiative_id`, purge phase, checkpoint ids)
  - [ ] `.cursor/rules/database-migrations.mdc` — N/A
- [x] ADRs:
  - [x] ADR-001 — durable store (**Accepted**)
  - [x] ADR-003 — Forge reads (**Accepted**)
  - [x] ADR-005 — programme-token (**Accepted**)
  - [x] ADR-009 — no mutate from CAP-10 (**Accepted**; REQ-28)
  - [x] ADR-010 — lane intake / closure Enter-at (**Accepted**; do not change start API)
- [x] Spec: `docs/specification/product/INIT-GATEFLOW-011-gateflow.md` — REQ-25, REQ-26, REQ-27 (+ REQ-28); route `GET /api/v1/initiatives/{initiative_id}/closure`
- [x] Plan §9 WorkManifest W9 (lines 1740–1832); GOAL-W9 ~615–621
- [x] Purge SSOT: `prayog-skills/references/artifact-write-contract.md`; `prayog-skills/skills/development/purge-initiative-artifacts-app/SKILL.md`
- [x] Board wave issue: https://github.com/drivestream-lab/gateflow/issues/170 — TASK list (projection only):
  - [ ] TASK-W9-01 — implements REQ-25, REQ-26, REQ-27 — depends_on: [] — files: `closure_preview_service.py`, `closure_preview_models.py`, `test_closure_preview_service.py` (create) — exit: `make test`
  - [ ] TASK-W9-02 — implements REQ-25, REQ-26, REQ-27, REQ-28 — depends_on: [TASK-W9-01] — files: `initiatives_routes.py`, `test_initiatives_read_api.py` (modify) — exit: `make test` — GET `…/closure` GET-only
  - [ ] TASK-W9-03 — implements REQ-25, REQ-26, REQ-27, REQ-28 — depends_on: [TASK-W9-02] — files: `verify_closure_preview.py` (create), `tests/README.md`, as-built (modify) — exit: `make check && make test`

---

### Governance alignment

- [x] Slice does not contradict listed ADRs — GET-only CAP-10; CAP-01 reuse; purge plan from skill allowlist
- [x] Plan TASK MDC / ADR notes for W9 reviewed
- [x] Cited ADRs are **Accepted** in `docs/specification/adr/`

---

### Must update (via `/loop-spec`)

- [ ] As-built — INIT-GATEFLOW-011 W9 matrix (REQ-25/26/27/28)
- [ ] `tests/README.md` — feature map for `verify_closure_preview`
- [ ] Unit — pre "not yet run" plan from allowlist; post actual lists; CAP-01 signoff-app/meta; API 401/200/404/405
- [ ] Live — `tests/verify/verify_closure_preview.py` (human at wave-acceptance)
- [ ] ADR — no supersede required

---

### Must not

- [ ] Invent a delete list independent of purge-app allowlist (REQ-25)
- [ ] Treat missing purge as ready/clean without "not yet run" (REQ-25 failure mode)
- [ ] Fork CAP-01 for closure signoff checkpoints (REQ-27)
- [ ] Add non-GET product routes or Forge/board writes (REQ-28)
- [ ] Call `POST …/closure/start` or dispatch purge from the preview GET
- [ ] Regress W8 merge/completion or earlier initiative GETs
- [ ] Open a branch, commit, push, PR, labels, or board issues from this skill
- [ ] Mutate approved WorkManifest intent

---

### Verification plan

| Layer | What it proves | Command |
|-------|----------------|---------|
| Static check | Format, lint, types, layers | `make check` |
| Unit | Pre/post preview + CAP-01 signoff reuse; GET-only | `make test` |
| Live verify | Human at `wave-acceptance` | `.venv/bin/python -m tests.verify.verify_closure_preview` |
| Ground check | Assigned REQs + boundaries | N/A — `/ground-spec` Pass-2 |

> P15 applicable — new GET: `/api/v1/initiatives/{initiative_id}/closure`.

### Human wave-acceptance (after loop-spec + Draft PR)

- [ ] Run `.venv/bin/python -m tests.verify.verify_closure_preview`
- [ ] Inspect pre/post + CAP-01 signoff fields; no GitHub/board writes
- [ ] Label tip `wave-accepted`
- [ ] Tip hygiene before Pass-2 closeout

---

### Tracker / PR (read-only context)

- Initiative: INIT-GATEFLOW-011
- Issue: [#170](https://github.com/drivestream-lab/gateflow/issues/170) (EPIC [#160](https://github.com/drivestream-lab/gateflow/issues/160))
- Spec path: `docs/specification/product/INIT-GATEFLOW-011-gateflow.md`
- Verify command (human): `.venv/bin/python -m tests.verify.verify_closure_preview`
- ADRs in scope: ADR-001, ADR-003, ADR-005, ADR-009, ADR-010
- Wave head: `develop` @ `c114e94`

---

### Checklist publish readiness (on `pass`)

| Field | Value |
|-------|-------|
| Workflow outcome | `pass` — gate verdict PASS; WorkManifest clean; commands resolved |
| Next | `loop-spec` (`skill`) — `external_action: false` |
| Forge (this hop) | `commit_workspace` **required** — publish `Pre-Implement-INIT-GATEFLOW-011-W9.md` to bound `head_ref` |
| Later | After `/loop-spec`, `wave-pr-action` opens Draft PR |

Recommend `/commit-workspace` after authorization. Do not open the PR here.

---

### Merge order (if cross-module / cross-service)

N/A — single-repo. TASK-W9-01 → TASK-W9-02 → TASK-W9-03.

```yaml
handoff:
  contract: sdd-delivery/v2
  stage: pre-implement
  outcome: pass
  artifact:
    path: docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W9.md
  blockers: []
  signals:
    initiative: INIT-GATEFLOW-011
    delivery_wave: W9
    ticket_id: "170"
    ticket_url: https://github.com/drivestream-lab/gateflow/issues/170
    epic_ticket_id: "160"
    epic_ticket_url: https://github.com/drivestream-lab/gateflow/issues/160
    wave_head: develop
    wave_head_sha: c114e9443007d12add56f5d201a531fcd7d526c5
    wave_branch_planned: feature/INIT-GATEFLOW-011-w9-closure-preview
    prior_wave: W8
    prior_wave_approved: true
    prior_ground_report: docs/specification/reports/Ground-Report-INIT-GATEFLOW-011-W8.md
    manifest_depends_on: [W1, W8]
    tasks:
      - TASK-W9-01
      - TASK-W9-02
      - TASK-W9-03
    implements:
      - REQ-25
      - REQ-26
      - REQ-27
      - REQ-28
    check_command: make check
    test_command: make test
    verify_command: .venv/bin/python -m tests.verify.verify_closure_preview
    ground_command: "N/A — /ground-spec Pass-2 pin skill"
    p15_applicable: true
    live_script_planned: tests/verify/verify_closure_preview.py
  next_candidates:
    - loop-spec
  human_checkpoint: false
  external_action: false
  forge:
    action: commit_workspace
    commit_workspace: required
    head_ref: develop
    paths:
      - docs/specification/reports/Pre-Implement-INIT-GATEFLOW-011-W9.md
```
