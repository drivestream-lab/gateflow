"""Minimal WorkManifest plan fixtures for forge board-seed unit tests."""

PRAYOG_V1_BOARD_FIXTURE = """\
## 9. WorkManifest

```yaml
apiVersion: prayog/v1
kind: WorkManifest
initiative: INIT-TEST-001
epic:
  id: EPIC
  title: EPIC title
  body: epic
work:
  - id: W0
    title: Wave 0
    depends_on: []
    codebase: drivestream-lab/gateflow
    spec_path: docs/specification/product/INIT-GATEFLOW-008-gateflow.md
    verify_command: "N/A — unit fixture only"
    tasks:
      - id: TASK-W0-01
        implements: [REQ-1]
        depends_on: []
        files:
          - path: src/models/work_manifest_models.py
            action: modify
        exit:
          criteria:
            - "Pin workmanifest_contract subprocess runs and rejects launchpad/v1"
          proof:
            kind: command
            command: "make test"
            expected: "exit 0"
            evidence_expected: "Wave-Execution-TEST § TASK-W0-01"
    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: false
        reason: "unit-only fixture for forge board seed tests"
```
"""

LAUNCHPAD_V1_BOARD_FIXTURE = """\
## 9. WorkManifest

```yaml
apiVersion: launchpad/v1
kind: WorkManifest
initiative: INIT-TEST-001
epic:
  id: EPIC
  title: EPIC title
  body: epic
work:
  - id: W0
    title: Wave 0
```
"""
