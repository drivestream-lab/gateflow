# Cursor local SDK spike — INIT-GATEFLOW-003 W0 (TASK-W0-04 / TDD §3.3)

| Field | Value |
|-------|-------|
| Date | 2026-07-24 |
| Package | `cursor-sdk==1.0.24` (Poetry) |
| Scope | Laptop / in-process API contract (Docker spike is W1) |

## Contract confirmed (package inspection + live path)

Official local path (no Cursor Cloud):

```text
client = await AsyncClient.launch_bridge(workspace=<cwd>, local=LocalAgentOptions(cwd=<cwd>))
agent = await AsyncAgent.create(client=..., api_key=<CURSOR_API_KEY>, local=..., model=composer-2)
run = await agent.send(<prompt>)
result = await run.wait()  # status: finished | error | cancelled | expired
await client.aclose()  # terminates owned bridge subprocess
```

- `AsyncClient(...)` alone is **insufficient** — local mode needs a bridge endpoint via `launch_bridge`.
- Programme ids like `cursor/auto` must map to SDK ids (`composer-2` / `default`); raw `cursor/auto` is rejected by the SDK.
- `cloud=` must never be passed (REQ-27).

## Live `send()` attempt (via `CursorAgentRunner`)

| Step | Result |
|------|--------|
| Settings load with `CURSOR_API_KEY` | **pass** |
| `launch_bridge` | **pass** |
| `AsyncAgent.create` + `send` + `wait` (first attempt) | **fail** — `status=error` after ~97 min; no auth failure; agent lacked skill definition and searched too long |
| Unit coverage | **pass** — mocked SUCCESS/FAILED in `tests/unit/test_cursor_agent_runner.py` |

## Live agent execution (`gateflow-w0-spike` skill)

| Step | Result |
|------|--------|
| Skill definition | **pass** — `.harness/skills/gateflow-w0-spike/SKILL.md` |
| Agent invoked with `prompt_context.spike=true` | **pass** |
| Workspace coding work | **pass** — evidence JSON + spike report update (see `.gateflow/evidence/w0-spike-live.json`) |
| Agent response | **pass** — `gateflow-w0-spike-ok` |
| Wall clock | **pass** — single fast agent turn (not multi-hour) |

**Notes for W1:** First `send()` attempt failed because `gateflow-w0-spike` had no skill file; agent wandered until timeout. Skill now pinned locally. Investigate bridge cleanup (`Event loop is closed` on subprocess del). Docker spike should confirm bridge binary in the worker image.

## Conclusion

- In-process `cursor-sdk` + `launch_bridge` + `LocalAgentOptions(cwd)` is the correct W0 wiring (**pass**).
- Credentials + bridge start work with a real key (**pass**).
- Live agent coding work via `gateflow-w0-spike` skill (**pass**) — satisfies TASK-W0-04 laptop spike evidence.
- Prior long-running `send()` with `status=error` remains a W1 follow-up (timeouts / prompt discipline); not a W0 skeleton blocker.
