# Docker / image spike — INIT-GATEFLOW-003 W1 (TASK-W1-01 / TDD §3.3)

| Field | Value |
|-------|-------|
| Date | 2026-07-24 |
| Image | `Dockerfile` → tag `gateflow-w1-spike:local` |
| Package | `cursor-sdk` via Poetry main deps (installed in image builder stage) |
| Scope | Gateflow-like Linux worker image + `CURSOR_API_KEY` + cwd |


> **Living supersession (config carrier):** `config/programme.yaml` / YAML `ProgrammeConfig` load are **removed**. Live authority is env (`GATEFLOW_*`), wave-start API, and pin `workflow.yaml` — ADR-004, INIT-002 A-7, as-built, and `docs/specification/reports/README.md`. Mentions below are wave-time evidence only.

## Contract probed

Official local path inside the container (same as laptop W0):

```text
AsyncClient.launch_bridge(workspace=<cwd>, local=LocalAgentOptions(cwd=<cwd>))
→ bridge subprocess from package-vendored Node
→ await client.aclose()
```

Vendored bits (no separate Node install required on the image):

| Path | Role |
|------|------|
| `…/cursor_sdk/_vendor/bridge/bin/node` | Linux Node binary shipped with `cursor-sdk` |
| `…/cursor_sdk/_vendor/bridge/bin/cursor-sdk-bridge` | Bridge launcher script |

## Results

| Step | Result |
|------|--------|
| `docker build -t gateflow-w1-spike:local .` | **pass** |
| Import `cursor_sdk` + `LocalAgentOptions` in runtime image | **pass** |
| Vendor `node` + `cursor-sdk-bridge` present in site-packages | **pass** |
| `ldd` on vendored `node` (aarch64) | **pass** — no missing shared libs on `python:3.12-slim` |
| `launch_bridge` + `aclose` with `CURSOR_API_KEY` + cwd `/workspace` | **pass** |

## Image notes for workers

- Current `Dockerfile` already installs main Poetry deps (includes `cursor-sdk`); bridge Node is **vendored** — do not assume host Node.
- Slim base provides glibc/`libstdc++` needed by the Linux Node binary (verified via `ldd`).
- Inject `CURSOR_API_KEY` at runtime (env / secret store). Never bake the key into the image or committed programme config.
- Worker cwd must be the target workspace (bind-mount or checkout) so `LocalAgentOptions(cwd=…)` matches the run workspace.
- Full Scenario B prove-it (`send`/`wait` + coding work) is **TASK-W1-04** live verify — this spike only proves bridge start in-image.

## Blockers

None for W1 Scenario B exit based on this spike.

## Conclusion

**pass** — `cursor-sdk` bridge works in the Gateflow Docker image with `CURSOR_API_KEY` + cwd.
