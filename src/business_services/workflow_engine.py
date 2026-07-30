"""WorkflowEngine — resolve next node from pin workflow + handoff (no dispatch)."""

from pathlib import Path
from typing import Any, Optional

import yaml
from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.models.forge_models import NodeForgePolicy, parse_node_forge
from src.models.forge_types import AuthorizationModeType
from src.models.handoff_models import HandoffEnvelope, ResolvedWorkflowNode

DEFAULT_WORKFLOW_PATH = Path("prayog-skills/workflow.yaml")
DEFAULT_CONTRACT_PATH = Path("prayog-skills/delivery-contract.yaml")
INSTALLED_CONTRACT = "sdd-delivery/v2"


class WorkflowEngine(BaseBusinessService):
    """Load pinned workflow artifacts and resolve the next node (W0: resolve only)."""

    @inject
    def __init__(self) -> None:
        super().__init__()
        self._workflow: Optional[dict[str, Any]] = None
        self._contract_id: Optional[str] = None

    def load_pin(
        self,
        workflow_path: Path = DEFAULT_WORKFLOW_PATH,
        contract_path: Path = DEFAULT_CONTRACT_PATH,
    ) -> None:
        if not workflow_path.is_file():
            raise FileNotFoundError(f"Pinned workflow not found: {workflow_path}")
        if not contract_path.is_file():
            raise FileNotFoundError(f"Pinned delivery-contract not found: {contract_path}")

        workflow_raw = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
        contract_raw = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
        if not isinstance(workflow_raw, dict):
            raise ValueError("workflow.yaml must be a mapping")
        if not isinstance(contract_raw, dict):
            raise ValueError("delivery-contract.yaml must be a mapping")

        self._workflow = workflow_raw
        self._contract_id = str(
            workflow_raw.get("contract") or contract_raw.get("id") or INSTALLED_CONTRACT
        )
        self.logger.info(
            "Workflow pin loaded",
            workflow_path=str(workflow_path),
            contract_id=self._contract_id,
        )

    def resolve_next(self, handoff: HandoffEnvelope) -> ResolvedWorkflowNode:
        """Resolve next node from handoff.stage + handoff.outcome. No allowlists."""
        if self._workflow is None:
            self.load_pin()
        assert self._workflow is not None

        if handoff.contract != (self._contract_id or INSTALLED_CONTRACT):
            raise ValueError(
                f"Handoff contract {handoff.contract!r} does not match "
                f"installed {(self._contract_id or INSTALLED_CONTRACT)!r}"
            )

        nodes = self._workflow.get("nodes")
        if not isinstance(nodes, dict):
            raise ValueError("workflow.yaml missing nodes mapping")

        current = nodes.get(handoff.stage)
        if not isinstance(current, dict):
            raise ValueError(f"Unknown workflow stage: {handoff.stage}")

        outcomes = current.get("outcomes")
        if not isinstance(outcomes, dict):
            raise ValueError(f"Stage {handoff.stage} missing outcomes mapping")

        next_id = outcomes.get(handoff.outcome)
        if next_id is None:
            raise ValueError(f"No transition for stage={handoff.stage} outcome={handoff.outcome}")
        next_id_str = str(next_id)
        resolved = self.get_node(next_id_str)
        self.logger.info(
            "Resolved next workflow node",
            from_stage=handoff.stage,
            outcome=handoff.outcome,
            next_node=resolved.node_id,
            node_type=resolved.node_type,
            dispatch=resolved.dispatch,
            commit_workspace=resolved.forge.commit_workspace.value,
            authorization=(
                resolved.authorization.value if resolved.authorization is not None else None
            ),
        )
        return resolved

    def get_node(self, node_id: str) -> ResolvedWorkflowNode:
        """Look up a node by id from the pin (includes forge policy)."""
        if self._workflow is None:
            self.load_pin()
        assert self._workflow is not None
        nodes = self._workflow.get("nodes")
        if not isinstance(nodes, dict):
            raise ValueError("workflow.yaml missing nodes mapping")
        raw = nodes.get(node_id)
        if not isinstance(raw, dict):
            raise ValueError(f"Unknown workflow node: {node_id}")
        return self._to_resolved(node_id, raw)

    def known_node_ids(self) -> set[str]:
        """Return all node ids from the pinned workflow (no allowlists)."""
        if self._workflow is None:
            self.load_pin()
        assert self._workflow is not None
        nodes = self._workflow.get("nodes")
        if not isinstance(nodes, dict):
            raise ValueError("workflow.yaml missing nodes mapping")
        return {str(nid) for nid in nodes.keys()}

    def require_orchestrated_skill(self, node_id: str) -> ResolvedWorkflowNode:
        """Fail-fast: node must exist, be skill, and dispatch=orchestrated."""
        resolved = self.get_node(node_id)
        if resolved.node_type != "skill" or resolved.dispatch != "orchestrated":
            raise ValueError(
                f"start_node {node_id!r} must be type=skill with dispatch=orchestrated "
                f"(got type={resolved.node_type!r} dispatch={resolved.dispatch!r})"
            )
        return resolved

    @staticmethod
    def _to_resolved(node_id: str, raw: dict[str, Any]) -> ResolvedWorkflowNode:
        node_type = str(raw.get("type", "unknown"))
        dispatch_raw = raw.get("dispatch")
        dispatch = str(dispatch_raw) if dispatch_raw is not None else None
        next_outcomes = raw.get("outcomes")
        outcomes_map = (
            {str(k): str(v) for k, v in next_outcomes.items()}
            if isinstance(next_outcomes, dict)
            else {}
        )
        forge: NodeForgePolicy = parse_node_forge(raw.get("forge"))
        authorization = WorkflowEngine._parse_authorization(node_id, node_type, raw)
        return ResolvedWorkflowNode(
            node_id=node_id,
            node_type=node_type,
            dispatch=dispatch,
            outcomes=outcomes_map,
            forge=forge,
            authorization=authorization,
        )

    @staticmethod
    def _parse_authorization(
        node_id: str,
        node_type: str,
        raw: dict[str, Any],
    ) -> AuthorizationModeType | None:
        """Require authorization on external-action; ignore elsewhere."""
        if node_type != "external-action":
            return None
        raw_auth = raw.get("authorization")
        if raw_auth is None:
            raise ValueError(
                f"external-action node {node_id!r} missing required authorization "
                f"(expected 'explicit' or 'automated')"
            )
        try:
            return AuthorizationModeType(str(raw_auth))
        except ValueError as exc:
            raise ValueError(
                f"external-action node {node_id!r} has unknown authorization "
                f"{raw_auth!r} (expected 'explicit' or 'automated')"
            ) from exc


def get_workflow_engine() -> WorkflowEngine:
    from src.di.dependency_container import provide_service

    return provide_service(WorkflowEngine)
