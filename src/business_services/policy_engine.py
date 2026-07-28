"""PolicyEngine — dispatch / stop / block against pin + handoff (no allowlists)."""

from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.business_services.workflow_engine import WorkflowEngine
from src.configs.orchestration_settings import OrchestrationSettings
from src.models.control_plane_models import PolicyDecision, TriggerContext
from src.models.handoff_models import HandoffEnvelope
from src.models.policy_types import PolicyDecisionType

_STOP_NODE_TYPES = frozenset(
    {
        "human-checkpoint",
        "external-action",
        "decision",
        "terminal",
    }
)


class PolicyEngine(BaseBusinessService):
    """Evaluate whether the next workflow node may be agent-dispatched."""

    @inject
    def __init__(self, workflow_engine: WorkflowEngine) -> None:
        super().__init__()
        self._workflow_engine = workflow_engine

    def evaluate_dispatch(
        self,
        handoff: HandoffEnvelope,
        trigger: TriggerContext,
        retry_counter: int = 0,
    ) -> PolicyDecision:
        """Dispatch only skill + orchestrated; never silent on pin failure."""
        _ = trigger  # reserved for future repo/initiative policy signals
        orchestration = OrchestrationSettings.get_instance()

        if handoff.outcome == "findings" and retry_counter >= orchestration.findings_budget:
            return PolicyDecision(
                decision=PolicyDecisionType.STOP,
                block_reason=(
                    f"Retry budget exhausted: findings_budget={orchestration.findings_budget} "
                    f"retry_counter={retry_counter} last_stage={handoff.stage}"
                ),
                retry_counter=retry_counter,
            )

        if handoff.human_checkpoint:
            return PolicyDecision(
                decision=PolicyDecisionType.STOP,
                block_reason="handoff.human_checkpoint is true",
                retry_counter=retry_counter,
            )

        if handoff.blockers:
            return PolicyDecision(
                decision=PolicyDecisionType.STOP,
                block_reason=f"Unresolved handoff blockers: {', '.join(handoff.blockers)}",
                retry_counter=retry_counter,
            )

        try:
            next_node = self._workflow_engine.resolve_next(handoff)
        except FileNotFoundError as exc:
            return PolicyDecision(
                decision=PolicyDecisionType.BLOCK,
                block_reason=f"Pin unavailable: {exc}",
                retry_counter=retry_counter,
            )
        except ValueError as exc:
            return PolicyDecision(
                decision=PolicyDecisionType.BLOCK,
                block_reason=str(exc),
                retry_counter=retry_counter,
            )

        if next_node.node_type in _STOP_NODE_TYPES:
            return PolicyDecision(
                decision=PolicyDecisionType.STOP,
                next_node=next_node,
                block_reason=(f"Stop at node {next_node.node_id} type={next_node.node_type}"),
                retry_counter=retry_counter,
            )

        if next_node.node_type == "skill" and next_node.dispatch == "orchestrated":
            return PolicyDecision(
                decision=PolicyDecisionType.DISPATCH,
                next_node=next_node,
                retry_counter=retry_counter,
            )

        # Missing/manual dispatch ⇒ non-dispatch (manual observe / stop for W1)
        dispatch_label = next_node.dispatch or "manual"
        return PolicyDecision(
            decision=PolicyDecisionType.STOP,
            next_node=next_node,
            block_reason=(
                f"No AgentRunner dispatch for node {next_node.node_id} "
                f"type={next_node.node_type} dispatch={dispatch_label}"
            ),
            retry_counter=retry_counter,
        )


def get_policy_engine() -> PolicyEngine:
    from src.di.dependency_container import provide_service

    return provide_service(PolicyEngine)
