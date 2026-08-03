# W0 prove-out checklist — INIT-GATEFLOW-009

| Field | Value |
|-------|-------|
| Initiative | INIT-GATEFLOW-009 |
| Wave | W0 |
| Implements | REQ-2 |
| Purpose | Preconditions PE must satisfy before W1 spec-lane live prove-out |
| Date | 2026-08-03 |

This checklist is the W0 deliverable for **REQ-2**. Complete every section before
starting W1 (`verify_spec_lane` / spec Pass-1 live prove-out). Do not invent
fixtures or meta paths at W1 time — bind them here first.

---

## 1. Meta PR accept preconditions (Gate 1)

Spec lane start **fail-closes** when meta accept-gate preconditions are not met
(ADR-010; REQ-3).

| Item | Required value | How to verify |
|------|----------------|---------------|
| Meta PR URL | `https://github.com/drivestream-lab/prayog-meta/pull/23` | PR exists; not closed without replacement |
| Approved meta head SHA | `6660aa4fefbcd80324cb970aa5bab642d3e5e0a1` | GitHub review APPROVED on this commit; label `impact-map-lgtm` present |
| PRD digest match | `sha256:76ab22b3c197b9d0cb6b08e6cea379c4e07b3a471b8a88203fddca6014c1c012` | Matches spec header + meta PR head `prd/INIT-GATEFLOW-009.md` |
| Impact-map revision | `1` | Matches spec header + `prayog-meta/prd/reports/Impact-Map-INIT-GATEFLOW-009.md` |
| Repo scope digest | `sha256:d0a2b62632113db0fa64cb7d7e63dc393fa5a8217092dda242a99b3392978e9b` | gateflow is in affected scope (not deferred) |
| Initiative id alignment | `INIT-GATEFLOW-009` | Derived from meta PR title/labels matches request `initiative_id` |

**PE action:** If meta head moves after Gate 1 approval, re-confirm digest/revision
alignment before W1 start — do not reuse stale head without re-approval.

---

## 2. Dual workspace bind (spec lane)

Per ADR-010, spec lane requires **two absolute filesystem roots**:

| Bind key | Role | Example (local dogfood) |
|----------|------|-------------------------|
| `workspace` | App coding root — durable writes / forge head | `/Users/…/gateflow` |
| `meta_workspace` | Meta read root — Gate 1 package intake | `/Users/…/prayog-meta` |

**Pre-flight checks:**

- [ ] `workspace` path exists and is a git checkout of `drivestream-lab/gateflow`
- [ ] `meta_workspace` path exists and is a git checkout of `drivestream-lab/prayog-meta`
- [ ] Meta checkout contains `prd/INIT-GATEFLOW-009.md` and impact map at revision `1`
- [ ] Both paths are **absolute** (relative paths fail closed at API edge)
- [ ] Meta tree is **read intake only** — durable spec writes target app `workspace` / app forge head

**API fields** (on `POST /api/v1/waves/spec/start` body):

```yaml
meta_pr_url: https://github.com/drivestream-lab/prayog-meta/pull/23
meta_workspace: /absolute/path/to/prayog-meta
workspace: /absolute/path/to/gateflow
org: drivestream-lab
repo: gateflow
```

---

## 3. Programme token

All wave mutations require programme-token auth (ADR-005).

| Item | Where | Notes |
|------|-------|-------|
| `PROGRAMME_SERVICE_TOKEN` | Verify client `.env` | Signs API calls from `verify_spec_lane` |
| Gateflow runtime auth | Gateflow `.env` (API + worker) | Must accept the same token class |
| 401 without token | Unit: `test_programme_token_api` | Confirms fail-closed edge |

**PE action:**

```bash
# verify client (tests/verify/*)
set -a && source .env && set +a
# confirm token present — never commit .env
test -n "$PROGRAMME_SERVICE_TOKEN" && echo "token set"
```

---

## 4. Reviewer tip-inspection steps (W1 success criteria)

W1 success (REQ-8) requires human attestation that the **Draft Spec PR tip**
contains committed outputs from automated orchestrated hops — an empty Draft Spec PR
does **not** satisfy initiative success.

After W1 live run completes, reviewer inspects the Draft Spec PR tip:

| Step | What to check |
|------|---------------|
| 1 | PR exists (opened/updated by automated `spec-pr-action`) |
| 2 | PR tip includes artifacts from orchestrated hops executed on the run (e.g. spec slice, feasibility report as chain progresses) |
| 3 | Run timeline shows `api_trigger`, stage commits, and terminal `stopped` at honest gate |
| 4 | `run_stopped` event includes handoff context (`stage`, `outcome`, `blockers`, `next_candidates`) |
| 5 | Run record exposes `pr_number` when walker reached `spec-pr-action` |
| 6 | No forbidden forge mutate after stop (no merge, no `*-lgtm` labels) |

