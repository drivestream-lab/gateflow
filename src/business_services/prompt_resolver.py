"""PromptResolver — pin package resolve / validate / {{var}} render (ADR-007)."""

import re
from pathlib import Path

import yaml
from injector import inject

from src.business_services.base_business_service import BaseBusinessService
from src.models.prompt_package_models import (
    BoundPromptInputs,
    PromptPackageSchemaDocument,
    PromptResolveError,
    RenderedPrompt,
    ResolvedPromptPackage,
)

_PLACEHOLDER_RE = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")
_FORBIDDEN_ENGINE_RE = re.compile(
    r"\{\%|\%\}|\{\#|\#\}|\{\{\s*[^}]+\|[^\s}]|\{\{\s*[^}]+\s+[^}]+\}\}"
)
_PIN_AREAS = ("development", "requirements")


class PromptResolver(BaseBusinessService):
    """Resolve pin prompt packages and render simple ``{{var}}`` substitution."""

    @inject
    def __init__(self) -> None:
        super().__init__()

    def resolve_package(self, workspace_root: str, skill_id: str) -> ResolvedPromptPackage:
        """Locate ``prompts/`` under pin skills tree; fail closed if missing."""
        cleaned_skill = skill_id.strip()
        if not cleaned_skill:
            raise PromptResolveError("prompt_package_missing", detail="empty skill_id")
        root = Path(workspace_root)
        for area in _PIN_AREAS:
            prompts_dir = root / "prayog-skills" / "skills" / area / cleaned_skill / "prompts"
            template_path = prompts_dir / "template.md"
            schema_path = prompts_dir / "schema.yaml"
            if template_path.is_file() and schema_path.is_file():
                return self._load_package(
                    prompts_dir=prompts_dir,
                    template_path=template_path,
                    schema_path=schema_path,
                    skill_id=cleaned_skill,
                )
        raise PromptResolveError(
            "prompt_package_missing",
            detail=f"no prompts package for skill_id={cleaned_skill!r}",
        )

    def bind_and_render(
        self,
        package: ResolvedPromptPackage,
        bound_inputs: BoundPromptInputs,
    ) -> RenderedPrompt:
        """Validate bound map against schema and render simple ``{{var}}`` only."""
        values = self._validate_bound_map(package.package_schema, bound_inputs)
        message = self._render_template(package.template_text, package.package_schema, values)
        return RenderedPrompt(
            message=message,
            prompt_id=package.prompt_id,
            prompt_revision=package.prompt_revision,
        )

    def _load_package(
        self,
        *,
        prompts_dir: Path,
        template_path: Path,
        schema_path: Path,
        skill_id: str,
    ) -> ResolvedPromptPackage:
        try:
            raw = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise PromptResolveError(
                "prompt_package_unreadable",
                detail=str(exc),
            ) from exc
        if not isinstance(raw, dict):
            raise PromptResolveError(
                "prompt_schema_invalid", detail="schema root must be a mapping"
            )
        try:
            schema = PromptPackageSchemaDocument.model_validate(raw)
        except Exception as exc:
            raise PromptResolveError("prompt_schema_invalid", detail=str(exc)) from exc
        if schema.prompt_id != skill_id:
            raise PromptResolveError(
                "prompt_schema_invalid",
                detail=(
                    f"schema prompt_id {schema.prompt_id!r} does not match skill_id {skill_id!r}"
                ),
            )
        try:
            template_text = template_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise PromptResolveError(
                "prompt_package_unreadable",
                detail=str(exc),
            ) from exc
        return ResolvedPromptPackage(
            prompt_id=schema.prompt_id,
            prompt_revision=schema.revision,
            template_text=template_text,
            package_schema=schema,
            package_dir=str(prompts_dir),
        )

    def _validate_bound_map(
        self,
        schema: PromptPackageSchemaDocument,
        bound_inputs: BoundPromptInputs,
    ) -> dict[str, str]:
        raw = {
            "ticket": bound_inputs.ticket,
            "initiative": bound_inputs.initiative,
            "skill_id": bound_inputs.skill_id,
            "workspace": bound_inputs.workspace,
            "handoff_path": bound_inputs.handoff_path,
        }
        values: dict[str, str] = {}
        for name, decl in schema.variables.items():
            present = name in raw and raw[name] is not None
            value = "" if not present else str(raw[name])
            if decl.required and value.strip() == "":
                raise PromptResolveError(
                    "prompt_bind_required_missing",
                    detail=f"required variable {name!r} missing or empty",
                )
            values[name] = value if present else ""
        return values

    def _render_template(
        self,
        template_text: str,
        schema: PromptPackageSchemaDocument,
        values: dict[str, str],
    ) -> str:
        if _FORBIDDEN_ENGINE_RE.search(template_text):
            raise PromptResolveError(
                "prompt_template_engine_feature",
                detail="only simple {{var}} substitution is supported",
            )
        declared = set(schema.variables.keys())
        placeholders = set(_PLACEHOLDER_RE.findall(template_text))
        undeclared = placeholders - declared
        if undeclared:
            raise PromptResolveError(
                "prompt_template_undeclared_var",
                detail=f"undeclared placeholders: {sorted(undeclared)}",
            )

        def _sub(match: re.Match[str]) -> str:
            name = match.group(1)
            return values.get(name, "")

        return _PLACEHOLDER_RE.sub(_sub, template_text)


def get_prompt_resolver() -> PromptResolver:
    from src.di.dependency_container import provide_service

    return provide_service(PromptResolver)
