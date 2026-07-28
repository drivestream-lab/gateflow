# Specification reports

Wave evidence for feasibility, technical review, implementation plans, pre-implement
checklists, and ground reports.

## Living SSOT (do not treat wave docs as current inventory)

| Concern | Living source |
|---------|---------------|
| What is implemented today | `docs/specification/as-built/` |
| Architecture decisions | `docs/specification/adr/` |
| Active product requirements | `docs/specification/product/` |

**Programme config carrier:** `config/programme.yaml` and YAML `ProgrammeConfig`
load are **gone**. Non-secret runtime knobs live in env-backed settings
(`GATEFLOW_*`), wave-start API fields, and pin `prayog-skills/workflow.yaml`.
Secrets stay in env / secret store. See **ADR-004** and INIT-002 **A-7**.

Older reports below may still name `programme.yaml` as **wave-time evidence**
(what that wave designed or grounded). Those lines are **not** current module
inventory. Prefer as-built when the two disagree.