**Expected W1 stop (pin `v0.5.0-rc.2`, Q-1 resolution):**

- Happy path: orchestrated chain `spec-draft` → automated `spec-pr-action` →
  `initiative-feasibility` → `spec-technical-review` → **STOP** at
  `technical-review-approval` (human-checkpoint)
- Blocked path: `spec-draft` outcome `blocked` → STOP at `spec-human-decision`

Record attestation in `docs/specification/reports/Live-Verify-INIT-GATEFLOW-009-W1.md`
(W1 deliverable — not this checklist).

---

## 5. Live-verify config knobs (W1 — `tests/config.yaml` / `verify_spec_lane`)

W1 live prove-out uses the opt-in script — **not** `verify_all`.

### Runtime prerequisites

| Service | Required | Notes |
|---------|----------|-------|
| Gateflow API + worker | yes | `make run` in separate terminal |
| Postgres (migrated) | yes | `runs.meta_pr_url` / `meta_head_sha` columns |
| `CURSOR_API_KEY` | yes | Gateflow runtime `.env` (not verify config) |
| GitHub forge creds | yes | Repo write for `ensure_branch` + `open_draft_pr` |

See runbook: `docs/runbooks/w1-runtime-api-worker.md`.

### `tests/config.yaml` — `features.spec_lane` (W1)

Copy from `tests/config.yaml.example` if missing. Minimum knobs:

```yaml
gateflow:
  base_url: http://127.0.0.1:8080
  require_worker: true
  org: drivestream-lab
  repo: gateflow
  base_branch: develop

features:
  spec_lane:
    enabled: true
    evidence: /absolute/path/to/run_gateflow/evidence/spec-lane-live-009-w1.json
    timeout_s: 3600
    wave_start:
      org: drivestream-lab
      repo: gateflow
      start_node: spec-draft
      runner: cursor
      model_id: cursor/auto
      initiative_id: INIT-GATEFLOW-009
      wave_id: W1
      ticket_id: "122"
      branch_slug: spec-lane
      meta_pr_url: https://github.com/drivestream-lab/prayog-meta/pull/23
      meta_workspace: /absolute/path/to/prayog-meta
      workspace: /absolute/path/to/gateflow
```

| Knob | Purpose |
|------|---------|
| `enabled: true` | Opt-in gate — script exits early when false |
| `require_worker: true` | Asserts worker is processing jobs |
| `start_node: spec-draft` | Must be orchestrated on active pin |
| `meta_pr_url` / `meta_workspace` / `workspace` | Dual bind per §2 |
| `initiative_id` / `wave_id` / `ticket_id` | Wave identity (board #122 for W1) |
| `branch_slug` | Slug only — do **not** prefix `w0-`/`w1-` (wave token inserted by naming) |
| `evidence` | Post-run JSON assert path (verify-only, not API field) |
| `timeout_s` | Poll budget for long Cursor hops |

### Command

```bash
set -a && source .env && set +a
make run   # separate terminal: API + worker
.venv/bin/python -m tests.verify.verify_spec_lane
```

**Exit 0** when: spec start accepted; Cursor stages success for executed hops;
terminal `stopped` at valid gate; `pr_number` present when reached.

### Pin consume (REQ-1 — confirmed W0)

| Item | Value |
|------|-------|
| Harness pin ref | `v0.5.0-rc.2` (`.harness-pin.yaml` `agent_skills.ref`) |
| Submodule HEAD | `72ad383a13499b7d4cc69ea5c44d30e9302d0685` (tag tip) |
| `spec-draft` dispatch | `orchestrated` |
| `spec-pr-action` authorization | `automated` |

---

## 6. W0 exit gate (this wave)

| Item | Status |
|------|--------|
| Pin consume verified (REQ-1) | Complete — see §5 pin table |
| This checklist published (REQ-2) | Complete — this file |
| W1 live verify | **Deferred** — execute per §5 after W0 Draft PR lands |

---

## References

- Spec: `docs/specification/product/INIT-GATEFLOW-009-gateflow.md` (REQ-1…REQ-2)
- Plan W0: `docs/specification/reports/Implementation-Plan-INIT-GATEFLOW-009.md` §2 W0
- ADR-010: dual workspace + meta intake authority
- ADR-009: forge publish/mutate authority
- Verify script: `tests/verify/verify_spec_lane.py`
- Tests README: `tests/README.md`
